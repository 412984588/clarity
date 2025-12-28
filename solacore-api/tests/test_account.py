import pytest
from app.models.user import User
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


async def _register_user(client: AsyncClient, email: str, fingerprint: str) -> str:
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "StrongPass1",
            "device_fingerprint": fingerprint,
            "device_name": "test-device",
        },
    )
    assert response.status_code == 201
    return response.cookies["access_token"]


@pytest.mark.asyncio
async def test_account_export_returns_user_data(client: AsyncClient):
    token = await _register_user(client, "export-user@example.com", "export-device-1")

    response = await client.get(
        "/account/export", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "export-user@example.com"
    assert "password_hash" not in data["user"]
    assert data["devices"]


@pytest.mark.asyncio
async def test_account_delete_removes_user(client: AsyncClient):
    token = await _register_user(client, "delete-user@example.com", "delete-device-1")

    response = await client.delete(
        "/account", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204

    async with TestingSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        assert users == []

    followup = await client.get(
        "/account/export", headers={"Authorization": f"Bearer {token}"}
    )
    assert followup.status_code == 401
