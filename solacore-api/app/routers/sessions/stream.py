# 会话流式路由：处理 SSE 消息流与 Solve 流程推进

import json
from typing import AsyncGenerator
from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import SSE_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.solve_session import SessionStatus, SolveSession, SolveStep
from app.models.step_history import StepHistory
from app.models.user import User
from app.schemas.session import MessageRequest
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.services.content_filter import sanitize_user_input, strip_pii
from app.services.crisis_detector import detect_crisis, get_crisis_response
from app.services.emotion_detector import detect_emotion
from app.utils.docs import COMMON_ERROR_RESPONSES
from app.utils.error_handlers import handle_sse_error
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import (
    STEP_SYSTEM_PROMPTS,
    _handle_step_transition,
    _prepare_step_history,
    _save_ai_message,
    _save_user_message,
)

router = APIRouter()


@router.post(
    "/{session_id}/messages",
    response_class=StreamingResponse,
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
                        'data: {"content": "我能理解你的感受，"}\n\n'
                        "event: done\n"
                        'data: {"next_step": "clarify", "emotion_detected": "sadness"}\n\n'
                    )
                }
            },
        },
    },
)
@limiter.limit(SSE_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def stream_messages(
    request: Request,
    response: Response,
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
            # 准备 StepHistory
            active_step_history = _prepare_step_history(
                db, step_history, session, current_step_enum
            )

            # 保存用户消息并立即提交，避免在AI流式响应期间持有DB连接
            _save_user_message(db, session, current_step_enum, data.content)
            await db.commit()

            # 流式输出 AI 响应（此时DB连接已释放）
            ai_response_parts: list[str] = []
            async for token in ai_service.stream(system_prompt, sanitized_input):
                ai_response_parts.append(token)
                payload = json.dumps({"content": token})
                yield f"event: token\ndata: {payload}\n\n"

            # AI响应完成后，重新开启事务保存回复和状态
            # 保存 AI 回复
            _save_ai_message(db, session, current_step_enum, "".join(ai_response_parts))

            # 处理状态转换和分析
            next_step = await _handle_step_transition(
                db,
                analytics_service,
                session,
                active_step_history,
                current_step_enum,
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
            # 使用统一的 SSE 错误处理
            async for error_event in handle_sse_error(
                db,
                e,
                {
                    "session_id": str(session_id),
                    "step": current_step,
                    "user_id": str(current_user.id),
                },
            ):
                yield error_event

    return StreamingResponse(event_generator(), media_type="text/event-stream")
