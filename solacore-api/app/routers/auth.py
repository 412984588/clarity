from app.utils.datetime_utils import utc_now
from datetime import timedelta
import hashlib
import logging
import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, Request
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
    TokenResponse,
    RefreshRequest,
    OAuthRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.utils.security import decode_token, hash_password

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit(AUTH_RATE_LIMIT)
async def register(
    request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)
):
    """注册新用户"""
    service = AuthService(db)
    try:
        _, tokens = await service.register(data)
        return tokens
    except ValueError as e:
        error_code = str(e)
        if error_code == "EMAIL_ALREADY_EXISTS":
            raise HTTPException(status_code=409, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})


@router.post("/login", response_model=TokenResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def login(
    request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)
):
    """邮箱登录"""
    service = AuthService(db)
    try:
        _, tokens = await service.login(data)
        return tokens
    except ValueError as e:
        error_code = str(e)
        if error_code == "INVALID_CREDENTIALS":
            raise HTTPException(status_code=401, detail={"error": error_code})
        if error_code == "DEVICE_LIMIT_REACHED":
            raise HTTPException(status_code=403, detail={"error": error_code})
        if error_code == "DEVICE_BOUND_TO_OTHER":
            raise HTTPException(status_code=403, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})


@router.post("/beta-login", response_model=TokenResponse)
async def beta_login(
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
        user = User(
            email=beta_email,
            password_hash=hash_password(random_password),
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
        error_code = str(e)
        if error_code == "DEVICE_LIMIT_REACHED":
            raise HTTPException(status_code=403, detail={"error": error_code})
        if error_code == "DEVICE_BOUND_TO_OTHER":
            raise HTTPException(status_code=403, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})

    await db.commit()
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """刷新 access token"""
    service = AuthService(db)
    try:
        tokens = await service.refresh_token(data.refresh_token)
        return tokens
    except ValueError as e:
        error_code = str(e)
        if error_code == "INVALID_TOKEN":
            raise HTTPException(status_code=401, detail={"error": error_code})
        if error_code == "TOKEN_EXPIRED":
            raise HTTPException(status_code=401, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
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

    reset_token.user.password_hash = hash_password(data.new_password)  # type: ignore[assignment]
    reset_token.used_at = utc_now()  # type: ignore[assignment]

    await db.execute(
        delete(ActiveSession).where(ActiveSession.user_id == reset_token.user_id)
    )

    await db.commit()
    return {"message": "Password reset successful"}


@router.post("/logout", status_code=204)
async def logout(
    token: str | None = Header(None, alias="Authorization"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """登出 - 使当前 access token 对应 session 失效"""
    if not token:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1]

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    session_id = payload.get("sid")
    try:
        session_uuid = UUID(str(session_id))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail={"error": "SESSION_NOT_FOUND"})

    await db.execute(
        delete(ActiveSession).where(
            ActiveSession.id == session_uuid,
            ActiveSession.user_id == current_user.id,
        )
    )
    await db.commit()
    return None


@router.post("/oauth/google", response_model=TokenResponse)
async def google_oauth(data: OAuthRequest, db: AsyncSession = Depends(get_db)):
    """Google OAuth 登录"""
    service = OAuthService(db)
    try:
        user, tokens = await service.google_auth(data)
        return tokens
    except ValueError as e:
        error_code = str(e)
        if "GOOGLE_TOKEN_INVALID" in error_code:
            raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})
        if error_code == "EMAIL_NOT_VERIFIED":
            raise HTTPException(status_code=400, detail={"error": error_code})
        if error_code == "DEVICE_LIMIT_REACHED":
            raise HTTPException(status_code=403, detail={"error": error_code})
        if error_code == "DEVICE_BOUND_TO_OTHER":
            raise HTTPException(status_code=403, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})


@router.post("/oauth/apple", response_model=TokenResponse)
async def apple_oauth(data: OAuthRequest, db: AsyncSession = Depends(get_db)):
    """Apple Sign-in 登录"""
    service = OAuthService(db)
    try:
        user, tokens = await service.apple_auth(data)
        return tokens
    except ValueError as e:
        error_code = str(e)
        if "APPLE_TOKEN" in error_code:
            raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})
        if error_code == "OAUTH_ACCOUNT_NOT_LINKED":
            # Apple 后续登录但找不到用户记录
            raise HTTPException(status_code=400, detail={"error": error_code})
        if error_code == "DEVICE_LIMIT_REACHED":
            raise HTTPException(status_code=403, detail={"error": error_code})
        if error_code == "DEVICE_BOUND_TO_OTHER":
            raise HTTPException(status_code=403, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})


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
