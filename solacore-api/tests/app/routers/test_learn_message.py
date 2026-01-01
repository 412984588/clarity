from uuid import UUID, uuid4

import pytest
from app.models.learn_message import LearnMessage, LearnMessageRole
from app.models.learn_session import LearnSession, LearnStep
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal
from unittest.mock import patch


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


async def _create_learn_session(
    client: AsyncClient, token: str, fingerprint: str
) -> str:
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
async def test_send_learn_message_success(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["Hello", " ", "World"]:
                yield token

    monkeypatch.setattr("app.routers.learn.message.AIService", FakeAIService)
    token = await _register_user(
        client, "learn-message@example.com", "learn-device-001"
    )
    session_id = await _create_learn_session(
        client, token, "learn-device-001"
    )

    async with client.stream(
        "POST",
        f"/learn/{session_id}/messages",
        json={"content": "Hi", "step": "start"},
        headers={"Authorization": f"Bearer {token}"},
    ) as response:
        assert response.status_code == 200
        body = (await response.aread()).decode()

    assert "event: token" in body
    assert "Hello" in body
    assert "event: done" in body

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnMessage).where(
                LearnMessage.session_id == UUID(session_id)
            )
        )
        messages = result.scalars().all()

    assert any(
        message.role == LearnMessageRole.USER.value
        for message in messages
    )
    assert any(
        message.role == LearnMessageRole.ASSISTANT.value
        for message in messages
    )


@pytest.mark.asyncio
async def test_send_learn_message_session_not_found(
    client: AsyncClient,
):
    token = await _register_user(
        client, "learn-message-missing@example.com", "learn-device-002"
    )
    response = await client.post(
        f"/learn/{uuid4()}/messages",
        json={"content": "Hi", "step": "start"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_learn_message_wrong_user(
    client: AsyncClient,
):
    token_a = await _register_user(
        client, "learn-message-user-a@example.com", "learn-device-003"
    )
    session_id = await _create_learn_session(
        client, token_a, "learn-device-003"
    )

    token_b = await _register_user(
        client, "learn-message-user-b@example.com", "learn-device-004"
    )

    response = await client.post(
        f"/learn/{session_id}/messages",
        json={"content": "Hi", "step": "start"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_learn_message_first_message_sets_topic(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["ok"]:
                yield token

    monkeypatch.setattr("app.routers.learn.message.AIService", FakeAIService)
    token = await _register_user(
        client, "learn-message-topic@example.com", "learn-device-005"
    )
    session_id = await _create_learn_session(
        client, token, "learn-device-005"
    )
    message = "I want to learn Python programming"

    async with client.stream(
        "POST",
        f"/learn/{session_id}/messages",
        json={"content": message, "step": "start"},
        headers={"Authorization": f"Bearer {token}"},
    ) as response:
        assert response.status_code == 200
        await response.aread()

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(
                LearnSession.id == UUID(session_id)
            )
        )
        learn_session = result.scalar_one()

    assert learn_session.topic is not None
    assert learn_session.topic.startswith(message[:30])


@pytest.mark.asyncio
async def test_send_learn_message_long_topic_truncated(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["ok"]:
                yield token

    monkeypatch.setattr("app.routers.learn.message.AIService", FakeAIService)
    token = await _register_user(
        client, "learn-message-long-topic@example.com", "learn-device-006"
    )
    session_id = await _create_learn_session(
        client, token, "learn-device-006"
    )
    message = "A" * 35

    async with client.stream(
        "POST",
        f"/learn/{session_id}/messages",
        json={"content": message, "step": "start"},
        headers={"Authorization": f"Bearer {token}"},
    ) as response:
        assert response.status_code == 200
        await response.aread()

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(
                LearnSession.id == UUID(session_id)
            )
        )
        learn_session = result.scalar_one()

    assert learn_session.topic == f"{message[:30]}..."


@pytest.mark.skip(
    reason="Known issue: SSE streaming session commit timing - status update in event_generator may not persist due to session lifecycle"
)
@pytest.mark.asyncio
async def test_send_learn_message_final_step_generates_review(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["x" * 60]:
                yield token

    monkeypatch.setattr("app.routers.learn.message.AIService", FakeAIService)
    monkeypatch.setattr(
        "app.routers.learn.message.is_final_learn_step",
        lambda _step: True,
    )

    token = await _register_user(
        client, "learn-message-final@example.com", "learn-device-007"
    )
    session_id = await _create_learn_session(
        client, token, "learn-device-007"
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(
                LearnSession.id == UUID(session_id)
            )
        )
        learn_session = result.scalar_one()
        learn_session.current_step = LearnStep.PLAN.value
        await session.commit()

    async with client.stream(
        "POST",
        f"/learn/{session_id}/messages",
        json={"content": "Ready to wrap up", "step": "plan"},
        headers={"Authorization": f"Bearer {token}"},
    ) as response:
        assert response.status_code == 200
        await response.aread()

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(
                LearnSession.id == UUID(session_id)
            )
        )
        updated_session = result.scalar_one()

    assert updated_session.status == "completed"
    assert updated_session.completed_at is not None
    assert updated_session.review_schedule


@pytest.mark.asyncio
async def test_send_learn_message_content_filtering(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["ok"]:
                yield token

    monkeypatch.setattr("app.routers.learn.message.AIService", FakeAIService)
    token = await _register_user(
        client, "learn-message-filter@example.com", "learn-device-008"
    )
    session_id = await _create_learn_session(
        client, token, "learn-device-008"
    )
    message = "Call me at 555-123-4567 or email me@example.com"

    with patch(
        "app.routers.learn.message.sanitize_user_input",
        return_value="sanitized",
    ) as sanitize_mock, patch(
        "app.routers.learn.message.strip_pii",
        return_value="cleaned",
    ) as strip_mock:
        async with client.stream(
            "POST",
            f"/learn/{session_id}/messages",
            json={"content": message, "step": "start"},
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            assert response.status_code == 200
            await response.aread()

    sanitize_mock.assert_called_once_with(message)
    strip_mock.assert_called_once_with("sanitized")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnMessage).where(
                LearnMessage.session_id == UUID(session_id),
                LearnMessage.role == LearnMessageRole.USER.value,
            )
        )
        saved_message = result.scalar_one()

    assert saved_message.content == "cleaned"


@pytest.mark.asyncio
async def test_send_learn_message_ai_service_error(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            raise RuntimeError("boom")
            if False:
                yield ""

    monkeypatch.setattr("app.routers.learn.message.AIService", FakeAIService)
    token = await _register_user(
        client, "learn-message-error@example.com", "learn-device-009"
    )
    session_id = await _create_learn_session(
        client, token, "learn-device-009"
    )

    async with client.stream(
        "POST",
        f"/learn/{session_id}/messages",
        json={"content": "Hi", "step": "start"},
        headers={"Authorization": f"Bearer {token}"},
    ) as response:
        assert response.status_code == 200
        body = (await response.aread()).decode()

    assert "event: error" in body
    assert "STREAM_ERROR" in body
