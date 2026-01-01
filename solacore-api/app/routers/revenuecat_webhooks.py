import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from app.config import get_settings
from app.database import get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.models.webhook_event import ProcessedWebhookEvent
from app.services.cache_service import CacheService
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
cache_service = CacheService()


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
            return (
                datetime.fromisoformat(normalized)
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
            )
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


def _compute_payload_hash(payload: dict) -> str:
    """计算 payload 的 SHA256 哈希（用于调试/审计）"""
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


async def _check_and_record_event(
    db: AsyncSession, event_id: str, event_type: str, payload_hash: str
) -> bool:
    """
    检查事件是否已处理，如未处理则记录。
    返回 True 表示事件是新的（需要处理），False 表示已处理（跳过）。
    使用 INSERT ... ON CONFLICT DO NOTHING 确保幂等性。
    """
    if not event_id:
        return True  # 无 event_id 的事件总是处理

    stmt = (
        pg_insert(ProcessedWebhookEvent)
        .values(
            event_id=event_id,
            event_type=event_type,
            source="revenuecat",
            payload_hash=payload_hash,
            processed_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        .on_conflict_do_nothing(index_elements=["event_id"])
    )

    result = await db.execute(stmt)
    # rowcount > 0 表示插入成功（新事件），0 表示冲突（已处理）
    return result.rowcount > 0  # type: ignore[attr-defined]


def _compute_subscription_updates(
    event_type: str,
    entitlement_ids: list[str],
    period_end: Optional[datetime],
    existing_sub: Optional[Subscription],
) -> dict:
    """根据事件类型计算订阅状态更新"""
    # 默认值：保持现有状态或使用 free tier 默认值
    updates = {
        "tier": existing_sub.tier if existing_sub else "free",
        "status": existing_sub.status if existing_sub else "active",
        "cancel_at_period_end": existing_sub.cancel_at_period_end
        if existing_sub
        else False,
        "current_period_end": period_end
        or (existing_sub.current_period_end if existing_sub else None),
    }

    # 事件类型处理逻辑
    if event_type == "INITIAL_PURCHASE":
        updates.update(
            {
                "tier": _entitlement_to_tier(entitlement_ids),
                "status": "active",
                "cancel_at_period_end": False,
            }
        )
    elif event_type in ("RENEWAL", "BILLING_ISSUE"):
        updates["status"] = "active" if event_type == "RENEWAL" else "past_due"
    elif event_type == "CANCELLATION":
        updates["cancel_at_period_end"] = True
    elif event_type == "EXPIRATION":
        updates.update(
            {"tier": "free", "status": "expired", "cancel_at_period_end": False}
        )
    elif event_type == "PRODUCT_CHANGE":
        updates["tier"] = _entitlement_to_tier(entitlement_ids)

    return updates


async def _upsert_subscription(
    db: AsyncSession,
    user_id: UUID,
    tier: str,
    status: str,
    cancel_at_period_end: bool,
    current_period_end: Optional[datetime],
) -> None:
    """
    使用 UPSERT 更新订阅状态，避免并发写脏数据。
    """
    values = {
        "user_id": user_id,
        "tier": tier,
        "status": status,
        "cancel_at_period_end": cancel_at_period_end,
    }
    if current_period_end:
        values["current_period_end"] = current_period_end

    stmt = pg_insert(Subscription).values(**values)
    update_dict = {
        "tier": stmt.excluded.tier,
        "status": stmt.excluded.status,
        "cancel_at_period_end": stmt.excluded.cancel_at_period_end,
    }
    if current_period_end:
        update_dict["current_period_end"] = stmt.excluded.current_period_end

    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id"],
        set_=update_dict,
    )
    await db.execute(stmt)


def _verify_webhook_auth(authorization: Optional[str], secret: str) -> None:
    """验证 Webhook 认证令牌"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"error": "MISSING_AUTH"})
    token = authorization.replace("Bearer ", "", 1).strip()
    if token != secret:
        raise HTTPException(status_code=401, detail={"error": "INVALID_AUTH"})


def _get_user_id_from_event(event: dict) -> UUID | None:
    """从事件中提取并验证用户 UUID"""
    app_user_id = event.get("app_user_id")
    if not app_user_id:
        return None
    try:
        return UUID(str(app_user_id))
    except (TypeError, ValueError):
        return None


@router.post("/revenuecat")
async def revenuecat_webhook(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    if not settings.payments_enabled:
        raise HTTPException(status_code=501, detail={"error": "PAYMENTS_DISABLED"})

    _verify_webhook_auth(authorization, settings.revenuecat_webhook_secret)

    payload = await request.json()
    event = payload.get("event", payload)
    event_type = str(event.get("type") or event.get("event_type") or "").upper()
    event_id = str(event.get("id") or event.get("event_id") or "")
    payload_hash = _compute_payload_hash(payload)

    # 幂等性检查
    if not await _check_and_record_event(db, event_id, event_type, payload_hash):
        logger.info(f"RevenueCat webhook 重复事件已跳过: event_id={event_id}")
        return {"received": True}

    user_uuid = _get_user_id_from_event(event)
    if not user_uuid:
        logger.warning(
            f"RevenueCat webhook 缺少有效 app_user_id: event_type={event_type}"
        )
        await db.commit()
        return {"received": True}

    # 获取用户和当前订阅
    user_result = await db.execute(select(User).where(User.id == user_uuid))
    user = user_result.scalar_one_or_none()
    if not user:
        logger.warning(
            f"RevenueCat webhook 用户不存在: user_id={user_uuid}, event_type={event_type}"
        )
        await db.commit()
        return {"received": True}

    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    existing_sub = sub_result.scalar_one_or_none()

    # 解析事件数据并计算更新
    entitlement_ids = _extract_entitlement_ids(event)
    period_end = _parse_timestamp(
        event.get("expiration_at_ms")
        or event.get("expiration_at")
        or event.get("expires_at_ms")
        or event.get("expires_at")
    )

    updates = _compute_subscription_updates(
        event_type, entitlement_ids, period_end, existing_sub
    )

    # 执行更新
    await _upsert_subscription(db, user_id=user.id, **updates)
    await cache_service.invalidate_subscription(user.id)
    await db.commit()

    logger.info(
        f"RevenueCat webhook 处理成功: event_id={event_id}, event_type={event_type}, user_id={user.id}"
    )
    return {"received": True}
