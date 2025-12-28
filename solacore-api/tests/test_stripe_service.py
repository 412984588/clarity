"""Tests for Stripe service helpers."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import app.services.stripe_service as stripe_service
import pytest
from app.models.subscription import Subscription
from app.models.user import User


@pytest.fixture
def stripe_settings():
    return SimpleNamespace(
        stripe_secret_key="sk_test_123",
        stripe_webhook_secret="whsec_test_123",
        stripe_success_url="https://example.com/success",
        stripe_cancel_url="https://example.com/cancel",
    )


@pytest.fixture
def sync_to_thread(monkeypatch):
    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(stripe_service.asyncio, "to_thread", fake_to_thread)


@pytest.mark.asyncio
async def test_create_checkout_session_creates_customer_and_session(
    stripe_settings, sync_to_thread
):
    customer_create = MagicMock(return_value={"id": "cus_123"})
    session_create = MagicMock(return_value={"url": "https://checkout", "id": "cs_123"})

    user = User(email="stripe-new@example.com")
    user.id = uuid4()
    user.subscription = Subscription(user_id=user.id)

    with patch(
        "app.services.stripe_service.get_settings", return_value=stripe_settings
    ):
        with (
            patch(
                "app.services.stripe_service.stripe.Customer.create", customer_create
            ),
            patch(
                "app.services.stripe_service.stripe.checkout.Session.create",
                session_create,
            ),
        ):
            url, session_id = await stripe_service.create_checkout_session(
                user, "price_123"
            )

    assert url == "https://checkout"
    assert session_id == "cs_123"
    assert user.subscription.stripe_customer_id == "cus_123"
    customer_create.assert_called_once_with(
        email=str(user.email),
        metadata={"user_id": str(user.id)},
    )
    session_create.assert_called_once_with(
        customer="cus_123",
        mode="subscription",
        line_items=[{"price": "price_123", "quantity": 1}],
        success_url=stripe_settings.stripe_success_url,
        cancel_url=stripe_settings.stripe_cancel_url,
        client_reference_id=str(user.id),
        metadata={"user_id": str(user.id), "price_id": "price_123"},
    )


@pytest.mark.asyncio
async def test_create_checkout_session_uses_existing_customer(
    stripe_settings, sync_to_thread
):
    customer_create = MagicMock()
    session_create = MagicMock(return_value={"url": "https://checkout", "id": "cs_999"})

    user = User(email="stripe-existing@example.com")
    user.id = uuid4()
    subscription = Subscription(user_id=user.id)
    subscription.stripe_customer_id = "cus_existing"
    user.subscription = subscription

    with patch(
        "app.services.stripe_service.get_settings", return_value=stripe_settings
    ):
        with (
            patch(
                "app.services.stripe_service.stripe.Customer.create", customer_create
            ),
            patch(
                "app.services.stripe_service.stripe.checkout.Session.create",
                session_create,
            ),
        ):
            url, session_id = await stripe_service.create_checkout_session(
                user, "price_456"
            )

    assert url == "https://checkout"
    assert session_id == "cs_999"
    customer_create.assert_not_called()


@pytest.mark.asyncio
async def test_create_checkout_session_requires_subscription(stripe_settings):
    user = User(email="stripe-missing@example.com")
    user.id = uuid4()

    with patch(
        "app.services.stripe_service.get_settings", return_value=stripe_settings
    ):
        with pytest.raises(ValueError, match="NO_SUBSCRIPTION"):
            await stripe_service.create_checkout_session(user, "price_123")


@pytest.mark.asyncio
async def test_create_portal_session(stripe_settings, sync_to_thread):
    portal_create = MagicMock(return_value={"url": "https://portal"})

    with patch(
        "app.services.stripe_service.get_settings", return_value=stripe_settings
    ):
        with patch(
            "app.services.stripe_service.stripe.billing_portal.Session.create",
            portal_create,
        ):
            url = await stripe_service.create_portal_session("cus_321")

    assert url == "https://portal"
    portal_create.assert_called_once_with(
        customer="cus_321",
        return_url=stripe_settings.stripe_success_url,
    )


def test_verify_webhook(stripe_settings):
    payload = b'{"id":"evt_123"}'
    signature = "sig_test"
    event = {"id": "evt_123"}

    construct_event = MagicMock(return_value=event)

    with patch(
        "app.services.stripe_service.get_settings", return_value=stripe_settings
    ):
        with patch(
            "app.services.stripe_service.stripe.Webhook.construct_event",
            construct_event,
        ):
            result = stripe_service.verify_webhook(payload, signature)

    assert result == event
    construct_event.assert_called_once_with(
        payload=payload,
        sig_header=signature,
        secret=stripe_settings.stripe_webhook_secret,
    )
