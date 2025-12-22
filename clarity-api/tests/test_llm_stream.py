"""LLM stream tests."""
import json

import pytest
from httpx import AsyncClient

from app.routers import sessions as sessions_router


async def _register_user(client: AsyncClient, email: str, fingerprint: str) -> str:
    response = await client.post("/auth/register", json={
        "email": email,
        "password": "Password123",
        "device_fingerprint": fingerprint
    })
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_llm_stream_emits_tokens_and_done(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["foo", "bar"]:
                yield token

    monkeypatch.setattr(sessions_router, "AIService", FakeAIService)

    token = await _register_user(client, "llm-stream@example.com", "llm-device-001")
    create_resp = await client.post(
        "/sessions",
        json={},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Device-Fingerprint": "llm-device-001",
        },
    )
    session_id = create_resp.json()["session_id"]

    async with client.stream(
        "POST",
        f"/sessions/{session_id}/messages",
        json={"content": "hello", "step": "receive"},
        headers={"Authorization": f"Bearer {token}"},
    ) as response:
        assert response.status_code == 200
        body = (await response.aread()).decode()

    assert "event: token" in body
    assert "foo" in body
    assert "bar" in body
    assert "event: done" in body

    lines = body.splitlines()
    done_payload = None
    for idx, line in enumerate(lines):
        if line == "event: done" and idx + 1 < len(lines):
            data_line = lines[idx + 1]
            if data_line.startswith("data: "):
                done_payload = json.loads(data_line[len("data: "):])
                break

    assert done_payload is not None
    assert done_payload["next_step"] == "clarify"
    assert done_payload["emotion_detected"] == "neutral"
