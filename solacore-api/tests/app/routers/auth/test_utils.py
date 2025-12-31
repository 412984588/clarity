import types
from dataclasses import dataclass
from uuid import uuid4

import asyncio
import pytest
from fastapi import Response
from unittest.mock import AsyncMock

from app.models.user import User
from app.routers.auth import utils as auth_utils


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str


def _set_settings(monkeypatch, *, debug: bool, cookie_domain: str) -> None:
    settings = types.SimpleNamespace(debug=debug, cookie_domain=cookie_domain)
    monkeypatch.setattr(auth_utils, "settings", settings)


def test_set_auth_cookies_sets_expected_flags(monkeypatch):
    # Arrange
    _set_settings(monkeypatch, debug=False, cookie_domain="")
    response = Response()

    # Act
    auth_utils.set_auth_cookies(response, "access-123", "refresh-456")

    # Assert
    cookies = response.headers.getlist("set-cookie")
    assert len(cookies) == 2
    assert any("access_token=access-123" in cookie for cookie in cookies)
    assert any("refresh_token=refresh-456" in cookie for cookie in cookies)
    for cookie in cookies:
        assert "HttpOnly" in cookie
        assert "SameSite=lax" in cookie
        assert "Secure" in cookie
        assert "Domain=" not in cookie


def test_set_auth_cookies_includes_domain_when_configured(monkeypatch):
    # Arrange
    _set_settings(monkeypatch, debug=False, cookie_domain=".example.com")
    response = Response()

    # Act
    auth_utils.set_auth_cookies(response, "access-123", "refresh-456")

    # Assert
    cookies = response.headers.getlist("set-cookie")
    assert any("Domain=.example.com" in cookie for cookie in cookies)


def test_set_session_cookies_sets_auth_and_csrf(monkeypatch):
    # Arrange
    response = Response()
    calls = {"auth": None, "csrf": None}

    def fake_set_auth_cookies(resp, access_token, refresh_token):
        calls["auth"] = (resp, access_token, refresh_token)

    def fake_set_csrf_cookies(resp, token):
        calls["csrf"] = (resp, token)

    monkeypatch.setattr(auth_utils, "set_auth_cookies", fake_set_auth_cookies)
    monkeypatch.setattr(auth_utils, "set_csrf_cookies", fake_set_csrf_cookies)
    monkeypatch.setattr(auth_utils, "generate_csrf_token", lambda: "csrf-123")

    # Act
    auth_utils.set_session_cookies(response, "access-123", "refresh-456")

    # Assert
    assert calls["auth"] == (response, "access-123", "refresh-456")
    assert calls["csrf"] == (response, "csrf-123")


def test_create_auth_response_sets_cookies_and_invalidates_cache(monkeypatch):
    # Arrange
    response = Response()
    user = User(
        id=uuid4(),
        email="test@example.com",
        auth_provider="email",
        locale="en",
    )
    tokens = TokenPair(access_token="access-123", refresh_token="refresh-456")

    set_cookies_calls = []

    def fake_set_session_cookies(resp, access_token, refresh_token):
        set_cookies_calls.append((resp, access_token, refresh_token))

    monkeypatch.setattr(auth_utils, "set_session_cookies", fake_set_session_cookies)
    monkeypatch.setattr(
        auth_utils.cache_service,
        "invalidate_sessions",
        AsyncMock(),
    )

    # Act
    result = asyncio.run(auth_utils.create_auth_response(response, user, tokens))

    # Assert
    assert set_cookies_calls == [(response, "access-123", "refresh-456")]
    auth_utils.cache_service.invalidate_sessions.assert_awaited_once_with(user.id)
    assert result.user.id == user.id
    assert result.user.email == "test@example.com"
    assert result.user.auth_provider == "email"
    assert result.user.locale == "en"
