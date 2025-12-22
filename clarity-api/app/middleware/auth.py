from app.utils.datetime_utils import utc_now
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import ActiveSession
from app.models.user import User
from app.utils.security import decode_token


async def get_current_user(
    token: Optional[str] = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """从 Authorization header 获取当前用户"""
    if not token:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1]

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    user_id = payload.get("sub")
    session_id = payload.get("sid")
    try:
        user_uuid = UUID(str(user_id))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    try:
        session_uuid = UUID(str(session_id))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail={"error": "SESSION_NOT_FOUND"})

    session_result = await db.execute(
        select(ActiveSession).where(
            ActiveSession.id == session_uuid,
            ActiveSession.user_id == user_uuid,
            ActiveSession.expires_at > utc_now()
        )
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=401, detail={"error": "SESSION_REVOKED"})

    # 鉴权只需要 User 基础信息，不需要加载关联数据
    result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    return user
