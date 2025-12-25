import pytest
import jwt
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.oauth_service import OAuthService, _apple_key_cache


@pytest.fixture
def oauth_service():
    db = MagicMock()
    db.execute = AsyncMock()
    return OAuthService(db)


@pytest.fixture(autouse=True)
def clear_apple_key_cache():
    _apple_key_cache.clear()
    yield
    _apple_key_cache.clear()


@pytest.mark.asyncio
async def test_exchange_apple_auth_code(oauth_service):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"keys": [{"kid": "apple-key-1"}]}

    with patch("app.services.oauth_service.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock()
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )
        keys = await oauth_service._get_apple_public_keys()

    assert keys["keys"][0]["kid"] == "apple-key-1"
    assert _apple_key_cache["keys"] == keys
    mock_client.return_value.__aenter__.return_value.get.assert_awaited_once_with(
        "https://appleid.apple.com/auth/keys"
    )


@pytest.mark.asyncio
async def test_verify_apple_identity_token(oauth_service):
    apple_keys = {"keys": [{"kid": "apple-key-1"}]}
    payload = {
        "sub": "apple-user-123",
        "email": "apple-user@example.com",
        "email_verified": "true",
    }

    with (
        patch.object(
            oauth_service, "_get_apple_public_keys", new_callable=AsyncMock
        ) as get_keys_mock,
        patch(
            "app.services.oauth_service.jwt.get_unverified_header",
            return_value={"kid": "apple-key-1"},
        ),
        patch(
            "app.services.oauth_service.jwt.algorithms.RSAAlgorithm.from_jwk",
            return_value="public-key",
        ),
        patch(
            "app.services.oauth_service.jwt.decode", return_value=payload
        ) as decode_mock,
    ):
        get_keys_mock.return_value = apple_keys
        result = await oauth_service._verify_apple_token("test-token")

    assert result["sub"] == "apple-user-123"
    assert result["email"] == "apple-user@example.com"
    assert result["email_verified"] is True
    decode_mock.assert_called_once()


@pytest.mark.asyncio
async def test_apple_auth_invalid_code(oauth_service):
    missing_keys = {"keys": [{"kid": "other-key"}]}
    valid_keys = {"keys": [{"kid": "apple-key-1"}]}

    with (
        patch.object(
            oauth_service, "_get_apple_public_keys", new_callable=AsyncMock
        ) as get_keys_mock,
        patch(
            "app.services.oauth_service.jwt.get_unverified_header",
            return_value={"kid": "apple-key-1"},
        ),
    ):
        get_keys_mock.return_value = missing_keys
        with pytest.raises(
            ValueError, match="APPLE_TOKEN_INVALID: APPLE_KEY_NOT_FOUND"
        ):
            await oauth_service._verify_apple_token("test-token")

    with (
        patch.object(
            oauth_service, "_get_apple_public_keys", new_callable=AsyncMock
        ) as get_keys_mock,
        patch(
            "app.services.oauth_service.jwt.get_unverified_header",
            return_value={"kid": "apple-key-1"},
        ),
        patch(
            "app.services.oauth_service.jwt.algorithms.RSAAlgorithm.from_jwk",
            return_value="public-key",
        ),
        patch(
            "app.services.oauth_service.jwt.decode",
            side_effect=jwt.ExpiredSignatureError(),
        ),
    ):
        get_keys_mock.return_value = valid_keys
        with pytest.raises(ValueError, match="APPLE_TOKEN_EXPIRED"):
            await oauth_service._verify_apple_token("test-token")

    with (
        patch.object(
            oauth_service, "_get_apple_public_keys", new_callable=AsyncMock
        ) as get_keys_mock,
        patch(
            "app.services.oauth_service.jwt.get_unverified_header",
            return_value={"kid": "apple-key-1"},
        ),
        patch(
            "app.services.oauth_service.jwt.algorithms.RSAAlgorithm.from_jwk",
            return_value="public-key",
        ),
        patch(
            "app.services.oauth_service.jwt.decode",
            side_effect=jwt.InvalidTokenError("bad token"),
        ),
    ):
        get_keys_mock.return_value = valid_keys
        with pytest.raises(ValueError, match="APPLE_TOKEN_INVALID: bad token"):
            await oauth_service._verify_apple_token("test-token")

    # Unlinked Apple account without email should be rejected early.
    with patch.object(
        oauth_service,
        "_get_user_by_provider",
        new_callable=AsyncMock,
        return_value=None,
    ):
        with pytest.raises(ValueError, match="OAUTH_ACCOUNT_NOT_LINKED"):
            await oauth_service._process_oauth_login(
                email=None,
                provider="apple",
                provider_id="apple-user-123",
                device_fingerprint="device-apple-1",
                device_name=None,
            )


@pytest.mark.asyncio
async def test_exchange_google_auth_code(oauth_service):
    idinfo = {
        "sub": "google-user-123",
        "email": "google-user@example.com",
        "name": "Google User",
        "picture": "https://example.com/avatar.png",
        "email_verified": True,
        "iss": "accounts.google.com",
    }

    with patch(
        "app.services.oauth_service.id_token.verify_oauth2_token", return_value=idinfo
    ) as verify_mock:
        result = await oauth_service._verify_google_token("test-token")

    assert result["sub"] == "google-user-123"
    assert result["email"] == "google-user@example.com"
    verify_mock.assert_called_once()


@pytest.mark.asyncio
async def test_verify_google_id_token(oauth_service):
    invalid_issuer = {
        "sub": "google-user-123",
        "email": "google-user@example.com",
        "email_verified": True,
        "iss": "https://invalid-issuer.example.com",
    }
    with patch(
        "app.services.oauth_service.id_token.verify_oauth2_token",
        return_value=invalid_issuer,
    ):
        with pytest.raises(ValueError, match="INVALID_TOKEN_ISSUER"):
            await oauth_service._verify_google_token("test-token")

    unverified_email = {
        "sub": "google-user-456",
        "email": "google-user@example.com",
        "email_verified": False,
        "iss": "accounts.google.com",
    }
    with patch(
        "app.services.oauth_service.id_token.verify_oauth2_token",
        return_value=unverified_email,
    ):
        with pytest.raises(ValueError, match="EMAIL_NOT_VERIFIED"):
            await oauth_service._verify_google_token("test-token")


@pytest.mark.asyncio
async def test_google_auth_invalid_code(oauth_service):
    with patch(
        "app.services.oauth_service.id_token.verify_oauth2_token",
        side_effect=ValueError("invalid token"),
    ):
        with pytest.raises(ValueError, match="GOOGLE_TOKEN_INVALID: invalid token"):
            await oauth_service._verify_google_token("bad-token")

    result = await oauth_service._get_user_by_provider("google", "")
    assert result is None
    oauth_service.db.execute.assert_not_awaited()
