# Contributing Guide

Thanks for your interest in improving Solacore API. This guide explains how to set up the development environment, follow code standards, and submit changes safely.

## Development environment setup

- Requirements:
  - Python 3.11+
  - Poetry 1.7+
  - Docker + Docker Compose (for Postgres/Redis)

```bash
poetry install --with dev
cp .env.example .env

docker compose up -d db redis
poetry run alembic upgrade head

poetry run uvicorn app.main:app --reload
```

## Code standards

- Formatting and linting: Ruff
- Type checking: mypy

```bash
poetry run ruff format .
poetry run ruff check .
poetry run mypy app --ignore-missing-imports
```

Notes:
- Pre-commit also runs `ruff`, `ruff-format`, and `isort` automatically.

## Git hooks (pre-commit)

Install hooks to enforce linting, typing, and commit message rules:

```bash
./scripts/setup-hooks.sh
```

Hooks include:
- pre-commit: format + lint + mypy
- commit-msg: commit message format
- pre-push: pytest with coverage gate

## Commit message format

We use a conventional format enforced by `scripts/check-commit-msg.py`:

```
<type>(<scope>): <subject>
```

Allowed types:
- feat, fix, docs, style, refactor, perf, test, chore

Example:
```
feat(auth): add oauth refresh flow
```

## Branch naming

Use feature branches. The minimum requirement is:
- `feature/<short-name>`

Other common variants:
- `fix/<short-name>`
- `chore/<short-name>`

## Pull request workflow

1. Create a feature branch from `main`.
2. Keep PRs focused and small when possible.
3. Update docs if behavior or APIs change.
4. Run checks locally:
   - `ruff format` / `ruff check`
   - `mypy`
   - `pytest` with coverage
5. Open a PR and request at least 1 reviewer.
6. Address review feedback and keep the PR up to date.

## Testing requirements

Coverage must be >= 85% (enforced by pre-push hook):

```bash
poetry run pytest --cov=app --cov-fail-under=85
```

If you change critical logic, add tests covering:
- happy path
- expected error cases
- edge cases and timeouts

## Reporting issues

If you find a bug, please open an issue with:
- steps to reproduce
- expected vs actual behavior
- logs or stack traces (redact secrets)

Thanks for contributing.
