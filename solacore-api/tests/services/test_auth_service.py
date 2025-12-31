"""
AuthService 单元测试

覆盖函数：
- register: 用户注册
- login: 用户登录
- refresh_token: 刷新令牌
- logout: 用户登出
- get_user_by_id: 查询用户
- _get_or_create_device: 设备管理
- _create_session: 会话创建
"""

from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest
from app.models.device import Device
from app.models.session import ActiveSession
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import BETA_DEVICE_LIMIT, AuthService
from app.utils.datetime_utils import utc_now
from app.utils.security import create_refresh_token, hash_token
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
class TestRegister:
    """测试用户注册"""

    async def test_register_success(self):
        """正常注册流程"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)
            data = RegisterRequest(
                email="test@example.com",
                password="SecurePass123!",
                device_fingerprint="test-device-001",
                device_name="Test iPhone 15",
            )

            user, tokens = await service.register(data)

            # 验证用户创建
            assert user.email == "test@example.com"
            assert user.password_hash is not None
            assert user.auth_provider == "email"

            # 验证订阅创建
            result = await db.execute(
                select(Subscription).where(Subscription.user_id == user.id)
            )
            subscription = result.scalar_one()
            assert subscription.tier == "free"

            # 验证设备创建
            result = await db.execute(select(Device).where(Device.user_id == user.id))
            device = result.scalar_one()
            assert device.device_fingerprint == "test-device-001"
            assert device.device_name == "Test iPhone 15"
            assert device.platform == "ios"

            # 验证会话创建
            result = await db.execute(
                select(ActiveSession).where(ActiveSession.user_id == user.id)
            )
            session = result.scalar_one()
            assert session.device_id == device.id

            # 验证 tokens
            assert tokens.access_token is not None
            assert tokens.refresh_token is not None
            assert tokens.expires_in == 3600
            assert tokens.user_id == user.id

    async def test_register_duplicate_email(self):
        """邮箱已存在"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 第一次注册
            data1 = RegisterRequest(
                email="duplicate@example.com",
                password="Pass123!",
                device_fingerprint="device-001",
                device_name="Device 1",
            )
            await service.register(data1)

            # 第二次注册相同邮箱
            data2 = RegisterRequest(
                email="duplicate@example.com",
                password="DiffPass456!",
                device_fingerprint="device-002",
                device_name="Device 2",
            )
            with pytest.raises(ValueError, match="EMAIL_ALREADY_EXISTS"):
                await service.register(data2)


@pytest.mark.asyncio
class TestLogin:
    """测试用户登录"""

    async def test_login_success(self):
        """正常登录流程"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 先注册
            register_data = RegisterRequest(
                email="login@example.com",
                password="LoginPass123!",
                device_fingerprint="login-device-001",
                device_name="Login Device",
            )
            await service.register(register_data)

            # 登录
            login_data = LoginRequest(
                email="login@example.com",
                password="LoginPass123!",
                device_fingerprint="login-device-001",
                device_name="Login Device",
            )
            user, tokens = await service.login(login_data)

            assert user.email == "login@example.com"
            assert tokens.access_token is not None
            assert tokens.refresh_token is not None

    async def test_login_wrong_password(self):
        """密码错误"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 先注册
            register_data = RegisterRequest(
                email="wrongpass@example.com",
                password="CorrectPass123!",
                device_fingerprint="device-001",
                device_name="Device",
            )
            await service.register(register_data)

            # 错误密码登录
            login_data = LoginRequest(
                email="wrongpass@example.com",
                password="WrongPassword!",
                device_fingerprint="device-001",
                device_name="Device",
            )
            with pytest.raises(ValueError, match="INVALID_CREDENTIALS"):
                await service.login(login_data)

    async def test_login_user_not_found(self):
        """用户不存在"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)
            login_data = LoginRequest(
                email="nonexistent@example.com",
                password="AnyPass123!",
                device_fingerprint="device-001",
                device_name="Device",
            )
            with pytest.raises(ValueError, match="INVALID_CREDENTIALS"):
                await service.login(login_data)

    async def test_login_creates_new_device(self):
        """登录时创建新设备"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 先注册
            register_data = RegisterRequest(
                email="newdevice@example.com",
                password="Pass123!",
                device_fingerprint="device-001",
                device_name="Device 1",
            )
            user, _ = await service.register(register_data)

            # 重新创建 service（使用新 session 避免缓存问题）
            async with TestingSessionLocal() as db2:
                service2 = AuthService(db2)

                # 用不同设备登录
                login_data = LoginRequest(
                    email="newdevice@example.com",
                    password="Pass123!",
                    device_fingerprint="device-002",
                    device_name="Samsung Galaxy S24",
                )
                _, tokens = await service2.login(login_data)

                # 验证设备创建
                result = await db2.execute(
                    select(Device).where(Device.user_id == user.id)
                )
                devices = result.scalars().all()
                assert len(devices) == 2
                assert any(d.device_fingerprint == "device-002" for d in devices)
                assert any(d.platform == "android" for d in devices)


