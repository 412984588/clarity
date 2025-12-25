from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.analytics_event import AnalyticsEvent
from app.models.device import Device
from app.models.session import ActiveSession
from app.models.solve_session import SolveSession
from app.models.step_history import StepHistory
from app.models.user import User
from app.utils.datetime_utils import utc_now

router = APIRouter(prefix="/account", tags=["account"])


def _dt(value: object | None) -> Optional[str]:
    if isinstance(value, datetime):
        return value.isoformat()
    return None


@router.get("/export")
async def export_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.subscription))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail={"error": "USER_NOT_FOUND"})

    devices = (
        (await db.execute(select(Device).where(Device.user_id == user.id)))
        .scalars()
        .all()
    )
    active_sessions = (
        (
            await db.execute(
                select(ActiveSession).where(ActiveSession.user_id == user.id)
            )
        )
        .scalars()
        .all()
    )
    solve_sessions = (
        (await db.execute(select(SolveSession).where(SolveSession.user_id == user.id)))
        .scalars()
        .all()
    )
    step_history = (
        (
            await db.execute(
                select(StepHistory)
                .join(SolveSession, StepHistory.session_id == SolveSession.id)
                .where(SolveSession.user_id == user.id)
            )
        )
        .scalars()
        .all()
    )
    analytics_events = (
        (
            await db.execute(
                select(AnalyticsEvent)
                .join(SolveSession, AnalyticsEvent.session_id == SolveSession.id)
                .where(SolveSession.user_id == user.id)
            )
        )
        .scalars()
        .all()
    )
    subscription = user.subscription

    return {
        "exported_at": utc_now().isoformat(),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "auth_provider": user.auth_provider,
            "auth_provider_id": user.auth_provider_id,
            "locale": user.locale,
            "is_active": user.is_active,
            "created_at": _dt(user.created_at),
            "updated_at": _dt(user.updated_at),
        },
        "subscription": (
            {
                "id": str(subscription.id),
                "tier": str(subscription.tier),
                "status": str(subscription.status),
                "current_period_start": _dt(subscription.current_period_start),
                "current_period_end": _dt(subscription.current_period_end),
                "cancel_at_period_end": bool(subscription.cancel_at_period_end),
                "created_at": _dt(subscription.created_at),
                "updated_at": _dt(subscription.updated_at),
            }
            if subscription
            else None
        ),
        "devices": [
            {
                "id": str(device.id),
                "device_name": device.device_name,
                "platform": device.platform,
                "is_active": device.is_active,
                "created_at": _dt(device.created_at),
                "last_active_at": _dt(device.last_active_at),
                "last_removal_at": _dt(device.last_removal_at),
            }
            for device in devices
        ],
        "active_sessions": [
            {
                "id": str(session.id),
                "device_id": str(session.device_id),
                "created_at": _dt(session.created_at),
                "expires_at": _dt(session.expires_at),
            }
            for session in active_sessions
        ],
        "solve_sessions": [
            {
                "id": str(session.id),
                "status": str(session.status),
                "current_step": str(session.current_step),
                "locale": session.locale,
                "first_step_action": session.first_step_action,
                "reminder_time": _dt(session.reminder_time),
                "created_at": _dt(session.created_at),
                "completed_at": _dt(session.completed_at),
            }
            for session in solve_sessions
        ],
        "step_history": [
            {
                "id": str(step.id),
                "session_id": str(step.session_id),
                "step": step.step,
                "started_at": _dt(step.started_at),
                "completed_at": _dt(step.completed_at),
                "message_count": int(step.message_count or 0),
            }
            for step in step_history
        ],
        "analytics_events": [
            {
                "id": str(event.id),
                "session_id": str(event.session_id) if event.session_id else None,
                "event_type": event.event_type,
                "payload": event.payload,
                "created_at": _dt(event.created_at),
            }
            for event in analytics_events
        ],
    }


@router.delete("", status_code=204)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        delete(User).where(User.id == current_user.id).returning(User.id)
    )
    deleted_id = result.scalar_one_or_none()
    if not deleted_id:
        raise HTTPException(status_code=404, detail={"error": "USER_NOT_FOUND"})
    await db.commit()
    return None
