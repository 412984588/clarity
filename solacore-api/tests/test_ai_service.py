"""Tests for AIService streaming helpers."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import app.services.ai_service as ai_module
import httpx
import pytest
from app.services.ai_service import AIService


class FakeStreamResponse:
    def __init__(self, lines: list[str]):
        self._lines = lines

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        return None

    async def aiter_lines(self):
        for line in self._lines:
            yield line


class FakeAsyncClient:
    def __init__(self, lines: list[str]):
        self._lines = lines

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def stream(self, method, url, headers=None, json=None):
        return FakeStreamResponse(self._lines)


def _make_settings(**overrides):
    defaults = {
        "llm_provider": "openai",
        "openai_api_key": "test-openai-key",
        "anthropic_api_key": "test-anthropic-key",
        "openrouter_api_key": "test-openrouter-key",
        "openrouter_base_url": "https://openrouter.ai/api/v1",
        "openrouter_app_name": "",
        "openrouter_referer": "",
        "openrouter_reasoning_fallback": False,
        "llm_model": "gpt-test",
        "llm_timeout": 1,
        "llm_max_tokens": 128,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


async def _collect(async_generator):
    return [item async for item in async_generator]


@pytest.fixture
def ai_settings():
    return _make_settings()


@pytest.fixture
def ai_service(ai_settings):
    with patch("app.services.ai_service.get_settings", return_value=ai_settings):
        service = AIService()
    return service


@pytest.mark.parametrize(
    ("provider", "method_name"),
    [
        ("openai", "_stream_openai"),
        ("anthropic", "_stream_anthropic"),
        ("openrouter", "_stream_openrouter"),
    ],
)
def test_get_stream_generator_routes(ai_service, provider, method_name, monkeypatch):
    sentinel = object()
    monkeypatch.setattr(ai_service, method_name, lambda *args, **kwargs: sentinel)
    ai_service.provider = provider
    assert ai_service._get_stream_generator("system", "user") is sentinel


def test_get_stream_generator_rejects_unknown_provider(ai_service):
    ai_service.provider = "unknown"
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        ai_service._get_stream_generator("system", "user")


@pytest.mark.asyncio
async def test_stream_retries_after_timeout(ai_service, monkeypatch):
    attempts = {"count": 0}

    async def flaky_generator():
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise httpx.TimeoutException("timeout")
        yield "ok"

    monkeypatch.setattr(
        ai_service, "_get_stream_generator", lambda *args, **kwargs: flaky_generator()
    )
    sleep_mock = AsyncMock()
    monkeypatch.setattr(ai_module.asyncio, "sleep", sleep_mock)

    result = await _collect(ai_service.stream("system", "user"))

    assert result == ["ok"]
    assert attempts["count"] == 2
    sleep_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_stream_openai_parses_content(ai_service, monkeypatch):
    ai_service.settings.openai_api_key = "test-openai-key"
    lines = [
        "event: ping",
        'data: {"choices":[{"delta":{"content":"Hello"}}]}',
        "data: {invalid",
        "data: [DONE]",
    ]
    monkeypatch.setattr(
        ai_module.httpx, "AsyncClient", lambda *args, **kwargs: FakeAsyncClient(lines)
    )

    result = await _collect(ai_service._stream_openai("system", "user"))

    assert result == ["Hello"]


@pytest.mark.asyncio
async def test_stream_openai_requires_api_key(ai_service):
    ai_service.settings.openai_api_key = ""
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        await _collect(ai_service._stream_openai("system", "user"))


@pytest.mark.asyncio
async def test_stream_openrouter_reasoning_fallback(ai_service, monkeypatch):
    ai_service.settings.openrouter_api_key = "test-openrouter-key"
    ai_service.settings.openrouter_base_url = "https://openrouter.ai/api/v1/"
    ai_service.settings.openrouter_reasoning_fallback = True
    ai_service.settings.enable_reasoning_output = True  # 必须开启才能输出 reasoning
    lines = [
        'data: {"choices":[{"delta":{"reasoning":"Think"}}]}',
        'data: {"choices":[{"delta":{"reasoning":"ing"}}]}',
        "data: [DONE]",
    ]
    monkeypatch.setattr(
        ai_module.httpx, "AsyncClient", lambda *args, **kwargs: FakeAsyncClient(lines)
    )

    result = await _collect(ai_service._stream_openrouter("system", "user"))

    assert result == ["Thinking"]


@pytest.mark.asyncio
async def test_stream_anthropic_parses_content(ai_service, monkeypatch):
    ai_service.settings.anthropic_api_key = "test-anthropic-key"
    lines = [
        'data: {"type":"content_block_delta","delta":{"text":"Hi"}}',
        'data: {"type":"message_stop"}',
    ]
    monkeypatch.setattr(
        ai_module.httpx, "AsyncClient", lambda *args, **kwargs: FakeAsyncClient(lines)
    )

    result = await _collect(ai_service._stream_anthropic("system", "user"))

    assert result == ["Hi"]
