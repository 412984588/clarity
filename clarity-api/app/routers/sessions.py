from app.utils.datetime_utils import utc_now
from datetime import datetime
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
from app.models.step_history import StepHistory
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
from app.services.analytics_service import AnalyticsService
from app.services.content_filter import sanitize_user_input, strip_pii
from app.services.state_machine import can_transition, get_next_step, is_final_step

router = APIRouter(prefix="/sessions", tags=["sessions"])

SESSION_LIMITS = {"free": 10, "standard": 100, "pro": 0}
STEP_SYSTEM_PROMPTS = {
    SolveStep.RECEIVE.value: (
        "You are Clarity, a supportive problem-solving coach. "
        "In the Receive step, listen carefully, acknowledge feelings, and summarize the issue. "
        "After responding, include a short line `NEXT_STEP: <step>` where <step> is one of "
        "receive, clarify, reframe, options, commit."
    ),
    SolveStep.CLARIFY.value: (
        "You are Clarity. In the Clarify step, ask concise questions to uncover context, constraints, and goals."
        " After responding, include a short line `NEXT_STEP: <step>` where <step> is one of "
        "receive, clarify, reframe, options, commit."
    ),
    SolveStep.REFRAME.value: (
        "You are Clarity. In the Reframe step, help reframe the problem into a solvable, actionable statement."
        " After responding, include a short line `NEXT_STEP: <step>` where <step> is one of "
        "receive, clarify, reframe, options, commit."
    ),
    SolveStep.OPTIONS.value: (
        "You are Clarity. In the Options step, propose a few concrete options with brief trade-offs."
        " After responding, include a short line `NEXT_STEP: <step>` where <step> is one of "
        "receive, clarify, reframe, options, commit."
    ),
    SolveStep.COMMIT.value: (
        "You are Clarity. In the Commit step, help the user choose a path and define the next small action."
        " After responding, include a short line `NEXT_STEP: <step>` where <step> is one of "
        "receive, clarify, reframe, options, commit."
    ),
}


def _period_start_for_tier(subscription: Subscription) -> datetime:
    if subscription.tier == "free":
        anchor = subscription.created_at or utc_now()
        return anchor.replace(hour=0, minute=0, second=0, microsecond=0)
    if subscription.current_period_start:
        return subscription.current_period_start  # type: ignore[return-value]
    return utc_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)


async def _get_or_create_usage(
    db: AsyncSession,
    subscription: Subscription,
) -> Usage:
    """获取或创建当月 Usage 记录，使用 PostgreSQL upsert 保证并发安全"""
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    period_start = _period_start_for_tier(subscription)

    # 使用 PostgreSQL 的 INSERT ON CONFLICT 实现并发安全的 upsert
    stmt = pg_insert(Usage).values(
        user_id=subscription.user_id,
        period_start=period_start,
        session_count=0,
    )
    stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "period_start"])
    await db.execute(stmt)
    await db.flush()

    # 查询并返回记录（无论是新建还是已存在）
    result = await db.execute(
        select(Usage).where(
            Usage.user_id == subscription.user_id, Usage.period_start == period_start
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
            Device.device_fingerprint == device_fingerprint,
        )
    )
    device = device_result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=403, detail={"error": "DEVICE_NOT_FOUND"})

    subscription_result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = subscription_result.scalar_one_or_none()
    if not subscription:
        subscription = Subscription(user_id=current_user.id, tier="free")
        db.add(subscription)
        await db.flush()

    tier: str = str(subscription.tier)
    sessions_limit: int = SESSION_LIMITS.get(tier, SESSION_LIMITS["free"])

    usage = await _get_or_create_usage(db, subscription)
    if sessions_limit > 0 and (usage.session_count or 0) >= sessions_limit:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "QUOTA_EXCEEDED",
                "usage": {
                    "used": int(usage.session_count or 0),
                    "limit": sessions_limit,
                    "tier": tier,
                },
                "upgrade_url": "/subscriptions/checkout",
            },
        )
    usage.session_count = (usage.session_count or 0) + 1  # type: ignore[assignment]

    session = SolveSession(
        user_id=current_user.id,
        device_id=device.id,
        status=SessionStatus.ACTIVE.value,
        current_step=SolveStep.RECEIVE.value,
    )
    db.add(session)
    await db.flush()

    # 创建初始 StepHistory
    step_history = StepHistory(
        session_id=session.id,
        step=SolveStep.RECEIVE.value,
        started_at=utc_now(),
    )
    db.add(step_history)

    # 记录 session_started 事件
    analytics_service = AnalyticsService(db)
    await analytics_service.emit(
        "session_started",
        session.id,
        {"user_id": str(current_user.id), "device_id": str(device.id)},
    )

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
        select(func.count(SolveSession.id)).where(
            SolveSession.user_id == current_user.id
        )
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
            SolveSession.id == session_id, SolveSession.user_id == current_user.id
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
            SolveSession.id == session_id, SolveSession.user_id == current_user.id
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
    analytics_service = AnalyticsService(db)

    try:
        current_step_enum = SolveStep(current_step)
    except ValueError:
        current_step_enum = SolveStep.RECEIVE
        session.current_step = current_step_enum.value

    async def event_generator() -> AsyncGenerator[str, None]:
        # 获取或创建当前步骤的 StepHistory
        step_history_result = await db.execute(
            select(StepHistory)
            .where(
                StepHistory.session_id == session.id,
                StepHistory.step == current_step_enum.value,
                StepHistory.completed_at.is_(None),
            )
            .order_by(StepHistory.started_at.desc())
            .limit(1)
        )
        step_history = step_history_result.scalar_one_or_none()
        if not step_history:
            step_history = StepHistory(
                session_id=session.id,
                step=current_step_enum.value,
                started_at=utc_now(),
            )
            db.add(step_history)
            await db.flush()

        # 增加消息计数
        step_history.message_count = (step_history.message_count or 0) + 1

        # 流式输出 AI 响应
        async for token in ai_service.stream(system_prompt, sanitized_input):
            payload = json.dumps({"content": token})
            yield f"event: token\ndata: {payload}\n\n"

        # 获取下一步
        next_step_enum = get_next_step(current_step_enum)
        next_step = (
            next_step_enum.value if next_step_enum else current_step_enum.value
        )
        now = utc_now()

        # 处理状态转换
        if next_step_enum and can_transition(current_step_enum, next_step_enum):
            step_history.completed_at = now
            db.add(
                StepHistory(
                    session_id=session.id,
                    step=next_step_enum.value,
                    started_at=now,
                )
            )
            session.current_step = next_step_enum.value
            await analytics_service.emit(
                "step_completed",
                session.id,
                {"from_step": current_step_enum.value, "to_step": next_step_enum.value},
            )
        elif is_final_step(current_step_enum):
            # 最终步骤完成
            if step_history.completed_at is None:
                step_history.completed_at = now
                await analytics_service.emit(
                    "step_completed",
                    session.id,
                    {"step": current_step_enum.value},
                )
            session.status = SessionStatus.COMPLETED.value
            session.completed_at = now
            await analytics_service.emit(
                "session_completed",
                session.id,
                {"final_step": current_step_enum.value},
            )

        await db.commit()
        done_payload = json.dumps(
            {"next_step": next_step, "emotion_detected": "neutral"}
        )
        yield f"event: done\ndata: {done_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
