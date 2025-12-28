from app.utils.datetime_utils import utc_now
from datetime import timedelta
import hashlib
import logging
import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.csrf import (
    clear_csrf_cookies,
    generate_csrf_token,
    set_csrf_cookies,
)
from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    AUTH_RATE_LIMIT,
    FORGOT_PASSWORD_RATE_LIMIT,
    OAUTH_RATE_LIMIT,
    ip_rate_limit_key,
    limiter,
    user_rate_limit_key,
)
from app.models.device import Device
from app.models.password_reset import PasswordResetToken
from app.models.session import ActiveSession
from app.models.subscription import Subscription
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.cache_service import CacheService
from app.services.email_service import send_password_reset_email
from app.services.oauth_service import OAuthService
from app.schemas.auth import (
    ActiveSessionResponse,
    AuthSuccessResponse,
    BetaLoginRequest,
    CsrfTokenResponse,
    DeviceResponse,
    FeatureConfigResponse,
    ForgotPasswordRequest,
    LoginRequest,
    OAuthRequest,
    RegisterRequest,
    ResetPasswordRequest,
    StatusMessageResponse,
    UserResponse,
)
from app.utils.docs import COMMON_ERROR_RESPONSES
from app.utils.exceptions import raise_auth_error
from app.utils.security import decode_token, hash_password_async

logger = logging.getLogger(__name__)
settings = get_settings()
cache_service = CacheService()

router = APIRouter(prefix="/auth", tags=["Auth"])


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


def set_session_cookies(
    response: Response, access_token: str, refresh_token: str
) -> None:
    set_auth_cookies(response, access_token, refresh_token)
    set_csrf_cookies(response, generate_csrf_token())


@router.get(
    "/csrf",
    response_model=CsrfTokenResponse,
    summary="获取 CSRF Token",
    description=(
        "生成新的 CSRF Token，并写入 `csrf_token` 与 `csrf_token_http` 两个 cookie。"
        "用于 Cookie 认证下的写操作。"
    ),
    responses=COMMON_ERROR_RESPONSES,
)
async def get_csrf_token(response: Response):
    """生成 CSRF Token 并写入双 Cookie，供后续写操作使用。"""
    token = generate_csrf_token()
    set_csrf_cookies(response, token)
    return {"csrf_token": token}


@router.post(
    "/register",
    response_model=AuthSuccessResponse,
    status_code=201,
    summary="注册新用户",
    description=(
        "使用邮箱与密码注册新账号，成功后写入 httpOnly 的 access/refresh cookies。"
        "注册接口免 CSRF 校验。"
    ),
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    AUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False
)
async def register(
    request: Request,
    response: Response,
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """注册新用户并写入认证 Cookie，返回用户基础信息。"""
    service = AuthService(db)
    try:
        user, tokens = await service.register(data)
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
        raise_auth_error(e, context="register")


@router.post(
    "/login",
    response_model=AuthSuccessResponse,
    summary="邮箱登录",
    description="使用邮箱与密码登录，成功后写入 httpOnly 的 access/refresh cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    AUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False
)
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """邮箱登录并写入认证 Cookie，返回用户基础信息。"""
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
    description=(
        "仅在 Beta 模式开启时可用，自动登录到测试账号并写入认证 cookies。"
    ),
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    AUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False
)
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


@router.post(
    "/refresh",
    response_model=AuthSuccessResponse,
    summary="刷新访问令牌",
    description="使用 refresh_token cookie 刷新 access token，并更新认证 cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """刷新 access token 并更新认证 Cookie。"""
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
        set_session_cookies(response, tokens.access_token, tokens.refresh_token)
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


@router.post(
    "/forgot-password",
    response_model=StatusMessageResponse,
    summary="发送密码重置邮件",
    description=(
        "提交邮箱地址触发密码重置邮件发送。为避免用户枚举，"
        "无论邮箱是否存在都返回同样的响应。"
    ),
    responses={
        **COMMON_ERROR_RESPONSES,
        200: {
            "description": "请求已受理",
            "content": {
                "application/json": {
                    "example": {
                        "message": "If an account exists, a reset link has been sent"
                    }
                }
            },
        },
    },
)
@limiter.limit(
    FORGOT_PASSWORD_RATE_LIMIT,
    key_func=ip_rate_limit_key,
    override_defaults=False,
)  # 防止邮件轰炸：每小时最多 3 次
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """发送密码重置邮件，始终返回成功提示以防止枚举攻击。"""
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


@router.post(
    "/reset-password",
    response_model=StatusMessageResponse,
    summary="重置密码",
    description="使用重置 token 更新密码，并清理所有活跃会话。",
    responses={
        **COMMON_ERROR_RESPONSES,
        200: {
            "description": "重置成功",
            "content": {
                "application/json": {"example": {"message": "Password reset successful"}}
            },
        },
    },
)
async def reset_password(
    data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """使用重置 token 更新密码并清理历史会话。"""
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
    await cache_service.invalidate_sessions(reset_token.user_id)
    return {"message": "Password reset successful"}


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
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
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


@router.post(
    "/oauth/google/code",
    response_model=AuthSuccessResponse,
    summary="Google OAuth 授权码登录",
    description="使用 OAuth 授权码换取令牌并登录，成功后写入认证 cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    OAUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False
)
async def google_oauth_code(
    response: Response,
    request: Request,
    code: str = Query(
        ...,
        description="Google OAuth 授权码",
        example="4/0AX4XfWj8M7WmC9o0pP3yR",
    ),
    device_fingerprint: str | None = Query(
        default=None,
        description="设备指纹（用于识别登录设备）",
        example="web-2f1a8c7d",
    ),
    device_name: str | None = Query(
        default=None,
        description="设备名称",
        example="Chrome on macOS",
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
        # 设置 httpOnly cookies
        set_session_cookies(response, tokens.access_token, tokens.refresh_token)
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


@router.post(
    "/oauth/google",
    response_model=AuthSuccessResponse,
    summary="Google OAuth 登录",
    description="使用 Google ID Token 登录，成功后写入认证 cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    OAUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False
)
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
        # 设置 httpOnly cookies
        set_session_cookies(response, tokens.access_token, tokens.refresh_token)
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


@router.post(
    "/oauth/apple",
    response_model=AuthSuccessResponse,
    summary="Apple Sign-in 登录",
    description="使用 Apple ID Token 登录，成功后写入认证 cookies。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    OAUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False
)
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
        # 设置 httpOnly cookies
        set_session_cookies(response, tokens.access_token, tokens.refresh_token)
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


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="返回当前登录用户的基础信息。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """获取当前登录用户的基础资料。"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        auth_provider=current_user.auth_provider,
        locale=current_user.locale,
    )


