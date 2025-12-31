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

import asyncio
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


def unique_device_fingerprint(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


def unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}@example.com"


@pytest.mark.asyncio
class TestRegister:
    """测试用户注册"""

    async def test_register_success(self):
        """正常注册流程"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)
            device_fingerprint = unique_device_fingerprint("test-device")
            email = unique_email("test-register-success")
            data = RegisterRequest(
                email=email,
                password="SecurePass123!",
                device_fingerprint=device_fingerprint,
                device_name="Test iPhone 15",
            )

            user, tokens = await service.register(data)

            # 验证用户创建
            assert user.email == email
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
            assert device.device_fingerprint == device_fingerprint
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
            device_fingerprint_1 = unique_device_fingerprint("duplicate-device")
            email = unique_email("duplicate-email")
            data1 = RegisterRequest(
                email=email,
                password="Pass123!",
                device_fingerprint=device_fingerprint_1,
                device_name="Device 1",
            )
            await service.register(data1)

            # 第二次注册相同邮箱
            device_fingerprint_2 = unique_device_fingerprint("duplicate-device")
            data2 = RegisterRequest(
                email=email,
                password="DiffPass456!",
                device_fingerprint=device_fingerprint_2,
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
            device_fingerprint = unique_device_fingerprint("login-device")
            email = unique_email("login-success")
            register_data = RegisterRequest(
                email=email,
                password="LoginPass123!",
                device_fingerprint=device_fingerprint,
                device_name="Login Device",
            )
            await service.register(register_data)

            # 登录
            login_data = LoginRequest(
                email=email,
                password="LoginPass123!",
                device_fingerprint=device_fingerprint,
                device_name="Login Device",
            )
            user, tokens = await service.login(login_data)

            assert user.email == email
            assert tokens.access_token is not None
            assert tokens.refresh_token is not None

    async def test_login_wrong_password(self):
        """密码错误"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 先注册
            device_fingerprint = unique_device_fingerprint("wrongpass-device")
            email = unique_email("login-wrongpass")
            register_data = RegisterRequest(
                email=email,
                password="CorrectPass123!",
                device_fingerprint=device_fingerprint,
                device_name="Device",
            )
            await service.register(register_data)

            # 错误密码登录
            login_data = LoginRequest(
                email=email,
                password="WrongPassword!",
                device_fingerprint=device_fingerprint,
                device_name="Device",
            )
            with pytest.raises(ValueError, match="INVALID_CREDENTIALS"):
                await service.login(login_data)

    async def test_login_user_not_found(self):
        """用户不存在"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)
            device_fingerprint = unique_device_fingerprint("nonexistent-device")
            email = unique_email("login-nonexistent")
            login_data = LoginRequest(
                email=email,
                password="AnyPass123!",
                device_fingerprint=device_fingerprint,
                device_name="Device",
            )
            with pytest.raises(ValueError, match="INVALID_CREDENTIALS"):
                await service.login(login_data)

    async def test_login_creates_new_device(self):
        """登录时创建新设备"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 先注册
            device_fingerprint_1 = unique_device_fingerprint("newdevice")
            email = unique_email("login-newdevice")
            register_data = RegisterRequest(
                email=email,
                password="Pass123!",
                device_fingerprint=device_fingerprint_1,
                device_name="Device 1",
            )
            user, _ = await service.register(register_data)

            # 重新创建 service（使用新 session 避免缓存问题）
            async with TestingSessionLocal() as db2:
                service2 = AuthService(db2)

                # 用不同设备登录
                device_fingerprint_2 = unique_device_fingerprint("newdevice")
                login_data = LoginRequest(
                    email=email,
                    password="Pass123!",
                    device_fingerprint=device_fingerprint_2,
                    device_name="Samsung Galaxy S24",
                )
                _, tokens = await service2.login(login_data)

                # 验证设备创建
                result = await db2.execute(
                    select(Device).where(Device.user_id == user.id)
                )
                devices = result.scalars().all()
                assert len(devices) == 2
                assert any(
                    d.device_fingerprint == device_fingerprint_2 for d in devices
                )
                assert any(d.platform == "android" for d in devices)


