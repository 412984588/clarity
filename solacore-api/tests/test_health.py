from __future__ import annotations

import asyncio
import builtins
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from app.utils import health as health_module


def _make_settings(**overrides) -> SimpleNamespace:
    defaults = {
        "redis_url": "redis://localhost:6379/0",
        "llm_provider": "openai",
        "openai_api_key": "key",
        "anthropic_api_key": "",
        "openrouter_api_key": "",
        "openrouter_base_url": "https://openrouter.ai/api/v1",
        "openrouter_referer": "",
        "openrouter_app_name": "",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_iso_timestamp_and_latency(monkeypatch) -> None:
    ts = health_module._iso_timestamp()
    assert ts

    monkeypatch.setattr(health_module.time, "monotonic", lambda: 10.5)
    assert health_module._latency_ms(10.0) == 500


@pytest.mark.asyncio
async def test_run_check_handles_outcomes() -> None:
    async def ok():
        return {"status": "up"}

    async def timeout():
        raise asyncio.TimeoutError()

    async def boom():
        raise RuntimeError("boom")

    name, result = await health_module._run_check("ok", ok)
    assert name == "ok"
    assert result == {"status": "up"}

    name, result = await health_module._run_check("timeout", timeout)
    assert result == {"status": "down", "error": "timeout"}

    name, result = await health_module._run_check("boom", boom)
    assert result == {"status": "down", "error": "exception"}


@pytest.mark.asyncio
async def test_check_database_up_and_down(monkeypatch) -> None:
    @asynccontextmanager
    async def ok_session():
        session = AsyncMock()
        session.execute = AsyncMock()
        yield session

    monkeypatch.setattr(health_module, "AsyncSessionLocal", lambda: ok_session())
    result = await health_module._check_database()
    assert result["status"] == "up"

    @asynccontextmanager
    async def bad_session():
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=Exception("boom"))
        yield session

    monkeypatch.setattr(health_module, "AsyncSessionLocal", lambda: bad_session())
    result = await health_module._check_database()
    assert result["status"] == "down"


@pytest.mark.asyncio
async def test_check_redis_missing_url(monkeypatch) -> None:
    monkeypatch.setattr(
        health_module, "get_settings", lambda: _make_settings(redis_url="")
    )
    result = await health_module._check_redis()
    assert result == {"status": "down", "error": "missing_url"}


@pytest.mark.asyncio
async def test_check_redis_up_and_down(monkeypatch) -> None:
    monkeypatch.setattr(health_module, "get_settings", lambda: _make_settings())

    client = AsyncMock()
    client.ping = AsyncMock()
    client.close = AsyncMock()
    client.connection_pool.disconnect = AsyncMock()

    with patch("app.utils.health.Redis.from_url", return_value=client):
        result = await health_module._check_redis()

    assert result["status"] == "up"
    client.close.assert_awaited_once()
    client.connection_pool.disconnect.assert_awaited_once()

    client = AsyncMock()
    client.ping = AsyncMock(side_effect=Exception("boom"))
    client.close = AsyncMock()
    client.connection_pool.disconnect = AsyncMock()

    with patch("app.utils.health.Redis.from_url", return_value=client):
        result = await health_module._check_redis()

    assert result["status"] == "down"


@pytest.mark.asyncio
async def test_check_disk_and_memory(monkeypatch) -> None:
    usage = SimpleNamespace(total=100, used=20)
    monkeypatch.setattr(health_module.shutil, "disk_usage", lambda _: usage)
    result = await health_module._check_disk()
    assert result["status"] == "up"

    usage = SimpleNamespace(total=100, used=95)
    monkeypatch.setattr(health_module.shutil, "disk_usage", lambda _: usage)
    result = await health_module._check_disk()
    assert result["status"] == "down"

    monkeypatch.setattr(health_module, "_memory_usage_percent", lambda: None)
    result = await health_module._check_memory()
    assert result == {"status": "down", "error": "unavailable"}

    monkeypatch.setattr(health_module, "_memory_usage_percent", lambda: 20.0)
    result = await health_module._check_memory()
    assert result["status"] == "up"

    monkeypatch.setattr(health_module, "_memory_usage_percent", lambda: 95.0)
    result = await health_module._check_memory()
    assert result["status"] == "down"


def test_memory_usage_percent_with_psutil(monkeypatch) -> None:
    class DummyPsutil:
        @staticmethod
        def virtual_memory():
            return SimpleNamespace(percent=25.5)

    monkeypatch.setitem(__import__("sys").modules, "psutil", DummyPsutil)
    assert health_module._memory_usage_percent() == 25.5


def test_memory_usage_percent_with_sysconf(monkeypatch) -> None:
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "psutil":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    def fake_sysconf(name: str):
        values = {
            "SC_PAGE_SIZE": 1,
            "SC_PHYS_PAGES": 100,
            "SC_AVPHYS_PAGES": 25,
        }
        return values[name]

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(health_module.os, "sysconf", fake_sysconf)
    assert health_module._memory_usage_percent() == 75.0


