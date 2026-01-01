"""学习功能路由 - 工具列表"""

import re

from app.learn.prompts.registry import TOOL_REGISTRY
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import Depends, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from . import router


class LearnToolItem(BaseModel):
    """工具信息"""

    id: str = Field(..., description="工具ID")
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    estimated_minutes: int = Field(..., ge=1, description="预计用时(分钟)")
    scenarios: list[str] = Field(..., alias="适用场景", description="适用场景")

    model_config = ConfigDict(populate_by_name=True)


class LearnToolListResponse(BaseModel):
    """工具列表响应"""

    tools: list[LearnToolItem]


def _estimate_minutes(duration: str | None) -> int:
    """从时长文本中估算分钟数"""
    if not duration:
        return 5
    numbers = [int(value) for value in re.findall(r"\d+", duration)]
    if not numbers:
        return 5
    return max(numbers)


@router.get(
    "/tools",
    response_model=LearnToolListResponse,
    summary="获取工具列表",
    description="获取学习工具列表及其元数据。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def list_learn_tools(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
):
    """获取工具列表"""
    tools = []
    for tool_id, metadata in TOOL_REGISTRY.items():
        duration = metadata.get("duration")
        duration_str = str(duration) if duration else None
        tools.append(
            LearnToolItem(
                id=tool_id,
                name=str(metadata.get("name", "")),
                description=str(metadata.get("description", "")),
                estimated_minutes=_estimate_minutes(duration_str),
                scenarios=list(metadata.get("scenarios", [])),
            )
        )

    return LearnToolListResponse(tools=tools)
