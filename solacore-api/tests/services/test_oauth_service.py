"""OAuth Service 单元测试

测试范围:
1. Google token 验证（成功/失败）
2. Apple token 验证（成功/失败/公钥缓存）
3. 用户创建/获取逻辑
4. OAuth 登录流程
5. Google code 交换流程
6. 公开 API 方法
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.auth import OAuthRequest
from app.services.oauth_service import OAuthService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_db():
    """Mock 数据库会话"""
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def oauth_service(mock_db):
    """创建 OAuthService 实例"""
    return OAuthService(mock_db)


class TestVerifyGoogleToken:
    """测试 Google token 验证"""

    @pytest.mark.asyncio
    async def test_verify_google_token_success(self, oauth_service):
        """测试 Google token 验证成功"""
        mock_idinfo = {
            "sub": "google-123",
            "email": "user@gmail.com",
            "email_verified": True,
            "iss": "accounts.google.com",
            "name": "Test User",
            "picture": "https://example.com/photo.jpg",
        }

        with patch(
            "app.services.oauth_service.id_token.verify_oauth2_token",
            return_value=mock_idinfo,
        ):
            result = await oauth_service._verify_google_token("fake-token")

        assert result["sub"] == "google-123"
        assert result["email"] == "user@gmail.com"
        assert result["name"] == "Test User"
        assert result["picture"] == "https://example.com/photo.jpg"

    @pytest.mark.asyncio
    async def test_verify_google_token_invalid_issuer(self, oauth_service):
        """测试 Google token 签发者无效"""
        mock_idinfo = {
            "sub": "google-123",
            "email": "user@gmail.com",
            "email_verified": True,
            "iss": "malicious.com",  # 错误的签发者
        }

        with patch(
            "app.services.oauth_service.id_token.verify_oauth2_token",
            return_value=mock_idinfo,
        ):
            with pytest.raises(ValueError, match="INVALID_TOKEN_ISSUER"):
                await oauth_service._verify_google_token("fake-token")

    @pytest.mark.asyncio
    async def test_verify_google_token_email_not_verified(self, oauth_service):
        """测试 Google token 邮箱未验证"""
        mock_idinfo = {
            "sub": "google-123",
            "email": "user@gmail.com",
            "email_verified": False,  # 邮箱未验证
            "iss": "accounts.google.com",
        }

        with patch(
            "app.services.oauth_service.id_token.verify_oauth2_token",
            return_value=mock_idinfo,
        ):
            with pytest.raises(ValueError, match="EMAIL_NOT_VERIFIED"):
                await oauth_service._verify_google_token("fake-token")

    @pytest.mark.asyncio
    async def test_verify_google_token_invalid_token(self, oauth_service):
        """测试 Google token 无效（库抛出异常）"""
        with patch(
            "app.services.oauth_service.id_token.verify_oauth2_token",
            side_effect=ValueError("Invalid token"),
        ):
            with pytest.raises(ValueError, match="GOOGLE_TOKEN_INVALID"):
                await oauth_service._verify_google_token("invalid-token")


class TestVerifyAppleToken:
    """测试 Apple token 验证"""

    @pytest.mark.asyncio
    async def test_verify_apple_token_success(self, oauth_service):
        """测试 Apple token 验证成功"""
        mock_payload = {
            "sub": "apple-123",
            "email": "user@icloud.com",
            "email_verified": "true",
        }

        mock_header = {"kid": "key-001"}
        mock_keys = {
            "keys": [{"kid": "key-001", "kty": "RSA", "n": "fake_n", "e": "AQAB"}]
        }

        with (
            patch(
                "app.services.oauth_service.jwt.get_unverified_header",
                return_value=mock_header,
            ),
            patch("app.services.oauth_service.jwt.decode", return_value=mock_payload),
            patch.object(
                oauth_service, "_get_apple_public_keys", return_value=mock_keys
            ),
        ):
            result = await oauth_service._verify_apple_token("fake-apple-token")

        assert result["sub"] == "apple-123"
        assert result["email"] == "user@icloud.com"
        assert result["email_verified"] is True

    @pytest.mark.asyncio
    async def test_verify_apple_token_no_email(self, oauth_service):
        """测试 Apple token 无 email（后续登录场景）"""
        mock_payload = {
            "sub": "apple-123",
            # 无 email 字段（Apple 后续登录不返回）
        }

        mock_header = {"kid": "key-001"}
        mock_keys = {
            "keys": [{"kid": "key-001", "kty": "RSA", "n": "fake_n", "e": "AQAB"}]
        }

        with (
            patch(
                "app.services.oauth_service.jwt.get_unverified_header",
                return_value=mock_header,
            ),
            patch("app.services.oauth_service.jwt.decode", return_value=mock_payload),
            patch.object(
                oauth_service, "_get_apple_public_keys", return_value=mock_keys
            ),
        ):
            result = await oauth_service._verify_apple_token("fake-apple-token")

        assert result["sub"] == "apple-123"
        assert result["email"] is None

    @pytest.mark.asyncio
    async def test_verify_apple_token_key_not_found(self, oauth_service):
        """测试 Apple 公钥不存在"""
        mock_header = {"kid": "unknown-key"}
        mock_keys = {
            "keys": [{"kid": "key-001", "kty": "RSA", "n": "fake_n", "e": "AQAB"}]
        }

        with (
            patch(
                "app.services.oauth_service.jwt.get_unverified_header",
                return_value=mock_header,
            ),
            patch.object(
                oauth_service, "_get_apple_public_keys", return_value=mock_keys
            ),
        ):
            with pytest.raises(ValueError, match="APPLE_KEY_NOT_FOUND"):
                await oauth_service._verify_apple_token("fake-apple-token")

    @pytest.mark.asyncio
    async def test_verify_apple_token_expired(self, oauth_service):
        """测试 Apple token 已过期"""
        mock_header = {"kid": "key-001"}
        mock_keys = {
            "keys": [{"kid": "key-001", "kty": "RSA", "n": "fake_n", "e": "AQAB"}]
        }

        with (
            patch(
                "app.services.oauth_service.jwt.get_unverified_header",
                return_value=mock_header,
            ),
            patch(
                "app.services.oauth_service.jwt.decode",
                side_effect=__import__("jwt").ExpiredSignatureError,
            ),
            patch.object(
                oauth_service, "_get_apple_public_keys", return_value=mock_keys
            ),
        ):
            with pytest.raises(ValueError, match="APPLE_TOKEN_EXPIRED"):
                await oauth_service._verify_apple_token("expired-token")


class TestGetOrCreateUser:
    """测试用户创建/获取逻辑"""

    @pytest.mark.asyncio
    async def test_get_existing_user_by_email(self, oauth_service, mock_db):
        """测试获取已存在的用户（通过 email）"""
        existing_user = User(
            id=1,
            email="existing@example.com",
            auth_provider="google",
            auth_provider_id="old-google-123",
        )
        existing_user.subscription = Subscription(user_id=1, tier="free")

        # Mock 数据库查询返回现有用户
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_db.execute.return_value = mock_result

        user = await oauth_service._get_or_create_user(
            email="existing@example.com",
            provider="google",
            provider_id="new-google-456",
        )

        # 应该返回现有用户，并更新 provider_id
        assert user.email == "existing@example.com"
        assert user.auth_provider == "google"
        assert user.auth_provider_id == "new-google-456"  # 更新为新的 ID
        mock_db.add.assert_not_called()  # 不应该添加新用户

    @pytest.mark.asyncio
    async def test_create_new_user(self, oauth_service, mock_db):
        """测试创建新用户"""
        # Mock 数据库查询返回 None（用户不存在）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Mock flush 后设置用户 ID
        def mock_flush_side_effect():
            for call in mock_db.add.call_args_list:
                obj = call[0][0]
                if isinstance(obj, User):
                    obj.id = 999

        mock_db.flush.side_effect = mock_flush_side_effect

        _ = await oauth_service._get_or_create_user(
            email="newuser@example.com",
            provider="apple",
            provider_id="apple-789",
        )

        # 应该创建新用户
        assert mock_db.add.call_count == 2  # User + Subscription
        user_obj = mock_db.add.call_args_list[0][0][0]
        assert isinstance(user_obj, User)
        assert user_obj.email == "newuser@example.com"
        assert user_obj.auth_provider == "apple"
        assert user_obj.auth_provider_id == "apple-789"
        assert user_obj.password_hash is None  # OAuth 用户无密码

        # 应该创建 Free 订阅
        sub_obj = mock_db.add.call_args_list[1][0][0]
        assert isinstance(sub_obj, Subscription)
        assert sub_obj.tier == "free"

    @pytest.mark.asyncio
    async def test_existing_user_same_provider(self, oauth_service, mock_db):
        """测试已存在用户使用相同 provider 登录"""
        existing_user = User(
            id=1,
            email="user@example.com",
            auth_provider="google",
            auth_provider_id="google-old",
        )
        existing_user.subscription = Subscription(user_id=1, tier="pro")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_db.execute.return_value = mock_result

        user = await oauth_service._get_or_create_user(
            email="user@example.com",
            provider="google",
            provider_id="google-new",
        )

        # 应该更新 provider_id
        assert user.auth_provider_id == "google-new"
        mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_existing_user_different_provider(self, oauth_service, mock_db):
        """测试已存在用户尝试用不同 provider 登录"""
        existing_user = User(
            id=1,
            email="user@example.com",
            auth_provider="google",
            auth_provider_id="google-123",
        )
        existing_user.subscription = Subscription(user_id=1, tier="free")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_db.execute.return_value = mock_result

        user = await oauth_service._get_or_create_user(
            email="user@example.com",
            provider="apple",  # 不同的 provider
            provider_id="apple-456",
        )

        # 应该返回现有用户，但不更新 provider（防止覆盖原有绑定）
        assert user.auth_provider == "google"  # 保持原 provider
        assert user.auth_provider_id == "google-123"  # 保持原 ID
        mock_db.add.assert_not_called()


class TestProcessOAuthLogin:
    """测试完整 OAuth 登录流程"""

    @pytest.mark.asyncio
    async def test_process_oauth_login_new_user(self, oauth_service, mock_db):
        """测试新用户 OAuth 登录"""
        # Mock _get_user_by_provider 返回 None（新用户）
        with patch.object(oauth_service, "_get_user_by_provider", return_value=None):
            # Mock _get_or_create_user
            new_user = User(
                id=1,
                email="newuser@example.com",
                auth_provider="google",
                auth_provider_id="google-123",
            )
            new_user.subscription = Subscription(user_id=1, tier="free")

            with patch.object(
                oauth_service, "_get_or_create_user", return_value=new_user
            ):
                # Mock AuthService 方法
                mock_device = MagicMock()
                mock_tokens = MagicMock()
                oauth_service.auth_service._get_or_create_device = AsyncMock(
                    return_value=mock_device
                )
                oauth_service.auth_service._create_session = AsyncMock(
                    return_value=mock_tokens
                )

                user, tokens = await oauth_service._process_oauth_login(
                    email="newuser@example.com",
                    provider="google",
                    provider_id="google-123",
                    device_fingerprint="device-001",
                    device_name="iPhone 15",
                )

                # 验证结果
                assert user.email == "newuser@example.com"
                assert tokens == mock_tokens
                mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_oauth_login_existing_user(self, oauth_service, mock_db):
        """测试已存在用户 OAuth 登录"""
        existing_user = User(
            id=1,
            email="user@example.com",
            auth_provider="apple",
            auth_provider_id="apple-123",
        )
        existing_user.subscription = Subscription(user_id=1, tier="pro")

        # Mock _get_user_by_provider 返回现有用户
        with patch.object(
            oauth_service, "_get_user_by_provider", return_value=existing_user
        ):
            # Mock AuthService 方法
            mock_device = MagicMock()
            mock_tokens = MagicMock()
            oauth_service.auth_service._get_or_create_device = AsyncMock(
                return_value=mock_device
            )
            oauth_service.auth_service._create_session = AsyncMock(
                return_value=mock_tokens
            )

            user, tokens = await oauth_service._process_oauth_login(
                email=None,  # Apple 后续登录无 email
                provider="apple",
                provider_id="apple-123",
                device_fingerprint="device-002",
                device_name=None,
            )

            # 验证结果
            assert user.id == 1
            assert tokens == mock_tokens
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_oauth_login_apple_no_email_no_user(self, oauth_service):
        """测试 Apple 后续登录但找不到用户（异常场景）"""
        # Mock _get_user_by_provider 返回 None
        with patch.object(oauth_service, "_get_user_by_provider", return_value=None):
            # 无 email 且找不到用户，应该抛出异常
            with pytest.raises(ValueError, match="OAUTH_ACCOUNT_NOT_LINKED"):
                await oauth_service._process_oauth_login(
                    email=None,  # Apple 后续登录无 email
                    provider="apple",
                    provider_id="apple-orphan",
                    device_fingerprint="device-003",
                    device_name=None,
                )


class TestApplePublicKeyCache:
    """测试 Apple 公钥缓存机制"""

    @pytest.mark.asyncio
    async def test_apple_keys_cached(self, oauth_service):
        """测试 Apple 公钥缓存生效"""
        mock_keys = {"keys": [{"kid": "key-001"}]}

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_keys
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            # 第一次调用，应该发起 HTTP 请求
            keys1 = await oauth_service._get_apple_public_keys()
            assert keys1 == mock_keys
            assert mock_get.call_count == 1

            # 第二次调用，应该使用缓存，不发起新请求
            keys2 = await oauth_service._get_apple_public_keys()
            assert keys2 == mock_keys
            assert mock_get.call_count == 1  # 仍然是 1 次

    @pytest.mark.asyncio
    async def test_apple_keys_cache_cleared(self, oauth_service):
        """测试缓存清空后重新获取"""
        from app.services.oauth_service import _apple_key_cache

        # 清空缓存
        _apple_key_cache.clear()

        mock_keys = {"keys": [{"kid": "key-002"}]}

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_keys
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            keys = await oauth_service._get_apple_public_keys()
            assert keys == mock_keys
            assert mock_get.call_count == 1

        # 清理
        _apple_key_cache.clear()


class TestExchangeGoogleCode:
    """测试 Google authorization code 交换"""

    @pytest.mark.asyncio
    async def test_exchange_google_code_success(self, oauth_service):
        """测试成功交换 Google code"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id_token": "fake-id-token-123",
            "access_token": "fake-access-token",
            "refresh_token": "fake-refresh-token",
        }

        with (
            patch("httpx.AsyncClient.post", return_value=mock_response),
            patch(
                "app.services.oauth_service.settings.google_client_secret",
                "fake-client-secret",
            ),
        ):
            id_token = await oauth_service._exchange_google_code("auth-code-456")

        assert id_token == "fake-id-token-123"

    @pytest.mark.asyncio
    async def test_exchange_google_code_failed(self, oauth_service):
        """测试 Google code 交换失败"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "invalid_grant"

        with (
            patch("httpx.AsyncClient.post", return_value=mock_response),
            patch(
                "app.services.oauth_service.settings.google_client_secret",
                "fake-client-secret",
            ),
        ):
            with pytest.raises(ValueError, match="GOOGLE_CODE_EXCHANGE_FAILED"):
                await oauth_service._exchange_google_code("invalid-code")

    @pytest.mark.asyncio
    async def test_exchange_google_code_no_client_secret(self, oauth_service):
        """测试缺少 GOOGLE_CLIENT_SECRET 配置"""
        with patch("app.services.oauth_service.settings.google_client_secret", None):
            with pytest.raises(ValueError, match="GOOGLE_CLIENT_SECRET_NOT_CONFIGURED"):
                await oauth_service._exchange_google_code("some-code")


class TestGetUserByProvider:
    """测试通过 provider_id 查询用户"""

    @pytest.mark.asyncio
    async def test_get_user_by_provider_found(self, oauth_service, mock_db):
        """测试找到用户"""
        existing_user = User(
            id=1,
            email="user@example.com",
            auth_provider="google",
            auth_provider_id="google-123",
        )
        existing_user.subscription = Subscription(user_id=1, tier="pro")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_db.execute.return_value = mock_result

        user = await oauth_service._get_user_by_provider("google", "google-123")

        assert user is not None
        assert user.id == 1
        assert user.auth_provider_id == "google-123"

    @pytest.mark.asyncio
    async def test_get_user_by_provider_not_found(self, oauth_service, mock_db):
        """测试未找到用户"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        user = await oauth_service._get_user_by_provider("apple", "apple-orphan")

        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_provider_no_id(self, oauth_service):
        """测试 provider_id 为空"""
        user = await oauth_service._get_user_by_provider("google", "")

        assert user is None