def test_should_check_external_api(monkeypatch) -> None:
    monkeypatch.setattr(
        health_module,
        "get_settings",
        lambda: _make_settings(llm_provider="openai", openai_api_key=""),
    )
    assert health_module._should_check_external_api() is False

    monkeypatch.setattr(
        health_module,
        "get_settings",
        lambda: _make_settings(llm_provider="anthropic", anthropic_api_key="key"),
    )
    assert health_module._should_check_external_api() is True

    monkeypatch.setattr(
        health_module,
        "get_settings",
        lambda: _make_settings(llm_provider="other", openrouter_api_key="key"),
    )
    assert health_module._should_check_external_api() is True


@pytest.mark.asyncio
async def test_check_external_api_openai_paths(monkeypatch) -> None:
    monkeypatch.setattr(
        health_module, "get_settings", lambda: _make_settings(openai_api_key="")
    )
    result = await health_module._check_external_api()
    assert result["status"] == "skipped"

    monkeypatch.setattr(
        health_module, "get_settings", lambda: _make_settings(openai_api_key="key")
    )

    success_response = MagicMock()
    success_response.status_code = 200
    with patch("app.utils.health.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock()
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=success_response
        )
        result = await health_module._check_external_api()

    assert result["status"] == "up"

    failure_response = MagicMock()
    failure_response.status_code = 500
    with patch("app.utils.health.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock()
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=failure_response
        )
        result = await health_module._check_external_api()

    assert result["status"] == "down"
    assert result["status_code"] == 500

    with patch("app.utils.health.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock()
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.HTTPError("boom")
        )
        result = await health_module._check_external_api()

    assert result["status"] == "down"


@pytest.mark.asyncio
async def test_check_external_api_openrouter(monkeypatch) -> None:
    settings = _make_settings(
        llm_provider="other",
        openrouter_api_key="key",
        openrouter_base_url="https://openrouter.ai/api/v1",
    )
    monkeypatch.setattr(health_module, "get_settings", lambda: settings)

    response = MagicMock()
    response.status_code = 200
    with patch("app.utils.health.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock()
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=response
        )
        result = await health_module._check_external_api()

    assert result["provider"] == "openrouter"
    assert result["status"] == "up"


@pytest.mark.asyncio
async def test_build_readiness_report_statuses(monkeypatch) -> None:
    async def make_check(status: str):
        async def _check():
            return {"status": status}

        return _check

    monkeypatch.setattr(health_module, "_check_database", await make_check("up"))
    monkeypatch.setattr(health_module, "_check_redis", await make_check("up"))
    monkeypatch.setattr(health_module, "_check_disk", await make_check("up"))
    monkeypatch.setattr(health_module, "_check_memory", await make_check("up"))
    monkeypatch.setattr(health_module, "_should_check_external_api", lambda: True)
    monkeypatch.setattr(
        health_module, "_check_external_api", await make_check("skipped")
    )

    report = await health_module._build_readiness_report()
    assert report["status"] == "healthy"

    monkeypatch.setattr(health_module, "_check_external_api", await make_check("down"))
    report = await health_module._build_readiness_report()
    assert report["status"] == "degraded"

    monkeypatch.setattr(health_module, "_check_database", await make_check("down"))
    report = await health_module._build_readiness_report()
    assert report["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_get_readiness_report_uses_cache(monkeypatch) -> None:
    report = {"status": "healthy"}
    build_mock = AsyncMock(return_value=report)
    monkeypatch.setattr(health_module, "_build_readiness_report", build_mock)
    monkeypatch.setattr(
        health_module, "_ready_cache", {"timestamp": 0.0, "report": None}
    )
    monkeypatch.setattr(health_module.time, "monotonic", lambda: 100.0)

    result1 = await health_module.get_readiness_report()
    result2 = await health_module.get_readiness_report()

    assert result1 is report
    assert result2 is report
    assert build_mock.await_count == 1


@pytest.mark.asyncio
async def test_get_liveness_report() -> None:
    report = await health_module.get_liveness_report()
    assert report["status"] == "healthy"
    assert report["checks"]["service"]["status"] == "up"


@pytest.mark.asyncio
async def test_get_active_session_counts(monkeypatch) -> None:
    result_obj = MagicMock()
    result_obj.scalar_one.return_value = 3

    @asynccontextmanager
    async def ok_session():
        session = AsyncMock()
        session.execute = AsyncMock(return_value=result_obj)
        yield session

    monkeypatch.setattr(health_module, "AsyncSessionLocal", lambda: ok_session())
    assert await health_module.get_active_sessions_count() == 3
    assert await health_module.get_active_users_count() == 3

    @asynccontextmanager
    async def bad_session():
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=Exception("boom"))
        yield session

    monkeypatch.setattr(health_module, "AsyncSessionLocal", lambda: bad_session())
    assert await health_module.get_active_sessions_count() == -1
    assert await health_module.get_active_users_count() == -1
