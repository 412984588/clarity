from __future__ import annotations

from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.cache_service import (
    CacheService,
    DEVICE_TTL_SECONDS,
    SESSIONS_TTL_SECONDS,
    SUBSCRIPTION_TTL_SECONDS,
    USER_TTL_SECONDS,
)


@pytest.mark.asyncio
async def test_cache_service_user_paths() -> None:
    fake_cache = MagicMock()
    fake_cache.get = AsyncMock(return_value={"id": "user"})
    fake_cache.set = AsyncMock()
    fake_cache.delete = AsyncMock()
    service = CacheService(fake_cache)

    user_id = uuid4()
    result = await service.get_user(user_id)
    assert result == {"id": "user"}
    fake_cache.get.assert_awaited_once_with(f"user:{user_id}")

    await service.set_user(user_id, {"name": "Ada"})
    fake_cache.set.assert_awaited_once_with(
        f"user:{user_id}", {"name": "Ada"}, ttl=USER_TTL_SECONDS
    )

    await service.invalidate_user(user_id)
    fake_cache.delete.assert_awaited_once_with(f"user:{user_id}")


@pytest.mark.asyncio
async def test_cache_service_subscription_paths() -> None:
    fake_cache = MagicMock()
    fake_cache.get = AsyncMock(return_value={"plan": "pro"})
    fake_cache.set = AsyncMock()
    fake_cache.delete = AsyncMock()
    service = CacheService(fake_cache)

    user_id = uuid4()
    result = await service.get_subscription(user_id)
    assert result == {"plan": "pro"}
    fake_cache.get.assert_awaited_once_with(f"subscription:{user_id}")

    await service.set_subscription(user_id, {"plan": "pro"})
    fake_cache.set.assert_awaited_once_with(
        f"subscription:{user_id}", {"plan": "pro"}, ttl=SUBSCRIPTION_TTL_SECONDS
    )

    await service.invalidate_subscription(user_id)
    fake_cache.delete.assert_awaited_once_with(f"subscription:{user_id}")


@pytest.mark.asyncio
async def test_cache_service_sessions_paths() -> None:
    fake_cache = MagicMock()
    fake_cache.get = AsyncMock(return_value=["session-1"])
    fake_cache.set = AsyncMock()
    fake_cache.delete = AsyncMock()
    service = CacheService(fake_cache)

    user_id = uuid4()
    result = await service.get_sessions(user_id)
    assert result == ["session-1"]
    fake_cache.get.assert_awaited_once_with(f"sessions:{user_id}")

    await service.set_sessions(user_id, ["session-1"])
    fake_cache.set.assert_awaited_once_with(
        f"sessions:{user_id}", ["session-1"], ttl=SESSIONS_TTL_SECONDS
    )

    await service.invalidate_sessions(user_id)
    fake_cache.delete.assert_awaited_once_with(f"sessions:{user_id}")


@pytest.mark.asyncio
async def test_cache_service_device_paths() -> None:
    fake_cache = MagicMock()
    fake_cache.get = AsyncMock(return_value={"device": "phone"})
    fake_cache.set = AsyncMock()
    fake_cache.delete = AsyncMock()
    service = CacheService(fake_cache)

    device_id = uuid4()
    result = await service.get_device(device_id)
    assert result == {"device": "phone"}
    fake_cache.get.assert_awaited_once_with(f"device:{device_id}")

    await service.set_device(device_id, {"device": "phone"})
    fake_cache.set.assert_awaited_once_with(
        f"device:{device_id}", {"device": "phone"}, ttl=DEVICE_TTL_SECONDS
    )

    await service.invalidate_device(device_id)
    fake_cache.delete.assert_awaited_once_with(f"device:{device_id}")