@router.get(
    "/devices",
    response_model=list[DeviceResponse],
    summary="获取活跃设备列表",
    description="返回当前用户的活跃设备列表。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def list_devices(
    request: Request,
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取当前用户的活跃设备列表。"""
    # 只查询需要的字段，不加载关联数据
    result = await db.execute(
        select(Device)
        .where(Device.user_id == current_user.id, Device.is_active.is_(True))
        .order_by(Device.created_at.asc())
    )
    devices = result.scalars().all()
    response: list[dict[str, object]] = []
    for device in devices:
        cached_device = await cache_service.get_device(device.id)
        if isinstance(cached_device, dict):
            response.append(cached_device)
            continue
        payload = {
            "id": str(device.id),
            "device_name": device.device_name,
            "platform": device.platform,
            "last_active_at": device.last_active_at.isoformat()
            if device.last_active_at
            else None,
            "is_active": device.is_active,
        }
        response.append(payload)
        await cache_service.set_device(device.id, payload)
    return response


@router.delete(
    "/devices/{device_id}",
    status_code=204,
    summary="解绑设备",
    description="撤销指定设备的登录授权，并终止该设备的活跃会话。",
    responses={
        **COMMON_ERROR_RESPONSES,
        204: {"description": "No Content"},
    },
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def revoke_device(
    request: Request,
    device_id: UUID = Path(
        ...,
        description="设备 ID",
        example="1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e6f",
    ),
    device_fingerprint: str = Header(
        ...,
        alias="X-Device-Fingerprint",
        description="当前设备指纹，用于避免解绑自己",
        example="ios-4f3e9b2c",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """解绑设备并清理相关会话。"""
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
    await cache_service.invalidate_device(device_id)
    await cache_service.invalidate_sessions(current_user.id)
    return None


@router.get(
    "/sessions",
    response_model=list[ActiveSessionResponse],
    summary="获取活跃会话列表",
    description="返回当前用户的活跃登录会话。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def list_sessions(
    request: Request,
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取当前用户的活跃会话列表。"""
    cached_sessions = await cache_service.get_sessions(current_user.id)
    if isinstance(cached_sessions, list):
        return cached_sessions
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
    response = [
        {
            "id": str(session.id),
            "device_id": str(session.device_id) if session.device_id else None,
            "created_at": session.created_at.isoformat()
            if session.created_at
            else None,
            "expires_at": session.expires_at.isoformat()
            if session.expires_at
            else None,
        }
        for session in sessions
    ]
    await cache_service.set_sessions(current_user.id, response)
    return response


@router.delete(
    "/sessions/{session_id}",
    status_code=204,
    summary="终止单个会话",
    description="终止指定会话并使其立即失效。",
    responses={
        **COMMON_ERROR_RESPONSES,
        204: {"description": "No Content"},
    },
)
@limiter.limit(
    API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False
)
async def revoke_session(
    request: Request,
    session_id: UUID = Path(
        ...,
        description="会话 ID",
        example="5f1c9b3e-7c2a-4d1a-9a1d-0b8f7c5f2c10",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """终止指定活跃会话。"""
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
    await cache_service.invalidate_sessions(current_user.id)
    return None


@router.get(
    "/config/features",
    response_model=FeatureConfigResponse,
    summary="获取前端功能开关",
    description="返回前端需要的功能开关与版本信息。",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_features():
    """返回前端功能开关配置与版本信息。"""
    return {
        "payments_enabled": settings.payments_enabled,
        "beta_mode": settings.beta_mode,
        "app_version": settings.app_version,
    }
