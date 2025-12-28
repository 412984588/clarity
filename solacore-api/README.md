# Solacore API

![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)
![Tests](https://img.shields.io/badge/tests-manual-lightgrey)
![License](https://img.shields.io/badge/license-MIT-blue)

FastAPI backend for authentication, Solve sessions, subscriptions, and account management.

## Features

- FastAPI + async SQLAlchemy with Alembic migrations
- Authentication with email/password and OAuth (Google, Apple)
- SSE streaming for Solve sessions
- Redis caching with TTL-based invalidation
- Rate limiting via SlowAPI (IP and user based)
- Monitoring stack: Prometheus, Grafana, Sentry
- Webhooks for Stripe and RevenueCat
- Health probes and structured logging

## Quick start

```bash
poetry install --with dev
cp .env.example .env

docker compose up -d db redis
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

Open API docs at `http://localhost:8000/docs`.

## Documentation

- `docs/DEVELOPMENT.md` - local development
- `docs/DEPLOYMENT.md` - production deployment
- `docs/ARCHITECTURE.md` - system architecture
- `docs/MONITORING.md` - metrics and alerting
- `docs/CONTRIBUTING.md` - contribution guide
- `docs/API.md` - API overview

## Contributing

See `docs/CONTRIBUTING.md`.

## Contributors

- Maintainer: Zhiming Deng
- All contributors: https://github.com/412984588/clarity/graphs/contributors

## License

MIT
# Auto-deploy test Fri Dec 26 17:39:43 EST 2025
