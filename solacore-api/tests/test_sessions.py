"""Session tests."""

from uuid import UUID, uuid4

import pytest
from app.config import Settings
from app.middleware.rate_limit import limiter
from app.models.solve_session import SolveStep
from app.models.step_history import StepHistory
from app.models.subscription import Subscription, Usage
from app.utils.security import decode_token
from httpx import AsyncClient, Response
from sqlalchemy import delete, select
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
    # httpOnly cookie mode: get token from cookie
    return response.cookies["access_token"]


async def _create_session(
    client: AsyncClient, token: str, fingerprint: str
) -> Response:
    return await client.post(
        "/sessions",
        json={},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Device-Fingerprint": fingerprint,
        },
    )


async def _set_subscription_tier(user_id: UUID, tier: str) -> None:
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one()
        subscription.tier = tier  # type: ignore[assignment]
        await session.commit()


def _bypass_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(limiter, "enabled", False, raising=False)
    monkeypatch.setattr(limiter, "_enabled", False, raising=False)


@pytest.mark.asyncio
async def test_revoked_session_invalidates_token(client: AsyncClient):
    register_resp = await client.post(
        "/auth/register",
        json={
            "email": "revoke-session-token@example.com",
            "password": "Password123",
            "device_fingerprint": "session-token-001",
        },
    )
    assert register_resp.status_code == 201
    # httpOnly cookie mode: get token from cookie
    access_token = register_resp.cookies["access_token"]

    payload = decode_token(access_token) or {}
    session_id = UUID(str(payload.get("sid")))

    revoke_resp = await client.delete(
        f"/auth/sessions/{session_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert revoke_resp.status_code == 204

    devices_resp = await client.get(
        "/auth/devices", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert devices_resp.status_code == 401
    assert devices_resp.json()["detail"]["error"] == "SESSION_REVOKED"


@pytest.mark.asyncio
async def test_sessions_unauthenticated_returns_401(client: AsyncClient):
    response = await client.get("/sessions")
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_create_session_returns_201(client: AsyncClient):
    token = await _register_user(
        client, "session-create@example.com", "session-device-001"
    )
    response = await _create_session(client, token, "session-device-001")
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "active"
    assert data["current_step"] == "receive"
    assert "usage" in data


@pytest.mark.asyncio
async def test_create_session_device_not_found(client: AsyncClient):
    token = await _register_user(
        client, "session-device-missing@example.com", "session-device-009"
    )
    response = await _create_session(client, token, "session-device-missing")
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "DEVICE_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_session_creates_subscription_if_missing(client: AsyncClient):
    token = await _register_user(
        client, "session-subscription-missing@example.com", "session-device-010"
    )
    payload = decode_token(token) or {}
    user_id = UUID(str(payload.get("sub")))

    async with TestingSessionLocal() as session:
        await session.execute(
            delete(Subscription).where(Subscription.user_id == user_id)
        )
        await session.commit()

    response = await _create_session(client, token, "session-device-010")
    assert response.status_code == 201

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one()

    assert subscription.tier == "free"


@pytest.mark.asyncio
async def test_create_session_beta_mode_unlimited(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    beta_settings = Settings()
    beta_settings.beta_mode = True
    monkeypatch.setattr(
        "app.routers.sessions.create.get_settings", lambda: beta_settings
    )

    token = await _register_user(
        client, "session-beta@example.com", "session-device-011"
    )
    last_response = None
    for _ in range(12):
        last_response = await _create_session(client, token, "session-device-011")
        assert last_response.status_code == 201

    assert last_response is not None
    assert last_response.json()["usage"]["sessions_limit"] == 0


@pytest.mark.asyncio
async def test_create_session_quota_exceeded(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    # 确保 beta_mode 关闭，以便 session 限制生效
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "beta_mode", False)

    token = await _register_user(
        client, "session-quota@example.com", "session-device-012"
    )
    payload = decode_token(token) or {}
    user_id = UUID(str(payload.get("sub")))

    # 清理 Usage 表，确保测试从干净状态开始
    async with TestingSessionLocal() as session:
        await session.execute(delete(Usage).where(Usage.user_id == user_id))
        await session.commit()

    for _ in range(10):
        response = await _create_session(client, token, "session-device-012")
        assert response.status_code == 201

    response = await _create_session(client, token, "session-device-012")
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "QUOTA_EXCEEDED"

    async with TestingSessionLocal() as session:
        result = await session.execute(select(Usage).where(Usage.user_id == user_id))
        usage = result.scalar_one()

    assert usage.session_count == 10


@pytest.mark.asyncio
async def test_create_session_standard_tier_limit(client: AsyncClient):
    token = await _register_user(
        client, "session-standard@example.com", "session-device-013"
    )
    payload = decode_token(token) or {}
    user_id = UUID(str(payload.get("sub")))
    await _set_subscription_tier(user_id, "standard")

    last_response = None
    for _ in range(11):
        last_response = await _create_session(client, token, "session-device-013")
        assert last_response.status_code == 201

    assert last_response is not None
    assert last_response.json()["usage"]["tier"] == "standard"


@pytest.mark.asyncio
async def test_create_session_pro_tier_unlimited(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    _bypass_rate_limit(monkeypatch)
    token = await _register_user(
        client, "session-pro@example.com", "session-device-014"
    )
    payload = decode_token(token) or {}
    user_id = UUID(str(payload.get("sub")))
    await _set_subscription_tier(user_id, "pro")

    last_response = None
    for _ in range(201):
        last_response = await _create_session(client, token, "session-device-014")
        assert last_response.status_code == 201

    assert last_response is not None
    assert last_response.json()["usage"]["tier"] == "pro"


@pytest.mark.asyncio
async def test_list_sessions_returns_array(client: AsyncClient):
    token = await _register_user(
        client, "session-list@example.com", "session-device-002"
    )
    await client.post(
        "/sessions",
        json={},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Device-Fingerprint": "session-device-002",
        },
    )
    response = await client.get(
        "/sessions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["sessions"], list)
    assert data["total"] >= 1
    assert data["limit"] == 20
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_get_session_returns_correct_data(client: AsyncClient):
    token = await _register_user(
        client, "session-get@example.com", "session-device-003"
    )
    create_resp = await client.post(
        "/sessions",
        json={},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Device-Fingerprint": "session-device-003",
        },
    )
    session_id = create_resp.json()["session_id"]

    response = await client.get(
        f"/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["status"] == "active"
    assert data["current_step"] == "receive"


@pytest.mark.asyncio
async def test_get_other_users_session_returns_404(client: AsyncClient):
    token_a = await _register_user(
        client, "session-user-a@example.com", "session-device-004"
    )
    create_resp = await client.post(
        "/sessions",
        json={},
        headers={
            "Authorization": f"Bearer {token_a}",
            "X-Device-Fingerprint": "session-device-004",
        },
    )
    session_id = create_resp.json()["session_id"]

    token_b = await _register_user(
        client, "session-user-b@example.com", "session-device-005"
    )
    response = await client.get(
        f"/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_sse_endpoint_returns_event_stream(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["hello", "world"]:
                yield token

    monkeypatch.setattr("app.routers.sessions.stream.AIService", FakeAIService)
    token = await _register_user(
        client, "session-sse@example.com", "session-device-006"
    )
    create_resp = await client.post(
        "/sessions",
        json={},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Device-Fingerprint": "session-device-006",
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
        assert response.headers["content-type"].startswith("text/event-stream")
        body = (await response.aread()).decode()

    assert "event: token" in body
    assert "hello" in body
    assert "event: done" in body


@pytest.mark.asyncio
async def test_sse_invalid_session_returns_404(client: AsyncClient):
    token = await _register_user(
        client, "session-invalid@example.com", "session-device-007"
    )
    response = await client.post(
        f"/sessions/{uuid4()}/messages",
        json={"content": "hello", "step": "receive"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_sse_updates_step_history_message_count(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    class FakeAIService:
        async def stream(self, system_prompt: str, user_prompt: str):
            for token in ["ping"]:
                yield token

    monkeypatch.setattr("app.routers.sessions.stream.AIService", FakeAIService)
    token = await _register_user(
        client, "session-step-history@example.com", "session-device-008"
    )
    create_resp = await client.post(
        "/sessions",
        json={},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Device-Fingerprint": "session-device-008",
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
        await response.aread()

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(StepHistory)
            .where(
                StepHistory.session_id == UUID(session_id),
                StepHistory.step == SolveStep.RECEIVE.value,
            )
            .order_by(StepHistory.started_at.desc())
            .limit(1)
        )
        step_history = result.scalar_one_or_none()

    assert step_history is not None
    assert step_history.message_count == 1
