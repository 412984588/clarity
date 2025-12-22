import logging
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.subscription import Subscription
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# LRU-style 幂等性缓存，防止内存无限增长
# 生产环境建议迁移到 Redis (TTL=24h)
_MAX_PROCESSED_EVENTS = 10000
processed_event_ids: OrderedDict[str, bool] = OrderedDict()


def _entitlement_to_tier(entitlement_ids: list[str]) -> str:
    settings = get_settings()
    if settings.revenuecat_entitlement_pro in entitlement_ids:
        return "pro"
    if settings.revenuecat_entitlement_standard in entitlement_ids:
        return "standard"
    return "free"


def _parse_timestamp(value: Optional[object]) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 1_000_000_000_000 else value
        return datetime.fromtimestamp(seconds, tz=timezone.utc).replace(tzinfo=None)
    if isinstance(value, str):
        try:
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized).astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError:
            return None
    return None


def _extract_entitlement_ids(event: dict) -> list[str]:
    entitlement_ids = event.get("entitlement_ids")
    if isinstance(entitlement_ids, list):
        return [str(item) for item in entitlement_ids]
    entitlements = event.get("entitlements") or {}
    if isinstance(entitlements, dict):
        return [str(key) for key in entitlements.keys()]
    return []


@router.post("/revenuecat")
async def revenuecat_webhook(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"error": "MISSING_AUTH"})
    token = authorization.replace("Bearer ", "", 1).strip()
    if token != settings.revenuecat_webhook_secret:
        raise HTTPException(status_code=401, detail={"error": "INVALID_AUTH"})

    payload = await request.json()
    event = payload.get("event", payload)
    event_type = str(event.get("type") or event.get("event_type") or "").upper()
    event_id = str(event.get("id") or event.get("event_id") or "")

    if event_id and event_id in processed_event_ids:
        return {"received": True}
    if event_id:
        processed_event_ids[event_id] = True
        # LRU 淘汰：超过最大容量时删除最早的条目
        while len(processed_event_ids) > _MAX_PROCESSED_EVENTS:
            processed_event_ids.popitem(last=False)

    app_user_id = event.get("app_user_id")
    if not app_user_id:
        logger.warning(f"RevenueCat webhook 缺少 app_user_id: event_type={event_type}")
        return {"received": True}

    try:
        user_uuid = UUID(str(app_user_id))
    except (TypeError, ValueError):
        logger.error(f"RevenueCat webhook app_user_id 无法解析为 UUID: {app_user_id}, event_type={event_type}")
        return {"received": True}

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning(f"RevenueCat webhook 用户不存在: user_id={app_user_id}, event_type={event_type}")
        return {"received": True}

    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    subscription = result.scalar_one_or_none()
    if not subscription:
        subscription = Subscription(user_id=user.id, tier="free")
        db.add(subscription)
        await db.flush()

    entitlement_ids = _extract_entitlement_ids(event)
    period_end = _parse_timestamp(
        event.get("expiration_at_ms")
        or event.get("expiration_at")
        or event.get("expires_at_ms")
        or event.get("expires_at")
    )

    if event_type == "INITIAL_PURCHASE":
        # 新购：更新 tier 并激活订阅
        subscription.tier = _entitlement_to_tier(entitlement_ids)  # type: ignore[assignment]
        subscription.status = "active"  # type: ignore[assignment]
        subscription.cancel_at_period_end = False  # type: ignore[assignment]
        if period_end:
            subscription.current_period_end = period_end  # type: ignore[assignment]
    elif event_type == "RENEWAL":
        # 续费：刷新到期时间
        if period_end:
            subscription.current_period_end = period_end  # type: ignore[assignment]
        subscription.status = "active"  # type: ignore[assignment]
    elif event_type == "CANCELLATION":
        # 取消：到期后不续费
        subscription.cancel_at_period_end = True  # type: ignore[assignment]
    elif event_type == "EXPIRATION":
        # 过期：降级为 free
        subscription.tier = "free"  # type: ignore[assignment]
        subscription.status = "expired"  # type: ignore[assignment]
        subscription.cancel_at_period_end = False  # type: ignore[assignment]
        if period_end:
            subscription.current_period_end = period_end  # type: ignore[assignment]
    elif event_type == "BILLING_ISSUE":
        # 账单问题：标记为 past_due
        subscription.status = "past_due"  # type: ignore[assignment]
    elif event_type == "PRODUCT_CHANGE":
        # 产品切换：更新 tier
        subscription.tier = _entitlement_to_tier(entitlement_ids)  # type: ignore[assignment]

    await db.commit()
    return {"received": True}
