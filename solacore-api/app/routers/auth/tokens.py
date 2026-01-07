"""Token 管理端点

提供 Token 刷新和登出功能
"""

from typing import Optional
from uuid import UUID

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.csrf import clear_csrf_cookies
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.session import ActiveSession
from app.models.user import User
from app.schemas.auth import AuthSuccessResponse, RefreshRequest
from app.services.auth_service import AuthService
from app.services.cache_service import CacheService
from app.utils.docs import COMMON_ERROR_RESPONSES
from app.utils.exceptions import raise_auth_error
from app.utils.security import decode_token
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import create_auth_response

settings = get_settings()
cache_service = CacheService()

router = APIRouter()


@router.post(
    "/refresh",
    response_model=AuthSuccessResponse,
    summary="刷新访问令牌",
    description="使用 refresh_token（cookie 或 body）刷新 access token，并更新认证 cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def refresh(
    request: Request,
    response: Response,
    data: Optional[RefreshRequest] = Body(default=None),
    db: AsyncSession = Depends(get_db),
):
    """刷新 access token（支持 cookie 和 body 两种方式）"""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token and data and data.refresh_token:
        refresh_token = data.refresh_token
    if not refresh_token:
        raise HTTPException(status_code=401, detail={"error": "MISSING_REFRESH_TOKEN"})

    service = AuthService(db)
    try:
        tokens = await service.refresh_token(refresh_token)
        payload = decode_token(tokens.access_token)
        if not payload:
            raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail={"error": "USER_NOT_FOUND"})

        return await create_auth_response(response, user, tokens, db)
    except ValueError as e:
        raise_auth_error(e, context="refresh")


@router.post(
    "/logout",
    status_code=204,
    summary="登出并撤销当前会话",
    description="撤销当前 access token 对应的会话并清除认证 cookies。",
    responses={
        **COMMON_ERROR_RESPONSES,
        204: {"description": "No Content"},
    },
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def logout(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """使当前 access token 对应 session 失效并清除认证 Cookie。"""
    # 优先从 cookie 读取 token
    token = request.cookies.get("access_token")

    # 如果 cookie 没有，从 Authorization 头读取（向后兼容）
    if not token:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        else:
            token = auth_header

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    session_id = payload.get("sid")
    try:
        session_uuid = UUID(str(session_id))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail={"error": "SESSION_NOT_FOUND"})

    # 删除数据库中的 session
    await db.execute(
        delete(ActiveSession).where(
            ActiveSession.id == session_uuid,
            ActiveSession.user_id == current_user.id,
        )
    )
    await db.commit()
    await cache_service.invalidate_sessions(current_user.id)

    # 清除 cookies (httpOnly cookies 模式)
    # 必须使用与设置时相同的 domain 参数，否则无法清除
    cookie_params = {}
    if settings.cookie_domain:
        cookie_params["domain"] = settings.cookie_domain

    response.delete_cookie("access_token", **cookie_params)
    response.delete_cookie("refresh_token", **cookie_params)
    clear_csrf_cookies(response)
    return None
