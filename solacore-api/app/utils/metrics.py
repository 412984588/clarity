from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._request_counts: dict[tuple[str, str, str], int] = defaultdict(int)
        self._request_duration_sum: dict[tuple[str, str, str], float] = defaultdict(
            float
        )
        self._request_duration_count: dict[tuple[str, str, str], int] = defaultdict(int)
        self._cache_hits = 0
        self._cache_misses = 0
        self._db_query_duration_sum = 0.0
        self._db_query_duration_count = 0
        self._redis_command_duration_sum: dict[str, float] = defaultdict(float)
        self._redis_command_duration_count: dict[str, int] = defaultdict(int)

    def record_request(
        self, duration_seconds: float, *, method: str, path: str, status_code: int
    ) -> None:
        key = (method, path, str(status_code))
        with self._lock:
            self._request_counts[key] += 1
            self._request_duration_sum[key] += max(duration_seconds, 0.0)
            self._request_duration_count[key] += 1

    def record_cache_hit(self) -> None:
        with self._lock:
            self._cache_hits += 1

    def record_cache_miss(self) -> None:
        with self._lock:
            self._cache_misses += 1

    def record_db_query(self, duration_seconds: float) -> None:
        with self._lock:
            self._db_query_duration_sum += max(duration_seconds, 0.0)
            self._db_query_duration_count += 1

    def record_redis_command(self, duration_seconds: float, *, command: str) -> None:
        with self._lock:
            self._redis_command_duration_sum[command] += max(duration_seconds, 0.0)
            self._redis_command_duration_count[command] += 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            total_cache = self._cache_hits + self._cache_misses
            cache_hit_rate = self._cache_hits / total_cache if total_cache > 0 else 0.0
            total_request_count = sum(self._request_counts.values())
            total_request_duration_sum = sum(self._request_duration_sum.values())
            total_request_duration_count = sum(self._request_duration_count.values())
            avg_duration = (
                total_request_duration_sum / total_request_duration_count
                if total_request_duration_count > 0
                else 0.0
            )
            return {
                "request_count": total_request_count,
                "request_duration": avg_duration,
                "request_counts": dict(self._request_counts),
                "request_duration_sum": dict(self._request_duration_sum),
                "request_duration_count": dict(self._request_duration_count),
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "cache_hit_rate": cache_hit_rate,
                "db_query_duration_sum": self._db_query_duration_sum,
                "db_query_duration_count": self._db_query_duration_count,
                "redis_command_duration_sum": dict(self._redis_command_duration_sum),
                "redis_command_duration_count": dict(
                    self._redis_command_duration_count
                ),
            }


