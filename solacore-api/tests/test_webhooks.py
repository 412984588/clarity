"""Webhook endpoint tests."""

import json
from unittest.mock import patch
from uuid import uuid4

import pytest
from app.config import get_settings
from app.models.subscription import Subscription
from app.models.user import User
from app.models.webhook_event import ProcessedWebhookEvent
from httpx import AsyncClient
from sqlalchemy import select
from tests.conftest import TestingSessionLocal


async def _create_user_with_subscription(email: str) -> str:
    """Create a user with subscription directly in DB."""
    async with TestingSessionLocal() as session:
        user = User(email=email, password_hash="test", auth_provider="email")
        session.add(user)
        await session.flush()

        subscription = Subscription(
            user_id=user.id,
            tier="free",
            status="active",
            stripe_customer_id=f"cus_{uuid4().hex[:14]}",
            stripe_subscription_id=f"sub_{uuid4().hex[:14]}",
        )
        session.add(subscription)
        await session.commit()
        return str(user.id)


@pytest.fixture(autouse=True)
def _configure_payments(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "payments_enabled", True)
    monkeypatch.setattr(settings, "stripe_price_standard", "price_standard")
    monkeypatch.setattr(settings, "stripe_price_pro", "price_pro")


@pytest.mark.asyncio
async def test_webhook_missing_signature_returns_400(client: AsyncClient):
    """Webhook without signature returns 400."""
    response = await client.post(
        "/webhooks/stripe",
        content=json.dumps({"type": "test"}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "MISSING_SIGNATURE"


@pytest.mark.asyncio
async def test_webhook_invalid_signature_returns_400(client: AsyncClient):
    """Webhook with invalid signature returns 400."""
    with patch("app.routers.webhooks.stripe_service") as mock_stripe:
        import stripe

        mock_stripe.verify_webhook.side_effect = (
            stripe.error.SignatureVerificationError("Invalid", "sig")
        )

        response = await client.post(
            "/webhooks/stripe",
            content=json.dumps({"type": "test"}),
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "invalid_sig",
            },
        )
    assert response.status_code == 400
    assert response.json()["error"] == "INVALID_SIGNATURE"


@pytest.mark.asyncio
async def test_webhook_checkout_completed(client: AsyncClient):
    """checkout.session.completed updates subscription."""
    user_id = await _create_user_with_subscription("webhook-checkout@example.com")

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_new_customer",
                "subscription": "sub_new_subscription",
                "client_reference_id": user_id,
                "metadata": {"user_id": user_id, "price_id": "price_standard"},
            }
        },
    }

    with patch("app.routers.webhooks.stripe_service") as mock_stripe:
        mock_stripe.verify_webhook.return_value = event
        with patch("app.routers.webhooks.get_settings") as mock_settings:
            mock_settings.return_value.stripe_price_standard = "price_standard"
            mock_settings.return_value.stripe_price_pro = "price_pro"
            mock_settings.return_value.payments_enabled = True

            response = await client.post(
                "/webhooks/stripe",
                content=json.dumps(event),
                headers={
                    "Content-Type": "application/json",
                    "Stripe-Signature": "valid_sig",
                },
            )

    assert response.status_code == 200
    assert response.json() == {"received": True}


@pytest.mark.asyncio
async def test_webhook_stripe_idempotency(client: AsyncClient):
    """Duplicate Stripe events are ignored via DB idempotency."""
    user_id = await _create_user_with_subscription("webhook-idempotency@example.com")

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_new_customer",
                "subscription": "sub_new_subscription",
                "client_reference_id": user_id,
                "metadata": {"user_id": user_id, "price_id": "price_standard"},
            }
        },
    }

    with patch("app.routers.webhooks.stripe_service") as mock_stripe:
        mock_stripe.verify_webhook.return_value = event
        with patch("app.routers.webhooks.get_settings") as mock_settings:
            mock_settings.return_value.stripe_price_standard = "price_standard"
            mock_settings.return_value.stripe_price_pro = "price_pro"
            mock_settings.return_value.payments_enabled = True

            first = await client.post(
                "/webhooks/stripe",
                content=json.dumps(event),
                headers={
                    "Content-Type": "application/json",
                    "Stripe-Signature": "valid_sig",
                },
            )
            second = await client.post(
                "/webhooks/stripe",
                content=json.dumps(event),
                headers={
                    "Content-Type": "application/json",
                    "Stripe-Signature": "valid_sig",
                },
            )

    assert first.status_code == 200
    assert second.status_code == 200

    async with TestingSessionLocal() as session:
        result = await session.execute(select(ProcessedWebhookEvent))
        events = result.scalars().all()
        assert len(events) == 1
        assert events[0].source == "stripe"


@pytest.mark.asyncio
async def test_webhook_invoice_paid(client: AsyncClient):
    """invoice.paid updates subscription period."""
    user_id = await _create_user_with_subscription("webhook-invoice@example.com")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        customer_id = sub.stripe_customer_id

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "invoice.paid",
        "data": {
            "object": {
                "customer": customer_id,
                "subscription": "sub_test",
                "lines": {
                    "data": [{"period": {"start": 1704067200, "end": 1706745600}}]
                },
            }
        },
    }

    with patch("app.routers.webhooks.stripe_service") as mock_stripe:
        mock_stripe.verify_webhook.return_value = event

        response = await client.post(
            "/webhooks/stripe",
            content=json.dumps(event),
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "valid_sig",
            },
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_payment_failed(client: AsyncClient):
    """invoice.payment_failed marks subscription as past_due."""
    user_id = await _create_user_with_subscription("webhook-failed@example.com")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        customer_id = sub.stripe_customer_id

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "invoice.payment_failed",
        "data": {"object": {"customer": customer_id, "subscription": "sub_test"}},
    }

    with patch("app.routers.webhooks.stripe_service") as mock_stripe:
        mock_stripe.verify_webhook.return_value = event

        response = await client.post(
            "/webhooks/stripe",
            content=json.dumps(event),
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "valid_sig",
            },
        )

    assert response.status_code == 200

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.status == "past_due"


@pytest.mark.asyncio
async def test_webhook_subscription_deleted(client: AsyncClient):
    """customer.subscription.deleted downgrades to free."""
    user_id = await _create_user_with_subscription("webhook-deleted@example.com")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        sub.tier = "standard"
        await session.commit()
        customer_id = sub.stripe_customer_id
        subscription_id = sub.stripe_subscription_id

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": subscription_id, "customer": customer_id}},
    }

    with patch("app.routers.webhooks.stripe_service") as mock_stripe:
        mock_stripe.verify_webhook.return_value = event

        response = await client.post(
            "/webhooks/stripe",
            content=json.dumps(event),
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "valid_sig",
            },
        )

    assert response.status_code == 200

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.tier == "free"
        assert sub.status == "canceled"
