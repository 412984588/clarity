"""Auth Login 路由测试 - Beta Login 功能"""

import pytest
from app.models.subscription import Subscription
from app.models.user import User
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_beta_login_disabled(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    """测试 Beta mode 关闭时返回 403"""
    # Mock settings.beta_mode = False
    from app.routers.auth import login

    fake_settings = type("Settings", (), {"beta_mode": False})()
    monkeypatch.setattr(login, "settings", fake_settings)

    response = await client.post(
        "/auth/beta-login",
        json={},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "BETA_MODE_DISABLED"


@pytest.mark.asyncio
async def test_beta_login_create_new_user(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    """测试 Beta mode 开启时自动创建新用户和订阅"""
    # Mock settings.beta_mode = True
    from app.routers.auth import login

    fake_settings = type("Settings", (), {"beta_mode": True})()
    monkeypatch.setattr(login, "settings", fake_settings)

    # 确保 beta 用户不存在
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "beta-tester@solacore.app")
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            await session.delete(existing_user)
            await session.commit()

    # Beta 登录
    response = await client.post(
        "/auth/beta-login",
        json={
            "device_fingerprint": "beta-device-001",
            "device_name": "Beta Test Device",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "beta-tester@solacore.app"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    # 验证用户和订阅已创建
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "beta-tester@solacore.app")
        )
        user = result.scalar_one()
        assert user is not None
        assert user.auth_provider == "email"

        # 验证订阅已创建
        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        )
        subscription = result.scalar_one()
        assert subscription.tier == "free"


@pytest.mark.asyncio
async def test_beta_login_existing_user_no_subscription(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    """测试 Beta 用户存在但无订阅时自动创建订阅"""
    # Mock settings.beta_mode = True
    from app.routers.auth import login

    fake_settings = type("Settings", (), {"beta_mode": True})()
    monkeypatch.setattr(login, "settings", fake_settings)

    # 创建 beta 用户但不创建订阅
    async with TestingSessionLocal() as session:
        # 删除已有用户（如果存在）
        result = await session.execute(
            select(User).where(User.email == "beta-tester@solacore.app")
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            await session.delete(existing_user)
            await session.commit()

        # 创建用户但不创建订阅
        from app.utils.security import hash_password_async

        hashed_pw = await hash_password_async("beta-password")
        user = User(
            email="beta-tester@solacore.app",
            password_hash=hashed_pw,
            auth_provider="email",
        )
        session.add(user)
        await session.commit()
        user_id = user.id

    # Beta 登录
    response = await client.post(
        "/auth/beta-login",
        json={},
    )

    assert response.status_code == 200

    # 验证订阅已自动创建
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one()
        assert subscription.tier == "free"


@pytest.mark.asyncio
async def test_beta_login_existing_user_with_subscription(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    """测试 Beta 用户存在且有订阅时直接登录"""
    # Mock settings.beta_mode = True
    from app.routers.auth import login

    fake_settings = type("Settings", (), {"beta_mode": True})()
    monkeypatch.setattr(login, "settings", fake_settings)

    # 创建 beta 用户和订阅
    async with TestingSessionLocal() as session:
        # 删除已有用户（如果存在）
        result = await session.execute(
            select(User).where(User.email == "beta-tester@solacore.app")
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            await session.delete(existing_user)
            await session.commit()

        # 创建用户和订阅
        from app.utils.security import hash_password_async

        hashed_pw = await hash_password_async("beta-password")
        user = User(
            email="beta-tester@solacore.app",
            password_hash=hashed_pw,
            auth_provider="email",
        )
        session.add(user)
        await session.flush()

        subscription = Subscription(user_id=user.id, tier="pro")
        session.add(subscription)
        await session.commit()
        subscription_id = subscription.id

    # Beta 登录
    response = await client.post(
        "/auth/beta-login",
        json={
            "device_fingerprint": "beta-device-002",
            "device_name": "Beta Device 2",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "beta-tester@solacore.app"

    # 验证订阅未被修改
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one()
        assert subscription.tier == "pro"  # 保持原有 tier


@pytest.mark.asyncio
async def test_beta_login_default_device_info(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    """测试 Beta login 使用默认 device_fingerprint 和 device_name"""
    # Mock settings.beta_mode = True
    from app.routers.auth import login

    fake_settings = type("Settings", (), {"beta_mode": True})()
    monkeypatch.setattr(login, "settings", fake_settings)

    # Beta 登录不提供 device_fingerprint 和 device_name
    response = await client.post(
        "/auth/beta-login",
        json={},
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data

    # 验证使用了默认值（device_fingerprint = f"beta:{user.id}"）
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "beta-tester@solacore.app")
        )
        user = result.scalar_one()

        from app.models.device import Device

        result = await session.execute(select(Device).where(Device.user_id == user.id))
        device = result.scalar_one()
        assert device.device_fingerprint == f"beta:{user.id}"
        assert device.device_name == "Beta Device"


@pytest.mark.asyncio
async def test_beta_login_custom_device_info(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    """测试 Beta login 使用自定义 device_fingerprint 和 device_name"""
    # Mock settings.beta_mode = True
    from app.routers.auth import login

    fake_settings = type("Settings", (), {"beta_mode": True})()
    monkeypatch.setattr(login, "settings", fake_settings)

    # Beta 登录提供自定义设备信息
    response = await client.post(
        "/auth/beta-login",
        json={
            "device_fingerprint": "custom-beta-fingerprint",
            "device_name": "Custom Beta Device",
        },
    )

    assert response.status_code == 200

    # 验证使用了自定义值
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "beta-tester@solacore.app")
        )
        user = result.scalar_one()

        from app.models.device import Device

        result = await session.execute(
            select(Device).where(
                Device.user_id == user.id,
                Device.device_fingerprint == "custom-beta-fingerprint",
            )
        )
        device = result.scalar_one_or_none()
        assert device is not None
        assert device.device_name == "Custom Beta Device"
