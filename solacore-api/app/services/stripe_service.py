import asyncio
from typing import Tuple

import stripe
from app.config import get_settings
from app.models.subscription import Subscription
from app.models.user import User

STRIPE_API_VERSION = "2024-12-18.acacia"


def _configure_stripe():
    settings = get_settings()
    stripe.api_key = settings.stripe_secret_key
    stripe.api_version = STRIPE_API_VERSION
    return settings


async def create_checkout_session(
    user: User, subscription: Subscription, price_id: str
) -> Tuple[str, str]:
    settings = _configure_stripe()
    if not subscription:
        raise ValueError("NO_SUBSCRIPTION")

    customer_id = subscription.stripe_customer_id
    if not customer_id:
        customer = await asyncio.to_thread(
            stripe.Customer.create,
            email=str(user.email),
            metadata={"user_id": str(user.id)},
        )
        customer_id = customer.get("id")
        subscription.stripe_customer_id = customer_id  # type: ignore[assignment]

    session = await asyncio.to_thread(
        stripe.checkout.Session.create,
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=settings.stripe_success_url,
        cancel_url=settings.stripe_cancel_url,
        client_reference_id=str(user.id),
        metadata={"user_id": str(user.id), "price_id": price_id},
    )

    return str(session.get("url") or ""), str(session.get("id") or "")


async def create_portal_session(customer_id: str) -> str:
    settings = _configure_stripe()
    return_url = settings.stripe_success_url or settings.stripe_cancel_url
    session = await asyncio.to_thread(
        stripe.billing_portal.Session.create,
        customer=customer_id,
        return_url=return_url,
    )
    return str(session.get("url") or "")


def verify_webhook(payload: bytes, signature: str):
    settings = _configure_stripe()
    return stripe.Webhook.construct_event(
        payload=payload,
        sig_header=signature,
        secret=settings.stripe_webhook_secret,
    )
