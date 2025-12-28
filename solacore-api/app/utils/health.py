from __future__ import annotations

import asyncio
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable

import httpx
from redis.asyncio import Redis
from sqlalchemy import func, select, text

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.session import ActiveSession
from app.utils.datetime_utils import utc_now

CHECK_TIMEOUT_SECONDS = 2.0
CACHE_TTL_SECONDS = 5.0
MIN_AVAILABLE_PERCENT = 10.0
DISK_USAGE_PATH = Path("/")

_ready_cache: dict[str, Any] = {"timestamp": 0.0, "report": None}
_ready_lock = asyncio.Lock()


def _iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _latency_ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)


async def _run_check(
    name: str, fn: Callable[[], Awaitable[dict[str, Any]]]
) -> tuple[str, dict[str, Any]]:
    try:
        result = await asyncio.wait_for(fn(), timeout=CHECK_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        return name, {"status": "down", "error": "timeout"}
    except Exception:
        return name, {"status": "down", "error": "exception"}
    return name, result


async def _check_database() -> dict[str, Any]:
    start = time.monotonic()
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "up", "latency_ms": _latency_ms(start)}
    except Exception:
        return {"status": "down", "latency_ms": _latency_ms(start)}


async def _check_redis() -> dict[str, Any]:
    settings = get_settings()
    if not settings.redis_url:
        return {"status": "down", "error": "missing_url"}
    start = time.monotonic()
    client = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=CHECK_TIMEOUT_SECONDS,
        socket_timeout=CHECK_TIMEOUT_SECONDS,
        health_check_interval=30,
    )
    try:
        await client.ping()
        return {"status": "up", "latency_ms": _latency_ms(start)}
    except Exception:
        return {"status": "down", "latency_ms": _latency_ms(start)}
    finally:
        await client.close()
        await client.connection_pool.disconnect()


async def _check_disk() -> dict[str, Any]:
    usage = await asyncio.to_thread(shutil.disk_usage, DISK_USAGE_PATH)
    usage_percent = round((usage.used / usage.total) * 100, 2)
    available_percent = 100 - usage_percent
    status = "up" if available_percent >= MIN_AVAILABLE_PERCENT else "down"
    return {"status": status, "usage_percent": usage_percent}


def _memory_usage_percent() -> float | None:
    try:
        import psutil  # type: ignore[import-untyped]
    except ImportError:
        psutil = None

    if psutil is not None:
        return float(psutil.virtual_memory().percent)

    if not hasattr(os, "sysconf"):
        return None

    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        phys_pages = os.sysconf("SC_PHYS_PAGES")
        avail_pages = os.sysconf("SC_AVPHYS_PAGES")
    except (ValueError, OSError):
        return None

    total = page_size * phys_pages
    available = page_size * avail_pages
    if total <= 0:
        return None
    used_percent = (1 - (available / total)) * 100
    return round(used_percent, 2)


async def _check_memory() -> dict[str, Any]:
    usage_percent = await asyncio.to_thread(_memory_usage_percent)
    if usage_percent is None:
        return {"status": "down", "error": "unavailable"}
    available_percent = 100 - usage_percent
    status = "up" if available_percent >= MIN_AVAILABLE_PERCENT else "down"
    return {"status": status, "usage_percent": usage_percent}


async def _check_external_api() -> dict[str, Any]:
    settings = get_settings()
    provider = settings.llm_provider
    headers: dict[str, str] = {}
    url = ""

    if provider == "openai":
        if not settings.openai_api_key:
            return {
                "status": "skipped",
                "reason": "missing_api_key",
                "provider": provider,
            }
        url = "https://api.openai.com/v1/models"
        headers["Authorization"] = f"Bearer {settings.openai_api_key}"
    elif provider == "anthropic":
        if not settings.anthropic_api_key:
            return {
                "status": "skipped",
                "reason": "missing_api_key",
                "provider": provider,
            }
        url = "https://api.anthropic.com/v1/models"
        headers["x-api-key"] = settings.anthropic_api_key
        headers["anthropic-version"] = "2023-06-01"
    elif settings.openrouter_api_key:
        provider = "openrouter"
        url = f"{settings.openrouter_base_url.rstrip('/')}/models"
        headers["Authorization"] = f"Bearer {settings.openrouter_api_key}"
        if settings.openrouter_referer:
            headers["HTTP-Referer"] = settings.openrouter_referer
        if settings.openrouter_app_name:
            headers["X-Title"] = settings.openrouter_app_name
    else:
        return {"status": "skipped", "reason": "not_configured"}

    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=CHECK_TIMEOUT_SECONDS) as client:
            response = await client.get(url, headers=headers)
    except httpx.HTTPError:
        return {
            "status": "down",
            "provider": provider,
            "latency_ms": _latency_ms(start),
        }

    if 200 <= response.status_code < 300:
        return {
            "status": "up",
            "provider": provider,
            "latency_ms": _latency_ms(start),
        }
    return {
        "status": "down",
        "provider": provider,
        "status_code": response.status_code,
        "latency_ms": _latency_ms(start),
    }


def _should_check_external_api() -> bool:
    settings = get_settings()
    if settings.llm_provider == "openai":
        return bool(settings.openai_api_key)
    if settings.llm_provider == "anthropic":
        return bool(settings.anthropic_api_key)
    return bool(settings.openrouter_api_key)


async def get_liveness_report() -> dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": _iso_timestamp(),
        "checks": {"service": {"status": "up"}},
    }


async def _build_readiness_report() -> dict[str, Any]:
    checks: dict[str, Callable[[], Awaitable[dict[str, Any]]]] = {
        "database": _check_database,
        "redis": _check_redis,
        "disk": _check_disk,
        "memory": _check_memory,
    }
    if _should_check_external_api():
        checks["external_api"] = _check_external_api

    results = await asyncio.gather(
        *(_run_check(name, fn) for name, fn in checks.items())
    )
    checks_payload = {name: payload for name, payload in results}

    required_checks = {"database", "redis", "disk", "memory"}
    required_ok = all(
        checks_payload.get(name, {}).get("status") == "up"
        for name in required_checks
    )

    optional_ok = True
    external_status = checks_payload.get("external_api", {}).get("status")
    if external_status and external_status not in {"up", "skipped"}:
        optional_ok = False

    if required_ok and optional_ok:
        overall_status = "healthy"
    elif required_ok:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "timestamp": _iso_timestamp(),
        "checks": checks_payload,
    }


async def get_readiness_report() -> dict[str, Any]:
    now = time.monotonic()
    cached_report = _ready_cache.get("report")
    if cached_report and (now - _ready_cache["timestamp"]) < CACHE_TTL_SECONDS:
        return cached_report

    async with _ready_lock:
        now = time.monotonic()
        cached_report = _ready_cache.get("report")
        if cached_report and (now - _ready_cache["timestamp"]) < CACHE_TTL_SECONDS:
            return cached_report

        report = await _build_readiness_report()
        _ready_cache["timestamp"] = time.monotonic()
        _ready_cache["report"] = report
        return report


async def get_active_sessions_count() -> int:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.count())
                .select_from(ActiveSession)
                .where(ActiveSession.expires_at > utc_now())
            )
            return int(result.scalar_one())
    except Exception:
        return -1


async def get_active_users_count() -> int:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.count(func.distinct(ActiveSession.user_id)))
                .where(ActiveSession.expires_at > utc_now())
            )
            return int(result.scalar_one())
    except Exception:
        return -1
