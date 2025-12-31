"""
OAuth 相关测试

修复 Gemini 审查指出的问题：
1. 使用 AsyncMock 正确 mock async 方法
2. 简化 patch 写法
3. 更新测试匹配新的错误码
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# Google OAuth 测试用户信息 fixture
GOOGLE_USER_INFO = {
    "sub": "google-user-123",
    "email": "googleuser@gmail.com",
    "name": "Google User",
    "email_verified": True,
    "iss": "accounts.google.com",
}


@pytest.mark.asyncio
async def test_google_oauth_success(client: AsyncClient):
    """测试 Google OAuth 成功登录"""
    with patch(
        "app.services.oauth_service.OAuthService._verify_google_token",
        new_callable=AsyncMock,
        return_value=GOOGLE_USER_INFO,
    ):
        response = await client.post(
            "/auth/oauth/google",
            json={
                "id_token": "fake-google-token",
                "device_fingerprint": "oauth-device-001",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert "user" in data  # 验证返回用户信息


@pytest.mark.asyncio
async def test_google_oauth_creates_new_user(client: AsyncClient):
    """测试 Google OAuth 创建新用户"""
    mock_user_info = {
        "sub": "google-user-456",
        "email": "newgoogleuser@gmail.com",
        "name": "New Google User",
        "email_verified": True,
        "iss": "https://accounts.google.com",
    }

    with patch(
        "app.services.oauth_service.OAuthService._verify_google_token",
        new_callable=AsyncMock,
        return_value=mock_user_info,
    ):
        response = await client.post(
            "/auth/oauth/google",
            json={
                "id_token": "fake-google-token-new",
                "device_fingerprint": "oauth-device-002",
            },
        )

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_google_oauth_links_existing_user(client: AsyncClient):
    """测试 Google OAuth 绑定已存在的邮箱用户"""
    # 先用邮箱注册
    await client.post(
        "/auth/register",
        json={
            "email": "existinguser@gmail.com",
            "password": "Password123",
            "device_fingerprint": "oauth-device-003",
        },
    )

    # 然后用同样邮箱的 Google 账户登录
    mock_user_info = {
        "sub": "google-user-789",
        "email": "existinguser@gmail.com",
        "name": "Existing User",
        "email_verified": True,
        "iss": "accounts.google.com",
    }

    with patch(
        "app.services.oauth_service.OAuthService._verify_google_token",
        new_callable=AsyncMock,
        return_value=mock_user_info,
    ):
        response = await client.post(
            "/auth/oauth/google",
            json={
                "id_token": "fake-google-token-existing",
                "device_fingerprint": "oauth-device-003",
            },
        )

        assert response.status_code == 200
        assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_google_oauth_invalid_token(client: AsyncClient):
    """测试 Google OAuth 无效 token"""
    with patch(
        "app.services.oauth_service.OAuthService._verify_google_token",
        new_callable=AsyncMock,
        side_effect=ValueError("GOOGLE_TOKEN_INVALID: Token is invalid"),
    ):
        response = await client.post(
            "/auth/oauth/google",
            json={
                "id_token": "invalid-google-token",
                "device_fingerprint": "oauth-device-004",
            },
        )

        assert response.status_code == 401
        assert response.json()["error"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_google_oauth_email_not_verified(client: AsyncClient):
    """测试 Google OAuth 邮箱未验证"""
    with patch(
        "app.services.oauth_service.OAuthService._verify_google_token",
        new_callable=AsyncMock,
        side_effect=ValueError("EMAIL_NOT_VERIFIED"),
    ):
        response = await client.post(
            "/auth/oauth/google",
            json={
                "id_token": "fake-google-token-unverified",
                "device_fingerprint": "oauth-device-005",
            },
        )

        assert response.status_code == 400
        assert response.json()["error"] == "EMAIL_NOT_VERIFIED"


@pytest.mark.asyncio
async def test_apple_oauth_success(client: AsyncClient):
    """测试 Apple Sign-in 成功登录（首次登录，有 email）"""
    mock_user_info = {
        "sub": "apple-user-123",
        "email": "appleuser@icloud.com",
        "email_verified": True,
    }

    with patch(
        "app.services.oauth_service.OAuthService._verify_apple_token",
        new_callable=AsyncMock,
        return_value=mock_user_info,
    ):
        response = await client.post(
            "/auth/oauth/apple",
            json={
                "id_token": "fake-apple-token",
                "device_fingerprint": "apple-device-001",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert "user" in data  # 验证返回用户信息


@pytest.mark.asyncio
async def test_apple_oauth_invalid_token(client: AsyncClient):
    """测试 Apple Sign-in 无效 token"""
    with patch(
        "app.services.oauth_service.OAuthService._verify_apple_token",
        new_callable=AsyncMock,
        side_effect=ValueError("APPLE_TOKEN_INVALID: Invalid token"),
    ):
        response = await client.post(
            "/auth/oauth/apple",
            json={
                "id_token": "invalid-apple-token",
                "device_fingerprint": "apple-device-002",
            },
        )

        assert response.status_code == 401


@pytest.mark.asyncio
async def test_apple_oauth_subsequent_login_succeeds(client: AsyncClient):
    """测试 Apple Sign-in 后续登录（无 email）可通过 provider_id 找回用户"""
    first_login_info = {
        "sub": "apple-user-no-email",
        "email": "appleuser@icloud.com",
        "email_verified": True,
    }

    with patch(
        "app.services.oauth_service.OAuthService._verify_apple_token",
        new_callable=AsyncMock,
        return_value=first_login_info,
    ):
        first_response = await client.post(
            "/auth/oauth/apple",
            json={
                "id_token": "fake-apple-token-first",
                "device_fingerprint": "apple-device-003",
            },
        )
        assert first_response.status_code == 200

    subsequent_login_info = {
        "sub": "apple-user-no-email",
        "email": None,  # 后续登录无 email
        "email_verified": True,
    }

    with patch(
        "app.services.oauth_service.OAuthService._verify_apple_token",
        new_callable=AsyncMock,
        return_value=subsequent_login_info,
    ):
        response = await client.post(
            "/auth/oauth/apple",
            json={
                "id_token": "fake-apple-token-no-email",
                "device_fingerprint": "apple-device-003",
            },
        )

        assert response.status_code == 200
        assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_google_oauth_issuer_invalid(client: AsyncClient):
    """测试 Google OAuth 签发者无效"""
    with patch(
        "app.services.oauth_service.OAuthService._verify_google_token",
        new_callable=AsyncMock,
        side_effect=ValueError("INVALID_TOKEN_ISSUER"),
    ):
        response = await client.post(
            "/auth/oauth/google",
            json={
                "id_token": "fake-token-wrong-issuer",
                "device_fingerprint": "oauth-device-006",
            },
        )

        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_TOKEN_ISSUER"
