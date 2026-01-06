# AGENTS.md - Solacore Codebase Guide

> Guidelines for AI coding agents working in this monorepo.

## Project Structure

```
solacore/
├── solacore-api/      # FastAPI backend (Python 3.11+)
├── solacore-web/      # Next.js 16 web app (React 19, TypeScript)
├── solacore-mobile/   # Expo/React Native mobile app
└── docs/              # Documentation
```

---

## Build / Lint / Test Commands

### Backend (solacore-api)

```bash
cd solacore-api

# Setup
poetry install --with dev
cp .env.example .env
docker compose up -d db redis
poetry run alembic upgrade head

# Development
poetry run uvicorn app.main:app --reload

# Linting & Formatting
poetry run ruff check .                    # Lint
poetry run ruff check . --fix              # Lint + fix
poetry run ruff format .                   # Format
poetry run mypy app                        # Type check

# Testing
poetry run pytest                          # All tests
poetry run pytest tests/test_auth.py       # Single file
poetry run pytest tests/test_auth.py::test_register_success  # Single test
poetry run pytest -x                       # Stop on first failure
poetry run pytest --cov=app --cov-report=html  # Coverage report
```

### Web Frontend (solacore-web)

```bash
cd solacore-web

# Setup
npm install
cp .env.example .env.local

# Development
npm run dev

# Build & Lint
npm run build                              # Production build
npm run lint                               # ESLint
npx tsc --noEmit                           # Type check only
```

### Mobile (solacore-mobile)

```bash
cd solacore-mobile

# Setup
npm install

# Development
npx expo start

# Lint
npm run lint                               # ESLint
npm run lint:fix                           # ESLint + fix
npx tsc --noEmit                           # Type check
```

---

## Code Style Guidelines

### Python (solacore-api)

**Formatting**: Ruff (black-compatible) + isort (black profile)

**Imports**: Standard library → Third-party → Local (absolute imports)
```python
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.cache_service import CacheService
```

**Type Hints**: Required for function signatures
```python
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> User:
    ...
```

**Docstrings**: Chinese allowed, triple quotes
```python
async def export_account(...) -> dict[str, Any]:
    """导出当前账户的所有相关数据，便于数据携带与合规导出。"""
```

**Error Handling**: HTTPException with structured detail
```python
raise HTTPException(status_code=404, detail={"error": "USER_NOT_FOUND"})
raise HTTPException(status_code=409, detail={"error": "EMAIL_ALREADY_EXISTS"})
```

**Naming**: snake_case for functions/variables, PascalCase for classes

**Router Pattern**:
```python
router = APIRouter(prefix="/account", tags=["Account"])

@router.get("/export", summary="导出账户数据", responses={...})
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key)
async def export_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    ...
```

### TypeScript/React (solacore-web)

**Formatting**: Prettier (via lint-staged)

**Strict Mode**: Enabled in tsconfig.json

**Imports**: Use path aliases, group by type
```typescript
"use client";

import React, { useCallback, useContext, useEffect, useState } from "react";

import type { User } from "@/lib/types";
import { getCurrentUser, logout } from "@/lib/auth";
```

**Components**: Functional with explicit return types
```typescript
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  ...
}
```

**Hooks**: Export custom hooks separately
```typescript
export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
```

**UI Components**: Use shadcn/ui pattern with cva
```typescript
import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva("base-classes", { variants: {...} });
```

**Naming**: camelCase for functions/variables, PascalCase for components

### React Native (solacore-mobile)

Same as solacore-web, plus:
- Use Expo SDK modules
- Platform-specific code via `.ios.tsx` / `.android.tsx` when needed

---

## Testing Patterns

### Python Tests (pytest + pytest-asyncio)

```python
"""认证相关测试"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """测试成功注册"""
    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123",
            "device_fingerprint": "test-device-001",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
```

**Fixtures**: Defined in `conftest.py`, use `client` fixture for API tests

**Test File Naming**: `test_*.py`

**Test Function Naming**: `test_<action>_<scenario>`

---

## Pre-commit Hooks

Root-level `.husky/pre-commit` runs:
1. `solacore-api`: `poetry run pre-commit run --all-files`
2. `solacore-web`: `npx lint-staged`
3. `solacore-mobile`: `npx lint-staged`

---

## Key Conventions

### Error Codes

Use uppercase snake_case error codes:
- `INVALID_CREDENTIALS`
- `USER_NOT_FOUND`
- `EMAIL_ALREADY_EXISTS`
- `INVALID_TOKEN`

### API Response Format

Success: Return data directly or with wrapper
```json
{"user": {...}, "message": "操作成功"}
```

Error: Structured error object
```json
{"error": "ERROR_CODE", "detail": "Human readable message"}
```

### Database

- PostgreSQL 15 with async SQLAlchemy
- Alembic for migrations: `poetry run alembic revision --autogenerate -m "message"`
- Redis for caching with TTL-based invalidation

### Authentication

- httpOnly cookies for tokens (access_token, refresh_token)
- CSRF protection via X-CSRF-Token header
- Device fingerprinting for session management

---

## Common Gotchas

1. **CSRF Token Required**: All POST/PUT/PATCH/DELETE requests need X-CSRF-Token header
2. **Async Everywhere**: Backend uses async/await throughout - don't mix sync calls
3. **Test Isolation**: Each test gets fresh DB state via `_truncate_tables()`
4. **Coverage Threshold**: Backend requires 85% coverage (`--cov-fail-under=85`)
5. **Type Checking**: Run `mypy app` before committing Python changes
6. **Path Aliases**: Use `@/` imports in TypeScript, never relative `../../`

---

## Quick Reference

| Task | Command |
|------|---------|
| Run API tests | `cd solacore-api && poetry run pytest` |
| Run single test | `poetry run pytest tests/test_auth.py::test_login_success` |
| Check Python types | `poetry run mypy app` |
| Format Python | `poetry run ruff format .` |
| Lint TypeScript | `cd solacore-web && npm run lint` |
| Check TS types | `npx tsc --noEmit` |
| Start API | `poetry run uvicorn app.main:app --reload` |
| Start Web | `cd solacore-web && npm run dev` |
| DB migration | `poetry run alembic upgrade head` |
| New migration | `poetry run alembic revision --autogenerate -m "desc"` |
