"""OAuth 相关测试"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch


@pytest.mark.asyncio
async def test_google_oauth_success(client: AsyncClient):
    """测试 Google OAuth 成功登录"""
    # Mock Google token 验证
    mock_user_info = {
        "sub": "google-user-123",
        "email": "googleuser@gmail.com",
        "name": "Google User",
        "email_verified": True,
        "iss": "accounts.google.com"
    }

    with patch("app.services.oauth_service.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = mock_user_info

        response = await client.post("/auth/oauth/google", json={
            "id_token": "fake-google-token",
            "device_fingerprint": "oauth-device-001"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_google_oauth_creates_new_user(client: AsyncClient):
    """测试 Google OAuth 创建新用户"""
    mock_user_info = {
        "sub": "google-user-456",
        "email": "newgoogleuser@gmail.com",
        "name": "New Google User",
        "email_verified": True,
        "iss": "https://accounts.google.com"
    }

    with patch("app.services.oauth_service.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = mock_user_info

        response = await client.post("/auth/oauth/google", json={
            "id_token": "fake-google-token-new",
            "device_fingerprint": "oauth-device-002"
        })

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_google_oauth_links_existing_user(client: AsyncClient):
    """测试 Google OAuth 绑定已存在的邮箱用户"""
    # 先用邮箱注册
    await client.post("/auth/register", json={
        "email": "existinguser@gmail.com",
        "password": "Password123",
        "device_fingerprint": "oauth-device-003"
    })

    # 然后用同样邮箱的 Google 账户登录
    mock_user_info = {
        "sub": "google-user-789",
        "email": "existinguser@gmail.com",
        "name": "Existing User",
        "email_verified": True,
        "iss": "accounts.google.com"
    }

    with patch("app.services.oauth_service.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = mock_user_info

        response = await client.post("/auth/oauth/google", json={
            "id_token": "fake-google-token-existing",
            "device_fingerprint": "oauth-device-003"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


@pytest.mark.asyncio
async def test_google_oauth_invalid_token(client: AsyncClient):
    """测试 Google OAuth 无效 token"""
    with patch("app.services.oauth_service.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.side_effect = ValueError("Token is invalid")

        response = await client.post("/auth/oauth/google", json={
            "id_token": "invalid-google-token",
            "device_fingerprint": "oauth-device-004"
        })

        assert response.status_code == 401
        assert response.json()["detail"]["error"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_google_oauth_email_not_verified(client: AsyncClient):
    """测试 Google OAuth 邮箱未验证"""
    mock_user_info = {
        "sub": "google-user-unverified",
        "email": "unverified@gmail.com",
        "name": "Unverified User",
        "email_verified": False,
        "iss": "accounts.google.com"
    }

    with patch("app.services.oauth_service.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = mock_user_info

        response = await client.post("/auth/oauth/google", json={
            "id_token": "fake-google-token-unverified",
            "device_fingerprint": "oauth-device-005"
        })

        assert response.status_code == 400
        assert response.json()["detail"]["error"] == "EMAIL_NOT_VERIFIED"


@pytest.mark.asyncio
async def test_apple_oauth_success(client: AsyncClient):
    """测试 Apple Sign-in 成功登录"""
    mock_apple_keys = {
        "keys": [{
            "kty": "RSA",
            "kid": "test-kid",
            "use": "sig",
            "alg": "RS256",
            "n": "test-n",
            "e": "AQAB"
        }]
    }

    mock_payload = {
        "sub": "apple-user-123",
        "email": "appleuser@icloud.com",
        "email_verified": "true",
        "iss": "https://appleid.apple.com"
    }

    with patch("app.services.oauth_service.OAuthService._get_apple_public_keys") as mock_keys, \
         patch("app.services.oauth_service.jwt.get_unverified_header") as mock_header, \
         patch("app.services.oauth_service.jwt.algorithms.RSAAlgorithm.from_jwk") as mock_jwk, \
         patch("app.services.oauth_service.jwt.decode") as mock_decode:

        mock_keys.return_value = mock_apple_keys
        mock_header.return_value = {"kid": "test-kid", "alg": "RS256"}
        mock_jwk.return_value = "fake-key"
        mock_decode.return_value = mock_payload

        response = await client.post("/auth/oauth/apple", json={
            "id_token": "fake-apple-token",
            "device_fingerprint": "apple-device-001"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


@pytest.mark.asyncio
async def test_apple_oauth_invalid_token(client: AsyncClient):
    """测试 Apple Sign-in 无效 token"""
    mock_apple_keys = {
        "keys": [{
            "kty": "RSA",
            "kid": "test-kid",
            "use": "sig",
            "alg": "RS256",
            "n": "test-n",
            "e": "AQAB"
        }]
    }

    with patch("app.services.oauth_service.OAuthService._get_apple_public_keys") as mock_keys, \
         patch("app.services.oauth_service.jwt.get_unverified_header") as mock_header, \
         patch("app.services.oauth_service.jwt.algorithms.RSAAlgorithm.from_jwk") as mock_jwk, \
         patch("app.services.oauth_service.jwt.decode") as mock_decode:

        mock_keys.return_value = mock_apple_keys
        mock_header.return_value = {"kid": "test-kid", "alg": "RS256"}
        mock_jwk.return_value = "fake-key"
        mock_decode.side_effect = Exception("Invalid token")

        response = await client.post("/auth/oauth/apple", json={
            "id_token": "invalid-apple-token",
            "device_fingerprint": "apple-device-002"
        })

        assert response.status_code == 401


@pytest.mark.asyncio
async def test_apple_oauth_email_not_provided(client: AsyncClient):
    """测试 Apple Sign-in 邮箱未提供（用户隐藏邮箱）"""
    # 直接 mock _verify_apple_token 方法返回 EMAIL_NOT_PROVIDED 错误
    with patch.object(
        __import__("app.services.oauth_service", fromlist=["OAuthService"]).OAuthService,
        "_verify_apple_token",
        side_effect=ValueError("EMAIL_NOT_PROVIDED")
    ):
        response = await client.post("/auth/oauth/apple", json={
            "id_token": "fake-apple-token-no-email",
            "device_fingerprint": "apple-device-003"
        })

        assert response.status_code == 400
        assert response.json()["detail"]["error"] == "EMAIL_NOT_PROVIDED"
