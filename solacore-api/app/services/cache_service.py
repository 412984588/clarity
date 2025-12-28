from __future__ import annotations

from typing import Any
from uuid import UUID

from app.utils.cache import RedisCache
from app.utils.cache import cache as redis_cache

USER_TTL_SECONDS = 600
SUBSCRIPTION_TTL_SECONDS = 300
SESSIONS_TTL_SECONDS = 120
DEVICE_TTL_SECONDS = 1800


class CacheService:
    def __init__(self, cache: RedisCache | None = None) -> None:
        self._cache = cache or redis_cache

    @staticmethod
    def _normalize_id(value: UUID | str) -> str:
        return str(value)

    def _user_key(self, user_id: UUID | str) -> str:
        return f"user:{self._normalize_id(user_id)}"

    def _subscription_key(self, user_id: UUID | str) -> str:
        return f"subscription:{self._normalize_id(user_id)}"

    def _sessions_key(self, user_id: UUID | str) -> str:
        return f"sessions:{self._normalize_id(user_id)}"

    def _device_key(self, device_id: UUID | str) -> str:
        return f"device:{self._normalize_id(device_id)}"

    async def get_user(self, user_id: UUID | str) -> dict[str, Any] | None:
        return await self._cache.get(self._user_key(user_id))

    async def set_user(self, user_id: UUID | str, payload: dict[str, Any]) -> None:
        await self._cache.set(self._user_key(user_id), payload, ttl=USER_TTL_SECONDS)

    async def invalidate_user(self, user_id: UUID | str) -> None:
        await self._cache.delete(self._user_key(user_id))

    async def get_subscription(self, user_id: UUID | str) -> dict[str, Any] | None:
        return await self._cache.get(self._subscription_key(user_id))

    async def set_subscription(
        self, user_id: UUID | str, payload: dict[str, Any]
    ) -> None:
        await self._cache.set(
            self._subscription_key(user_id),
            payload,
            ttl=SUBSCRIPTION_TTL_SECONDS,
        )

    async def invalidate_subscription(self, user_id: UUID | str) -> None:
        await self._cache.delete(self._subscription_key(user_id))

    async def get_sessions(self, user_id: UUID | str) -> Any | None:
        return await self._cache.get(self._sessions_key(user_id))

    async def set_sessions(self, user_id: UUID | str, payload: Any) -> None:
        await self._cache.set(
            self._sessions_key(user_id),
            payload,
            ttl=SESSIONS_TTL_SECONDS,
        )

    async def invalidate_sessions(self, user_id: UUID | str) -> None:
        await self._cache.delete(self._sessions_key(user_id))

    async def get_device(self, device_id: UUID | str) -> dict[str, Any] | None:
        return await self._cache.get(self._device_key(device_id))

    async def set_device(self, device_id: UUID | str, payload: dict[str, Any]) -> None:
        await self._cache.set(
            self._device_key(device_id),
            payload,
            ttl=DEVICE_TTL_SECONDS,
        )

    async def invalidate_device(self, device_id: UUID | str) -> None:
        await self._cache.delete(self._device_key(device_id))
