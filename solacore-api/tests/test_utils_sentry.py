from __future__ import annotations

from unittest.mock import patch

from app.config import Settings
from app.utils import sentry as sentry_utils
from fastapi import FastAPI
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
        "client": ("127.0.0.1", 1234),
    }
    if headers:
        scope["headers"].extend(
            [(key.lower().encode(), value.encode()) for key, value in headers.items()]
        )
    if cookies:
        cookie_value = "; ".join(f"{key}={value}" for key, value in cookies.items())
        scope["headers"].append((b"cookie", cookie_value.encode()))
    return Request(scope, receive=_receive)


def test_scrub_string_redacts_tokens() -> None:
    value = "Bearer abc.def.ghi eyJabc.def.ghi"
    scrubbed = sentry_utils._scrub_string(value)
    assert "Bearer ***REDACTED***" in scrubbed
    assert "***JWT_REDACTED***" in scrubbed


def test_scrub_sequence_redacts_sensitive_keys() -> None:
    payload = [
        ("password", "secret"),
        ("ok", "Bearer token"),
        "eyJabc.def.ghi",
    ]
    scrubbed = sentry_utils._scrub_sequence(payload)
    assert scrubbed[0] == ("password", sentry_utils._REDACTED)
    assert "Bearer ***REDACTED***" in scrubbed[1][1]
    assert "***JWT_REDACTED***" in scrubbed[2]


def test_scrub_sequence_returns_tuple_for_tuple() -> None:
    payload = (("token", "secret"), "safe")
    scrubbed = sentry_utils._scrub_sequence(payload)
    assert isinstance(scrubbed, tuple)
    assert scrubbed[0] == ("token", sentry_utils._REDACTED)


def test_scrub_mapping_recurses() -> None:
    payload = {
        "token": "secret",
        "nested": {"access_token": "abc"},
        "list": [("authorization", "Bearer token")],
    }
    scrubbed = sentry_utils._scrub_mapping(payload)
    assert scrubbed["token"] == sentry_utils._REDACTED
    assert scrubbed["nested"]["access_token"] == sentry_utils._REDACTED
    assert scrubbed["list"][0] == ("authorization", sentry_utils._REDACTED)


def test_before_breadcrumb_handles_empty() -> None:
    assert sentry_utils._before_breadcrumb({}, {}) == {}
    assert sentry_utils._before_breadcrumb(None, {}) is None


def test_before_send_scrubs_event() -> None:
    event = {"token": "secret", "message": "ok"}
    result = sentry_utils._before_send(event, {})
    assert result["token"] == sentry_utils._REDACTED


def test_extract_user_id_from_cookie() -> None:
    request = _make_request(cookies={"access_token": "token"})
    with patch(
        "app.utils.sentry.decode_token",
        return_value={"type": "access", "sub": "user-1"},
    ):
        assert sentry_utils._extract_user_id(request) == "user-1"


def test_extract_user_id_from_header_and_invalid_payload() -> None:
    request = _make_request(headers={"Authorization": "Bearer token"})
    with patch(
        "app.utils.sentry.decode_token",
        return_value={"type": "refresh", "sub": "user-1"},
    ):
        assert sentry_utils._extract_user_id(request) is None


def test_extract_user_id_without_token() -> None:
    request = _make_request()
    assert sentry_utils._extract_user_id(request) is None


def test_sentry_enabled_checks_debug_and_dsn() -> None:
    settings = Settings(sentry_dsn="", debug=False)
    assert sentry_utils._sentry_enabled(settings) is False
    settings = Settings(sentry_dsn="https://example", debug=True)
    assert sentry_utils._sentry_enabled(settings) is False
    settings = Settings(sentry_dsn="https://example", debug=False)
    assert sentry_utils._sentry_enabled(settings) is True


def test_setup_sentry_skips_when_disabled() -> None:
    app = FastAPI()
    settings = Settings(sentry_dsn="", debug=False)
    with patch("app.utils.sentry.sentry_sdk.init") as init_mock:
        sentry_utils.setup_sentry(app, settings)
    init_mock.assert_not_called()


def test_setup_sentry_registers_middleware() -> None:
    app = FastAPI()
    settings = Settings(sentry_dsn="https://example", debug=False)
    with (
        patch("app.utils.sentry.sentry_sdk.init") as init_mock,
        patch("app.utils.sentry.sentry_sdk.set_tag") as set_tag_mock,
    ):
        sentry_utils.setup_sentry(app, settings)

    init_mock.assert_called_once()
    assert set_tag_mock.call_count == 2
    assert any(
        middleware.cls.__name__ == "SentryAsgiMiddleware"
        for middleware in app.user_middleware
    )
