"""Sessions Update 路由测试 - 更新会话状态、步骤和提醒配置"""

from datetime import timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from app.models.solve_session import SessionStatus, SolveSession, SolveStep
from app.models.subscription import Subscription
from app.models.user import User
from app.utils.datetime_utils import utc_now
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


@pytest_asyncio.fixture
async def test_user_with_session():
    """创建测试用户和会话的 fixture"""
    async with TestingSessionLocal() as session:
        # 创建用户
        from app.utils.security import hash_password_async

        hashed_pw = await hash_password_async("test-password")
        user = User(
            email=f"test-{uuid4()}@example.com",
            password_hash=hashed_pw,
            auth_provider="email",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # 创建订阅
        subscription = Subscription(
            user_id=user.id,
            tier="free",
        )
        session.add(subscription)

        # 创建会话
        solve_session = SolveSession(
            user_id=user.id,
            status=SessionStatus.ACTIVE.value,
            current_step=SolveStep.RECEIVE.value,
            locale="zh-CN",
        )
        session.add(solve_session)
        await session.commit()
        await session.refresh(solve_session)

        user_id = user.id
        session_id = solve_session.id

    return user_id, session_id


@pytest.mark.asyncio
async def test_update_session_status_to_completed(
    client: AsyncClient, test_user_with_session
):
    """测试更新会话状态为已完成"""
    user_id, session_id = test_user_with_session

    # 登录获取 token
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)
    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)

    # 更新会话状态
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"status": "completed"},
        cookies=auth_cookies,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "updated_at" in data

    # 验证数据库中的状态已更新
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(SolveSession).where(SolveSession.id == session_id)
        )
        updated_session = result.scalar_one()
        assert updated_session.status == SessionStatus.COMPLETED.value
        assert updated_session.completed_at is not None


@pytest.mark.asyncio
async def test_update_session_step(client: AsyncClient, test_user_with_session):
    """测试更新会话步骤（合法转换：receive -> clarify）"""
    user_id, session_id = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)

    # 更新步骤：receive -> clarify
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"current_step": "clarify"},
        cookies=auth_cookies,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_step"] == "clarify"

    # 验证数据库
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(SolveSession).where(SolveSession.id == session_id)
        )
        updated_session = result.scalar_one()
        assert updated_session.current_step == SolveStep.CLARIFY.value


@pytest.mark.asyncio
async def test_update_session_invalid_step_transition(
    client: AsyncClient, test_user_with_session
):
    """测试非法步骤转换（receive -> commit 跨越多步）"""
    user_id, session_id = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)

    # 尝试非法转换：receive -> commit
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"current_step": "commit"},
        cookies=auth_cookies,
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "INVALID_STEP_TRANSITION"


@pytest.mark.asyncio
async def test_update_session_invalid_status(
    client: AsyncClient, test_user_with_session
):
    """测试使用非法状态值"""
    user_id, session_id = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)
    # 使用非法状态
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"status": "invalid_status"},
        cookies=auth_cookies,
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "INVALID_STATUS"


@pytest.mark.asyncio
async def test_update_session_invalid_step(client: AsyncClient, test_user_with_session):
    """测试使用非法步骤值"""
    user_id, session_id = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)

    # 使用非法步骤
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"current_step": "invalid_step"},
        cookies=auth_cookies,
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "INVALID_STEP"


@pytest.mark.asyncio
async def test_update_session_locale(client: AsyncClient, test_user_with_session):
    """测试更新会话语言配置"""
    user_id, session_id = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)
    # 更新 locale
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"locale": "en-US"},
        cookies=auth_cookies,
    )

    assert response.status_code == 200

    # 验证数据库
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(SolveSession).where(SolveSession.id == session_id)
        )
        updated_session = result.scalar_one()
        assert updated_session.locale == "en-US"


@pytest.mark.asyncio
async def test_update_session_first_step_action(
    client: AsyncClient, test_user_with_session
):
    """测试更新第一步行动"""
    user_id, session_id = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)

    # 更新 first_step_action
    action = "今晚早点睡，10点前关灯"
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"first_step_action": action},
        cookies=auth_cookies,
    )

    assert response.status_code == 200

    # 验证数据库
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(SolveSession).where(SolveSession.id == session_id)
        )
        updated_session = result.scalar_one()
        assert updated_session.first_step_action == action


