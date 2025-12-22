import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.device import Device
from app.models.solve_session import SolveSession, SessionStatus, SolveStep
from app.models.subscription import Subscription, Usage
from app.models.user import User
from app.schemas.session import (
    MessageRequest,
    SessionCreateResponse,
    SessionListResponse,
    SessionResponse,
    UsageResponse,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])

MOCK_RESPONSE = "I understand how you feel. Let me help you work through this."
SESSION_LIMITS = {"free": 10, "standard": 100, "pro": 1000}


async def _get_or_create_usage(
    db: AsyncSession,
    user_id: UUID,
) -> Usage:
    period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(Usage)
        .where(Usage.user_id == user_id)
        .order_by(Usage.created_at.desc())
    )
    usage = result.scalars().first()
    if not usage or usage.period_start < period_start:
        usage = Usage(user_id=user_id, period_start=period_start, session_count=0)
        db.add(usage)
        await db.flush()
    return usage


@router.post("", response_model=SessionCreateResponse, status_code=201)
async def create_session(
    current_user: User = Depends(get_current_user),
    device_fingerprint: str = Header(..., alias="X-Device-Fingerprint"),
    db: AsyncSession = Depends(get_db),
):
    """创建 Solve 会话"""
    device_result = await db.execute(
        select(Device).where(
            Device.user_id == current_user.id,
            Device.device_fingerprint == device_fingerprint
        )
    )
    device = device_result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=403, detail={"error": "DEVICE_NOT_FOUND"})

    subscription_result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = subscription_result.scalar_one_or_none()
    tier: str = str(subscription.tier) if subscription else "free"
    sessions_limit: int = SESSION_LIMITS.get(tier, SESSION_LIMITS["free"])

    usage = await _get_or_create_usage(db, current_user.id)  # type: ignore[arg-type]
    if (usage.session_count or 0) >= sessions_limit:
        raise HTTPException(status_code=403, detail={"error": "QUOTA_EXCEEDED"})
    usage.session_count = (usage.session_count or 0) + 1  # type: ignore[assignment]

    session = SolveSession(
        user_id=current_user.id,
        device_id=device.id,
        status=SessionStatus.ACTIVE.value,
        current_step=SolveStep.RECEIVE.value,
    )
    db.add(session)
    await db.flush()
    await db.commit()

    return SessionCreateResponse(
        session_id=session.id,  # type: ignore[arg-type]
        status=str(session.status),
        current_step=str(session.current_step),
        created_at=session.created_at,  # type: ignore[arg-type]
        usage=UsageResponse(
            sessions_used=int(usage.session_count or 0),
            sessions_limit=sessions_limit,
            tier=tier,
        ),
    )


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """列出当前用户的 Solve 会话"""
    total_result = await db.execute(
        select(func.count(SolveSession.id)).where(SolveSession.user_id == current_user.id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(SolveSession)
        .where(SolveSession.user_id == current_user.id)
        .order_by(SolveSession.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    sessions = result.scalars().all()

    return SessionListResponse(
        sessions=[SessionResponse.model_validate(session) for session in sessions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单个 Solve 会话"""
    result = await db.execute(
        select(SolveSession).where(
            SolveSession.id == session_id,
            SolveSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})
    return SessionResponse.model_validate(session)


@router.post("/{session_id}/messages")
async def stream_messages(
    session_id: UUID,
    data: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """SSE 流式返回 mock 回复"""
    result = await db.execute(
        select(SolveSession).where(
            SolveSession.id == session_id,
            SolveSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})
    if session.status == SessionStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail={"error": "SESSION_COMPLETED"})

    async def event_generator() -> AsyncGenerator[str, None]:
        for word in MOCK_RESPONSE.split():
            payload = json.dumps({"content": word})
            yield f"event: token\ndata: {payload}\n\n"
            await asyncio.sleep(0.05)
        done_payload = json.dumps({
            "next_step": SolveStep.CLARIFY.value,
            "emotion_detected": "neutral"
        })
        yield f"event: done\ndata: {done_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
