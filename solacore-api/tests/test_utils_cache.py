from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from redis.exceptions import RedisError

from app.utils import cache as cache_module


def _make_cache(client: AsyncMock | None) -> cache_module.RedisCache:
    instance = cache_module.RedisCache.__new__(cache_module.RedisCache)
    instance._client = client
    instance._pool = None
    instance._enabled = True
    return instance


def test_default_serializer_uses_isoformat() -> None:
    value = datetime(2024, 1, 1)
    assert cache_module._default_serializer(value) == value.isoformat()


def test_default_serializer_fallback() -> None:
    value = SimpleNamespace(value=1)
    assert cache_module._default_serializer(value) == str(value)


@pytest.mark.asyncio
async def test_get_returns_none_without_client() -> None:
    cache = _make_cache(None)
    assert await cache.get("missing") is None


@pytest.mark.asyncio
async def test_no_client_noops() -> None:
    cache = _make_cache(None)
    await cache.set("key", "value")
    await cache.delete("key")
    await cache.invalidate("pattern")
    await cache.close()


@pytest.mark.asyncio
async def test_get_cache_hit_records_metrics(monkeypatch) -> None:
    client = AsyncMock()
    client.get = AsyncMock(return_value='{"ok": true}')
    cache = _make_cache(client)

    record_hit = MagicMock()
    record_miss = MagicMock()
    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_cache_hit", record_hit)
    monkeypatch.setattr(cache_module.metrics, "record_cache_miss", record_miss)
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    result = await cache.get("key")

    assert result == {"ok": True}
    client.get.assert_awaited_once_with("key")
    record_hit.assert_called_once()
    record_miss.assert_not_called()
    assert record_cmd.call_args.kwargs["command"] == "get"


@pytest.mark.asyncio
async def test_get_cache_miss_on_none(monkeypatch) -> None:
    client = AsyncMock()
    client.get = AsyncMock(return_value=None)
    cache = _make_cache(client)

    record_miss = MagicMock()
    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_cache_miss", record_miss)
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    assert await cache.get("key") is None
    record_miss.assert_called_once()
    assert record_cmd.call_args.kwargs["command"] == "get"


@pytest.mark.asyncio
async def test_get_cache_miss_on_bad_json(monkeypatch) -> None:
    client = AsyncMock()
    client.get = AsyncMock(return_value="not-json")
    cache = _make_cache(client)

    record_miss = MagicMock()
    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_cache_miss", record_miss)
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    assert await cache.get("key") is None
    record_miss.assert_called_once()
    assert record_cmd.call_args.kwargs["command"] == "get"


@pytest.mark.asyncio
async def test_get_handles_redis_error(monkeypatch) -> None:
    client = AsyncMock()
    client.get = AsyncMock(side_effect=RedisError("boom"))
    cache = _make_cache(client)

    record_miss = MagicMock()
    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_cache_miss", record_miss)
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    assert await cache.get("key") is None
    record_miss.assert_called_once()
    assert record_cmd.call_args.kwargs["command"] == "get"


@pytest.mark.asyncio
async def test_set_serializes_and_records(monkeypatch) -> None:
    client = AsyncMock()
    client.set = AsyncMock()
    cache = _make_cache(client)

    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    await cache.set("key", {"value": 1}, ttl=30)
    client.set.assert_awaited_once()
    assert record_cmd.call_args.kwargs["command"] == "set"


@pytest.mark.asyncio
async def test_set_handles_redis_error(monkeypatch) -> None:
    client = AsyncMock()
    client.set = AsyncMock(side_effect=RedisError("boom"))
    cache = _make_cache(client)

    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    await cache.set("key", {"value": 1})
    assert record_cmd.call_args.kwargs["command"] == "set"


@pytest.mark.asyncio
async def test_delete_records_command(monkeypatch) -> None:
    client = AsyncMock()
    client.delete = AsyncMock()
    cache = _make_cache(client)

    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    await cache.delete("key")
    client.delete.assert_awaited_once_with("key")
    assert record_cmd.call_args.kwargs["command"] == "delete"


@pytest.mark.asyncio
async def test_invalidate_single_key(monkeypatch) -> None:
    client = AsyncMock()
    client.delete = AsyncMock()
    client.scan_iter = MagicMock()
    cache = _make_cache(client)

    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    await cache.invalidate("one")
    client.delete.assert_awaited_once_with("one")
    client.scan_iter.assert_not_called()
    assert record_cmd.call_args.kwargs["command"] == "invalidate"


@pytest.mark.asyncio
async def test_invalidate_pattern_deletes_keys(monkeypatch) -> None:
    client = AsyncMock()
    client.delete = AsyncMock()

    async def fake_scan_iter(match: str | None = None):
        for item in ["a", "b"]:
            yield item

    client.scan_iter = MagicMock(side_effect=fake_scan_iter)
    cache = _make_cache(client)

    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    await cache.invalidate("prefix*")
    client.delete.assert_awaited_once_with("a", "b")
    assert record_cmd.call_args.kwargs["command"] == "invalidate"


@pytest.mark.asyncio
async def test_invalidate_pattern_handles_empty(monkeypatch) -> None:
    client = AsyncMock()
    client.delete = AsyncMock()

    async def fake_scan_iter(match: str | None = None):
        if False:
            yield "unused"

    client.scan_iter = MagicMock(side_effect=fake_scan_iter)
    cache = _make_cache(client)

    record_cmd = MagicMock()
    monkeypatch.setattr(cache_module.metrics, "record_redis_command", record_cmd)

    await cache.invalidate("prefix*")
    client.delete.assert_not_called()
    assert record_cmd.call_args.kwargs["command"] == "invalidate"


@pytest.mark.asyncio
async def test_close_handles_errors() -> None:
    client = AsyncMock()
    client.close = AsyncMock(side_effect=RedisError("boom"))
    client.connection_pool = AsyncMock()
    client.connection_pool.disconnect = AsyncMock()
    cache = _make_cache(client)

    await cache.close()
    client.close.assert_awaited_once()
