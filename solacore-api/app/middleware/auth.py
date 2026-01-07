from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.session import ActiveSession
from app.models.user import User
from app.services.cache_service import CacheService
from app.utils.datetime_utils import utc_now
from app.utils.security import decode_token
from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

cache_service = CacheService()


def _extract_access_token(request: Request, auth_header: Optional[str]) -> str:
    """从 Authorization header 或 cookie 提取访问令牌（Header 优先）"""
    # 优先使用 Authorization Header（API 标准）
    if auth_header:
        return (
            auth_header.split(" ", 1)[1]
            if auth_header.startswith("Bearer ")
            else auth_header
        )

    # 后备使用 Cookie（浏览器场景）
    access_token = request.cookies.get("access_token")
    if access_token:
        return access_token

    raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})


def _validate_token_payload(payload: dict | None) -> tuple[UUID, UUID]:
    """验证 token payload 并提取 user_id 和 session_id"""
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    try:
        user_uuid = UUID(str(payload.get("sub")))
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"}) from e

    try:
        session_uuid = UUID(str(payload.get("sid")))
    except (TypeError, ValueError) as e:
        raise HTTPException(
            status_code=401, detail={"error": "SESSION_NOT_FOUND"}
        ) from e

    return user_uuid, session_uuid


async def _verify_active_session(
    db: AsyncSession, session_uuid: UUID, user_uuid: UUID
) -> None:
    """验证会话是否存在且未过期"""
    session_result = await db.execute(
        select(ActiveSession).where(
            ActiveSession.id == session_uuid,
            ActiveSession.user_id == user_uuid,
            ActiveSession.expires_at > utc_now(),
        )
    )
    if not session_result.scalar_one_or_none():
        raise HTTPException(status_code=401, detail={"error": "SESSION_REVOKED"})


async def _get_user_from_cache_or_db(db: AsyncSession, user_uuid: UUID) -> User:
    """从缓存或数据库获取用户"""
    cached_user = await cache_service.get_user(user_uuid)
    if isinstance(cached_user, dict) and cached_user.get("email"):
        if not cached_user.get("is_active", True):
            raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})
        return User(
            id=user_uuid,
            email=str(cached_user.get("email")),
            auth_provider=str(cached_user.get("auth_provider") or "email"),
            locale=str(cached_user.get("locale") or "en"),
            is_active=bool(cached_user.get("is_active", True)),
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    await cache_service.set_user(
        user.id,
        {
            "id": str(user.id),
            "email": user.email,
            "auth_provider": user.auth_provider,
            "locale": user.locale,
            "is_active": user.is_active,
        },
    )
    return user


async def get_current_user(
    request: Request,
    token: Optional[str] = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 httpOnly cookie 或 Authorization header 获取当前用户"""
    # 请求级缓存
    if hasattr(request.state, "current_user"):
        return request.state.current_user

    # 提取并验证 token
    access_token = _extract_access_token(request, token)
    payload = decode_token(access_token)
    user_uuid, session_uuid = _validate_token_payload(payload)

    # 验证会话
    await _verify_active_session(db, session_uuid, user_uuid)

    # 获取用户
    user = await _get_user_from_cache_or_db(db, user_uuid)
    request.state.current_user = user
    return user
