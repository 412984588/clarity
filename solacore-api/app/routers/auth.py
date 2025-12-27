from app.utils.datetime_utils import utc_now
from datetime import timedelta
import hashlib
import logging
import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter, AUTH_RATE_LIMIT
from app.models.device import Device
from app.models.password_reset import PasswordResetToken
from app.models.session import ActiveSession
from app.models.subscription import Subscription
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.email_service import send_password_reset_email
from app.services.oauth_service import OAuthService
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    BetaLoginRequest,
    AuthSuccessResponse,
    UserResponse,
    OAuthRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.utils.exceptions import raise_auth_error
from app.utils.security import decode_token, hash_password_async

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """设置认证 cookies (httpOnly, Secure, SameSite)"""
    cookie_config: dict = {
        "httponly": True,  # 防止 JavaScript 访问
        "secure": not settings.debug,  # 生产环境强制 HTTPS
        "samesite": "lax",  # CSRF 保护
    }

    # 生产环境设置 domain，允许跨子域名共享 cookie
    # 例如：.solacore.app 允许 api.solacore.app 和 www.solacore.app 共享
    if settings.cookie_domain:
        cookie_config["domain"] = settings.cookie_domain

    # Access token cookie (1小时过期)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=3600,  # 1 hour
        **cookie_config,
    )

    # Refresh token cookie (30天过期)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=30 * 24 * 3600,  # 30 days
        **cookie_config,
    )


