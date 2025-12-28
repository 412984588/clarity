"""PATCH /sessions tests."""

import pytest
from httpx import AsyncClient


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


async def _create_session(client: AsyncClient, token: str, fingerprint: str) -> str:
    response = await client.post(
        "/sessions",
        json={},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Device-Fingerprint": fingerprint,
        },
    )
    assert response.status_code == 201
    return response.json()["session_id"]


@pytest.mark.asyncio
async def test_update_status_success(client: AsyncClient):
    token = await _register_user(
        client, "session-patch-status@example.com", "session-patch-device-001"
    )
    session_id = await _create_session(client, token, "session-patch-device-001")

    response = await client.patch(
        f"/sessions/{session_id}",
        json={"status": "abandoned"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["status"] == "abandoned"
    assert data["current_step"] == "receive"
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_update_step_valid_transition(client: AsyncClient):
    token = await _register_user(
        client, "session-patch-step@example.com", "session-patch-device-002"
    )
    session_id = await _create_session(client, token, "session-patch-device-002")

    response = await client.patch(
        f"/sessions/{session_id}",
        json={"current_step": "clarify"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_step"] == "clarify"


@pytest.mark.asyncio
async def test_update_step_invalid_transition_fails(client: AsyncClient):
    token = await _register_user(
        client, "session-patch-invalid@example.com", "session-patch-device-003"
    )
    session_id = await _create_session(client, token, "session-patch-device-003")

    response = await client.patch(
        f"/sessions/{session_id}",
        json={"current_step": "commit"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "INVALID_STEP_TRANSITION"


@pytest.mark.asyncio
async def test_update_other_users_session_fails(client: AsyncClient):
    token_a = await _register_user(
        client, "session-patch-user-a@example.com", "session-patch-device-004"
    )
    session_id = await _create_session(client, token_a, "session-patch-device-004")

    token_b = await _register_user(
        client, "session-patch-user-b@example.com", "session-patch-device-005"
    )
    response = await client.patch(
        f"/sessions/{session_id}",
        json={"status": "abandoned"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "SESSION_NOT_FOUND"
