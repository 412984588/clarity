import hashlib
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import stripe
from app.config import get_settings
from app.database import get_db
from app.models.subscription import Subscription, Usage
from app.models.webhook_event import ProcessedWebhookEvent
from app.services import stripe_service
from app.services.cache_service import CacheService
from app.utils.datetime_utils import utc_now
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
cache_service = CacheService()


def _resolve_tier(price_id: str) -> Optional[str]:
    settings = get_settings()
    price_to_tier = {
        settings.stripe_price_standard: "standard",
        settings.stripe_price_pro: "pro",
    }
    return price_to_tier.get(price_id)


def _period_start_from_timestamp(timestamp: Optional[int]) -> datetime:
    if timestamp is None:
        return utc_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(tzinfo=None)


def _period_end_from_timestamp(timestamp: Optional[int]) -> Optional[datetime]:
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(tzinfo=None)


def _compute_payload_hash(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


async def _check_and_record_event(
    db: AsyncSession, event_id: str, event_type: str, payload_hash: str
) -> bool:
    if not event_id:
        return True

    stmt = (
        pg_insert(ProcessedWebhookEvent)
        .values(
            event_id=event_id,
            event_type=event_type,
            source="stripe",
            payload_hash=payload_hash,
            processed_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        .on_conflict_do_nothing(index_elements=["event_id"])
    )

    result = await db.execute(stmt)
    return result.rowcount > 0  # type: ignore[attr-defined]


async def _get_subscription(
    db: AsyncSession,
    customer_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
) -> Optional[Subscription]:
    if subscription_id:
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            return subscription
    if customer_id:
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        )
        return result.scalar_one_or_none()
    return None


async def _reset_usage_for_period(
    db: AsyncSession,
    user_id: UUID,
    period_start: datetime,
) -> None:
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    stmt = pg_insert(Usage).values(
        user_id=user_id,
        period_start=period_start,
        session_count=0,
        updated_at=utc_now(),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "period_start"],
        set_={"session_count": 0, "updated_at": utc_now()},
    )
    await db.execute(stmt)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    response: Response,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    if not settings.payments_enabled:
        raise HTTPException(status_code=501, detail={"error": "PAYMENTS_DISABLED"})

    payload = await request.body()
    if not stripe_signature:
        return JSONResponse(
            status_code=400,
            content={"error": "MISSING_SIGNATURE"},
        )

    try:
        event = stripe_service.verify_webhook(payload, stripe_signature)
    except stripe.SignatureVerificationError:  # type: ignore[attr-defined]
        return JSONResponse(
            status_code=400,
            content={"error": "INVALID_SIGNATURE"},
        )

    event_id = str(event.get("id") or "")
    event_type = str(event.get("type") or "")
    payload_hash = _compute_payload_hash(payload)
    is_new_event = await _check_and_record_event(
        db, event_id=event_id, event_type=event_type, payload_hash=payload_hash
    )
    if not is_new_event:
        return {"received": True}

    data_object = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(db, data_object)
    elif event_type == "invoice.paid":
        await _handle_invoice_paid(db, data_object)
    elif event_type == "invoice.payment_failed":
        await _handle_invoice_payment_failed(db, data_object)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(db, data_object)

    await db.commit()
    return {"received": True}


async def _handle_checkout_completed(db: AsyncSession, session: dict) -> None:
    metadata = session.get("metadata") or {}
    user_id = metadata.get("user_id") or session.get("client_reference_id")
    if not user_id:
        return
    try:
        user_uuid = UUID(str(user_id))
    except (TypeError, ValueError):
        return

    price_id = metadata.get("price_id")
    tier = _resolve_tier(price_id) if price_id else None

    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_uuid)
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        return

    if tier:
        subscription.tier = tier  # type: ignore[assignment]

    subscription.stripe_customer_id = session.get("customer")  # type: ignore[assignment]
    subscription.stripe_subscription_id = session.get("subscription")  # type: ignore[assignment]
    subscription.status = "active"  # type: ignore[assignment]
    subscription.cancel_at_period_end = False  # type: ignore[assignment]
    await cache_service.invalidate_subscription(user_uuid)


async def _handle_invoice_paid(db: AsyncSession, invoice: dict) -> None:
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")
    subscription = await _get_subscription(db, customer_id, subscription_id)
    if not subscription:
        return

    period_start_ts = None
    period_end_ts = None
    lines = invoice.get("lines", {}).get("data", [])
    if lines:
        period = lines[0].get("period", {})
        period_start_ts = period.get("start")
        period_end_ts = period.get("end")

    period_start = _period_start_from_timestamp(period_start_ts)
    period_end = _period_end_from_timestamp(period_end_ts)

    subscription.status = "active"  # type: ignore[assignment]
    subscription.current_period_start = period_start  # type: ignore[assignment]
    subscription.current_period_end = period_end  # type: ignore[assignment]

    if str(subscription.tier) != "free":
        await _reset_usage_for_period(db, subscription.user_id, period_start)  # type: ignore[arg-type]
    await cache_service.invalidate_subscription(subscription.user_id)


async def _handle_invoice_payment_failed(db: AsyncSession, invoice: dict) -> None:
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")
    subscription = await _get_subscription(db, customer_id, subscription_id)
    if not subscription:
        return
    subscription.status = "past_due"  # type: ignore[assignment]
    await cache_service.invalidate_subscription(subscription.user_id)


async def _handle_subscription_deleted(
    db: AsyncSession, stripe_subscription: dict
) -> None:
    customer_id = stripe_subscription.get("customer")
    subscription_id = stripe_subscription.get("id")
    subscription = await _get_subscription(db, customer_id, subscription_id)
    if not subscription:
        return

    subscription.tier = "free"  # type: ignore[assignment]
    subscription.status = "canceled"  # type: ignore[assignment]
    subscription.stripe_subscription_id = None  # type: ignore[assignment]
    subscription.current_period_start = None  # type: ignore[assignment]
    subscription.current_period_end = None  # type: ignore[assignment]
    subscription.cancel_at_period_end = False  # type: ignore[assignment]
    await cache_service.invalidate_subscription(subscription.user_id)
