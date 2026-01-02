"""OAuth 认证端点

提供 Google OAuth 和 Apple Sign-in 登录功能
"""

from app.database import get_db
from app.middleware.rate_limit import OAUTH_RATE_LIMIT, ip_rate_limit_key, limiter
from app.schemas.auth import AuthSuccessResponse, OAuthRequest
from app.services.oauth_service import OAuthService
from app.utils.docs import COMMON_ERROR_RESPONSES
from app.utils.exceptions import raise_auth_error
from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import create_auth_response

router = APIRouter()


@router.post(
    "/oauth/google/code",
    response_model=AuthSuccessResponse,
    summary="Google OAuth 授权码登录",
    description="使用 OAuth 授权码换取令牌并登录，成功后写入认证 cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(OAUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False)
async def google_oauth_code(
    response: Response,
    request: Request,
    code: str = Query(
        ...,
        description="Google OAuth 授权码",
        examples=["4/0AX4XfWj8M7WmC9o0pP3yR"],
    ),
    device_fingerprint: str | None = Query(
        default=None,
        description="设备指纹（用于识别登录设备）",
        examples=["web-2f1a8c7d"],
    ),
    device_name: str | None = Query(
        default=None,
        description="设备名称",
        examples=["Chrome on macOS"],
    ),
    db: AsyncSession = Depends(get_db),
):
    """Google OAuth 授权码登录并写入认证 Cookie。"""
    service = OAuthService(db)
    try:
        user, tokens = await service.google_auth_with_code(
            code=code,
            device_fingerprint=device_fingerprint or f"web-{code[:8]}",
            device_name=device_name or "Web Browser",
        )
        return await create_auth_response(response, user, tokens, db)
    except ValueError as e:
        raise_auth_error(e, context="google_oauth_code")


@router.post(
    "/oauth/google",
    response_model=AuthSuccessResponse,
    summary="Google OAuth 登录",
    description="使用 Google ID Token 登录，成功后写入认证 cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(OAUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False)
async def google_oauth(
    response: Response,
    request: Request,
    data: OAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """使用 Google ID Token 登录并写入认证 Cookie。"""
    service = OAuthService(db)
    try:
        user, tokens = await service.google_auth(data)
        return await create_auth_response(response, user, tokens, db)
    except ValueError as e:
        raise_auth_error(e, context="google_oauth")


@router.post(
    "/oauth/apple",
    response_model=AuthSuccessResponse,
    summary="Apple Sign-in 登录",
    description="使用 Apple ID Token 登录，成功后写入认证 cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(OAUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False)
async def apple_oauth(
    response: Response,
    request: Request,
    data: OAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """使用 Apple Sign-in 登录并写入认证 Cookie。"""
    service = OAuthService(db)
    try:
        user, tokens = await service.apple_auth(data)
        return await create_auth_response(response, user, tokens, db)
    except ValueError as e:
        raise_auth_error(e, context="apple_oauth")