def format_prometheus_metrics(
    snapshot: dict[str, Any],
    *,
    active_sessions: int,
    active_users: int,
    db_pool: dict[str, Any] | None,
) -> str:
    request_count = int(snapshot.get("request_count", 0))
    request_duration = float(snapshot.get("request_duration", 0.0))
    cache_hit_rate = float(snapshot.get("cache_hit_rate", 0.0))
    cache_hits = int(snapshot.get("cache_hits", 0))
    cache_misses = int(snapshot.get("cache_misses", 0))
    request_counts: dict[tuple[str, str, str], int] = snapshot.get("request_counts", {})
    request_duration_sum: dict[tuple[str, str, str], float] = snapshot.get(
        "request_duration_sum", {}
    )
    request_duration_count: dict[tuple[str, str, str], int] = snapshot.get(
        "request_duration_count", {}
    )
    db_query_duration_sum = float(snapshot.get("db_query_duration_sum", 0.0))
    db_query_duration_count = int(snapshot.get("db_query_duration_count", 0))
    redis_command_duration_sum: dict[str, float] = snapshot.get(
        "redis_command_duration_sum", {}
    )
    redis_command_duration_count: dict[str, int] = snapshot.get(
        "redis_command_duration_count", {}
    )

    lines = [
        "# HELP http_requests_total Total number of HTTP requests",
        "# TYPE http_requests_total counter",
    ]

    for (method, path, status), value in sorted(request_counts.items()):
        labels = _format_labels({"method": method, "path": path, "status": status})
        lines.append(f"http_requests_total{labels} {value}")

    lines.extend(
        [
            "# HELP http_request_duration_seconds_sum Total request duration in seconds",
            "# TYPE http_request_duration_seconds_sum counter",
        ]
    )
    for (method, path, status), value in sorted(request_duration_sum.items()):
        labels = _format_labels({"method": method, "path": path, "status": status})
        lines.append(f"http_request_duration_seconds_sum{labels} {value:.6f}")

    lines.extend(
        [
            "# HELP http_request_duration_seconds_count Total request count for timing",
            "# TYPE http_request_duration_seconds_count counter",
        ]
    )
    for (method, path, status), value in sorted(request_duration_count.items()):
        labels = _format_labels({"method": method, "path": path, "status": status})
        lines.append(f"http_request_duration_seconds_count{labels} {value}")

    lines.extend(
        [
            "# HELP request_count Total number of HTTP requests (legacy)",
            "# TYPE request_count counter",
            f"request_count {request_count}",
            "# HELP request_duration Average request duration in seconds (legacy)",
            "# TYPE request_duration gauge",
            f"request_duration {request_duration:.6f}",
            "# HELP active_sessions Current active sessions",
            "# TYPE active_sessions gauge",
            f"active_sessions {active_sessions}",
            "# HELP active_users Current active users",
            "# TYPE active_users gauge",
            f"active_users {active_users}",
            "# HELP cache_hits_total Cache hits",
            "# TYPE cache_hits_total counter",
            f"cache_hits_total {cache_hits}",
            "# HELP cache_misses_total Cache misses",
            "# TYPE cache_misses_total counter",
            f"cache_misses_total {cache_misses}",
            "# HELP cache_hit_rate Cache hit rate (0-1)",
            "# TYPE cache_hit_rate gauge",
            f"cache_hit_rate {cache_hit_rate:.6f}",
            "# HELP db_query_duration_seconds_sum Total database query duration in seconds",
            "# TYPE db_query_duration_seconds_sum counter",
            f"db_query_duration_seconds_sum {db_query_duration_sum:.6f}",
            "# HELP db_query_duration_seconds_count Total database query count",
            "# TYPE db_query_duration_seconds_count counter",
            f"db_query_duration_seconds_count {db_query_duration_count}",
            "# HELP redis_command_duration_seconds_sum Total Redis command duration",
            "# TYPE redis_command_duration_seconds_sum counter",
        ]
    )

    for command, value in sorted(redis_command_duration_sum.items()):
        labels = _format_labels({"command": command})
        lines.append(f"redis_command_duration_seconds_sum{labels} {value:.6f}")

    lines.extend(
        [
            "# HELP redis_command_duration_seconds_count Total Redis command count",
            "# TYPE redis_command_duration_seconds_count counter",
        ]
    )
    for command, value in sorted(redis_command_duration_count.items()):
        labels = _format_labels({"command": command})
        lines.append(f"redis_command_duration_seconds_count{labels} {value}")

    if db_pool:
        pool_size = db_pool.get("size")
        checked_out = db_pool.get("checked_out")
        overflow = db_pool.get("overflow")
        if pool_size is not None:
            lines.extend(
                [
                    "# HELP db_pool_size Database connection pool size",
                    "# TYPE db_pool_size gauge",
                    f"db_pool_size {pool_size}",
                ]
            )
        if checked_out is not None:
            lines.extend(
                [
                    "# HELP db_pool_checked_out Checked out DB connections",
                    "# TYPE db_pool_checked_out gauge",
                    f"db_pool_checked_out {checked_out}",
                ]
            )
        if overflow is not None:
            lines.extend(
                [
                    "# HELP db_pool_overflow DB pool overflow connections",
                    "# TYPE db_pool_overflow gauge",
                    f"db_pool_overflow {overflow}",
                ]
            )

    return "\n".join(lines) + "\n"


def _format_labels(labels: dict[str, str]) -> str:
    if not labels:
        return ""
    parts = []
    for key in sorted(labels.keys()):
        value = labels[key]
        escaped = (
            str(value).replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
        )
        parts.append(f'{key}="{escaped}"')
    return "{" + ",".join(parts) + "}"


metrics = MetricsRegistry()
