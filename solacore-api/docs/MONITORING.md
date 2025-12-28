# Monitoring Guide

This guide covers Prometheus metrics, Grafana dashboards, Sentry error tracking, alerting rules, and log query tips.

## Prometheus metrics

The API exposes metrics at `GET /health/metrics` and Prometheus scrapes:

- `http_requests_total{method,path,status}`
- `http_request_duration_seconds_sum{method,path,status}`
- `http_request_duration_seconds_count{method,path,status}`
- `cache_hits_total`
- `cache_misses_total`
- `cache_hit_rate`
- `db_query_duration_seconds_sum`
- `db_query_duration_seconds_count`
- `redis_command_duration_seconds_sum{command}`
- `redis_command_duration_seconds_count{command}`
- `db_pool_size`
- `db_pool_checked_out`
- `db_pool_overflow`
- `active_sessions`
- `active_users`

Legacy (still exported for compatibility):
- `request_count`
- `request_duration`

Example PromQL queries:

- QPS:
  `sum(rate(http_requests_total[1m]))`
- Error rate:
  `sum(rate(http_requests_total{status=~"4..|5.."}[5m])) / sum(rate(http_requests_total[5m]))`
- P95 latency (if histogram is added later):
  `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`

Prometheus config lives in `monitoring/prometheus.yml`.

## Grafana dashboards

Grafana is provisioned automatically:
- Dashboard: `monitoring/grafana/dashboards/solacore.json`
- Datasource: `monitoring/grafana/provisioning/datasources/prometheus.yml`

Access Grafana at:
- `http://<host>:${GRAFANA_PORT:-3000}`

Default credentials (override in `.env`):
- `GRAFANA_ADMIN_USER`
- `GRAFANA_ADMIN_PASSWORD`

The dashboard includes:
- QPS, latency, error rate
- Request rate by endpoint
- DB query rate and latency
- Redis ops and latency
- Cache hit rate
- Host CPU, memory, disk usage
- Active users and sessions

## Sentry error tracking

Sentry is enabled when all of the following are true:
- `SENTRY_DSN` is set
- `DEBUG=false`

Key settings:
- `SENTRY_ENVIRONMENT`
- `SENTRY_TRACES_SAMPLE_RATE`

The SDK scrubs tokens and secrets before sending events. User IDs are attached from access tokens when available.

## Alerting rules

Alert rules are defined in `monitoring/alerts.yml` and loaded by Prometheus.

Current alerts:
- `ApiHighErrorRate`: 4xx/5xx > 5% for 5 minutes
- `ApiHighLatency`: average latency > 1s for 5 minutes

Update thresholds based on real traffic patterns.

## Log query tips

Production logs are structured JSON (via `structlog`). Example queries:

```bash
# show error logs only
docker compose logs -f api | jq 'select(.level=="error")'

# search by request id or user id in logs
docker compose logs api | rg "request_id|user_id"
```

If `jq` is not available, fall back to `rg`:

```bash
docker compose logs api | rg "error|exception|traceback"
```

## Health endpoints

Use these for ad-hoc checks:
- `GET /health`
- `GET /health/live`
- `GET /health/ready`
- `GET /health/metrics`
