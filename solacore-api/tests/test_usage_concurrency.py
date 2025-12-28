"""Usage concurrency tests."""

import asyncio

import pytest
from app.models.subscription import Usage
from app.models.user import User
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


async def _register_user(client: AsyncClient, email: str, fingerprint: str) -> str:
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


@pytest.mark.asyncio
async def test_usage_session_count_concurrent_requests(client: AsyncClient):
    email = "usage-concurrency@example.com"
    fingerprint = "usage-device-001"
    token = await _register_user(client, email, fingerprint)

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Device-Fingerprint": fingerprint,
    }

    async def create_session() -> None:
        response = await client.post("/sessions", json={}, headers=headers)
        assert response.status_code == 201

    await asyncio.gather(create_session(), create_session())

    async with TestingSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.email == email))
        user = user_result.scalar_one()
        usage_result = await session.execute(
            select(Usage).where(Usage.user_id == user.id)
        )
        usages = usage_result.scalars().all()

    assert len(usages) == 1
    assert usages[0].session_count == 2
