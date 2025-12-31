# 会话路由辅助工具：常量、状态转换与消息存储等共享逻辑

from datetime import datetime

from app.models.message import Message, MessageRole
from app.models.solve_session import SessionStatus, SolveSession, SolveStep
from app.models.step_history import StepHistory
from app.models.subscription import Subscription, Usage
from app.services.analytics_service import AnalyticsService
from app.services.state_machine import (
    can_transition,
    get_next_step,
    is_final_step,
    validate_transition,
)
from app.utils.datetime_utils import utc_now
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


def _prepare_step_history(
    db: AsyncSession,
    step_history: StepHistory | None,
    session: SolveSession,
    current_step_enum: SolveStep,
) -> StepHistory:
    """获取或创建当前步骤的 StepHistory"""
    active_step_history = step_history
    if active_step_history and active_step_history.step != current_step_enum.value:
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
    # 确保对象被 SQLAlchemy 跟踪（如果是已存在的对象）
    db.add(active_step_history)
    return active_step_history


def _save_user_message(
    db: AsyncSession,
    session: SolveSession,
    current_step_enum: SolveStep,
    content: str,
) -> None:
    """保存用户消息到数据库"""
    user_message = Message(
        session_id=session.id,
        role=MessageRole.USER.value,
        content=content,
        step=current_step_enum.value,
    )
    db.add(user_message)


def _save_ai_message(
    db: AsyncSession,
    session: SolveSession,
    current_step_enum: SolveStep,
    content: str,
) -> None:
    """保存 AI 回复到数据库"""
    ai_message = Message(
        session_id=session.id,
        role=MessageRole.ASSISTANT.value,
        content=content,
        step=current_step_enum.value,
    )
    db.add(ai_message)


async def _handle_step_transition(
    db: AsyncSession,
    analytics_service: AnalyticsService,
    session: SolveSession,
    active_step_history: StepHistory,
    current_step_enum: SolveStep,
) -> str:
    """处理状态转换和分析事件"""
    next_step_enum = get_next_step(current_step_enum)
    next_step = next_step_enum.value if next_step_enum else current_step_enum.value
    now = utc_now()

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
            {"from_step": current_step_enum.value, "to_step": next_step_enum.value},
            flush=False,
        )
    elif is_final_step(current_step_enum):
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

    return next_step


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


def _update_session_status(session: SolveSession, status_value: str) -> None:
    """更新会话状态"""
    try:
        status_enum = SessionStatus(status_value)
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail={"error": "INVALID_STATUS"}
        ) from exc
    session.status = status_enum.value  # type: ignore[assignment]
    if status_enum == SessionStatus.COMPLETED:
        session.completed_at = utc_now()  # type: ignore[assignment]


def _update_session_step(session: SolveSession, new_step_value: str) -> None:
    """更新会话步骤（含转换验证）"""
    try:
        next_step_enum = SolveStep(new_step_value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": "INVALID_STEP"}) from exc
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
