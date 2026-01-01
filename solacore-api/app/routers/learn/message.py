"""学习功能路由 - 发送消息（SSE 流式）"""

import json
from typing import AsyncGenerator
from uuid import UUID

from app.database import get_db
from app.learn.prompts import LEARN_STEP_PROMPTS
from app.learn.prompts.base import BASE_ROLE
from app.learn.prompts.registry import TOOL_REGISTRY
from app.learn.prompts.tools import (
    CHUNKING_PROMPT,
    DUAL_CODING_PROMPT,
    ERROR_DRIVEN_PROMPT,
    FEYNMAN_PROMPT,
    GROW_PROMPT,
    INTERLEAVING_PROMPT,
    PARETO_PROMPT,
    RETRIEVAL_PROMPT,
    SOCRATIC_PROMPT,
    SPACED_PROMPT,
)
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import SSE_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.learn_message import LearnMessage, LearnMessageRole
from app.models.learn_session import LearnSession, LearnStep
from app.models.user import User
from app.services.ai_service import AIService
from app.services.content_filter import sanitize_user_input, strip_pii
from app.utils.datetime_utils import utc_now
from app.utils.docs import COMMON_ERROR_RESPONSES
from app.utils.error_handlers import handle_sse_error
from fastapi import Depends, Header, HTTPException, Path, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import LearnMessageRequest, get_next_learn_step, is_final_learn_step, router
from .utils import _build_context_prompt, _generate_review_schedule, _validate_session

TOOL_PROMPTS = {
    "pareto": PARETO_PROMPT,
    "feynman": FEYNMAN_PROMPT,
    "chunking": CHUNKING_PROMPT,
    "dual_coding": DUAL_CODING_PROMPT,
    "interleaving": INTERLEAVING_PROMPT,
    "retrieval": RETRIEVAL_PROMPT,
    "spaced": SPACED_PROMPT,
    "grow": GROW_PROMPT,
    "socratic": SOCRATIC_PROMPT,
    "error_driven": ERROR_DRIVEN_PROMPT,
}


def _build_tool_prompt(tool: str) -> str:
    return "\n\n".join(
        [
            BASE_ROLE,
            f"当前方法论：{TOOL_PROMPTS[tool]}",
            "语言要求：必须用中文，语气温暖鼓励。",
            "回复长度：2-4句话，简洁有引导性。",
        ]
    )


@router.post(
    "/{session_id}/messages",
    summary="发送学习消息",
    description="向学习会话发送消息，获取 AI 基于方法论的引导回复。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(SSE_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def send_learn_message(
    request: Request,
    response: Response,
    message_request: LearnMessageRequest,
    session_id: UUID = Path(..., description="会话ID"),
    x_device_fingerprint: str | None = Header(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息并获取流式回复"""
    # 查询并验证会话
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = _validate_session(result.scalar_one_or_none())

    if not message_request.tool and not message_request.step:
        raise HTTPException(status_code=400, detail={"error": "STEP_OR_TOOL_REQUIRED"})

    if message_request.tool and message_request.tool not in TOOL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_TOOL", "tool": message_request.tool},
        )

    # 校验tool是否在会话tool_plan中（如果已设置plan）
    if message_request.tool and session.tool_plan:
        if message_request.tool not in session.tool_plan:
            raise HTTPException(
                status_code=400,
                detail={"error": "TOOL_NOT_IN_PLAN", "tool": message_request.tool},
            )

    step_value = message_request.step or session.current_step
    try:
        current_step = LearnStep(step_value)
    except ValueError:
        raise HTTPException(status_code=400, detail={"error": "INVALID_STEP"})

    # 内容过滤
    sanitized_content = sanitize_user_input(message_request.content)
    sanitized_content = strip_pii(sanitized_content)

    # 保存用户消息
    user_message = LearnMessage(
        session_id=session.id,
        role=LearnMessageRole.USER.value,
        content=sanitized_content,
        step=step_value,
    )
    user_message.tool = message_request.tool
    db.add(user_message)

    # 如果是第一条消息，提取学习主题
    if not session.topic and step_value == LearnStep.START.value:
        session.topic = sanitized_content[:30] + (
            "..." if len(sanitized_content) > 30 else ""
        )

    await db.commit()

    # 获取历史消息并构建上下文提示
    history_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in session.messages
        if msg.id != user_message.id
    ]
    user_prompt_with_history = _build_context_prompt(
        history_messages, sanitized_content
    )

    # 获取系统提示词和 AI 服务
    if message_request.tool:
        system_prompt = _build_tool_prompt(message_request.tool)
    else:
        system_prompt = LEARN_STEP_PROMPTS.get(
            current_step.value, LEARN_STEP_PROMPTS[LearnStep.START.value]
        )
    ai_service = AIService()

    async def event_generator() -> AsyncGenerator[str, None]:
        """SSE 事件生成器"""
        accumulated_content = ""

        try:
            # 流式接收 AI 回复
            async for token in ai_service.stream(
                system_prompt, user_prompt_with_history
            ):
                accumulated_content += token
                yield f"event: token\ndata: {json.dumps({'content': token})}\n\n"

            # 保存 AI 回复
            ai_message = LearnMessage(
                session_id=session.id,
                role=LearnMessageRole.ASSISTANT.value,
                content=accumulated_content,
                step=current_step.value,
            )
            ai_message.tool = message_request.tool
            db.add(ai_message)

            # 检查是否可以进入下一步
            next_step = get_next_learn_step(current_step)
            step_completed = len(accumulated_content) > 50

            # 如果是最后一步，生成复习计划
            if is_final_learn_step(current_step):
                session.status = "completed"
                session.completed_at = utc_now()
                session.review_schedule = _generate_review_schedule()

            await db.commit()
            await db.refresh(ai_message)

            # 发送完成事件
            done_data = json.dumps(
                {
                    "message_id": str(ai_message.id),
                    "next_step": next_step.value if next_step else None,
                    "step_completed": step_completed,
                    "session_completed": session.status == "completed",
                }
            )
            yield f"event: done\ndata: {done_data}\n\n"

        except Exception as e:
            # 使用统一的 SSE 错误处理
            async for error_event in handle_sse_error(
                db,
                e,
                {
                    "session_id": str(session_id),
                    "step": session.current_step,
                    "user_id": str(current_user.id),
                },
            ):
                yield error_event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
