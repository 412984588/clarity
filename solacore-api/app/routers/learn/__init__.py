"""学习功能路由 - 基于方法论引导的学习助手

内置方法论：
- 费曼学习法：用简单语言解释，测试真正理解程度
- 分块学习法：把大主题拆成小块，逐个攻克
- 主题交叉法：建立知识连接，启发跨界思考
- 艾宾浩斯遗忘曲线：科学的复习时间安排
- 双编码理论：文字+图像双重编码
- 80/20原则：找到20%的核心内容
- GROW模型：Goal→Reality→Options→Will
"""

# isort: skip_file
# 路由导入顺序影响 FastAPI 路由注册，必须保持 tools 在 history 之前

import logging
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.learn_message import LearnMessage, LearnMessageRole
from app.models.learn_session import LearnSession, LearnStep
from app.models.user import User
from app.utils.datetime_utils import utc_now
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/learn", tags=["Learn"])

# 步骤顺序定义
LEARN_STEP_ORDER = [
    LearnStep.START,
    LearnStep.EXPLORE,
    LearnStep.PRACTICE,
    LearnStep.PLAN,
]


def get_next_learn_step(current: LearnStep) -> LearnStep | None:
    """获取下一个学习步骤"""
    try:
        idx = LEARN_STEP_ORDER.index(current)
        if idx < len(LEARN_STEP_ORDER) - 1:
            return LEARN_STEP_ORDER[idx + 1]
        return None  # 已是最后一步
    except ValueError:
        return None


def is_final_learn_step(step: LearnStep) -> bool:
    """是否是最后一步"""
    return step == LearnStep.PLAN


# ==================== Pydantic Schemas ====================


class LearnSessionCreateResponse(BaseModel):
    """创建学习会话响应"""

    session_id: UUID = Field(..., description="会话ID")
    status: str = Field(..., description="会话状态")
    current_step: str = Field(..., description="当前步骤")
    created_at: datetime = Field(..., description="创建时间")


class LearnMessageRequest(BaseModel):
    """发送消息请求"""

    content: str = Field(..., min_length=1, max_length=4000, description="消息内容")
    step: str | None = Field(None, description="当前步骤")
    tool: str | None = Field(None, description="当前工具")


class LearnMessageResponse(BaseModel):
    """消息响应"""

    id: UUID
    role: str
    content: str
    step: str | None
    tool: str | None
    created_at: datetime


class LearnSessionResponse(BaseModel):
    """会话详情响应"""

    id: UUID
    status: str
    current_step: str
    topic: str | None
    key_concepts: list | None
    review_schedule: dict | None
    created_at: datetime
    completed_at: datetime | None
    messages: list[LearnMessageResponse] = []


class LearnSessionListItem(BaseModel):
    """会话列表项"""

    id: UUID
    status: str
    current_step: str
    topic: str | None
    created_at: datetime
    first_message: str | None = None


class LearnSessionListResponse(BaseModel):
    """会话列表响应"""

    sessions: list[LearnSessionListItem]
    total: int
    limit: int
    offset: int


# ==================== API 端点 ====================


@router.get(
    "",
    response_model=LearnSessionListResponse,
    summary="获取学习会话列表",
    description="获取当前用户的所有学习会话列表。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def list_learn_sessions(
    request: Request,
    response: Response,
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取学习会话列表"""
    # 子查询：获取每个会话的第一条用户消息
    first_message_subq = (
        select(
            LearnMessage.session_id,
            LearnMessage.content.label("first_message"),
        )
        .where(LearnMessage.role == LearnMessageRole.USER.value)
        .distinct(LearnMessage.session_id)
        .order_by(LearnMessage.session_id, LearnMessage.created_at.asc())
        .subquery()
    )

    # 主查询
    query = (
        select(LearnSession, first_message_subq.c.first_message)
        .outerjoin(
            first_message_subq,
            LearnSession.id == first_message_subq.c.session_id,
        )
        .where(LearnSession.user_id == current_user.id)
        .order_by(LearnSession.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    # 获取总数
    count_result = await db.execute(
        select(func.count(LearnSession.id)).where(
            LearnSession.user_id == current_user.id
        )
    )
    total = count_result.scalar() or 0

    sessions = []
    for session, first_message in rows:
        # 截断第一条消息
        truncated_message = None
        if first_message:
            truncated_message = (
                first_message[:50] + "..." if len(first_message) > 50 else first_message
            )

        sessions.append(
            LearnSessionListItem(
                id=session.id,
                status=str(session.status),
                current_step=str(session.current_step),
                topic=session.topic,
                created_at=session.created_at,  # type: ignore[arg-type]
                first_message=truncated_message,
            )
        )

    return LearnSessionListResponse(
        sessions=sessions,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/{session_id}",
    summary="更新学习会话",
    description="更新学习会话的状态或当前步骤。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def update_learn_session(
    request: Request,
    response: Response,
    session_id: UUID = Path(..., description="会话ID"),
    current_step: str | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新学习会话"""
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    if current_step:
        # 验证步骤值
        try:
            new_step = LearnStep(current_step)
            session.current_step = new_step.value
        except ValueError:
            raise HTTPException(status_code=400, detail={"error": "INVALID_STEP"})

    if status:
        if status not in ["active", "completed", "abandoned"]:
            raise HTTPException(status_code=400, detail={"error": "INVALID_STATUS"})
        session.status = status
        if status == "completed":
            session.completed_at = utc_now()

    await db.commit()
    await db.refresh(session)

    return {
        "id": str(session.id),
        "status": session.status,
        "current_step": session.current_step,
        "topic": session.topic,
    }


@router.delete(
    "/{session_id}",
    status_code=204,
    summary="删除学习会话",
    description="删除指定的学习会话及其所有消息。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def delete_learn_session(
    request: Request,
    response: Response,
    session_id: UUID = Path(..., description="会话ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除学习会话"""
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    await db.delete(session)
    await db.commit()

    logger.info(
        f"Learn session {session_id} deleted by user {current_user.id}",
        extra={"session_id": str(session_id), "user_id": str(current_user.id)},
    )

    return None


from . import history  # noqa: E402,F401 # 通配路径最后
from . import tools  # noqa: E402,F401 # 具体路径优先，避免被 /{session_id} 捕获
from . import create, message, path, progress, switch_tool  # noqa: E402,F401

__all__ = ["router"]
