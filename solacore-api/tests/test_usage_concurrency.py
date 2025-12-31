"""Usage concurrency tests."""

import asyncio

import pytest
from app.models.subscription import Usage
from app.models.user import User
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


async def _register_user(client: AsyncClient, email: str, fingerprint: str) -> str:
    """注册用户并返回 token（使用符合规则的短密码）"""
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Pass1234",  # 8位,包含大写+数字,避免 bcrypt 72字节限制
            "device_fingerprint": fingerprint,
        },
    )
    assert response.status_code == 201
    return response.cookies["access_token"]


@pytest.mark.asyncio
async def test_usage_session_count_concurrent_requests(client: AsyncClient):
    """测试并发创建会话时 session_count 正确递增"""
    email = "usage-concurrency@example.com"
    fingerprint = "usage-device-001"
    token = await _register_user(client, email, fingerprint)

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Device-Fingerprint": fingerprint,
    }

    # 并发创建两个会话
    async def create_session() -> dict:
        response = await client.post("/sessions", json={}, headers=headers)
        assert response.status_code == 201
        return response.json()

    results = await asyncio.gather(create_session(), create_session())

    # 验证两个会话都创建成功
    assert len(results) == 2
    assert all("session_id" in r for r in results)

    # 验证数据库中 session_count 正确递增到 2
    async with TestingSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.email == email))
        user = user_result.scalar_one()
        usage_result = await session.execute(
            select(Usage).where(Usage.user_id == user.id)
        )
        usages = usage_result.scalars().all()

    # 应该只有一条 Usage 记录
    assert len(usages) == 1
    # session_count 应该是 2（原子递增保证了正确性）
    assert usages[0].session_count == 2
