from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from app.learn.prompts.registry import TOOL_REGISTRY
from app.models.learn_message import LearnMessage, LearnMessageRole
from app.models.learn_session import LearnSession
from app.routers.learn.create import DEFAULT_QUICK_TOOLS
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient,
) -> tuple[AsyncClient, str, str]:
    email = f"learn-tools-{uuid4()}@example.com"
    fingerprint = f"learn-device-{uuid4()}"
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123",
            "device_fingerprint": fingerprint,
        },
    )
    assert response.status_code == 201
    token = response.cookies["access_token"]
    return client, token, fingerprint


def _get_auth_headers(token: str, fingerprint: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "X-Device-Fingerprint": fingerprint,
    }


async def _create_learn_session(
    client: AsyncClient,
    token: str,
    fingerprint: str,
    mode: str | None = None,
) -> str:
    params = {"mode": mode} if mode else None
    response = await client.post(
        "/learn",
        params=params,
        headers=_get_auth_headers(token, fingerprint),
    )
    assert response.status_code == 201
    return response.json()["session_id"]


@pytest.mark.asyncio
async def test_get_tools_returns_expected_fields(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    response = await client.get(
        "/learn/tools",
        headers=_get_auth_headers(token, fingerprint),
    )

    assert response.status_code == 200
    data = response.json()
    tools = data["tools"]

    assert len(tools) == 10
    for tool in tools:
        assert "id" in tool
        assert "name" in tool
        assert "description" in tool
        assert "estimated_minutes" in tool
        assert "适用场景" in tool


@pytest.mark.asyncio
async def test_create_session_quick_mode_sets_tool_plan(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint, mode="quick")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(LearnSession.id == UUID(session_id))
        )
        learn_session = result.scalar_one()

    assert learn_session.learning_mode == "quick"
    assert learn_session.tool_plan == DEFAULT_QUICK_TOOLS


@pytest.mark.asyncio
async def test_create_session_deep_mode_sets_all_tools(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint, mode="deep")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(LearnSession.id == UUID(session_id))
        )
        learn_session = result.scalar_one()

    assert learn_session.learning_mode == "deep"
    assert learn_session.tool_plan == list(TOOL_REGISTRY.keys())


@pytest.mark.asyncio
async def test_create_session_custom_mode_sets_empty_tool_plan(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint, mode="custom")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(LearnSession.id == UUID(session_id))
        )
        learn_session = result.scalar_one()

    assert learn_session.learning_mode == "custom"
    assert learn_session.tool_plan == []


@pytest.mark.asyncio
async def test_create_session_defaults_to_quick_mode(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint)

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(LearnSession.id == UUID(session_id))
        )
        learn_session = result.scalar_one()

    assert learn_session.learning_mode == "quick"
    assert learn_session.tool_plan == DEFAULT_QUICK_TOOLS


