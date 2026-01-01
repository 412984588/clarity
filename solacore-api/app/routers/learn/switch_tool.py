"""学习功能路由 - 切换工具"""

from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.learn_session import LearnSession
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import Depends, HTTPException, Path, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import router
from .utils import _validate_session


class LearnSwitchToolRequest(BaseModel):
    """切换工具请求"""

    tool: str = Field(..., description="目标工具ID")


class LearnSwitchToolResponse(BaseModel):
    """切换工具响应"""

    session_id: UUID
    current_tool: str | None
    tool_plan: list[str]


@router.patch(
    "/{session_id}/current-tool",
    response_model=LearnSwitchToolResponse,
    summary="切换当前工具",
    description="在工具计划中切换当前使用的工具。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def switch_current_tool(
    request: Request,
    response: Response,
    payload: LearnSwitchToolRequest,
    session_id: UUID = Path(..., description="会话ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """切换当前工具"""
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = _validate_session(result.scalar_one_or_none())

    tool_plan = list(session.tool_plan or [])
    if payload.tool not in tool_plan:
        raise HTTPException(status_code=400, detail={"error": "TOOL_NOT_IN_PLAN"})

    session.current_tool = payload.tool
    await db.commit()
    await db.refresh(session)

    return LearnSwitchToolResponse(
        session_id=session.id,
        current_tool=session.current_tool,
        tool_plan=tool_plan,
    )
