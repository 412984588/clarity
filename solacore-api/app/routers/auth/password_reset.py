"""密码重置端点

提供忘记密码和重置密码功能
"""

import hashlib
import secrets
from datetime import timedelta

from app.config import get_settings
from app.database import get_db
from app.logging_config import get_logger
from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    FORGOT_PASSWORD_RATE_LIMIT,
    ip_rate_limit_key,
    limiter,
)
from app.models.password_reset import PasswordResetToken
from app.models.session import ActiveSession
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    StatusMessageResponse,
)
from app.services.cache_service import CacheService
from app.services.email_service import send_password_reset_email
from app.utils.datetime_utils import utc_now
from app.utils.docs import COMMON_ERROR_RESPONSES
from app.utils.security import hash_password_async
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = get_logger(__name__)
settings = get_settings()
cache_service = CacheService()

router = APIRouter()


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
    response: Response,
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
                "application/json": {
                    "example": {"message": "Password reset successful"}
                }
            },
        },
    },
)
@limiter.limit(API_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False)
async def reset_password(
    request: Request,
    response: Response,
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
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
