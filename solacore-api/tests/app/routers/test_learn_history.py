"""学习会话历史路由测试"""

from uuid import UUID, uuid4

import pytest
from app.models.learn_message import LearnMessage, LearnMessageRole
from app.models.learn_session import LearnSession, LearnStep
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


async def _create_learn_session(
    client: AsyncClient, token: str, fingerprint: str
) -> str:
    """创建学习会话并返回 session_id"""
    response = await client.post(
        "/learn",
        json={},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Device-Fingerprint": fingerprint,
        },
    )
    assert response.status_code == 201
    return response.json()["session_id"]


@pytest.mark.asyncio
async def test_get_learn_session_success_with_messages(client: AsyncClient):
    """测试成功获取学习会话详情（包含消息）"""
    token = await _register_user(
        client, "learn-history-1@example.com", "learn-device-101"
    )
    session_id = await _create_learn_session(client, token, "learn-device-101")

    # 添加一些消息
    async with TestingSessionLocal() as session:
        user_message = LearnMessage(
            session_id=UUID(session_id),
            role=LearnMessageRole.USER.value,
            content="Hello",
            step=LearnStep.START.value,
        )
        ai_message = LearnMessage(
            session_id=UUID(session_id),
            role=LearnMessageRole.ASSISTANT.value,
            content="Hi there!",
            step=LearnStep.START.value,
        )
        session.add(user_message)
        session.add(ai_message)
        await session.commit()

    # 获取会话详情
    response = await client.get(
        f"/learn/{session_id}?include_messages=true",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["status"] == "active"
    assert data["current_step"] == "start"
    assert "messages" in data
    assert len(data["messages"]) == 2
    assert data["messages"][0]["content"] == "Hello"
    assert data["messages"][1]["content"] == "Hi there!"


@pytest.mark.asyncio
async def test_get_learn_session_success_without_messages(client: AsyncClient):
    """测试成功获取学习会话详情（不包含消息）"""
    token = await _register_user(
        client, "learn-history-2@example.com", "learn-device-102"
    )
    session_id = await _create_learn_session(client, token, "learn-device-102")

    response = await client.get(
        f"/learn/{session_id}?include_messages=false",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["status"] == "active"
    assert data["messages"] == []


@pytest.mark.asyncio
async def test_get_learn_session_not_found(client: AsyncClient):
    """测试获取不存在的会话"""
    token = await _register_user(
        client, "learn-history-3@example.com", "learn-device-103"
    )

    fake_session_id = uuid4()
    response = await client.get(
        f"/learn/{fake_session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_learn_session_wrong_user(client: AsyncClient):
    """测试尝试访问其他用户的会话"""
    token_a = await _register_user(
        client, "learn-history-user-a@example.com", "learn-device-104"
    )
    session_id = await _create_learn_session(client, token_a, "learn-device-104")

    token_b = await _register_user(
        client, "learn-history-user-b@example.com", "learn-device-105"
    )

    response = await client.get(
        f"/learn/{session_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_learn_session_with_topic_and_schedule(client: AsyncClient):
    """测试获取带有 topic 和 review_schedule 的会话"""
    token = await _register_user(
        client, "learn-history-4@example.com", "learn-device-106"
    )
    session_id = await _create_learn_session(client, token, "learn-device-106")

    # 更新会话，添加 topic 和 review_schedule
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(LearnSession.id == UUID(session_id))
        )
        learn_session = result.scalar_one()
        learn_session.topic = "Learn Python"
        learn_session.review_schedule = {
            "day_1": "2024-01-02T00:00:00",
            "day_3": "2024-01-04T00:00:00",
        }
        await session.commit()

    response = await client.get(
        f"/learn/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Learn Python"
    assert data["review_schedule"] is not None
    assert "day_1" in data["review_schedule"]
