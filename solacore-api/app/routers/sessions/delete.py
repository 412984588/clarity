# 会话删除路由：删除会话及其关联数据

import logging
from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.solve_session import SolveSession
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)


@router.delete(
    "/{session_id}",
    status_code=204,
    summary="删除会话",
    description="删除指定的 Solve 会话及其所有相关消息。",
    responses={
        **COMMON_ERROR_RESPONSES,
        204: {"description": "会话已成功删除"},
        404: {
            "description": "会话不存在",
            "content": {
                "application/json": {
                    "example": {"detail": {"error": "SESSION_NOT_FOUND"}}
                }
            },
        },
    },
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def delete_session(
    request: Request,
    response: Response,
    session_id: UUID = Path(
        ...,
        description="会话 ID",
        examples=["2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f"],
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除 Solve 会话及其所有相关消息和历史记录。"""
    # 查询会话，确保只能删除自己的会话
    result = await db.execute(
        select(SolveSession).where(
            SolveSession.id == session_id, SolveSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    # 删除会话（级联删除会自动删除相关的消息和历史记录）
    await db.delete(session)
    await db.commit()

    logger.info(
        f"Session {session_id} deleted by user {current_user.id}",
        extra={"session_id": str(session_id), "user_id": str(current_user.id)},
    )

    # 返回 204 No Content
    return None
