from app.utils.datetime_utils import utc_now
from datetime import datetime
import json
import logging
from typing import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    SSE_RATE_LIMIT,
    limiter,
    user_rate_limit_key,
)
from app.models.device import Device
from app.models.solve_session import SolveSession, SessionStatus, SolveStep
from app.models.step_history import StepHistory
from app.models.message import Message, MessageRole
from app.models.subscription import Subscription, Usage
from app.models.user import User
from app.schemas.session import (
    MessageRequest,
    MessageResponse,
    SessionCreateResponse,
    SessionListItem,
    SessionListResponse,
    SessionResponse,
    SessionUpdateRequest,
    SessionUpdateResponse,
    UsageResponse,
)
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.services.content_filter import sanitize_user_input, strip_pii
from app.services.crisis_detector import detect_crisis, get_crisis_response
from app.services.emotion_detector import detect_emotion
from app.services.state_machine import (
    can_transition,
    get_next_step,
    is_final_step,
    validate_transition,
)
from app.utils.docs import COMMON_ERROR_RESPONSES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["Sessions"])

SESSION_LIMITS = {"free": 10, "standard": 100, "pro": 0}
STEP_SYSTEM_PROMPTS = {
    SolveStep.RECEIVE.value: """你是 Solacore，一位温暖、专业的情绪梳理助手。

当前阶段：接收 (Receive)
你的任务：
- 认真倾听用户的倾诉，不打断、不评判
- 用温暖的语言回应，让用户感到被理解
- 简要复述用户表达的核心情绪和困扰
- 引导用户继续表达，或准备进入下一步澄清

语言要求：必须用中文回复，语气温暖自然，像朋友聊天。
回复长度：2-4 句话，简洁有温度。""",
    SolveStep.CLARIFY.value: """你是 Solacore，一位温暖、专业的情绪梳理助手。

当前阶段：澄清 (Clarify)
你的任务：
- 通过提问帮助用户看清问题的本质
- 了解问题的背景、约束条件、真实诉求
- 问题要具体、有针对性，一次只问 1-2 个问题
- 帮助用户从混乱的情绪中理出头绪

语言要求：必须用中文回复，语气温暖自然，像朋友聊天。
回复长度：2-4 句话，包含 1-2 个引导性问题。""",
    SolveStep.REFRAME.value: """你是 Solacore，一位温暖、专业的情绪梳理助手。

当前阶段：重构 (Reframe)
你的任务：
- 帮助用户换个角度看问题
- 把模糊的焦虑转化为具体可解决的问题陈述
- 用"如何..."的句式重新定义问题
- 让用户看到问题背后的可能性

语言要求：必须用中文回复，语气温暖自然，像朋友聊天。
回复长度：2-4 句话，包含重构后的问题陈述。""",
    SolveStep.OPTIONS.value: """你是 Solacore，一位温暖、专业的情绪梳理助手。

当前阶段：选项 (Options)
你的任务：
- 提供 2-3 个具体可行的行动选项
- 简要说明每个选项的优缺点
- 让用户感受到"有路可走"
- 不替用户做决定，只提供选择

语言要求：必须用中文回复，语气温暖自然，像朋友聊天。
回复长度：列出 2-3 个选项，每个选项 1-2 句话描述。""",
    SolveStep.COMMIT.value: """你是 Solacore，一位温暖、专业的情绪梳理助手。

当前阶段：承诺 (Commit)
你的任务：
- 帮助用户选定一个方向
- 一起确定"今天/明天可以做的第一小步"
- 这一步要足够小、足够具体，5分钟内能完成
- 给用户信心和鼓励

语言要求：必须用中文回复，语气温暖自然，像朋友聊天。
回复长度：2-4 句话，明确第一步行动。""",
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


@router.post(
    "",
    response_model=SessionCreateResponse,
    status_code=201,
    summary="创建 Solve 会话",
    description="""
    创建一个新的 5 步 Solve 会话。

    **需要认证**: 是（Bearer Token / Cookie）

    **Headers 必须**:
    - `X-Device-Fingerprint`: 设备指纹

    **返回**: 新建会话的 ID 和初始状态
    """,
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def create_session(
    request: Request,
    current_user: User = Depends(get_current_user),
    device_fingerprint: str = Header(
        ...,
        alias="X-Device-Fingerprint",
        description="设备指纹，用于识别当前设备",
        example="ios-4f3e9b2c",
    ),
    db: AsyncSession = Depends(get_db),
):
    """创建新的 Solve 会话并返回会话基础信息与使用量。"""
    device_result = await db.execute(
        select(Device).where(
            Device.user_id == current_user.id,
            Device.device_fingerprint == device_fingerprint,
        )
    )
    # 使用 .first() 容错重复记录（数据库可能存在历史重复数据）
    device = device_result.scalars().first()
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

    # Beta 模式移除 session 限制
    settings = get_settings()
    if settings.beta_mode:
        sessions_limit = 0  # 0 表示无限制

    usage = await _get_or_create_usage(db, subscription)

    # 原子递增 session_count，避免并发丢失更新
    from sqlalchemy import update

    period_start = _period_start_for_tier(subscription)
    stmt = (
        update(Usage)
        .where(Usage.user_id == current_user.id, Usage.period_start == period_start)
        .values(session_count=Usage.session_count + 1)
        .returning(Usage.session_count)
    )
    result = await db.execute(stmt)
    new_count = result.scalar_one()

    # 检查是否超限（递增后再检查，避免竞态条件）
    if sessions_limit > 0 and new_count > sessions_limit:
        # 超限则回滚递增
        rollback_stmt = (
            update(Usage)
            .where(Usage.user_id == current_user.id, Usage.period_start == period_start)
            .values(session_count=Usage.session_count - 1)
        )
        await db.execute(rollback_stmt)
        raise HTTPException(
            status_code=403,
            detail={
                "error": "QUOTA_EXCEEDED",
                "usage": {
                    "used": new_count - 1,
                    "limit": sessions_limit,
                    "tier": tier,
                },
                "upgrade_url": "/subscriptions/checkout",
            },
        )

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
        session.id,  # type: ignore[arg-type]
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


@router.get(
    "",
    response_model=SessionListResponse,
    summary="获取会话列表",
    description="获取当前用户的所有会话列表，支持分页。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def list_sessions(
    request: Request,
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="分页大小（1-100）",
        example=20,
    ),
    offset: int = Query(
        0,
        ge=0,
        description="分页偏移量",
        example=0,
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分页返回当前用户的 Solve 会话列表。"""
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
        sessions=[SessionListItem.model_validate(session) for session in sessions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    response_model_exclude_none=True,
    summary="获取单个会话详情",
    description=(
        "获取指定会话的详细信息。默认不返回消息历史，"
        "需要时可通过 include_messages=true 返回分页消息。"
    ),
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def get_session(
    request: Request,
    session_id: UUID = Path(
        ...,
        description="会话 ID",
        example="2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
    ),
    include_messages: bool = Query(
        False,
        description="是否返回会话消息（默认不返回）",
        example=False,
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="消息分页大小，仅 include_messages=true 生效",
        example=20,
    ),
    offset: int = Query(
        0,
        ge=0,
        description="消息分页偏移，仅 include_messages=true 生效",
        example=0,
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单个 Solve 会话详情，可选返回消息列表。"""
    result = await db.execute(
        select(SolveSession)
        .options(noload(SolveSession.messages))
        .where(SolveSession.id == session_id, SolveSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})
    messages = None
    if include_messages:
        messages_result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
            .limit(limit)
            .offset(offset)
        )
        message_rows = messages_result.scalars().all()
        messages = [MessageResponse.model_validate(message) for message in message_rows]

    return SessionResponse(
        id=session.id,
        status=str(session.status),
        current_step=str(session.current_step),
        created_at=session.created_at,
        completed_at=session.completed_at,
        messages=messages,
    )


@router.patch(
    "/{session_id}",
    response_model=SessionUpdateResponse,
    summary="更新会话状态",
    description="更新 Solve 会话的状态、步骤或本地化配置。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def update_session(
    request: Request,
    updates: SessionUpdateRequest,
    session_id: UUID = Path(
        ...,
        description="会话 ID",
        example="2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新 Solve 会话状态、步骤或提醒信息。"""
    result = await db.execute(
        select(SolveSession).where(
            SolveSession.id == session_id, SolveSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    if updates.status is not None:
        try:
            status_enum = SessionStatus(updates.status)
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail={"error": "INVALID_STATUS"}
            ) from exc
        session.status = status_enum.value  # type: ignore[assignment]
        if status_enum == SessionStatus.COMPLETED:
            session.completed_at = utc_now()  # type: ignore[assignment]

    if updates.current_step is not None:
        try:
            next_step_enum = SolveStep(updates.current_step)
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail={"error": "INVALID_STEP"}
            ) from exc
        try:
            current_step_enum = SolveStep(str(session.current_step))
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail={"error": "INVALID_CURRENT_STEP"}
            ) from exc
        if not validate_transition(current_step_enum, next_step_enum):
            raise HTTPException(
                status_code=400, detail={"error": "INVALID_STEP_TRANSITION"}
            )
        session.current_step = next_step_enum.value  # type: ignore[assignment]

    if updates.locale is not None:
        session.locale = updates.locale  # type: ignore[assignment]
    if updates.first_step_action is not None:
        session.first_step_action = updates.first_step_action  # type: ignore[assignment]
    if updates.reminder_time is not None:
        session.reminder_time = updates.reminder_time  # type: ignore[assignment]

    await db.commit()

    return SessionUpdateResponse(
        id=str(session.id),
        status=str(session.status),
        current_step=str(session.current_step),
        updated_at=utc_now(),
    )


@router.post(
    "/{session_id}/messages",
    summary="发送消息并获取 AI 回复",
    description="""
    向指定会话发送消息，获取 SSE 流式 AI 回复。

    **响应格式**: Server-Sent Events (SSE)

    **事件类型**:
    - `token`: AI 生成的文本片段
    - `done`: 生成完成，包含元数据
    - `error`: 发生错误
    """,
    responses={
        **COMMON_ERROR_RESPONSES,
        200: {
            "description": "SSE Stream",
            "content": {
                "text/event-stream": {
                    "example": (
                        "event: token\n"
                        "data: {\"content\": \"我能理解你的感受，\"}\n\n"
                        "event: done\n"
                        "data: {\"next_step\": \"clarify\", \"emotion_detected\": \"sadness\"}\n\n"
                    )
                }
            },
        },
    },
)
@limiter.limit(
    SSE_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def stream_messages(
    request: Request,
    data: MessageRequest,
    session_id: UUID = Path(
        ...,
        description="会话 ID",
        example="2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """向会话发送消息并以 SSE 方式流式返回 AI 回复。"""
    result = await db.execute(
        select(SolveSession, StepHistory)
        .outerjoin(
            StepHistory,
            and_(
                StepHistory.session_id == SolveSession.id,
                StepHistory.step == SolveSession.current_step,
                StepHistory.completed_at.is_(None),
            ),
        )
        .where(SolveSession.id == session_id, SolveSession.user_id == current_user.id)
        .order_by(StepHistory.started_at.desc())
        .limit(1)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})
    session, step_history = row
    if session.status == SessionStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail={"error": "SESSION_COMPLETED"})

    # 危机检测 - 在处理消息之前检查
    crisis_result = detect_crisis(data.content)
    if crisis_result.blocked:
        analytics_service = AnalyticsService(db)
        await analytics_service.emit(
            "crisis_detected",
            session.id,  # type: ignore[arg-type]
            {"keyword": crisis_result.matched_keyword},
            flush=False,
        )
        await db.commit()
        # 返回危机资源响应，不继续 Solve 流程
        return get_crisis_response()

    current_step = str(session.current_step)
    system_prompt = STEP_SYSTEM_PROMPTS.get(
        current_step,
        STEP_SYSTEM_PROMPTS[SolveStep.RECEIVE.value],
    )
    sanitized_input = strip_pii(sanitize_user_input(data.content))
    ai_service = AIService()
    analytics_service = AnalyticsService(db)

    # 情绪检测
    emotion_result = detect_emotion(data.content)

    try:
        current_step_enum = SolveStep(current_step)
    except ValueError:
        current_step_enum = SolveStep.RECEIVE
        session.current_step = current_step_enum.value  # type: ignore[assignment]

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # 获取或创建当前步骤的 StepHistory
            active_step_history = step_history
            if (
                active_step_history
                and active_step_history.step != current_step_enum.value
            ):
                active_step_history = None
            if not active_step_history:
                active_step_history = StepHistory(
                    session_id=session.id,
                    step=current_step_enum.value,
                    started_at=utc_now(),
                )
                db.add(active_step_history)

            # 增加消息计数
            active_step_history.message_count = (  # type: ignore[assignment]
                (active_step_history.message_count or 0) + 1
            )

            # 保存用户消息到数据库
            user_message = Message(
                session_id=session.id,
                role=MessageRole.USER.value,
                content=data.content,  # 保存原始内容
                step=current_step_enum.value,
            )
            db.add(user_message)

            # 流式输出 AI 响应，同时累积完整回复
            ai_response_parts: list[str] = []
            async for token in ai_service.stream(system_prompt, sanitized_input):
                ai_response_parts.append(token)
                payload = json.dumps({"content": token})
                yield f"event: token\ndata: {payload}\n\n"

            # 保存 AI 回复到数据库
            ai_content = "".join(ai_response_parts)
            ai_message = Message(
                session_id=session.id,
                role=MessageRole.ASSISTANT.value,
                content=ai_content,
                step=current_step_enum.value,
            )
            db.add(ai_message)

            # 获取下一步
            next_step_enum = get_next_step(current_step_enum)
            next_step = (
                next_step_enum.value if next_step_enum else current_step_enum.value
            )
            now = utc_now()

            # 处理状态转换
            if next_step_enum and can_transition(current_step_enum, next_step_enum):
                active_step_history.completed_at = now  # type: ignore[assignment]
                db.add(
                    StepHistory(
                        session_id=session.id,
                        step=next_step_enum.value,
                        started_at=now,
                    )
                )
                session.current_step = next_step_enum.value  # type: ignore[assignment]
                await analytics_service.emit(
                    "step_completed",
                    session.id,  # type: ignore[arg-type]
                    {
                        "from_step": current_step_enum.value,
                        "to_step": next_step_enum.value,
                    },
                    flush=False,
                )
            elif is_final_step(current_step_enum):
                # 最终步骤完成
                if active_step_history.completed_at is None:
                    active_step_history.completed_at = now  # type: ignore[assignment]
                    await analytics_service.emit(
                        "step_completed",
                        session.id,  # type: ignore[arg-type]
                        {"step": current_step_enum.value},
                        flush=False,
                    )
                session.status = SessionStatus.COMPLETED.value  # type: ignore[assignment]
                session.completed_at = now  # type: ignore[assignment]
                await analytics_service.emit(
                    "session_completed",
                    session.id,  # type: ignore[arg-type]
                    {"final_step": current_step_enum.value},
                    flush=False,
                )

            await db.commit()
            done_payload = json.dumps(
                {
                    "next_step": next_step,
                    "emotion_detected": emotion_result.emotion.value,
                    "confidence": emotion_result.confidence,
                }
            )
            yield f"event: done\ndata: {done_payload}\n\n"
        except Exception as e:
            # 发生异常时回滚事务，防止连接泄漏
            await db.rollback()
            # 记录详细错误到日志，但不暴露给客户端
            logger.error(
                f"SSE stream error in session {session_id}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            # 客户端只返回通用错误码，不泄露内部详情
            error_payload = json.dumps({"error": "STREAM_ERROR"})
            yield f"event: error\ndata: {error_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