@router.post("/register", response_model=AuthSuccessResponse, status_code=201)
@limiter.limit(AUTH_RATE_LIMIT)
async def register(
    request: Request,
    response: Response,
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """注册新用户 (httpOnly cookies 模式)"""
    service = AuthService(db)
    try:
        user, tokens = await service.register(data)
        # 设置 httpOnly cookies
        set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
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
        raise_auth_error(e, context="register")


@router.post("/login", response_model=AuthSuccessResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """邮箱登录 (httpOnly cookies 模式)"""
    service = AuthService(db)
    try:
        user, tokens = await service.login(data)
        # 设置 httpOnly cookies
        set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
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


@router.post("/beta-login", response_model=AuthSuccessResponse)
async def beta_login(
    response: Response,
    data: BetaLoginRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Beta 模式自动登录"""
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
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    # 返回用户信息（不包含 token）
    return AuthSuccessResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            auth_provider=user.auth_provider,
            locale=user.locale,
        )
    )


@router.post("/refresh", response_model=AuthSuccessResponse)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """刷新 access token (httpOnly cookies 模式)"""
    # 从 cookie 读取 refresh_token
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail={"error": "MISSING_REFRESH_TOKEN"})

    service = AuthService(db)
    try:
        tokens = await service.refresh_token(refresh_token)
        # 获取用户信息
        payload = decode_token(tokens.access_token)
        if not payload:
            raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail={"error": "USER_NOT_FOUND"})

        # 设置 httpOnly cookies
        set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
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
        raise_auth_error(e, context="refresh")


@router.post("/forgot-password")
@limiter.limit("3/hour")  # 防止邮件轰炸：每小时最多 3 次
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """忘记密码（始终返回 200，防止时序攻击）"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    if user:
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=utc_now() + timedelta(minutes=30),
        )
        db.add(reset_token)
        await db.commit()

        # 发送邮件
        try:
            await send_password_reset_email(str(user.email), token)
        except Exception as e:
            logger.error(f"Password reset email error: {e}")

        # Debug 模式额外记录日志
        if settings.debug:
            logger.info(
                "Password reset link: %s/auth/reset?token=%s",
                settings.frontend_url,
                token,
            )

    return {"message": "If an account exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """重置密码"""
    token_hash = hashlib.sha256(data.token.encode()).hexdigest()
    result = await db.execute(
        select(PasswordResetToken)
        .options(selectinload(PasswordResetToken.user))
        .where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.expires_at > utc_now(),
            PasswordResetToken.used_at.is_(None),
        )
    )
    reset_token = result.scalar_one_or_none()

    if not reset_token or not reset_token.user:
        raise HTTPException(
            status_code=400, detail={"error": "INVALID_OR_EXPIRED_TOKEN"}
        )

    reset_token.user.password_hash = await hash_password_async(data.new_password)  # type: ignore[assignment]
    reset_token.used_at = utc_now()  # type: ignore[assignment]

    await db.execute(
        delete(ActiveSession).where(ActiveSession.user_id == reset_token.user_id)
    )

    await db.commit()
    return {"message": "Password reset successful"}


@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """登出 - 使当前 access token 对应 session 失效，清除 cookies"""
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

    # 清除 cookies (httpOnly cookies 模式)
    # 必须使用与设置时相同的 domain 参数，否则无法清除
    cookie_params = {}
    if settings.cookie_domain:
        cookie_params["domain"] = settings.cookie_domain

    response.delete_cookie("access_token", **cookie_params)
    response.delete_cookie("refresh_token", **cookie_params)
    return None


@router.post("/oauth/google/code", response_model=AuthSuccessResponse)
async def google_oauth_code(
    response: Response,
    code: str,
    device_fingerprint: str | None = None,
    device_name: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Google OAuth code exchange (标准 authorization code flow)"""
    service = OAuthService(db)
    try:
        user, tokens = await service.google_auth_with_code(
            code=code,
            device_fingerprint=device_fingerprint or f"web-{code[:8]}",
            device_name=device_name or "Web Browser",
        )
        # 设置 httpOnly cookies
        set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
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
        raise_auth_error(e, context="google_oauth_code")


@router.post("/oauth/google", response_model=AuthSuccessResponse)
async def google_oauth(
    response: Response,
    data: OAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """Google OAuth 登录 (httpOnly cookies 模式 - id_token 直接验证)"""
    service = OAuthService(db)
    try:
        user, tokens = await service.google_auth(data)
        # 设置 httpOnly cookies
        set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
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
        raise_auth_error(e, context="google_oauth")


@router.post("/oauth/apple", response_model=AuthSuccessResponse)
async def apple_oauth(
    response: Response,
    data: OAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """Apple Sign-in 登录 (httpOnly cookies 模式)"""
    service = OAuthService(db)
    try:
        user, tokens = await service.apple_auth(data)
        # 设置 httpOnly cookies
        set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
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
        raise_auth_error(e, context="apple_oauth")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户信息 (httpOnly cookies 模式)"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        auth_provider=current_user.auth_provider,
        locale=current_user.locale,
    )


@router.get("/devices")
async def list_devices(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取当前用户的活跃设备列表"""
    # 只查询需要的字段，不加载关联数据
    result = await db.execute(
        select(Device)
        .where(Device.user_id == current_user.id, Device.is_active.is_(True))
        .order_by(Device.created_at.asc())
    )
    devices = result.scalars().all()
    return [
        {
            "id": device.id,
            "device_name": device.device_name,
            "platform": device.platform,
            "last_active_at": device.last_active_at.isoformat()
            if device.last_active_at
            else None,
            "is_active": device.is_active,
        }
        for device in devices
    ]


@router.delete("/devices/{device_id}", status_code=204)
async def revoke_device(
    device_id: UUID,
    device_fingerprint: str = Header(..., alias="X-Device-Fingerprint"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """解绑设备"""
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail={"error": "DEVICE_NOT_FOUND"})

    if device.device_fingerprint == device_fingerprint:
        raise HTTPException(
            status_code=400, detail={"error": "CANNOT_REMOVE_CURRENT_DEVICE"}
        )

    # 使用 SQL 日期过滤，避免内存加载所有记录
    today = utc_now().date()
    removal_check = await db.execute(
        select(func.count())
        .select_from(Device)
        .where(
            Device.user_id == current_user.id,
            func.date(Device.last_removal_at) == today,
        )
    )
    if (removal_check.scalar() or 0) > 0:
        raise HTTPException(status_code=429, detail={"error": "REMOVAL_LIMIT_EXCEEDED"})

    device.is_active = False  # type: ignore[assignment]
    device.last_removal_at = utc_now()  # type: ignore[assignment]

    # 批量删除会话，避免 N+1 问题
    await db.execute(delete(ActiveSession).where(ActiveSession.device_id == device_id))

    await db.commit()
    return None


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取当前用户的活跃会话"""
    # 只查询需要的字段，不加载 device 关联
    result = await db.execute(
        select(ActiveSession)
        .where(
            ActiveSession.user_id == current_user.id,
            ActiveSession.expires_at > utc_now(),
        )
        .order_by(ActiveSession.created_at.asc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": session.id,
            "device_id": session.device_id,
            "created_at": session.created_at.isoformat()
            if session.created_at
            else None,
            "expires_at": session.expires_at.isoformat()
            if session.expires_at
            else None,
        }
        for session in sessions
    ]


@router.delete("/sessions/{session_id}", status_code=204)
async def revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """终止会话"""
    result = await db.execute(
        select(ActiveSession).where(
            ActiveSession.id == session_id, ActiveSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    await db.delete(session)
    await db.commit()
    return None


@router.get("/config/features")
async def get_features():
    """返回前端功能开关配置"""
    return {
        "payments_enabled": settings.payments_enabled,
        "beta_mode": settings.beta_mode,
        "app_version": settings.app_version,
    }
