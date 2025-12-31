"""Password reset tests."""

import hashlib
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from app.models.password_reset import PasswordResetToken
from app.models.session import ActiveSession
from app.models.user import User
from app.utils.datetime_utils import utc_now
from app.utils.security import verify_password
from httpx import AsyncClient
from sqlalchemy import func, select
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
@patch(
    "app.routers.auth.password_reset.send_password_reset_email", new_callable=AsyncMock
)
async def test_forgot_password_unknown_email_returns_200(
    mock_send_email: AsyncMock, client: AsyncClient
):
    """未知邮箱也返回 200（不泄露账号存在性）"""
    mock_send_email.return_value = True

    response = await client.post(
        "/auth/forgot-password", json={"email": "unknown@example.com"}
    )
    assert response.status_code == 200
    assert (
        response.json()["message"] == "If an account exists, a reset link has been sent"
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(select(func.count(PasswordResetToken.id)))
        assert result.scalar() == 0

    # 未知邮箱不应该发送邮件
    mock_send_email.assert_not_called()


@pytest.mark.asyncio
@patch(
    "app.routers.auth.password_reset.send_password_reset_email", new_callable=AsyncMock
)
async def test_forgot_password_known_email(
    mock_send_email: AsyncMock, client: AsyncClient
):
    """已注册邮箱生成 token"""
    mock_send_email.return_value = True

    await client.post(
        "/auth/register",
        json={
            "email": "known@example.com",
            "password": "Password123",
            "device_fingerprint": "reset-device-001",
        },
    )

    response = await client.post(
        "/auth/forgot-password", json={"email": "known@example.com"}
    )
    assert response.status_code == 200

    async with TestingSessionLocal() as session:
        user_result = await session.execute(
            select(User).where(User.email == "known@example.com")
        )
        user = user_result.scalar_one()

        token_result = await session.execute(
            select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
        )
        token = token_result.scalar_one()
        assert token.token_hash
        assert len(token.token_hash) == 64

    # 已知邮箱应该发送邮件
    mock_send_email.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_success(client: AsyncClient):
    """有效 token 能重置密码"""
    await client.post(
        "/auth/register",
        json={
            "email": "reset-success@example.com",
            "password": "Password123",
            "device_fingerprint": "reset-device-002",
        },
    )

    token = "reset-success-token"
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # 在单独的 session 中创建 token
    async with TestingSessionLocal() as session:
        user_result = await session.execute(
            select(User).where(User.email == "reset-success@example.com")
        )
        user = user_result.scalar_one()
        user_id = user.id

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=utc_now() + timedelta(minutes=30),
        )
        session.add(reset_token)
        await session.commit()

    response = await client.post(
        "/auth/reset-password", json={"token": token, "new_password": "NewPassword123"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successful"

    # 在新的 session 中验证结果
    async with TestingSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.id == user_id))
        updated_user = user_result.scalar_one()
        assert verify_password("NewPassword123", updated_user.password_hash)

        token_result = await session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash
            )
        )
        used_token = token_result.scalar_one()
        assert used_token.used_at is not None


@pytest.mark.asyncio
async def test_reset_password_token_single_use(client: AsyncClient):
    """token 只能用一次"""
    await client.post(
        "/auth/register",
        json={
            "email": "reset-single-use@example.com",
            "password": "Password123",
            "device_fingerprint": "reset-device-003",
        },
    )

    token = "reset-single-use-token"
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # 在单独的 session 中创建 token
    async with TestingSessionLocal() as session:
        user_result = await session.execute(
            select(User).where(User.email == "reset-single-use@example.com")
        )
        user = user_result.scalar_one()
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=utc_now() + timedelta(minutes=30),
        )
        session.add(reset_token)
        await session.commit()

    first_response = await client.post(
        "/auth/reset-password", json={"token": token, "new_password": "NewPassword123"}
    )
    assert first_response.status_code == 200

    second_response = await client.post(
        "/auth/reset-password", json={"token": token, "new_password": "AnotherPass123"}
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"]["error"] == "INVALID_OR_EXPIRED_TOKEN"


@pytest.mark.asyncio
async def test_reset_password_expired_token(client: AsyncClient):
    """过期 token 失败"""
    await client.post(
        "/auth/register",
        json={
            "email": "reset-expired@example.com",
            "password": "Password123",
            "device_fingerprint": "reset-device-004",
        },
    )

    token = "reset-expired-token"
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # 在单独的 session 中创建过期 token
    async with TestingSessionLocal() as session:
        user_result = await session.execute(
            select(User).where(User.email == "reset-expired@example.com")
        )
        user = user_result.scalar_one()
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=utc_now() - timedelta(minutes=1),
        )
        session.add(reset_token)
        await session.commit()

    response = await client.post(
        "/auth/reset-password", json={"token": token, "new_password": "NewPassword123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "INVALID_OR_EXPIRED_TOKEN"


@pytest.mark.asyncio
async def test_reset_password_invalidates_sessions(client: AsyncClient):
    """重置密码后旧 session 失效"""
    await client.post(
        "/auth/register",
        json={
            "email": "reset-sessions@example.com",
            "password": "Password123",
            "device_fingerprint": "reset-device-005",
        },
    )

    token = "reset-sessions-token"
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    async with TestingSessionLocal() as session:
        user_result = await session.execute(
            select(User).where(User.email == "reset-sessions@example.com")
        )
        user = user_result.scalar_one()
        session_result = await session.execute(
            select(func.count(ActiveSession.id)).where(ActiveSession.user_id == user.id)
        )
        assert (session_result.scalar() or 0) > 0

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=utc_now() + timedelta(minutes=30),
        )
        session.add(reset_token)
        await session.commit()
        user_id = user.id

    response = await client.post(
        "/auth/reset-password", json={"token": token, "new_password": "NewPassword123"}
    )
    assert response.status_code == 200

    async with TestingSessionLocal() as session:
        session_result = await session.execute(
            select(func.count(ActiveSession.id)).where(ActiveSession.user_id == user_id)
        )
        assert (session_result.scalar() or 0) == 0
