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
- Modular router architecture for improved maintainability

## Project structure

```
app/
├── routers/           # Modular API routes
│   ├── auth/         # Authentication endpoints (10 modules)
│   │   ├── __init__.py       # Route aggregation
│   │   ├── csrf.py           # CSRF token management
│   │   ├── register.py       # User registration
│   │   ├── login.py          # Login and beta login
│   │   ├── oauth.py          # OAuth (Google/Apple)
│   │   ├── password_reset.py # Password reset workflow
│   │   ├── tokens.py         # Token refresh and logout
│   │   ├── user.py           # User info and session management
│   │   ├── config.py         # Auth configuration
│   │   └── utils.py          # Shared auth helpers
│   ├── sessions/     # Solve session endpoints (6 modules)
│   │   ├── __init__.py       # Route aggregation
│   │   ├── create.py         # Create sessions
│   │   ├── list.py           # List and retrieve sessions
│   │   ├── stream.py         # SSE streaming messages
│   │   ├── update.py         # Update session title
│   │   ├── delete.py         # Delete sessions
│   │   └── utils.py          # Shared session helpers
│   ├── learn/        # Learning session endpoints (5 modules)
│   │   ├── __init__.py       # Route aggregation + methodology prompts
│   │   ├── create.py         # Create learning sessions
│   │   ├── message.py        # Send messages and SSE streaming
│   │   ├── history.py        # Session history and messages
│   │   └── utils.py          # Learning session helpers
│   ├── account.py    # Account management
│   ├── config.py     # Feature flags
│   ├── subscriptions.py      # Subscription management
│   ├── webhooks.py           # Stripe webhooks
│   └── revenuecat_webhooks.py # RevenueCat webhooks
├── startup/          # Application initialization (6 modules)
│   ├── __init__.py   # Exports create_app
│   ├── app.py        # Application factory
│   ├── config.py     # OpenAPI configuration
│   ├── lifespan.py   # Lifecycle events
│   ├── middleware.py # CORS, CSRF, rate limiting, metrics
│   └── routes.py     # Route and exception handler registration
├── services/         # Business logic layer
├── models/           # SQLAlchemy ORM models
├── schemas/          # Pydantic request/response schemas
├── middleware/       # Custom middleware
└── utils/            # Shared utilities
```

### Modular architecture benefits

- **Maintainability**: Each module focuses on a single responsibility (50-200 lines)
- **Collaboration**: Multiple developers can work on different modules without conflicts
- **Testability**: Independent modules are easier to test in isolation
- **Scalability**: New features can be added as new modules without touching existing code
- **Code reuse**: Shared utilities prevent code duplication (50+ lines eliminated)

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
