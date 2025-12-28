from __future__ import annotations

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
        self._client: Redis | None = None
        self._pool: ConnectionPool | None = None
        if not self._enabled:
            return

        self._pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=20,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            health_check_interval=30,
        )
        self._client = Redis(connection_pool=self._pool)

    async def get(self, key: str) -> Any | None:
        if not self._client:
            return None
        start = time.perf_counter()
        try:
            value = await self._client.get(key)
        except RedisError:
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
        if not self._client:
            return
        start = time.perf_counter()
        try:
            payload = json.dumps(value, default=_default_serializer)
            await self._client.set(key, payload, ex=ttl)
        except RedisError:
            logger.debug("Redis set failed", exc_info=True)
        finally:
            metrics.record_redis_command(time.perf_counter() - start, command="set")

    async def delete(self, key: str) -> None:
        if not self._client:
            return
        start = time.perf_counter()
        try:
            await self._client.delete(key)
        except RedisError:
            logger.debug("Redis delete failed", exc_info=True)
        finally:
            metrics.record_redis_command(time.perf_counter() - start, command="delete")

    async def invalidate(self, pattern: str) -> None:
        if not self._client:
            return
        start = time.perf_counter()
        try:
            if "*" not in pattern:
                await self._client.delete(pattern)
                return
            keys = [key async for key in self._client.scan_iter(match=pattern)]
            if keys:
                await self._client.delete(*keys)
        except RedisError:
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
        except RedisError:
            logger.debug("Redis close failed", exc_info=True)


cache = RedisCache()
