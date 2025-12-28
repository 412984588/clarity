# Deployment Guide

This guide explains how to deploy Solacore API using Docker Compose in production, including environment configuration, migrations, monitoring, and backups.

## Prerequisites

- Docker 24+
- Docker Compose v2
- A production `.env` file (see `.env.prod.example`)

## Environment configuration

1. Copy the template and fill secrets:

```bash
cp .env.prod.example .env
```

2. Update required values:
- `DEBUG=false`
- `DATABASE_URL`
- `JWT_SECRET`
- OAuth client IDs
- Stripe and RevenueCat secrets (if payments enabled)
- `SENTRY_DSN` (optional)
- Monitoring ports and Grafana credentials

## Start the stack

Use the production compose file:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Services included:
- `api` (FastAPI)
- `db` (PostgreSQL)
- `redis`
- `nginx`
- `backup`
- `prometheus`
- `grafana`
- `node-exporter`

## Database migrations

Run Alembic migrations after the first deploy (and on each release):

```bash
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

## Health checks

- Liveness: `GET /health/live`
- Readiness: `GET /health/ready`
- Metrics: `GET /health/metrics`

If NGINX is exposed on port 80/443, use the public domain:

```bash
curl https://<your-domain>/health/live
```

## Monitoring stack

Prometheus and Grafana are included in `docker-compose.prod.yml`.

- Prometheus: `http://<host>:${PROMETHEUS_PORT:-9090}`
- Grafana: `http://<host>:${GRAFANA_PORT:-3000}`

Grafana provisions the dashboard in `monitoring/grafana/dashboards/solacore.json` automatically.

## Backups

The `backup` service runs a daily cron at 02:00 and executes `scripts/backup_database.sh`.

Key settings (see `.env`):
- `BACKUP_DIR`
- `BACKUP_RETENTION_DAYS`
- `BACKUP_S3_BUCKET` (optional)

To restore a backup:

```bash
# copy backup file into the backup volume or container
# then execute restore

docker compose -f docker-compose.prod.yml exec backup \
  /scripts/restore_database.sh /backups/backup_YYYYMMDD_HHMMSS.sql.gz
```

## Updating the deployment

1. Pull latest code and rebuild images:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

2. Run migrations:

```bash
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

3. Verify health and metrics endpoints.

## Security checklist

- `DEBUG=false` in production.
- Rotate `JWT_SECRET` and all API keys.
- Use HTTPS via NGINX.
- Restrict Grafana access or disable anonymous mode.
- Set `CORS_ALLOWED_ORIGINS` explicitly.
