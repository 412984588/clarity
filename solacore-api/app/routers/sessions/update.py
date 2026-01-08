# 会话更新路由：更新状态、步骤与提醒相关字段

from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.solve_session import SolveSession
from app.models.user import User
from app.schemas.session import SessionUpdateRequest, SessionUpdateResponse
from app.utils.datetime_utils import utc_now
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import _update_session_status, _update_session_step

router = APIRouter()


@router.patch(
    "/{session_id}",
    response_model=SessionUpdateResponse,
    summary="更新会话状态",
    description="更新 Solve 会话的状态、步骤或本地化配置。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def update_session(
    request: Request,
    response: Response,
    updates: SessionUpdateRequest,
    session_id: UUID = Path(
        ...,
        description="会话 ID",
        examples=["2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f"],
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

    # 使用辅助函数更新状态和步骤
    if updates.status is not None:
        _update_session_status(session, updates.status)
    if updates.current_step is not None:
        _update_session_step(session, updates.current_step)

    # 直接更新简单字段
    if updates.locale is not None:
        session.locale = updates.locale  # type: ignore[assignment]
    if updates.first_step_action is not None:
        session.first_step_action = updates.first_step_action  # type: ignore[assignment]
    if updates.reminder_time is not None:
        session.reminder_time = updates.reminder_time  # type: ignore[assignment]
    if updates.tags is not None:
        session.tags = updates.tags  # type: ignore[assignment]

    await db.commit()

    session_response = SessionUpdateResponse(
        id=str(session.id),
        status=str(session.status),
        current_step=str(session.current_step),
        updated_at=utc_now(),
    )
    return session_response
