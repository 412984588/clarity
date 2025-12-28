from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.subscription import Subscription, Usage
from app.models.user import User
from app.schemas.subscription import (
    CheckoutRequest,
    CheckoutResponse,
    PortalResponse,
    SubscriptionResponse,
    UsageResponse,
)
from app.services.cache_service import CacheService
from app.services import stripe_service
from app.utils.datetime_utils import utc_now
from app.utils.docs import COMMON_ERROR_RESPONSES

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])
cache_service = CacheService()

SESSION_LIMITS = {"free": 10, "standard": 100}
TIER_RANK = {"free": 0, "standard": 1, "pro": 2}


def _resolve_tier(price_id: str) -> Optional[str]:
    settings = get_settings()
    price_to_tier = {
        settings.stripe_price_standard: "standard",
        settings.stripe_price_pro: "pro",
    }
    return price_to_tier.get(price_id)


def _period_start_for_tier(subscription: Subscription) -> datetime:
    tier = str(subscription.tier)
    if tier == "free":
        anchor: datetime = subscription.created_at or utc_now()  # type: ignore[assignment]
        return anchor.replace(hour=0, minute=0, second=0, microsecond=0)
    if subscription.current_period_start:
        return subscription.current_period_start  # type: ignore[return-value]
    return utc_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _subscription_payload(subscription: Subscription) -> dict[str, object]:
    return {
        "tier": str(subscription.tier),
        "status": str(subscription.status),
        "period_start": subscription.current_period_start.isoformat()
        if subscription.current_period_start
        else None,
        "period_end": subscription.current_period_end.isoformat()
        if subscription.current_period_end
        else None,
        "cancel_at_period_end": bool(subscription.cancel_at_period_end),
        "stripe_customer_id": subscription.stripe_customer_id,
    }


async def _get_or_create_usage(
    db: AsyncSession,
    subscription: Subscription,
) -> Usage:
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    period_start = _period_start_for_tier(subscription)

    stmt = pg_insert(Usage).values(
        user_id=subscription.user_id,
        period_start=period_start,
        session_count=0,
    )
    stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "period_start"])
    await db.execute(stmt)
    await db.flush()

    result = await db.execute(
        select(Usage).where(
            Usage.user_id == subscription.user_id, Usage.period_start == period_start
        )
    )
    return result.scalar_one()


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    summary="创建订阅结账会话",
    description="创建 Stripe Checkout 会话用于订阅升级。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def create_checkout(
    request: Request,
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建 Stripe Checkout 会话并返回跳转链接。"""
    settings = get_settings()
    if not settings.payments_enabled:
        raise HTTPException(status_code=501, detail={"error": "PAYMENTS_DISABLED"})

    tier = _resolve_tier(data.price_id)
    if not tier:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PRICE_ID"})

    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=400, detail={"error": "NO_SUBSCRIPTION"})

    current_rank = TIER_RANK.get(str(subscription.tier), 0)
    requested_rank = TIER_RANK.get(tier, 0)
    if str(subscription.status) != "canceled" and current_rank >= requested_rank:
        raise HTTPException(status_code=400, detail={"error": "ALREADY_SUBSCRIBED"})

    checkout_url, session_id = await stripe_service.create_checkout_session(
        current_user, subscription, data.price_id
    )
    await db.commit()
    await cache_service.invalidate_subscription(current_user.id)

    return CheckoutResponse(checkout_url=checkout_url, session_id=session_id)


@router.get(
    "/portal",
    response_model=PortalResponse,
    summary="获取订阅管理入口",
    description="创建 Stripe Customer Portal 会话，返回管理订阅的跳转链接。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def get_portal(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 Stripe Customer Portal 链接。"""
    settings = get_settings()
    if not settings.payments_enabled:
        raise HTTPException(status_code=501, detail={"error": "PAYMENTS_DISABLED"})

    cached_subscription = await cache_service.get_subscription(current_user.id)
    if isinstance(cached_subscription, dict) and cached_subscription.get(
        "stripe_customer_id"
    ):
        portal_url = await stripe_service.create_portal_session(
            str(cached_subscription.get("stripe_customer_id"))
        )
        return PortalResponse(portal_url=portal_url)

    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(status_code=404, detail={"error": "NO_SUBSCRIPTION"})

    await cache_service.set_subscription(
        current_user.id, _subscription_payload(subscription)
    )
    portal_url = await stripe_service.create_portal_session(
        str(subscription.stripe_customer_id)
    )
    return PortalResponse(portal_url=portal_url)


@router.get(
    "/current",
    response_model=SubscriptionResponse,
    summary="获取当前订阅状态",
    description="返回当前用户订阅等级与状态。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def get_current_subscription(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前订阅状态。"""
    settings = get_settings()
    if not settings.payments_enabled:
        raise HTTPException(status_code=501, detail={"error": "PAYMENTS_DISABLED"})

    cached_subscription = await cache_service.get_subscription(current_user.id)
    if (
        isinstance(cached_subscription, dict)
        and cached_subscription.get("tier")
        and cached_subscription.get("status")
    ):
        return SubscriptionResponse(
            tier=str(cached_subscription.get("tier") or ""),
            status=str(cached_subscription.get("status") or ""),
            period_start=cached_subscription.get("period_start"),
            period_end=cached_subscription.get("period_end"),
            cancel_at_period_end=bool(
                cached_subscription.get("cancel_at_period_end", False)
            ),
        )

    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail={"error": "NO_SUBSCRIPTION"})

    await cache_service.set_subscription(
        current_user.id, _subscription_payload(subscription)
    )
    return SubscriptionResponse(
        tier=str(subscription.tier),
        status=str(subscription.status),
        period_start=subscription.current_period_start,  # type: ignore[arg-type]
        period_end=subscription.current_period_end,  # type: ignore[arg-type]
        cancel_at_period_end=bool(subscription.cancel_at_period_end),
    )


@router.get(
    "/usage",
    response_model=UsageResponse,
    summary="获取订阅使用量",
    description="返回当前周期已使用的会话数量与限额。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def get_usage(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前订阅使用量统计。"""
    settings = get_settings()
    if not settings.payments_enabled:
        raise HTTPException(status_code=501, detail={"error": "PAYMENTS_DISABLED"})

    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail={"error": "NO_SUBSCRIPTION"})

    usage = await _get_or_create_usage(db, subscription)
    tier = str(subscription.tier)
    sessions_limit = SESSION_LIMITS.get(tier)

    return UsageResponse(
        tier=tier,
        sessions_used=int(usage.session_count or 0),
        sessions_limit=sessions_limit,
        period_start=usage.period_start,  # type: ignore[arg-type]
        period_end=subscription.current_period_end,  # type: ignore[arg-type]
        is_lifetime=tier == "free",
    )
