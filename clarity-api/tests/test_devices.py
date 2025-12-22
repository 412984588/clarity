"""设备与会话管理测试"""

from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.main import app
from app.middleware.auth import get_current_user
from app.models.device import Device
from app.models.session import ActiveSession
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.security import decode_token

# 使用 conftest.py 导出的 TestingSessionLocal
from tests.conftest import TestingSessionLocal


def _user_from_access_token(access_token: str) -> User:
    payload = decode_token(access_token) or {}
    user_id = UUID(payload.get("sub"))
    return User(id=user_id, email="test@example.com", auth_provider="email")


async def _set_subscription_tier(user_id: UUID, tier: str) -> None:
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one()
        subscription.tier = tier  # type: ignore[assignment]
        await session.commit()


async def _get_device_id(fingerprint: str) -> UUID:
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Device).where(Device.device_fingerprint == fingerprint)
        )
        device = result.scalar_one()
        return device.id  # type: ignore[return-value]


async def _get_session_id(device_id: UUID) -> UUID:
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(ActiveSession).where(ActiveSession.device_id == device_id)
        )
        session_obj = result.scalar_one()
        return session_obj.id  # type: ignore[return-value]


@pytest.mark.asyncio
async def test_list_devices(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "email": "device-list@example.com",
            "password": "Password123",
            "device_fingerprint": "device-list-001",
        },
    )
    access_token = response.json()["access_token"]
    user = _user_from_access_token(access_token)

    app.dependency_overrides[get_current_user] = lambda: user
    try:
        resp = await client.get(
            "/auth/devices", headers={"Authorization": f"Bearer {access_token}"}
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["is_active"] is True


@pytest.mark.asyncio
async def test_list_sessions(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "email": "session-list@example.com",
            "password": "Password123",
            "device_fingerprint": "session-list-001",
        },
    )
    access_token = response.json()["access_token"]
    user = _user_from_access_token(access_token)

    app.dependency_overrides[get_current_user] = lambda: user
    try:
        resp = await client.get(
            "/auth/sessions", headers={"Authorization": f"Bearer {access_token}"}
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_revoke_device_success(client: AsyncClient):
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": "revoke-device@example.com",
            "password": "Password123",
            "device_fingerprint": "device-old",
        },
    )
    access_token = register_resp.json()["access_token"]
    user = _user_from_access_token(access_token)
    await _set_subscription_tier(user.id, "standard")

    await client.post(
        "/auth/login",
        json={
            "email": "revoke-device@example.com",
            "password": "Password123",
            "device_fingerprint": "device-new",
        },
    )

    old_device_id = await _get_device_id("device-old")

    app.dependency_overrides[get_current_user] = lambda: user
    try:
        resp = await client.delete(
            f"/auth/devices/{old_device_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Device-Fingerprint": "device-new",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_cannot_revoke_current_device(client: AsyncClient):
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": "revoke-current@example.com",
            "password": "Password123",
            "device_fingerprint": "device-current",
        },
    )
    access_token = register_resp.json()["access_token"]
    user = _user_from_access_token(access_token)
    current_device_id = await _get_device_id("device-current")

    app.dependency_overrides[get_current_user] = lambda: user
    try:
        resp = await client.delete(
            f"/auth/devices/{current_device_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Device-Fingerprint": "device-current",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "CANNOT_REMOVE_CURRENT_DEVICE"


@pytest.mark.asyncio
async def test_revoke_limit_once_per_day(client: AsyncClient):
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": "revoke-limit@example.com",
            "password": "Password123",
            "device_fingerprint": "device-a",
        },
    )
    access_token = register_resp.json()["access_token"]
    user = _user_from_access_token(access_token)
    await _set_subscription_tier(user.id, "pro")

    await client.post(
        "/auth/login",
        json={
            "email": "revoke-limit@example.com",
            "password": "Password123",
            "device_fingerprint": "device-b",
        },
    )
    await client.post(
        "/auth/login",
        json={
            "email": "revoke-limit@example.com",
            "password": "Password123",
            "device_fingerprint": "device-c",
        },
    )

    device_a_id = await _get_device_id("device-a")
    device_b_id = await _get_device_id("device-b")

    app.dependency_overrides[get_current_user] = lambda: user
    try:
        first_resp = await client.delete(
            f"/auth/devices/{device_a_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Device-Fingerprint": "device-c",
            },
        )
        second_resp = await client.delete(
            f"/auth/devices/{device_b_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Device-Fingerprint": "device-c",
            },
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert first_resp.status_code == 204
    assert second_resp.status_code == 429
    assert second_resp.json()["detail"]["error"] == "REMOVAL_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_revoke_session_success(client: AsyncClient):
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": "revoke-session@example.com",
            "password": "Password123",
            "device_fingerprint": "session-old",
        },
    )
    access_token = register_resp.json()["access_token"]
    user = _user_from_access_token(access_token)
    await _set_subscription_tier(user.id, "standard")

    await client.post(
        "/auth/login",
        json={
            "email": "revoke-session@example.com",
            "password": "Password123",
            "device_fingerprint": "session-new",
        },
    )

    old_device_id = await _get_device_id("session-old")
    old_session_id = await _get_session_id(old_device_id)

    app.dependency_overrides[get_current_user] = lambda: user
    try:
        resp = await client.delete(
            f"/auth/sessions/{old_session_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_revoke_session_not_found(client: AsyncClient):
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": "revoke-session-missing@example.com",
            "password": "Password123",
            "device_fingerprint": "session-missing",
        },
    )
    access_token = register_resp.json()["access_token"]
    user = _user_from_access_token(access_token)

    app.dependency_overrides[get_current_user] = lambda: user
    try:
        resp = await client.delete(
            f"/auth/sessions/{uuid4()}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert resp.status_code == 404
    assert resp.json()["detail"]["error"] == "SESSION_NOT_FOUND"
