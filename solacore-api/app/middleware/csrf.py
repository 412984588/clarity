import re
import secrets
from typing import Iterable

from app.config import get_settings
from fastapi import HTTPException, Request, Response, status

CSRF_COOKIE_NAME = "csrf_token"
CSRF_COOKIE_HTTP_ONLY_NAME = "csrf_token_http"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_MAX_AGE = 30 * 24 * 3600

CSRF_PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
CSRF_EXEMPT_PATHS = {
    "/auth/register",
    "/auth/login",
    "/auth/beta-login",
    "/auth/refresh",  # Refresh token使用httpOnly cookie，不易受CSRF攻击
    "/auth/forgot-password",
    "/auth/reset-password",
    "/auth/oauth/google",
    "/auth/oauth/google/code",
    "/auth/oauth/apple",
}
CSRF_EXEMPT_PREFIXES = ("/webhooks",)
# SSE endpoint 需要豁免CSRF，因为EventSource无法发送自定义header
# 使用正则匹配具体路径模式，避免过度豁免
CSRF_EXEMPT_PATTERNS = (
    re.compile(
        r"^/sessions/[a-f0-9\-]{36}/messages$"
    ),  # POST /sessions/{uuid}/messages
)


def _normalize_path(path: str) -> str:
    normalized = path.rstrip("/")
    return normalized if normalized else "/"


def _is_exempt_path(path: str) -> bool:
    normalized = _normalize_path(path)
    if normalized in CSRF_EXEMPT_PATHS:
        return True
    if any(normalized.startswith(prefix) for prefix in CSRF_EXEMPT_PREFIXES):
        return True
    return any(pattern.match(normalized) for pattern in CSRF_EXEMPT_PATTERNS)


def _cookie_params(httponly: bool) -> dict:
    settings = get_settings()
    params: dict[str, object] = {
        "httponly": httponly,
        "secure": not settings.debug,
        "samesite": "lax",
    }
    if settings.cookie_domain:
        params["domain"] = settings.cookie_domain
    return params


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def set_csrf_cookies(response: Response, token: str) -> None:
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        max_age=CSRF_COOKIE_MAX_AGE,
        **_cookie_params(httponly=False),
    )
    response.set_cookie(
        key=CSRF_COOKIE_HTTP_ONLY_NAME,
        value=token,
        max_age=CSRF_COOKIE_MAX_AGE,
        **_cookie_params(httponly=True),
    )


def clear_csrf_cookies(response: Response) -> None:
    response.delete_cookie(CSRF_COOKIE_NAME, **_cookie_params(httponly=False))
    response.delete_cookie(CSRF_COOKIE_HTTP_ONLY_NAME, **_cookie_params(httponly=True))


def validate_csrf(
    request: Request,
    *,
    exempt_paths: Iterable[str] | None = None,
    exempt_prefixes: Iterable[str] | None = None,
) -> None:
    if request.method not in CSRF_PROTECTED_METHODS:
        return

    path = request.url.path
    exempt_paths_set = set(exempt_paths) if exempt_paths is not None else None
    exempt_prefixes_seq = (
        tuple(exempt_prefixes) if exempt_prefixes is not None else None
    )

    if exempt_paths_set is not None or exempt_prefixes_seq is not None:
        normalized = _normalize_path(path)
        if exempt_paths_set and normalized in exempt_paths_set:
            return
        if exempt_prefixes_seq and any(
            normalized.startswith(prefix) for prefix in exempt_prefixes_seq
        ):
            return
    else:
        if _is_exempt_path(path):
            return

    header_token = request.headers.get(CSRF_HEADER_NAME)
    csrf_token = request.cookies.get(CSRF_COOKIE_NAME)
    csrf_http_token = request.cookies.get(CSRF_COOKIE_HTTP_ONLY_NAME)

    if not header_token or not csrf_token or not csrf_http_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "CSRF_TOKEN_MISSING"},
        )

    if not secrets.compare_digest(
        header_token, csrf_token
    ) or not secrets.compare_digest(header_token, csrf_http_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "CSRF_TOKEN_INVALID"},
        )
