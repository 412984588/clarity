# Local Development Guide

This guide helps you get a local environment running quickly, including Docker Compose, migrations, tests, and debugging.

## Quick start (5 minutes)

```bash
# 1) install dependencies
poetry install --with dev

# 2) configure env
cp .env.example .env

# 3) start dependencies
docker compose up -d db redis

# 4) run migrations
poetry run alembic upgrade head

# 5) start API
poetry run uvicorn app.main:app --reload
```

Open API docs:
- `http://localhost:8000/docs`

## Docker Compose local environment

Start the full stack (API + Postgres + Redis):

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f api
```

Stop services:

```bash
docker compose down
```

## Database migrations

Create a new migration:

```bash
poetry run alembic revision -m "add new table"
```

Apply migrations:

```bash
poetry run alembic upgrade head
```

Rollback one revision:

```bash
poetry run alembic downgrade -1
```

## Running tests

```bash
poetry run pytest
```

Coverage (must be >= 85%):

```bash
poetry run pytest --cov=app --cov-fail-under=85
```

Targeted tests:

```bash
poetry run pytest -k "auth and not oauth"
```

## Debugging tips

- Set `DEBUG=true` in `.env` for verbose logs.
- Use `GET /health` and `GET /health/ready` to verify dependencies.
- Check metrics locally: `GET /health/metrics`.
- Use `--reload` for live code reloads.
- For SSE endpoints, use `curl -N` to keep the connection open.

## Common issues

- Port already in use: change `PORT` or stop the conflicting service.
- Postgres connection error: ensure `db` container is running and `DATABASE_URL` is correct.
- Redis connection error: verify `redis` container and `REDIS_URL`.
- Migration errors: ensure your database schema matches the Alembic history.
- Sentry not sending: confirm `DEBUG=false` and `SENTRY_DSN` is set.
