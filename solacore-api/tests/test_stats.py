"""统计功能测试"""

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
    cookies = response.cookies
    token = cookies.get("access_token")
    assert token is not None
    return token


def _get_auth_headers(token: str, fingerprint: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "X-Device-Fingerprint": fingerprint,
    }


@pytest.mark.asyncio
async def test_stats_overview_empty(client: AsyncClient):
    token = await _register_user(client, "stats-empty@example.com", "stats-device-001")
    headers = _get_auth_headers(token, "stats-device-001")

    response = await client.get("/stats/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total_sessions"] == 0
    assert data["status_distribution"] == {
        "active": 0,
        "completed": 0,
        "abandoned": 0,
    }
    assert data["top_tags"] == []
    assert data["daily_trend"] == []
    assert data["action_completion"] == {
        "total": 0,
        "completed": 0,
        "completion_rate": 0.0,
    }
    assert data["step_distribution"] == {
        "receive": 0,
        "clarify": 0,
        "reframe": 0,
        "options": 0,
        "commit": 0,
    }


@pytest.mark.asyncio
async def test_stats_overview_with_sessions(client: AsyncClient):
    token = await _register_user(
        client, "stats-sessions@example.com", "stats-device-002"
    )
    headers = _get_auth_headers(token, "stats-device-002")

    session_data = {
        "template_id": None,
        "locale": "zh",
    }

    await client.post("/sessions/", json=session_data, headers=headers)
    await client.post("/sessions/", json=session_data, headers=headers)

    response = await client.get("/stats/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total_sessions"] == 2
    assert data["status_distribution"]["active"] == 2


@pytest.mark.asyncio
async def test_stats_overview_with_tags(client: AsyncClient):
    token = await _register_user(client, "stats-tags@example.com", "stats-device-003")
    headers = _get_auth_headers(token, "stats-device-003")

    session_data = {
        "template_id": None,
        "locale": "zh",
    }

    response1 = await client.post("/sessions/", json=session_data, headers=headers)
    session1_id = response1.json()["session_id"]

    response2 = await client.post("/sessions/", json=session_data, headers=headers)
    session2_id = response2.json()["session_id"]

    await client.patch(
        f"/sessions/{session1_id}",
        json={"tags": ["工作", "紧急"]},
        headers=headers,
    )
    await client.patch(
        f"/sessions/{session2_id}",
        json={"tags": ["工作", "学习"]},
        headers=headers,
    )

    response = await client.get("/stats/overview", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data["top_tags"]) > 0
    work_tag = next((t for t in data["top_tags"] if t["tag"] == "工作"), None)
    assert work_tag is not None
    assert work_tag["count"] == 2


@pytest.mark.asyncio
async def test_stats_overview_unauthorized(client: AsyncClient):
    response = await client.get("/stats/overview")
    assert response.status_code == 401