class TestPublicAPIMethods:
    """测试公开 API 方法"""

    @pytest.mark.asyncio
    async def test_google_auth_with_code_success(self, oauth_service):
        """测试 Google OAuth code flow"""
        mock_user = User(id=1, email="user@gmail.com")
        mock_user.subscription = Subscription(user_id=1, tier="free")
        mock_tokens = MagicMock()

        with (
            patch.object(
                oauth_service, "_exchange_google_code", return_value="id-token-123"
            ),
            patch.object(
                oauth_service,
                "_verify_google_token",
                return_value={"email": "user@gmail.com", "sub": "google-123"},
            ),
            patch.object(
                oauth_service,
                "_process_oauth_login",
                return_value=(mock_user, mock_tokens),
            ),
        ):
            user, tokens = await oauth_service.google_auth_with_code(
                code="auth-code",
                device_fingerprint="device-001",
                device_name="iPhone",
            )

        assert user.email == "user@gmail.com"
        assert tokens == mock_tokens

    @pytest.mark.asyncio
    async def test_google_auth_success(self, oauth_service):
        """测试 Google OAuth id_token 直接验证"""
        mock_user = User(id=2, email="user2@gmail.com")
        mock_user.subscription = Subscription(user_id=2, tier="pro")
        mock_tokens = MagicMock()

        oauth_request = OAuthRequest(
            id_token="id-token-456",
            device_fingerprint="device-002",
            device_name="Android",
        )

        with (
            patch.object(
                oauth_service,
                "_verify_google_token",
                return_value={"email": "user2@gmail.com", "sub": "google-456"},
            ),
            patch.object(
                oauth_service,
                "_process_oauth_login",
                return_value=(mock_user, mock_tokens),
            ),
        ):
            user, tokens = await oauth_service.google_auth(oauth_request)

        assert user.email == "user2@gmail.com"
        assert tokens == mock_tokens

    @pytest.mark.asyncio
    async def test_apple_auth_success(self, oauth_service):
        """测试 Apple Sign-in"""
        mock_user = User(id=3, email="user@icloud.com")
        mock_user.subscription = Subscription(user_id=3, tier="free")
        mock_tokens = MagicMock()

        oauth_request = OAuthRequest(
            id_token="apple-id-token",
            device_fingerprint="device-003",
            device_name=None,
        )

        with (
            patch.object(
                oauth_service,
                "_verify_apple_token",
                return_value={"email": "user@icloud.com", "sub": "apple-789"},
            ),
            patch.object(
                oauth_service,
                "_process_oauth_login",
                return_value=(mock_user, mock_tokens),
            ),
        ):
            user, tokens = await oauth_service.apple_auth(oauth_request)

        assert user.email == "user@icloud.com"
        assert tokens == mock_tokens
