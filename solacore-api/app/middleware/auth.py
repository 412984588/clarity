from app.utils.datetime_utils import utc_now
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import ActiveSession
from app.models.user import User
from app.utils.security import decode_token


async def get_current_user(
    request: Request,
    token: Optional[str] = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 httpOnly cookie 或 Authorization header 获取当前用户"""
    # 请求级缓存：同一个 HTTP 请求内重复调用直接复用结果
    if hasattr(request.state, "current_user"):
        return request.state.current_user

    # 优先从 cookie 读取 access_token (httpOnly cookies 模式)
    access_token = request.cookies.get("access_token")

    # 如果 cookie 没有，尝试从 Authorization 头读取（向后兼容）
    if not access_token:
        if not token:
            raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})
        if token.startswith("Bearer "):
            access_token = token.split(" ", 1)[1]
        else:
            access_token = token

    token = access_token

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

    # 合并查询：一次 JOIN 获取 session + user，减少数据库往返
    result = await db.execute(
        select(ActiveSession, User)
        .outerjoin(User, ActiveSession.user_id == User.id)
        .where(
            ActiveSession.id == session_uuid,
            ActiveSession.user_id == user_uuid,
            ActiveSession.expires_at > utc_now(),
        )
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=401, detail={"error": "SESSION_REVOKED"})

    _session, user = row

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    request.state.current_user = user
    return user
