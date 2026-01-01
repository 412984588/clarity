"""学习功能路由 - 设置学习路径"""

from typing import Literal
from uuid import UUID

from app.database import get_db
from app.learn.prompts.registry import TOOL_REGISTRY
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

DEFAULT_QUICK_TOOLS = ["pareto", "feynman", "grow"]
DEFAULT_DEEP_TOOLS = list(TOOL_REGISTRY.keys())


class LearnPathRequest(BaseModel):
    """设置学习路径请求"""

    mode: Literal["quick", "deep", "custom"] = Field(..., description="学习模式")
    selected_tools: list[str] | None = Field(
        None, description="自选工具列表(仅 custom 模式使用)"
    )
    preferred_order: list[str] | None = Field(
        None, description="优先顺序(将被提升到前面)"
    )


class LearnPathResponse(BaseModel):
    """设置学习路径响应"""

    session_id: UUID
    mode: str
    current_tool: str | None
    tool_plan: list[str]


def _dedupe_tools(tools: list[str]) -> list[str]:
    """去重并保留顺序"""
    seen: set[str] = set()
    result: list[str] = []
    for tool in tools:
        if tool in seen:
            continue
        seen.add(tool)
        result.append(tool)
    return result


def _validate_tools(tools: list[str]) -> None:
    """验证工具是否合法"""
    valid_tools = set(TOOL_REGISTRY.keys())
    invalid = [tool for tool in tools if tool not in valid_tools]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_TOOL", "tools": invalid},
        )


def _apply_preferred_order(tools: list[str], preferred_order: list[str]) -> list[str]:
    """应用工具优先顺序"""
    preferred_order = _dedupe_tools(preferred_order)
    invalid = [tool for tool in preferred_order if tool not in tools]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_PREFERRED_ORDER", "tools": invalid},
        )
    remaining = [tool for tool in tools if tool not in preferred_order]
    return preferred_order + remaining


@router.post(
    "/{session_id}/path",
    response_model=LearnPathResponse,
    summary="设置学习路径",
    description="设置学习模式并生成工具学习路径。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def set_learn_path(
    request: Request,
    response: Response,
    payload: LearnPathRequest,
    session_id: UUID = Path(..., description="会话ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """设置学习路径"""
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = _validate_session(result.scalar_one_or_none())

    if payload.mode == "quick":
        tool_plan = DEFAULT_QUICK_TOOLS
    elif payload.mode == "deep":
        tool_plan = DEFAULT_DEEP_TOOLS
    else:
        if not payload.selected_tools:
            raise HTTPException(status_code=400, detail={"error": "TOOLS_REQUIRED"})
        tool_plan = _dedupe_tools(payload.selected_tools)

    _validate_tools(tool_plan)

    if payload.preferred_order:
        tool_plan = _apply_preferred_order(tool_plan, payload.preferred_order)

    if not tool_plan:
        raise HTTPException(status_code=400, detail={"error": "EMPTY_TOOL_PLAN"})

    session.learning_mode = payload.mode
    session.tool_plan = tool_plan
    session.current_tool = tool_plan[0]

    await db.commit()
    await db.refresh(session)

    return LearnPathResponse(
        session_id=session.id,
        mode=session.learning_mode,
        current_tool=session.current_tool,
        tool_plan=tool_plan,
    )
