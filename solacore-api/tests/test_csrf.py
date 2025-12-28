import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_csrf_missing_token_rejected(client_no_csrf: AsyncClient):
    register_resp = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "csrf-missing@example.com",
            "password": "Password123",
            "device_fingerprint": "csrf-device-001",
        },
    )
    assert register_resp.status_code == 201

    csrf_resp = await client_no_csrf.get("/auth/csrf")
    assert csrf_resp.status_code == 200

    response = await client_no_csrf.post(
        "/sessions",
        json={},
        headers={"X-Device-Fingerprint": "csrf-device-001"},
    )
    assert response.status_code == 403
    assert response.json()["error"] == "CSRF_TOKEN_MISSING"


@pytest.mark.asyncio
async def test_csrf_invalid_token_rejected(client_no_csrf: AsyncClient):
    register_resp = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "csrf-invalid@example.com",
            "password": "Password123",
            "device_fingerprint": "csrf-device-002",
        },
    )
    assert register_resp.status_code == 201

    csrf_resp = await client_no_csrf.get("/auth/csrf")
    assert csrf_resp.status_code == 200

    response = await client_no_csrf.post(
        "/sessions",
        json={},
        headers={
            "X-Device-Fingerprint": "csrf-device-002",
            "X-CSRF-Token": "invalid-token",
        },
    )
    assert response.status_code == 403
    assert response.json()["error"] == "CSRF_TOKEN_INVALID"


@pytest.mark.asyncio
async def test_csrf_valid_token_accepted(client_no_csrf: AsyncClient):
    register_resp = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "csrf-valid@example.com",
            "password": "Password123",
            "device_fingerprint": "csrf-device-003",
        },
    )
    assert register_resp.status_code == 201

    csrf_resp = await client_no_csrf.get("/auth/csrf")
    assert csrf_resp.status_code == 200
    token = csrf_resp.cookies.get("csrf_token")
    assert token

    response = await client_no_csrf.post(
        "/sessions",
        json={},
        headers={
            "X-Device-Fingerprint": "csrf-device-003",
            "X-CSRF-Token": token,
        },
    )
    assert response.status_code == 201