@pytest.mark.asyncio
class TestRefreshToken:
    """测试令牌刷新"""

    async def test_refresh_token_success(self):
        """正常刷新令牌"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            # 先注册
            device_fingerprint = unique_device_fingerprint("refresh-device")
            email = unique_email("refresh-success")
            register_data = RegisterRequest(
                email=email,
                password="Pass123!",
                device_fingerprint=device_fingerprint,
                device_name="Device",
            )
            _, tokens = await service.register(register_data)

            # 重新创建 service（使用新 session 避免 detached 状态）
            async with TestingSessionLocal() as db2:
                service2 = AuthService(db2)

                # 等待1.1秒确保JWT时间戳不同
                await asyncio.sleep(1.1)

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
                email=unique_email("refresh-expired"),
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            device = Device(
                user_id=user.id,
                device_fingerprint=unique_device_fingerprint("expired-device"),
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
            device_fingerprint = unique_device_fingerprint("logout-device")
            email = unique_email("logout-success")
            register_data = RegisterRequest(
                email=email,
                password="Pass123!",
                device_fingerprint=device_fingerprint,
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
            device_fingerprint = unique_device_fingerprint("getuser-device")
            email = unique_email("getuser-success")
            register_data = RegisterRequest(
                email=email,
                password="Pass123!",
                device_fingerprint=device_fingerprint,
                device_name="Device",
            )
            user, _ = await service.register(register_data)

            # 查询用户
            fetched_user = await service.get_user_by_id(user.id)
            assert fetched_user is not None
            assert fetched_user.id == user.id
            assert fetched_user.email == email
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
                email=unique_email("device-new"),
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            # 创建设备
            device_fingerprint = unique_device_fingerprint("new-device")
            device = await service._get_or_create_device(
                user, device_fingerprint, "iPhone 15 Pro", tier="free"
            )

            assert device.device_fingerprint == device_fingerprint
            assert device.device_name == "iPhone 15 Pro"
            assert device.platform == "ios"
            assert device.is_active is True

    async def test_get_or_create_device_existing_device(self):
        """获取现有设备"""
        async with TestingSessionLocal() as db:
            _ = AuthService(db)

            # 创建用户和设备
            email = unique_email("device-existing")
            user = User(
                email=email,
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            device_fingerprint = unique_device_fingerprint("existing-device")
            existing = Device(
                user_id=user.id,
                device_fingerprint=device_fingerprint,
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
                    select(User).where(User.email == email)
                )
                user_reloaded = result.scalar_one()

                # 获取设备（更新名称）
                device = await service2._get_or_create_device(
                    user_reloaded, device_fingerprint, "New Name", tier="free"
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
                email=unique_email("device-user1"),
                password_hash="hash",
                auth_provider="email",
            )
            user2 = User(
                email=unique_email("device-user2"),
                password_hash="hash",
                auth_provider="email",
            )
            db.add_all([user1, user2])
            await db.flush()

            # 用户1绑定设备
            device_fingerprint = unique_device_fingerprint("shared-device")
            device = Device(
                user_id=user1.id,
                device_fingerprint=device_fingerprint,
                device_name="Device",
            )
            db.add(device)
            await db.commit()

            # 用户2尝试使用相同设备
            with pytest.raises(ValueError, match="DEVICE_BOUND_TO_OTHER"):
                await service._get_or_create_device(
                    user2, device_fingerprint, "Device", tier="free"
                )

    @patch("app.services.auth_service.settings.beta_mode", False)
    async def test_get_or_create_device_limit_reached_free(self):
        """Free tier 设备上限"""
        async with TestingSessionLocal() as db:
            _ = AuthService(db)

            email = unique_email("device-limit")
            user = User(
                email=email,
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            # 创建 1 个设备（free tier 上限为 1）
            device_fingerprint = unique_device_fingerprint("limit-device")
            device1 = Device(
                user_id=user.id,
                device_fingerprint=device_fingerprint,
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
                    select(User).where(User.email == email)
                )
                user_reloaded = result.scalar_one()

                # 尝试创建第 2 个设备
                device_fingerprint_2 = unique_device_fingerprint("limit-device-2")
                with pytest.raises(ValueError, match="DEVICE_LIMIT_REACHED"):
                    await service2._get_or_create_device(
                        user_reloaded,
                        device_fingerprint_2,
                        "Device 2",
                        tier="free",
                    )

    @patch("app.services.auth_service.settings.beta_mode", True)
    async def test_get_or_create_device_beta_mode_limit(self):
        """Beta 模式设备上限"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            user = User(
                email=unique_email("device-beta"),
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            # 创建 10 个设备（Beta 上限）
            device_prefix = unique_device_fingerprint("beta-device")
            for i in range(BETA_DEVICE_LIMIT):
                device = Device(
                    user_id=user.id,
                    device_fingerprint=f"{device_prefix}-{i:03d}",
                    device_name=f"Beta Device {i}",
                    is_active=True,
                )
                db.add(device)
            await db.commit()

            # 尝试创建第 11 个设备
            with pytest.raises(ValueError, match="DEVICE_LIMIT_REACHED"):
                await service._get_or_create_device(
                    user, f"{device_prefix}-011", "Device 11", tier="free"
                )

    async def test_detect_platform_ios(self):
        """iOS 平台检测"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            user = User(
                email=unique_email("device-ios"),
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            device_fingerprint = unique_device_fingerprint("ios-device")
            device = await service._get_or_create_device(
                user, device_fingerprint, "iPhone 15 Pro Max", tier="free"
            )
            assert device.platform == "ios"

    async def test_detect_platform_android(self):
        """Android 平台检测"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            user = User(
                email=unique_email("device-android"),
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            device_fingerprint = unique_device_fingerprint("android-device")
            device = await service._get_or_create_device(
                user,
                device_fingerprint,
                "Samsung Galaxy S24 Ultra",
                tier="free",
            )
            assert device.platform == "android"

    async def test_detect_platform_unknown(self):
        """未知平台"""
        async with TestingSessionLocal() as db:
            service = AuthService(db)

            user = User(
                email=unique_email("device-unknown"),
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            device_fingerprint = unique_device_fingerprint("unknown-device")
            device = await service._get_or_create_device(
                user, device_fingerprint, "Unknown Device", tier="free"
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
                email=unique_email("session"),
                password_hash="hash",
                auth_provider="email",
            )
            db.add(user)
            await db.flush()

            device = Device(
                user_id=user.id,
                device_fingerprint=unique_device_fingerprint("session-device"),
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
