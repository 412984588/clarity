from uuid import UUID

import pytest
from app.main import app
from app.middleware.auth import get_current_user
from app.models.user import User
from app.utils.security import decode_token
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


def _user_from_access_token(access_token: str) -> User:
    """从 access_token 解码出 User 对象（用于 override dependency）"""
    payload = decode_token(access_token) or {}
    user_id = UUID(payload.get("sub"))
    return User(id=user_id, email="test@example.com", auth_provider="email")


async def _register_user(client: AsyncClient, email: str, fingerprint: str) -> str:
    """注册用户并返回 access_token"""
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Pass1234",  # 8位，包含大写字母和数字
            "device_fingerprint": fingerprint,
            "device_name": "test-device",
        },
    )
    assert response.status_code == 201
    return response.cookies["access_token"]


@pytest.mark.asyncio
async def test_account_export_returns_user_data(client: AsyncClient):
    token = await _register_user(client, "export-user@example.com", "export-device-1")
    user = _user_from_access_token(token)

    # Override dependency 以模拟认证
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = await client.get(
            "/account/export", headers={"Authorization": f"Bearer {token}"}
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "export-user@example.com"
    assert "password_hash" not in data["user"]
    assert data["devices"]


@pytest.mark.asyncio
async def test_account_delete_removes_user(client: AsyncClient):
    token = await _register_user(client, "delete-user@example.com", "delete-device-1")
    user = _user_from_access_token(token)

    # Override dependency 以模拟认证
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = await client.delete(
            "/account", headers={"Authorization": f"Bearer {token}"}
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 204

    # 验证用户已被删除
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        assert users == []

    # 验证删除后无法再访问（重新 override 以模拟已失效的 token）
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        followup = await client.get(
            "/account/export", headers={"Authorization": f"Bearer {token}"}
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    # 由于用户已删除，应该返回 404（而不是 401，因为 token 本身合法但用户不存在）
    assert followup.status_code == 404
