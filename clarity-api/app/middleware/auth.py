from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
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
    try:
        user_uuid = UUID(str(user_id))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    # 鉴权只需要 User 基础信息，不需要加载关联数据
    result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    return user
