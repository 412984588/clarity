"""Webhook endpoint tests."""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from app.config import get_settings
from app.models.subscription import Subscription, Usage
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


async def _create_user_with_subscription_tier(
    email: str,
    tier: str,
    customer_id: str | None = None,
    subscription_id: str | None = None,
) -> str:
    """Create a user with a specific subscription tier directly in DB."""
    async with TestingSessionLocal() as session:
        user = User(email=email, password_hash="test", auth_provider="email")
        session.add(user)
        await session.flush()

        subscription = Subscription(
            user_id=user.id,
            tier=tier,
            status="active",
            stripe_customer_id=customer_id or f"cus_{uuid4().hex[:14]}",
            stripe_subscription_id=subscription_id or f"sub_{uuid4().hex[:14]}",
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
async def test_webhook_payments_disabled_returns_501(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    """Webhook returns 501 when payments are disabled."""
    settings = get_settings()
    monkeypatch.setattr(settings, "payments_enabled", False)

    response = await client.post(
        "/webhooks/stripe",
        content=json.dumps({"type": "test"}),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 501
    assert response.json()["detail"]["error"] == "PAYMENTS_DISABLED"


@pytest.mark.asyncio
async def test_webhook_invalid_signature_returns_400(client: AsyncClient):
    """Webhook with invalid signature returns 400."""
    with patch("app.routers.webhooks.stripe_service") as mock_stripe:
        import stripe

        mock_stripe.verify_webhook.side_effect = stripe.SignatureVerificationError(
            "Invalid", "sig"
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
async def test_webhook_empty_event_id_still_processes(client: AsyncClient):
    """Empty event_id should still process without idempotency record."""
    user_id = await _create_user_with_subscription("webhook-empty-id@example.com")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        customer_id = sub.stripe_customer_id

    event = {
        "id": "",
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
        result = await session.execute(select(ProcessedWebhookEvent))
        events = result.scalars().all()
        assert events == []
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.status == "past_due"


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
async def test_webhook_checkout_completed_missing_user_id(client: AsyncClient):
    """checkout.session.completed ignores missing user_id."""
    user_id = await _create_user_with_subscription("webhook-missing-user@example.com")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        original_customer_id = sub.stripe_customer_id
        original_subscription_id = sub.stripe_subscription_id
        original_tier = sub.tier

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_new_customer",
                "subscription": "sub_new_subscription",
                "client_reference_id": "",
                "metadata": {},
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

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.stripe_customer_id == original_customer_id
        assert sub.stripe_subscription_id == original_subscription_id
        assert sub.tier == original_tier


@pytest.mark.asyncio
async def test_webhook_checkout_completed_invalid_user_id(client: AsyncClient):
    """checkout.session.completed ignores invalid user_id values."""
    user_id = await _create_user_with_subscription("webhook-invalid-user@example.com")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        original_customer_id = sub.stripe_customer_id
        original_subscription_id = sub.stripe_subscription_id

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_new_customer",
                "subscription": "sub_new_subscription",
                "client_reference_id": user_id,
                "metadata": {"user_id": "not-a-uuid", "price_id": "price_standard"},
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

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.stripe_customer_id == original_customer_id
        assert sub.stripe_subscription_id == original_subscription_id


@pytest.mark.asyncio
async def test_webhook_checkout_completed_subscription_not_found(
    client: AsyncClient,
):
    """checkout.session.completed handles missing subscription."""
    missing_user_id = str(uuid4())

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_new_customer",
                "subscription": "sub_new_subscription",
                "client_reference_id": missing_user_id,
                "metadata": {"user_id": missing_user_id, "price_id": "price_standard"},
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
async def test_webhook_checkout_completed_missing_price_id(client: AsyncClient):
    """checkout.session.completed keeps tier when price_id missing."""
    user_id = await _create_user_with_subscription("webhook-missing-price@example.com")

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_new_customer",
                "subscription": "sub_new_subscription",
                "client_reference_id": user_id,
                "metadata": {"user_id": user_id},
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

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.tier == "free"
        assert sub.stripe_customer_id == "cus_new_customer"
        assert sub.stripe_subscription_id == "sub_new_subscription"
        assert sub.status == "active"


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
async def test_webhook_invoice_paid_subscription_not_found(
    client: AsyncClient,
):
    """invoice.paid ignores missing subscription."""
    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "invoice.paid",
        "data": {
            "object": {
                "customer": f"cus_{uuid4().hex[:14]}",
                "subscription": f"sub_{uuid4().hex[:14]}",
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

    async with TestingSessionLocal() as session:
        result = await session.execute(select(Usage))
        usage = result.scalars().all()
        assert usage == []


@pytest.mark.asyncio
async def test_webhook_invoice_paid_empty_lines(client: AsyncClient):
    """invoice.paid uses fallback period when no lines data."""
    user_id = await _create_user_with_subscription("webhook-invoice-empty@example.com")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        customer_id = sub.stripe_customer_id

    fixed_now = datetime(2024, 2, 15, 12, 0, 0)
    expected_start = fixed_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "invoice.paid",
        "data": {
            "object": {
                "customer": customer_id,
                "subscription": "sub_test",
                "lines": {"data": []},
            }
        },
    }

    with patch("app.routers.webhooks.stripe_service") as mock_stripe:
        mock_stripe.verify_webhook.return_value = event
        with patch("app.routers.webhooks.utc_now", return_value=fixed_now):
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
        assert sub.current_period_start == expected_start
        assert sub.current_period_end is None


@pytest.mark.asyncio
async def test_webhook_invoice_paid_paid_tier_resets_usage(
    client: AsyncClient,
):
    """invoice.paid resets usage for paid tiers."""
    user_id = await _create_user_with_subscription_tier(
        "webhook-invoice-paid-tier@example.com",
        "standard",
    )

    period_start = datetime.fromtimestamp(1704067200, tz=timezone.utc).replace(
        tzinfo=None
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        customer_id = sub.stripe_customer_id
        user_uuid = sub.user_id

        usage = Usage(
            user_id=user_uuid,
            period_start=period_start,
            session_count=7,
        )
        session.add(usage)
        await session.commit()

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

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Usage).where(
                Usage.user_id == user_uuid,
                Usage.period_start == period_start,
            )
        )
        usage = result.scalar_one()
        assert usage.session_count == 0


@pytest.mark.asyncio
async def test_webhook_invoice_paid_lookup_by_customer_id(
    client: AsyncClient,
):
    """invoice.paid finds subscription by customer_id when subscription_id missing."""
    customer_id = f"cus_{uuid4().hex[:14]}"
    user_id = await _create_user_with_subscription_tier(
        "webhook-invoice-customer@example.com",
        "standard",
        customer_id=customer_id,
    )

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "invoice.paid",
        "data": {
            "object": {
                "customer": customer_id,
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

    expected_start = datetime.fromtimestamp(1704067200, tz=timezone.utc).replace(
        tzinfo=None
    )

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.current_period_start == expected_start


@pytest.mark.asyncio
async def test_webhook_invoice_paid_free_tier_does_not_reset_usage(
    client: AsyncClient,
):
    """invoice.paid should not reset usage for free tier."""
    user_id = await _create_user_with_subscription("webhook-invoice-free@example.com")

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
        with patch(
            "app.routers.webhooks._reset_usage_for_period", new=AsyncMock()
        ) as mock_reset:
            response = await client.post(
                "/webhooks/stripe",
                content=json.dumps(event),
                headers={
                    "Content-Type": "application/json",
                    "Stripe-Signature": "valid_sig",
                },
            )

    assert response.status_code == 200
    mock_reset.assert_not_called()


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
async def test_webhook_payment_failed_subscription_not_found(
    client: AsyncClient,
):
    """invoice.payment_failed ignores missing subscription."""
    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "customer": f"cus_{uuid4().hex[:14]}",
                "subscription": f"sub_{uuid4().hex[:14]}",
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
async def test_webhook_subscription_deleted_subscription_not_found(
    client: AsyncClient,
):
    """customer.subscription.deleted ignores missing subscription."""
    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": f"sub_{uuid4().hex[:14]}",
                "customer": f"cus_{uuid4().hex[:14]}",
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


@pytest.mark.asyncio
async def test_webhook_unknown_event_type(client: AsyncClient):
    """Unknown event types are acknowledged without processing."""
    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "charge.refunded",
        "data": {"object": {"id": f"ch_{uuid4().hex[:14]}"}},
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
