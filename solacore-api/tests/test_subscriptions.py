"""Subscription endpoint tests."""

import pytest
from app.config import get_settings
from app.models.subscription import Subscription
from app.models.user import User
from app.services import stripe_service
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal

STRIPE_PRICE_STANDARD = "price_standard_test"
STRIPE_PRICE_PRO = "price_pro_test"


@pytest.fixture(autouse=True)
def _configure_payments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STRIPE_PRICE_STANDARD", STRIPE_PRICE_STANDARD)
    monkeypatch.setenv("STRIPE_PRICE_PRO", STRIPE_PRICE_PRO)
    monkeypatch.setenv("PAYMENTS_ENABLED", "true")
    settings = get_settings()
    monkeypatch.setattr(settings, "payments_enabled", True)
    monkeypatch.setattr(settings, "stripe_price_standard", STRIPE_PRICE_STANDARD)
    monkeypatch.setattr(settings, "stripe_price_pro", STRIPE_PRICE_PRO)
    monkeypatch.setattr(settings, "stripe_success_url", "https://example.com/success")
    monkeypatch.setattr(settings, "stripe_cancel_url", "https://example.com/cancel")


async def _register_user(client: AsyncClient, email: str, fingerprint: str) -> str:
    """Helper to register user and get access token."""
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123",
            "device_fingerprint": fingerprint,
        },
    )
    return response.cookies["access_token"]


async def _update_subscription(email: str, **updates: object) -> Subscription:
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.email == email)
        )
        subscription = result.scalar_one()
        for key, value in updates.items():
            setattr(subscription, key, value)
        await session.commit()
        await session.refresh(subscription)
        return subscription


@pytest.mark.asyncio
async def test_subscriptions_unauthenticated_returns_401(client: AsyncClient):
    """Unauthenticated request returns 401."""
    response = await client.get("/subscriptions/current")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_subscription(client: AsyncClient):
    """Get current subscription returns user's subscription."""
    await _register_user(client, "sub-current@example.com", "sub-device-001")
    response = await client.get("/subscriptions/current")
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "free"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_usage(client: AsyncClient):
    """Get usage returns current usage stats."""
    await _register_user(client, "sub-usage@example.com", "sub-device-002")
    response = await client.get("/subscriptions/usage")
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "free"
    assert data["sessions_used"] == 0
    assert data["sessions_limit"] == 10
    assert data["is_lifetime"] is True


@pytest.mark.asyncio
async def test_checkout_invalid_price_id(client: AsyncClient):
    """Checkout with invalid price_id returns 400."""
    await _register_user(client, "sub-checkout@example.com", "sub-device-003")
    response = await client.post(
        "/subscriptions/checkout", json={"price_id": "invalid_price"}
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "INVALID_PRICE_ID"


@pytest.mark.asyncio
async def test_portal_no_customer_returns_404(client: AsyncClient):
    """Portal without stripe_customer_id returns 404."""
    await _register_user(client, "sub-portal@example.com", "sub-device-005")
    response = await client.get("/subscriptions/portal")
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "NO_SUBSCRIPTION"


@pytest.mark.asyncio
async def test_checkout_success(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """Checkout creates session successfully."""

    async def _mock_checkout_session(user, subscription, price_id):
        return ("https://checkout.stripe.com/session_xxx", "sess_xxx")

    monkeypatch.setattr(
        stripe_service, "create_checkout_session", _mock_checkout_session
    )

    await _register_user(client, "sub-checkout-success@example.com", "sub-device-006")
    response = await client.post(
        "/subscriptions/checkout", json={"price_id": STRIPE_PRICE_STANDARD}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["checkout_url"] == "https://checkout.stripe.com/session_xxx"
    assert data["session_id"] == "sess_xxx"


@pytest.mark.asyncio
async def test_checkout_already_subscribed(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    """Checkout returns error when already subscribed to requested tier."""

    async def _mock_checkout_session(user, subscription, price_id):
        return ("https://checkout.stripe.com/session_xxx", "sess_xxx")

    monkeypatch.setattr(
        stripe_service, "create_checkout_session", _mock_checkout_session
    )

    email = "sub-checkout-already@example.com"
    await _register_user(client, email, "sub-device-007")
    await _update_subscription(email, tier="standard", status="active")

    response = await client.post(
        "/subscriptions/checkout", json={"price_id": STRIPE_PRICE_STANDARD}
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "ALREADY_SUBSCRIBED"


@pytest.mark.asyncio
async def test_portal_success(client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """Portal creates session successfully."""

    async def _mock_portal_session(customer_id: str):
        return "https://billing.stripe.com/portal_xxx"

    monkeypatch.setattr(stripe_service, "create_portal_session", _mock_portal_session)

    email = "sub-portal-success@example.com"
    await _register_user(client, email, "sub-device-008")
    await _update_subscription(email, stripe_customer_id="cus_test_123")

    response = await client.get("/subscriptions/portal")

    assert response.status_code == 200
    data = response.json()
    assert data["portal_url"] == "https://billing.stripe.com/portal_xxx"