@pytest.mark.asyncio
async def test_set_learn_path_quick_mode(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint)

    response = await client.post(
        f"/learn/{session_id}/path",
        json={"mode": "quick"},
        headers=_get_auth_headers(token, fingerprint),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "quick"
    assert data["tool_plan"] == DEFAULT_QUICK_TOOLS
    assert data["current_tool"] == DEFAULT_QUICK_TOOLS[0]


@pytest.mark.asyncio
async def test_set_learn_path_deep_mode(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint)

    response = await client.post(
        f"/learn/{session_id}/path",
        json={"mode": "deep"},
        headers=_get_auth_headers(token, fingerprint),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "deep"
    assert data["tool_plan"] == list(TOOL_REGISTRY.keys())
    assert data["current_tool"] == list(TOOL_REGISTRY.keys())[0]


@pytest.mark.asyncio
async def test_set_learn_path_custom_mode_with_tools(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint)
    selected_tools = ["pareto", "feynman", "grow"]

    response = await client.post(
        f"/learn/{session_id}/path",
        json={"mode": "custom", "selected_tools": selected_tools},
        headers=_get_auth_headers(token, fingerprint),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "custom"
    assert data["tool_plan"] == selected_tools
    assert data["current_tool"] == selected_tools[0]


@pytest.mark.asyncio
async def test_set_learn_path_invalid_mode_returns_error(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint)

    response = await client.post(
        f"/learn/{session_id}/path",
        json={"mode": "invalid"},
        headers=_get_auth_headers(token, fingerprint),
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_set_learn_path_invalid_tool_returns_error(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint)

    response = await client.post(
        f"/learn/{session_id}/path",
        json={"mode": "custom", "selected_tools": ["not-a-tool"]},
        headers=_get_auth_headers(token, fingerprint),
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "INVALID_TOOL"


@pytest.mark.asyncio
async def test_switch_current_tool_in_plan(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint, mode="quick")

    response = await client.patch(
        f"/learn/{session_id}/current-tool",
        json={"tool": "feynman"},
        headers=_get_auth_headers(token, fingerprint),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_tool"] == "feynman"
    assert data["tool_plan"] == DEFAULT_QUICK_TOOLS


@pytest.mark.asyncio
async def test_switch_current_tool_not_in_plan_returns_error(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint, mode="quick")

    response = await client.patch(
        f"/learn/{session_id}/current-tool",
        json={"tool": "spaced"},
        headers=_get_auth_headers(token, fingerprint),
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "TOOL_NOT_IN_PLAN"


@pytest.mark.asyncio
async def test_get_learn_progress_returns_expected_values(
    authenticated_client: tuple[AsyncClient, str, str],
):
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint, mode="quick")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnSession).where(LearnSession.id == UUID(session_id))
        )
        learn_session = result.scalar_one()
        learn_session.current_tool = DEFAULT_QUICK_TOOLS[1]
        await session.commit()

    response = await client.get(
        f"/learn/{session_id}/progress",
        headers=_get_auth_headers(token, fingerprint),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "quick"
    assert data["tool_plan"] == DEFAULT_QUICK_TOOLS
    assert data["current_tool"] == DEFAULT_QUICK_TOOLS[1]
    assert data["completed_tools"] == [DEFAULT_QUICK_TOOLS[0]]
    assert data["progress_percentage"] == 33


@pytest.mark.asyncio
async def test_send_learn_message_with_tool_parameter(
    authenticated_client: tuple[AsyncClient, str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["ok"]:
                yield token

    monkeypatch.setattr("app.routers.learn.message.AIService", FakeAIService)
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint)

    async with client.stream(
        "POST",
        f"/learn/{session_id}/messages",
        json={"content": "Hi", "tool": "pareto"},
        headers=_get_auth_headers(token, fingerprint),
    ) as response:
        assert response.status_code == 200
        body = (await response.aread()).decode()

    assert "event: done" in body

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(LearnMessage).where(LearnMessage.session_id == UUID(session_id))
        )
        messages = result.scalars().all()

    assert any(
        message.role == LearnMessageRole.USER.value and message.tool == "pareto"
        for message in messages
    )
    assert any(
        message.role == LearnMessageRole.ASSISTANT.value and message.tool == "pareto"
        for message in messages
    )


@pytest.mark.asyncio
async def test_send_learn_message_with_step_parameter(
    authenticated_client: tuple[AsyncClient, str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["ok"]:
                yield token

    monkeypatch.setattr("app.routers.learn.message.AIService", FakeAIService)
    client, token, fingerprint = authenticated_client
    session_id = await _create_learn_session(client, token, fingerprint)

    async with client.stream(
        "POST",
        f"/learn/{session_id}/messages",
        json={"content": "Hi", "step": "start"},
        headers=_get_auth_headers(token, fingerprint),
    ) as response:
        assert response.status_code == 200
        body = (await response.aread()).decode()

    assert "event: done" in body
