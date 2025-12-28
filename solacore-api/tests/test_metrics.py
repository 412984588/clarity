from __future__ import annotations

from app.utils.metrics import MetricsRegistry, _format_labels, format_prometheus_metrics


def test_metrics_registry_snapshot_and_rates() -> None:
    registry = MetricsRegistry()
    registry.record_request(-1.0, method="GET", path="/", status_code=200)
    registry.record_request(2.0, method="GET", path="/", status_code=200)
    registry.record_cache_hit()
    registry.record_cache_miss()
    registry.record_db_query(-5.0)
    registry.record_redis_command(0.5, command="get")

    snapshot = registry.snapshot()

    assert snapshot["request_count"] == 2
    assert snapshot["request_duration"] == 1.0
    assert snapshot["cache_hit_rate"] == 0.5
    assert snapshot["db_query_duration_sum"] == 0.0
    assert snapshot["db_query_duration_count"] == 1
    assert snapshot["redis_command_duration_sum"]["get"] == 0.5


def test_format_labels_escapes_values() -> None:
    labels = {"path": '/foo"bar', "status": "200", "method": "GET\n"}
    formatted = _format_labels(labels)
    assert formatted == '{method="GET\\n",path="/foo\\"bar",status="200"}'


def test_format_prometheus_metrics_includes_pool_stats() -> None:
    snapshot = {
        "request_count": 1,
        "request_duration": 0.25,
        "request_counts": {("GET", "/", "200"): 1},
        "request_duration_sum": {("GET", "/", "200"): 0.25},
        "request_duration_count": {("GET", "/", "200"): 1},
        "cache_hits": 2,
        "cache_misses": 1,
        "cache_hit_rate": 0.66,
        "db_query_duration_sum": 1.5,
        "db_query_duration_count": 3,
        "redis_command_duration_sum": {"get": 0.5},
        "redis_command_duration_count": {"get": 2},
    }

    output = format_prometheus_metrics(
        snapshot,
        active_sessions=4,
        active_users=2,
        db_pool={"size": 5, "checked_out": 1, "overflow": 0},
    )

    assert "http_requests_total" in output
    assert "cache_hit_rate" in output
    assert "db_pool_size" in output
    assert "redis_command_duration_seconds_sum{command=\"get\"}" in output


def test_format_prometheus_metrics_without_pool() -> None:
    snapshot = {"request_count": 0, "request_duration": 0.0}
    output = format_prometheus_metrics(
        snapshot, active_sessions=0, active_users=0, db_pool=None
    )
    assert "db_pool_size" not in output
