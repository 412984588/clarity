from __future__ import annotations

import logging
import re
from typing import Any, Iterable

from fastapi import FastAPI, Request
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.config import Settings
from app.utils.security import decode_token

_REDACTED = "***REDACTED***"
_SENSITIVE_KEYS = {
    "password",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "cookie",
    "set-cookie",
    "secret",
    "api_key",
    "apikey",
}
_JWT_PATTERN = re.compile(
    r"eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*"
)
_BEARER_PATTERN = re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.IGNORECASE)


def _scrub_string(value: str) -> str:
    value = _JWT_PATTERN.sub("***JWT_REDACTED***", value)
    return _BEARER_PATTERN.sub("Bearer ***REDACTED***", value)


def _scrub_sequence(seq: Iterable[Any]) -> Any:
    items: list[Any] = []
    for item in seq:
        if (
            isinstance(item, (list, tuple))
            and len(item) == 2
            and isinstance(item[0], str)
        ):
            key = item[0]
            if key.lower() in _SENSITIVE_KEYS:
                items.append((key, _REDACTED))
                continue
        items.append(_scrub_value(item))
    return tuple(items) if isinstance(seq, tuple) else items


def _scrub_mapping(data: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in _SENSITIVE_KEYS:
            cleaned[key] = _REDACTED
        else:
            cleaned[key] = _scrub_value(value)
    return cleaned


def _scrub_value(value: Any) -> Any:
    if isinstance(value, dict):
        return _scrub_mapping(value)
    if isinstance(value, list):
        return _scrub_sequence(value)
    if isinstance(value, tuple):
        return _scrub_sequence(value)
    if isinstance(value, str):
        return _scrub_string(value)
    return value


def _before_send(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any]:
    return _scrub_mapping(event)


def _before_breadcrumb(
    crumb: dict[str, Any], hint: dict[str, Any]
) -> dict[str, Any] | None:
    if not crumb:
        return crumb
    return _scrub_mapping(crumb)


def _extract_user_id(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization") or request.headers.get(
            "authorization"
        )
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


def _sentry_enabled(settings: Settings) -> bool:
    return bool(settings.sentry_dsn.strip()) and not settings.debug


def setup_sentry(app: FastAPI, settings: Settings) -> None:
    if not _sentry_enabled(settings):
        return

    logging_integration = LoggingIntegration(
        level=logging.INFO, event_level=logging.ERROR
    )

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        release=settings.app_version,
        sample_rate=1.0,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        integrations=[FastApiIntegration(), logging_integration],
        before_send=_before_send,
        before_breadcrumb=_before_breadcrumb,
        send_default_pii=False,
    )

    sentry_sdk.set_tag("environment", settings.sentry_environment)
    sentry_sdk.set_tag("version", settings.app_version)

    @app.middleware("http")
    async def sentry_context_middleware(request: Request, call_next):
        with sentry_sdk.configure_scope() as scope:
            user_id = _extract_user_id(request)
            if user_id:
                scope.set_tag("user_id", user_id)
                scope.set_user({"id": user_id})
        return await call_next(request)

    app.add_middleware(SentryAsgiMiddleware)
