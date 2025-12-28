"""Rate limiting configuration and helpers."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

from app.config import get_settings
from app.utils.security import decode_token
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.types import ASGIApp, Receive, Scope, Send

settings = get_settings()


def _parse_ip_whitelist(raw: str) -> set[str]:
    return {item.strip() for item in raw.split(",") if item.strip()}


_rate_limit_ip_whitelist = _parse_ip_whitelist(settings.rate_limit_ip_whitelist)
_request_ip_ctx: ContextVar[Optional[str]] = ContextVar(
    "rate_limit_request_ip", default=None
)


def _is_request_whitelisted() -> bool:
    ip = _request_ip_ctx.get()
    return bool(ip and ip in _rate_limit_ip_whitelist)


class RateLimitContextMiddleware:
    """Capture request IP for whitelist checks in slowapi filters."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        token = _request_ip_ctx.set(get_remote_address(request))
        try:
            await self.app(scope, receive, send)
        finally:
            _request_ip_ctx.reset(token)


def _extract_user_id(request: Request) -> Optional[str]:
    cached_user = getattr(request.state, "current_user", None)
    if cached_user is not None:
        user_id = getattr(cached_user, "id", None)
        if user_id:
            return str(user_id)

    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = (
                auth_header.split(" ", 1)[1]
                if auth_header.startswith("Bearer ")
                else auth_header
            )

    if not token:
        return None

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    return str(user_id) if user_id else None


def ip_rate_limit_key(request: Request) -> str:
    """IP-based rate limit key."""
    return get_remote_address(request)


def user_rate_limit_key(request: Request) -> str:
    """User-first rate limit key with IP fallback."""
    user_id = _extract_user_id(request)
    if user_id:
        return f"user:{user_id}"
    return get_remote_address(request)


GLOBAL_RATE_LIMIT = settings.rate_limit_global
AUTH_RATE_LIMIT = settings.rate_limit_auth
OAUTH_RATE_LIMIT = settings.rate_limit_oauth
FORGOT_PASSWORD_RATE_LIMIT = settings.rate_limit_forgot_password
API_RATE_LIMIT = settings.rate_limit_api
SSE_RATE_LIMIT = settings.rate_limit_sse

_storage_uri = settings.rate_limit_redis_url or settings.redis_url

limiter = Limiter(
    key_func=ip_rate_limit_key,
    default_limits=[GLOBAL_RATE_LIMIT],
    headers_enabled=True,
    storage_uri=_storage_uri,
    in_memory_fallback_enabled=True,
)

# Whitelisted IPs bypass rate limiting checks entirely.
limiter._request_filters.append(_is_request_whitelisted)
