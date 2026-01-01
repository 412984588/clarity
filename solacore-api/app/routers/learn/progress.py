"""学习功能路由 - 会话进度"""

from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.learn_session import LearnSession
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import Depends, HTTPException, Path, Request, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import router


class LearnProgressResponse(BaseModel):
    """学习进度响应"""

    session_id: UUID
    mode: str
    current_tool: str | None
    tool_plan: list[str]
    completed_tools: list[str]
    progress_percentage: int


@router.get(
    "/{session_id}/progress",
    response_model=LearnProgressResponse,
    summary="查看学习进度",
    description="查看学习会话当前进度与已完成工具。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def get_learn_progress(
    request: Request,
    response: Response,
    session_id: UUID = Path(..., description="会话ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查看学习进度"""
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    tool_plan = list(session.tool_plan or [])
    completed_tools: list[str] = []
    if tool_plan and session.current_tool in tool_plan:
        current_index = tool_plan.index(session.current_tool)
        completed_tools = tool_plan[:current_index]

    progress_percentage = 0
    if tool_plan:
        progress_percentage = int(len(completed_tools) / len(tool_plan) * 100)

    return LearnProgressResponse(
        session_id=session.id,
        mode=session.learning_mode,
        current_tool=session.current_tool,
        tool_plan=tool_plan,
        completed_tools=completed_tools,
        progress_percentage=progress_percentage,
    )
