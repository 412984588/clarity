"""学习功能路由 - 会话详情与历史"""

from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.learn_session import LearnSession
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import Depends, HTTPException, Path, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import LearnSessionResponse, router


@router.get(
    "/{session_id}",
    response_model=LearnSessionResponse,
    summary="获取学习会话详情",
    description="获取指定学习会话的详细信息，包括消息历史。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def get_learn_session(
    request: Request,
    response: Response,
    session_id: UUID = Path(..., description="会话ID"),
    include_messages: bool = Query(True, description="是否包含消息历史"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取学习会话详情"""
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    return LearnSessionResponse(
        id=session.id,
        status=str(session.status),
        current_step=str(session.current_step),
        topic=session.topic,
        key_concepts=session.key_concepts,
        review_schedule=session.review_schedule,
        created_at=session.created_at,  # type: ignore[arg-type]
        completed_at=session.completed_at,
        messages=[
            {
                "id": msg.id,
                "role": str(msg.role),
                "content": msg.content,
                "step": str(msg.step),
                "created_at": msg.created_at,
            }
            for msg in session.messages
        ]
        if include_messages
        else [],
    )
