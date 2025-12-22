from app.utils.datetime_utils import utc_now
import json
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
from app.services.ai_service import AIService
from app.services.content_filter import sanitize_user_input, strip_pii

router = APIRouter(prefix="/sessions", tags=["sessions"])

SESSION_LIMITS = {"free": 10, "standard": 100, "pro": 1000}
STEP_SYSTEM_PROMPTS = {
    SolveStep.RECEIVE.value: (
        "You are Clarity, a supportive problem-solving coach. "
        "In the Receive step, listen carefully, acknowledge feelings, and summarize the issue."
    ),
    SolveStep.CLARIFY.value: (
        "You are Clarity. In the Clarify step, ask concise questions to uncover context, constraints, and goals."
    ),
    SolveStep.REFRAME.value: (
        "You are Clarity. In the Reframe step, help reframe the problem into a solvable, actionable statement."
    ),
    SolveStep.OPTIONS.value: (
        "You are Clarity. In the Options step, propose a few concrete options with brief trade-offs."
    ),
    SolveStep.COMMIT.value: (
        "You are Clarity. In the Commit step, help the user choose a path and define the next small action."
    ),
}


async def _get_or_create_usage(
    db: AsyncSession,
    user_id: UUID,
) -> Usage:
    """获取或创建当月 Usage 记录，使用 PostgreSQL upsert 保证并发安全"""
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    period_start = utc_now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    # 使用 PostgreSQL 的 INSERT ON CONFLICT 实现并发安全的 upsert
    stmt = pg_insert(Usage).values(
        user_id=user_id,
        period_start=period_start,
        session_count=0,
    )
    stmt = stmt.on_conflict_do_nothing(
        index_elements=["user_id", "period_start"]
    )
    await db.execute(stmt)
    await db.flush()

    # 查询并返回记录（无论是新建还是已存在）
    result = await db.execute(
        select(Usage).where(
            Usage.user_id == user_id, Usage.period_start == period_start
        )
    )
    return result.scalar_one()


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
    """SSE 流式返回 LLM 回复"""
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

    current_step = str(session.current_step)
    system_prompt = STEP_SYSTEM_PROMPTS.get(
        current_step,
        STEP_SYSTEM_PROMPTS[SolveStep.RECEIVE.value],
    )
    sanitized_input = strip_pii(sanitize_user_input(data.content))
    ai_service = AIService()

    async def event_generator() -> AsyncGenerator[str, None]:
        async for token in ai_service.stream(system_prompt, sanitized_input):
            payload = json.dumps({"content": token})
            yield f"event: token\ndata: {payload}\n\n"
        next_step = _next_step(current_step)
        done_payload = json.dumps({
            "next_step": next_step,
            "emotion_detected": "neutral"
        })
        yield f"event: done\ndata: {done_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


def _next_step(current_step: str) -> str:
    step_order = [
        SolveStep.RECEIVE.value,
        SolveStep.CLARIFY.value,
        SolveStep.REFRAME.value,
        SolveStep.OPTIONS.value,
        SolveStep.COMMIT.value,
    ]
    try:
        idx = step_order.index(current_step)
    except ValueError:
        return SolveStep.RECEIVE.value
    if idx + 1 >= len(step_order):
        return step_order[-1]
    return step_order[idx + 1]
