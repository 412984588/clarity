"""认证路由辅助函数

提供通用的认证响应构造函数和 Cookie 设置函数
"""

from app.config import get_settings
from app.middleware.csrf import generate_csrf_token, set_csrf_cookies
from app.models.user import User
from app.schemas.auth import AuthSuccessResponse, UserResponse
from app.services.cache_service import CacheService
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

settings = get_settings()
cache_service = CacheService()


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
    """设置会话 cookies（包含认证 cookies 和 CSRF token）"""
    set_auth_cookies(response, access_token, refresh_token)
    set_csrf_cookies(response, generate_csrf_token())


async def create_auth_response(
    response: Response,
    user: User,
    tokens,
    db: AsyncSession | None = None,
) -> AuthSuccessResponse:
    """统一的认证响应构造函数（Web cookie + Mobile token 双模式）"""
    set_session_cookies(response, tokens.access_token, tokens.refresh_token)
    await cache_service.invalidate_sessions(user.id)

    return AuthSuccessResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            auth_provider=user.auth_provider,
            locale=user.locale,
        ),
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        user_id=user.id,
    )