@pytest.mark.asyncio
class TestRefreshToken:
    """测试令牌刷新"""

    async def test_refresh_token_success(self):
        """正常刷新令牌"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 先注册
            register_data = RegisterRequest(
                email="refresh@example.com",
                password="Pass123!",
                device_fingerprint="device-001",
                device_name="Device",
            )
            _, tokens = await service.register(register_data)

            # 重新创建 service（使用新 session 避免 detached 状态）
            async with TestingSessionLocal() as db2:
                service2 = AuthService(db2)

                # 刷新令牌
                new_tokens = await service2.refresh_token(tokens.refresh_token)

                assert new_tokens.access_token is not None
                assert new_tokens.refresh_token is not None
                assert new_tokens.access_token != tokens.access_token
                assert new_tokens.refresh_token != tokens.refresh_token

    async def test_refresh_token_invalid(self):
        """无效的刷新令牌"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)
            with pytest.raises(ValueError, match="INVALID_TOKEN"):
                await service.refresh_token("invalid-token-12345")

    async def test_refresh_token_expired(self):
        """过期的刷新令牌"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 创建过期会话
            user = User(
                email="expired@example.com",
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            device = Device(
                user_id=user.id,
                device_fingerprint="device-001",
                device_name="Device",
            )
            db.add(device)
            await db.flush()

            session = ActiveSession(
                user_id=user.id,
                device_id=device.id,
                token_hash="",
                expires_at=utc_now() - timedelta(days=1),  # 已过期
            )
            db.add(session)
            await db.flush()

            expired_token = create_refresh_token(session.id)  # type: ignore
            session.token_hash = hash_token(expired_token)  # type: ignore
            await db.commit()

            # 尝试刷新过期令牌
            with pytest.raises(ValueError, match="INVALID_TOKEN"):
                await service.refresh_token(expired_token)


@pytest.mark.asyncio
class TestLogout:
    """测试用户登出"""

    async def test_logout_success(self):
        """正常登出"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 先注册
            register_data = RegisterRequest(
                email="logout@example.com",
                password="Pass123!",
                device_fingerprint="logout-device-unique-001",
                device_name="Device",
            )
            user, tokens = await service.register(register_data)

            # 获取会话
            result = await db.execute(
                select(ActiveSession).where(ActiveSession.user_id == user.id)
            )
            session = result.scalar_one()

            # 登出
            success = await service.logout(user.id, session.token_hash)  # type: ignore
            assert success is True

            # 验证会话已删除
            result = await db.execute(
                select(ActiveSession).where(ActiveSession.id == session.id)
            )
            assert result.scalar_one_or_none() is None

    async def test_logout_session_not_found(self):
        """会话不存在"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)
            fake_user_id = uuid4()
            success = await service.logout(fake_user_id, "nonexistent-token-hash")
            assert success is False


@pytest.mark.asyncio
class TestGetUserById:
    """测试根据 ID 查询用户"""

    async def test_get_user_by_id_success(self):
        """正常查询用户"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 先注册
            register_data = RegisterRequest(
                email="getuser@example.com",
                password="Pass123!",
                device_fingerprint="device-001",
                device_name="Device",
            )
            user, _ = await service.register(register_data)

            # 查询用户
            fetched_user = await service.get_user_by_id(user.id)
            assert fetched_user is not None
            assert fetched_user.id == user.id
            assert fetched_user.email == "getuser@example.com"
            assert fetched_user.subscription is not None
            assert fetched_user.subscription.tier == "free"

    async def test_get_user_by_id_not_found(self):
        """用户不存在"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)
            fake_id = uuid4()
            user = await service.get_user_by_id(fake_id)
            assert user is None


@pytest.mark.asyncio
class TestGetOrCreateDevice:
    """测试设备管理"""

    async def test_get_or_create_device_new_device(self):
        """创建新设备"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 创建用户
            user = User(
                email="device@example.com", password_hash="hash", auth_provider="email"
            )
            db.add(user)
            await db.flush()

            # 创建设备
            device = await service._get_or_create_device(
                user, "new-device-001", "iPhone 15 Pro", tier="free"
            )

            assert device.device_fingerprint == "new-device-001"
            assert device.device_name == "iPhone 15 Pro"
            assert device.platform == "ios"
            assert device.is_active is True

    async def test_get_or_create_device_existing_device(self):
        """获取现有设备"""
        async with TestingSessionLocal() as db:
            _ = AuthService(db)

            # 创建用户和设备
            user = User(
                email="existing@example.com",
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            existing = Device(
                user_id=user.id,
                device_fingerprint="existing-device",
                device_name="Old Name",
                platform="ios",
            )
            db.add(existing)
            await db.commit()

            # 重新创建 service（避免 detached 状态）
            async with TestingSessionLocal() as db2:
                service2 = AuthService(db2)

                # 重新查询用户（避免外键问题）
                result = await db2.execute(
                    select(User).where(User.email == "existing@example.com")
                )
                user_reloaded = result.scalar_one()

                # 获取设备（更新名称）
                device = await service2._get_or_create_device(
                    user_reloaded, "existing-device", "New Name", tier="free"
                )

                assert device.id == existing.id
                assert device.device_name == "New Name"
                assert device.last_active_at is not None

    async def test_get_or_create_device_bound_to_other_user(self):
        """设备已绑定其他用户"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 创建两个用户
            user1 = User(
                email="user1@example.com", password_hash="hash", auth_provider="email"
            )
            user2 = User(
                email="user2@example.com", password_hash="hash", auth_provider="email"
            )
            db.add_all([user1, user2])
            await db.flush()

            # 用户1绑定设备
            device = Device(
                user_id=user1.id,
                device_fingerprint="shared-device",
                device_name="Device",
            )
            db.add(device)
            await db.commit()

            # 用户2尝试使用相同设备
            with pytest.raises(ValueError, match="DEVICE_BOUND_TO_OTHER"):
                await service._get_or_create_device(
                    user2, "shared-device", "Device", tier="free"
                )

    async def test_get_or_create_device_limit_reached_free(self):
        """Free tier 设备上限"""
        async with TestingSessionLocal() as db:
            _ = AuthService(db)

            user = User(
                email="limit@example.com", password_hash="hash", auth_provider="email"
            )
            db.add(user)
            await db.flush()

            # 创建 1 个设备（free tier 上限为 1）
            device1 = Device(
                user_id=user.id,
                device_fingerprint="limit-device-001",
                device_name="Device 1",
                is_active=True,
            )
            db.add(device1)
            await db.commit()

            # 重新创建 service（避免 detached 状态）
            async with TestingSessionLocal() as db2:
                service2 = AuthService(db2)

                # 重新查询用户
                result = await db2.execute(
                    select(User).where(User.email == "limit@example.com")
                )
                user_reloaded = result.scalar_one()

                # 尝试创建第 2 个设备
                with pytest.raises(ValueError, match="DEVICE_LIMIT_REACHED"):
                    await service2._get_or_create_device(
                        user_reloaded, "limit-device-002", "Device 2", tier="free"
                    )

    @patch("app.services.auth_service.settings.beta_mode", True)
    async def test_get_or_create_device_beta_mode_limit(self):
        """Beta 模式设备上限"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            user = User(
                email="beta@example.com", password_hash="hash", auth_provider="email"
            )
            db.add(user)
            await db.flush()

            # 创建 10 个设备（Beta 上限）
            for i in range(BETA_DEVICE_LIMIT):
                device = Device(
                    user_id=user.id,
                    device_fingerprint=f"beta-device-{i:03d}",
                    device_name=f"Beta Device {i}",
                    is_active=True,
                )
                db.add(device)
            await db.commit()

            # 尝试创建第 11 个设备
            with pytest.raises(ValueError, match="DEVICE_LIMIT_REACHED"):
                await service._get_or_create_device(
                    user, "beta-device-011", "Device 11", tier="free"
                )

    async def test_detect_platform_ios(self):
        """iOS 平台检测"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            user = User(
                email="ios@example.com", password_hash="hash", auth_provider="email"
            )
            db.add(user)
            await db.flush()

            device = await service._get_or_create_device(
                user, "ios-device-unique-001", "iPhone 15 Pro Max", tier="free"
            )
            assert device.platform == "ios"

    async def test_detect_platform_android(self):
        """Android 平台检测"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            user = User(
                email="android@example.com", password_hash="hash", auth_provider="email"
            )
            db.add(user)
            await db.flush()

            device = await service._get_or_create_device(
                user,
                "android-device-unique-001",
                "Samsung Galaxy S24 Ultra",
                tier="free",
            )
            assert device.platform == "android"

    async def test_detect_platform_unknown(self):
        """未知平台"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            user = User(
                email="unknown@example.com", password_hash="hash", auth_provider="email"
            )
            db.add(user)
            await db.flush()

            device = await service._get_or_create_device(
                user, "unknown-device-unique-001", "Unknown Device", tier="free"
            )
            assert device.platform is None


@pytest.mark.asyncio
class TestCreateSession:
    """测试会话创建"""

    async def test_create_session(self):
        """正常创建会话"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 创建用户和设备
            user = User(
                email="session@example.com", password_hash="hash", auth_provider="email"
            )
            db.add(user)
            await db.flush()

            device = Device(
                user_id=user.id,
                device_fingerprint="device-001",
                device_name="Device",
            )
            db.add(device)
            await db.flush()

            # 创建会话
            tokens = await service._create_session(user, device)

            assert tokens.access_token is not None
            assert tokens.refresh_token is not None
            assert tokens.expires_in == 3600
            assert tokens.user_id == user.id

            # 验证会话存储
            result = await db.execute(
                select(ActiveSession).where(ActiveSession.user_id == user.id)
            )
            session = result.scalar_one()
            assert session.device_id == device.id
            assert session.token_hash is not None
            assert session.expires_at > utc_now()
