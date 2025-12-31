from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

from app.config import get_settings
from app.utils.metrics import metrics
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


def _default_serializer(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


class RedisCache:
    def __init__(self) -> None:
        settings = get_settings()
        self._enabled = bool(settings.redis_url)
        self._redis_url = settings.redis_url
        self._client: Redis | None = None
        self._pool: ConnectionPool | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    async def _ensure_client(self) -> Redis | None:
        if not self._enabled:
            return None

        loop = asyncio.get_running_loop()
        if self._client and self._loop is loop:
            return self._client

        if self._client:
            try:
                await self._client.close()
                await self._client.connection_pool.disconnect()
            except (RedisError, RuntimeError):
                logger.debug("Redis close failed", exc_info=True)

        self._pool = ConnectionPool.from_url(
            self._redis_url,
            max_connections=20,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            health_check_interval=30,
        )
        self._client = Redis(connection_pool=self._pool)
        self._loop = loop
        return self._client

    async def get(self, key: str) -> Any | None:
        client = await self._ensure_client()
        if not client:
            return None
        start = time.perf_counter()
        try:
            value = await client.get(key)
        except (RedisError, RuntimeError):
            logger.debug("Redis get failed", exc_info=True)
            metrics.record_cache_miss()
            return None
        finally:
            metrics.record_redis_command(time.perf_counter() - start, command="get")
        if value is None:
            metrics.record_cache_miss()
            return None
        try:
            payload = json.loads(value)
        except (TypeError, ValueError):
            metrics.record_cache_miss()
            return None
        metrics.record_cache_hit()
        return payload

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        client = await self._ensure_client()
        if not client:
            return
        start = time.perf_counter()
        try:
            payload = json.dumps(value, default=_default_serializer)
            await client.set(key, payload, ex=ttl)
        except (RedisError, RuntimeError):
            logger.debug("Redis set failed", exc_info=True)
        finally:
            metrics.record_redis_command(time.perf_counter() - start, command="set")

    async def delete(self, key: str) -> None:
        client = await self._ensure_client()
        if not client:
            return
        start = time.perf_counter()
        try:
            await client.delete(key)
        except (RedisError, RuntimeError):
            logger.debug("Redis delete failed", exc_info=True)
        finally:
            metrics.record_redis_command(time.perf_counter() - start, command="delete")

    async def invalidate(self, pattern: str) -> None:
        client = await self._ensure_client()
        if not client:
            return
        start = time.perf_counter()
        try:
            if "*" not in pattern:
                await client.delete(pattern)
                return
            keys = [key async for key in client.scan_iter(match=pattern)]
            if keys:
                await client.delete(*keys)
        except (RedisError, RuntimeError):
            logger.debug("Redis invalidate failed", exc_info=True)
        finally:
            metrics.record_redis_command(
                time.perf_counter() - start, command="invalidate"
            )

    async def close(self) -> None:
        if not self._client:
            return
        try:
            await self._client.close()
            await self._client.connection_pool.disconnect()
        except (RedisError, RuntimeError):
            logger.debug("Redis close failed", exc_info=True)


cache = RedisCache()
