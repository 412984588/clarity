"""登录端点

提供邮箱登录和 Beta 模式登录功能
"""

import secrets

from app.config import get_settings
from app.database import get_db
from app.logging_config import get_logger
from app.middleware.rate_limit import AUTH_RATE_LIMIT, ip_rate_limit_key, limiter
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.auth import (
    AuthSuccessResponse,
    BetaLoginRequest,
    LoginRequest,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.cache_service import CacheService
from app.utils.docs import COMMON_ERROR_RESPONSES
from app.utils.exceptions import raise_auth_error
from app.utils.security import hash_password_async
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .utils import set_session_cookies

logger = get_logger(__name__)
settings = get_settings()
cache_service = CacheService()

router = APIRouter()


@router.post(
    "/login",
    response_model=AuthSuccessResponse,
    summary="邮箱登录",
    description="使用邮箱与密码登录，成功后写入 httpOnly 的 access/refresh cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(AUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False)
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """邮箱登录并写入认证 Cookie，返回用户基础信息。"""
    log_context = {
        "email": data.email,
        "device_fingerprint": data.device_fingerprint,
        "device_name": data.device_name,
    }
    request.state.auth_context = log_context
    if settings.debug:
        logger.debug("auth.login.attempt", **log_context)
    else:
        logger.info("auth.login.attempt", **log_context)
    service = AuthService(db)
    try:
        user, tokens = await service.login(data)
        # 设置 httpOnly cookies
        set_session_cookies(response, tokens.access_token, tokens.refresh_token)
        await cache_service.invalidate_sessions(user.id)
        # 返回用户信息（不包含 token）
        return AuthSuccessResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                auth_provider=user.auth_provider,
                locale=user.locale,
            )
        )
    except ValueError as e:
        raise_auth_error(e, context="login")


@router.post(
    "/beta-login",
    response_model=AuthSuccessResponse,
    summary="Beta 模式自动登录",
    description=("仅在 Beta 模式开启时可用，自动登录到测试账号并写入认证 cookies。"),
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(AUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False)
async def beta_login(
    request: Request,
    response: Response,
    data: BetaLoginRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """在 Beta 模式下自动登录并创建会话。"""
    if not settings.beta_mode:
        raise HTTPException(status_code=403, detail={"error": "BETA_MODE_DISABLED"})

    beta_email = "beta-tester@solacore.app"
    result = await db.execute(
        select(User)
        .options(selectinload(User.subscription))
        .where(User.email == beta_email)
    )
    user = result.scalar_one_or_none()

    if not user:
        random_password = secrets.token_urlsafe(32)
        hashed_pw = await hash_password_async(random_password)
        user = User(
            email=beta_email,
            password_hash=hashed_pw,
            auth_provider="email",
        )
        db.add(user)
        await db.flush()

        subscription = Subscription(user_id=user.id, tier="free")
        db.add(subscription)
        await db.flush()
        await db.refresh(user, ["subscription"])
    elif not user.subscription:
        subscription = Subscription(user_id=user.id, tier="free")
        db.add(subscription)
        await db.flush()
        await db.refresh(user, ["subscription"])

    device_fingerprint = (
        data.device_fingerprint
        if data and data.device_fingerprint
        else f"beta:{user.id}"
    )
    device_name = data.device_name if data and data.device_name else "Beta Device"
    tier = user.subscription.tier if user.subscription else "free"

    service = AuthService(db)
    try:
        device = await service._get_or_create_device(
            user, device_fingerprint, device_name, tier=tier
        )
        tokens = await service._create_session(user, device)
    except ValueError as e:
        raise_auth_error(e, context="beta_login")

    await db.commit()
    # 设置 httpOnly cookies
    set_session_cookies(response, tokens.access_token, tokens.refresh_token)
    await cache_service.invalidate_sessions(user.id)
    # 返回用户信息（不包含 token）
    return AuthSuccessResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            auth_provider=user.auth_provider,
            locale=user.locale,
        )
    )