@pytest.mark.asyncio
async def test_update_session_reminder_time(
    client: AsyncClient, test_user_with_session
):
    """测试更新提醒时间"""
    user_id, session_id = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)
    # 更新 reminder_time
    tomorrow = utc_now() + timedelta(days=1)
    reminder_iso = tomorrow.isoformat()
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"reminder_time": reminder_iso},
        cookies=auth_cookies,
    )

    assert response.status_code == 200

    # 验证数据库
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(SolveSession).where(SolveSession.id == session_id)
        )
        updated_session = result.scalar_one()
        assert updated_session.reminder_time is not None
        # 允许小的时间差（秒级）
        diff = abs((updated_session.reminder_time - tomorrow).total_seconds())
        assert diff < 5


@pytest.mark.asyncio
async def test_update_session_multiple_fields(
    client: AsyncClient, test_user_with_session
):
    """测试同时更新多个字段"""
    user_id, session_id = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)

    # 同时更新多个字段
    tomorrow = utc_now() + timedelta(days=1)
    response = await client.patch(
        f"/sessions/{session_id}",
        json={
            "current_step": "clarify",
            "locale": "en-US",
            "first_step_action": "Take a deep breath",
            "reminder_time": tomorrow.isoformat(),
        },
        cookies=auth_cookies,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_step"] == "clarify"

    # 验证所有字段都已更新
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(SolveSession).where(SolveSession.id == session_id)
        )
        updated_session = result.scalar_one()
        assert updated_session.current_step == SolveStep.CLARIFY.value
        assert updated_session.locale == "en-US"
        assert updated_session.first_step_action == "Take a deep breath"
        assert updated_session.reminder_time is not None


@pytest.mark.asyncio
async def test_update_session_not_found(client: AsyncClient, test_user_with_session):
    """测试更新不存在的会话"""
    user_id, _ = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)
    # 使用不存在的会话 ID
    fake_session_id = uuid4()
    response = await client.patch(
        f"/sessions/{fake_session_id}",
        json={"status": "completed"},
        cookies=auth_cookies,
    )

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_session_unauthorized(client: AsyncClient, test_user_with_session):
    """测试未登录用户尝试更新会话（返回 403 因为缺少 CSRF token）"""
    _, session_id = test_user_with_session

    # 不登录直接请求（不提供认证 cookies）
    # 注意：会先被 CSRF 中间件拦截返回 403，而不是认证中间件的 401
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"status": "completed"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_session_forbidden_other_user(
    client: AsyncClient, test_user_with_session
):
    """测试用户尝试更新别人的会话"""
    _, session_id = test_user_with_session

    # 创建另一个用户
    async with TestingSessionLocal() as session:
        from app.utils.security import hash_password_async

        hashed_pw = await hash_password_async("other-password")
        other_user = User(
            email=f"other-{uuid4()}@example.com",
            password_hash=hashed_pw,
            auth_provider="email",
        )
        session.add(other_user)
        await session.commit()
        other_email = other_user.email

    # 用另一个用户登录
    login_response = await client.post(
        "/auth/login",
        json={
            "email": other_email,
            "password": "other-password",
            "device_fingerprint": "test-device-002",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)

    # 尝试更新第一个用户的会话
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"status": "completed"},
        cookies=auth_cookies,
    )

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_session_empty_payload(
    client: AsyncClient, test_user_with_session
):
    """测试空的更新请求（什么都不更新）"""
    user_id, session_id = test_user_with_session

    # 登录
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        email = user.email

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test-password",
            "device_fingerprint": "test-device-001",
        },
    )
    assert login_response.status_code == 200

    # 提取 cookies 用于后续请求
    auth_cookies = dict(login_response.cookies)
    # 获取更新前的数据
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(SolveSession).where(SolveSession.id == session_id)
        )
        old_session = result.scalar_one()
        old_status = old_session.status
        old_step = old_session.current_step

    # 发送空的更新请求
    response = await client.patch(
        f"/sessions/{session_id}",
        json={},
        cookies=auth_cookies,
    )

    assert response.status_code == 200

    # 验证数据未改变
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(SolveSession).where(SolveSession.id == session_id)
        )
        new_session = result.scalar_one()
        assert new_session.status == old_status
        assert new_session.current_step == old_step
