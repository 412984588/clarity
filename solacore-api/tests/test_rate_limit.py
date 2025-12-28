from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from app.middleware import rate_limit as rate_limit_module
from starlette.requests import Request


async def _receive() -> dict:
    return {"type": "http.request", "body": b"", "more_body": False}


def _make_request(
    *, headers: dict[str, str] | None = None, cookies: dict[str, str] | None = None
) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 5678),
    }
    if headers:
        scope["headers"].extend(
            [(key.lower().encode(), value.encode()) for key, value in headers.items()]
        )
    if cookies:
        cookie_value = "; ".join(f"{key}={value}" for key, value in cookies.items())
        scope["headers"].append((b"cookie", cookie_value.encode()))
    return Request(scope, receive=_receive)


def test_parse_ip_whitelist_strips_and_filters() -> None:
    result = rate_limit_module._parse_ip_whitelist(" 1.1.1.1, ,2.2.2.2 ,")
    assert result == {"1.1.1.1", "2.2.2.2"}


def test_is_request_whitelisted_checks_context(monkeypatch) -> None:
    monkeypatch.setattr(rate_limit_module, "_rate_limit_ip_whitelist", {"1.1.1.1"})
    token = rate_limit_module._request_ip_ctx.set("1.1.1.1")
    try:
        assert rate_limit_module._is_request_whitelisted() is True
    finally:
        rate_limit_module._request_ip_ctx.reset(token)

    token = rate_limit_module._request_ip_ctx.set("2.2.2.2")
    try:
        assert rate_limit_module._is_request_whitelisted() is False
    finally:
        rate_limit_module._request_ip_ctx.reset(token)


@pytest.mark.asyncio
async def test_rate_limit_context_middleware_sets_and_resets() -> None:
    captured = {}

    async def app(scope, receive, send):
        captured["ip"] = rate_limit_module._request_ip_ctx.get()
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"", "more_body": False})

    middleware = rate_limit_module.RateLimitContextMiddleware(app)

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        return None

    with patch("app.middleware.rate_limit.get_remote_address", return_value="9.9.9.9"):
        await middleware(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "query_string": b"",
                "headers": [],
                "client": ("9.9.9.9", 1234),
            },
            receive,
            send,
        )

    assert captured["ip"] == "9.9.9.9"
    assert rate_limit_module._request_ip_ctx.get() is None


@pytest.mark.asyncio
async def test_rate_limit_context_middleware_skips_non_http() -> None:
    called = {"value": False}

    async def app(scope, receive, send):
        called["value"] = True

    middleware = rate_limit_module.RateLimitContextMiddleware(app)

    async def receive():
        return {"type": "websocket.connect"}

    async def send(message):
        return None

    await middleware({"type": "websocket"}, receive, send)
    assert called["value"] is True


def test_extract_user_id_prefers_request_state() -> None:
    request = _make_request()
    request.state.current_user = SimpleNamespace(id="user-1")
    with patch("app.middleware.rate_limit.decode_token") as decode_mock:
        assert rate_limit_module._extract_user_id(request) == "user-1"
    decode_mock.assert_not_called()


def test_extract_user_id_from_cookie_and_header() -> None:
    request = _make_request(cookies={"access_token": "token"})
    with patch(
        "app.middleware.rate_limit.decode_token",
        return_value={"type": "access", "sub": "user-2"},
    ):
        assert rate_limit_module._extract_user_id(request) == "user-2"

    request = _make_request(headers={"Authorization": "Bearer token"})
    with patch(
        "app.middleware.rate_limit.decode_token",
        return_value={"type": "access", "sub": "user-3"},
    ):
        assert rate_limit_module._extract_user_id(request) == "user-3"


def test_extract_user_id_invalid_token() -> None:
    request = _make_request(headers={"Authorization": "token"})
    with patch(
        "app.middleware.rate_limit.decode_token",
        return_value={"type": "refresh", "sub": "user"},
    ):
        assert rate_limit_module._extract_user_id(request) is None


def test_ip_rate_limit_key_uses_remote_address() -> None:
    request = _make_request()
    with patch("app.middleware.rate_limit.get_remote_address", return_value="1.2.3.4"):
        assert rate_limit_module.ip_rate_limit_key(request) == "1.2.3.4"


def test_user_rate_limit_key_prefers_user() -> None:
    request = _make_request()
    with patch("app.middleware.rate_limit._extract_user_id", return_value="user-5"):
        assert rate_limit_module.user_rate_limit_key(request) == "user:user-5"

    with (
        patch("app.middleware.rate_limit._extract_user_id", return_value=None),
        patch("app.middleware.rate_limit.get_remote_address", return_value="5.6.7.8"),
    ):
        assert rate_limit_module.user_rate_limit_key(request) == "5.6.7.8"
