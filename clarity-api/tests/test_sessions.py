"""Session revoke security tests."""
from uuid import UUID

import pytest
from httpx import AsyncClient

from app.utils.security import decode_token


@pytest.mark.asyncio
async def test_revoked_session_invalidates_token(client: AsyncClient):
    register_resp = await client.post("/auth/register", json={
        "email": "revoke-session-token@example.com",
        "password": "Password123",
        "device_fingerprint": "session-token-001"
    })
    assert register_resp.status_code == 201
    access_token = register_resp.json()["access_token"]

    payload = decode_token(access_token) or {}
    session_id = UUID(str(payload.get("sid")))

    revoke_resp = await client.delete(
        f"/auth/sessions/{session_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert revoke_resp.status_code == 204

    devices_resp = await client.get(
        "/auth/devices",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert devices_resp.status_code == 401
    assert devices_resp.json()["detail"]["error"] == "SESSION_REVOKED"
