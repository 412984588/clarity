"""Token 管理路由测试 - refresh 和 logout"""

from uuid import UUID

import pytest
from app.models.session import ActiveSession
from app.utils.security import decode_token
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


async def _register_user(client: AsyncClient, email: str, fingerprint: str) -> str:
    """注册用户并返回 access_token"""
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123",
            "device_fingerprint": fingerprint,
        },
    )
    assert response.status_code == 201
    return response.cookies["access_token"]


@pytest.mark.asyncio
async def test_logout_success_from_cookie(client: AsyncClient):
    """测试使用 cookie 成功登出"""
    token = await _register_user(
        client, "logout-cookie@example.com", "logout-device-001"
    )

    # 从 token 获取 session_id
    payload = decode_token(token)
    assert payload is not None
    session_id = UUID(str(payload.get("sid")))

    # 验证 session 存在
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(ActiveSession).where(ActiveSession.id == session_id)
        )
        active_session = result.scalar_one_or_none()
        assert active_session is not None

    # 登出（使用 cookie）
    response = await client.post(
        "/auth/logout",
        cookies={"access_token": token},
    )

    assert response.status_code == 204
    # 验证 cookies 被清除
    assert (
        "access_token" not in response.cookies or response.cookies["access_token"] == ""
    )
    assert (
        "refresh_token" not in response.cookies
        or response.cookies["refresh_token"] == ""
    )

    # 验证 session 已删除
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(ActiveSession).where(ActiveSession.id == session_id)
        )
        deleted_session = result.scalar_one_or_none()
        assert deleted_session is None


@pytest.mark.asyncio
async def test_logout_success_from_header(client: AsyncClient):
    """测试使用 Authorization header 成功登出"""
    token = await _register_user(
        client, "logout-header@example.com", "logout-device-002"
    )

    # 从 token 获取 session_id
    payload = decode_token(token)
    assert payload is not None
    session_id = UUID(str(payload.get("sid")))

    # 登出（使用 Authorization header）
    response = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    # 验证 session 已删除
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(ActiveSession).where(ActiveSession.id == session_id)
        )
        deleted_session = result.scalar_one_or_none()
        assert deleted_session is None


@pytest.mark.asyncio
async def test_logout_missing_token(client: AsyncClient):
    """测试没有提供 token 时返回 401"""
    response = await client.post("/auth/logout")

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_logout_invalid_token_format(client: AsyncClient):
    """测试无效的 token 格式返回 401"""
    response = await client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_logout_non_access_token(client: AsyncClient):
    """测试使用 refresh token 尝试登出返回 401"""
    # 注册用户
    register_response = await client.post(
        "/auth/register",
        json={
            "email": "logout-refresh@example.com",
            "password": "Password123",
            "device_fingerprint": "logout-device-003",
        },
    )
    assert register_response.status_code == 201
    refresh_token = register_response.cookies["refresh_token"]

    # 尝试使用 refresh token 登出
    response = await client.post(
        "/auth/logout",
        cookies={"access_token": refresh_token},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_logout_already_deleted_session(client: AsyncClient):
    """测试登出一个已被删除的 session"""
    token = await _register_user(
        client, "logout-deleted@example.com", "logout-device-004"
    )

    # 从 token 获取 session_id
    payload = decode_token(token)
    assert payload is not None
    session_id = UUID(str(payload.get("sid")))

    # 手动删除 session
    async with TestingSessionLocal() as session:
        from sqlalchemy import delete

        await session.execute(
            delete(ActiveSession).where(ActiveSession.id == session_id)
        )
        await session.commit()

    # 尝试登出（session 已经不存在，token 无效）
    response = await client.post(
        "/auth/logout",
        cookies={"access_token": token},
    )

    # session 不存在时 get_current_user 会失败，返回 401
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "SESSION_REVOKED"


@pytest.mark.asyncio
async def test_refresh_missing_token(client: AsyncClient):
    """测试刷新时缺少 refresh_token"""
    response = await client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "MISSING_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient):
    """测试成功刷新 token"""
    # 注册用户
    register_response = await client.post(
        "/auth/register",
        json={
            "email": "refresh-success@example.com",
            "password": "Password123",
            "device_fingerprint": "refresh-device-001",
        },
    )
    assert register_response.status_code == 201
    refresh_token = register_response.cookies["refresh_token"]

    # 刷新 token
    response = await client.post(
        "/auth/refresh",
        cookies={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "refresh-success@example.com"

    # 验证返回了 tokens（注意：可能重用相同的 session，所以 token 可能相同）
    new_access_token = response.cookies.get("access_token")
    new_refresh_token = response.cookies.get("refresh_token")
    assert new_access_token is not None
    assert new_refresh_token is not None


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """测试使用无效的 refresh_token"""
    response = await client.post(
        "/auth/refresh",
        cookies={"refresh_token": "invalid-token"},
    )

    assert response.status_code == 401
    # refresh_token 无效会被 service 层捕获并转换为认证错误
    detail = response.json().get("detail")
    # detail 可能是字符串 "INVALID_TOKEN" 或字典 {"error": "INVALID_TOKEN"}
    assert detail == "INVALID_TOKEN" or (
        isinstance(detail, dict) and detail.get("error") == "INVALID_TOKEN"
    )
