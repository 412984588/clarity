# Epic 2: User Authentication - Executable Tasks

> **Version**: 1.0
> **Created**: 2025-12-22
> **Input**: docs/plan/epic-2-auth-plan.md
> **Total**: 28 tasks / 5 phases

---

## Phase 1: Core Authentication (Story 2.1 + 2.2)

### T-2.1.1: Add Auth Dependencies

| Item | Value |
|------|-------|
| **Command** | `cd solacore-api && poetry add passlib[bcrypt] python-jose[cryptography] httpx` |
| **Files** | `pyproject.toml`, `poetry.lock` |
| **Verify** | `poetry show passlib` 显示版本 |
| **Depends** | None |

---

### T-2.1.2: Create Auth Schemas

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-api/app/schemas/auth.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.schemas.auth import RegisterRequest; print('OK')"` |
| **Depends** | None |

---

### T-2.1.3: Extend User Model

| Item | Value |
|------|-------|
| **Command** | 更新文件 |
| **Files** | `solacore-api/app/models/user.py` (update) |
| **Verify** | `cd solacore-api && python -c "from app.models.user import User; print('OK')"` |
| **Depends** | None |

---

### T-2.1.4: Create Security Utilities

| Item | Value |
|------|-------|
| **Command** | 创建目录和文件 |
| **Files** | `solacore-api/app/utils/__init__.py`, `solacore-api/app/utils/security.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.utils.security import hash_password; print('OK')"` |
| **Depends** | T-2.1.1 (passlib), T-2.1.11 (config) |

---

### T-2.1.5: Create Device Model

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-api/app/models/device.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.models.device import Device; print('OK')"` |
| **Depends** | T-2.1.3 (User model) |

---

### T-2.1.6: Create ActiveSession Model

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-api/app/models/session.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.models.session import ActiveSession; print('OK')"` |
| **Depends** | T-2.1.3, T-2.1.5 |

---

### T-2.1.7: Create Subscription Model

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-api/app/models/subscription.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.models.subscription import Subscription, Usage; print('OK')"` |
| **Depends** | T-2.1.3 |

---

### T-2.1.8: Update Models __init__.py

| Item | Value |
|------|-------|
| **Command** | 更新文件 |
| **Files** | `solacore-api/app/models/__init__.py` (update) |
| **Verify** | `cd solacore-api && python -c "from app.models import User, Device, ActiveSession; print('OK')"` |
| **Depends** | T-2.1.3, T-2.1.5, T-2.1.6, T-2.1.7 |

---

### T-2.1.9: Create Auth Service

| Item | Value |
|------|-------|
| **Command** | 创建目录和文件 |
| **Files** | `solacore-api/app/services/__init__.py`, `solacore-api/app/services/auth_service.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.services.auth_service import AuthService; print('OK')"` |
| **Depends** | T-2.1.2, T-2.1.4, T-2.1.8 |

---

### T-2.1.10: Create Auth Router

| Item | Value |
|------|-------|
| **Command** | 创建目录和文件 |
| **Files** | `solacore-api/app/routers/__init__.py`, `solacore-api/app/routers/auth.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.routers.auth import router; print('OK')"` |
| **Depends** | T-2.1.9 |

---

### T-2.1.11: Update Config with JWT Settings

| Item | Value |
|------|-------|
| **Command** | 更新文件 |
| **Files** | `solacore-api/app/config.py` (update) |
| **Verify** | `cd solacore-api && python -c "from app.config import get_settings; s=get_settings(); print(s.jwt_algorithm)"` |
| **Depends** | None |

---

### T-2.1.12: Register Auth Router in Main

| Item | Value |
|------|-------|
| **Command** | 更新文件 |
| **Files** | `solacore-api/app/main.py` (update) |
| **Verify** | `curl http://localhost:8000/docs` 显示 auth 相关端点 |
| **Depends** | T-2.1.10 |

---

### T-2.1.13: Create Migration for Auth Tables

| Item | Value |
|------|-------|
| **Command** | `cd solacore-api && poetry run alembic revision --autogenerate -m "add auth tables" && poetry run alembic upgrade head` |
| **Files** | `alembic/versions/*.py` (auto-generated) |
| **Verify** | `psql -c "\dt"` 显示 users, devices, active_sessions, subscriptions, usage |
| **Depends** | T-2.1.8 |

---

### T-2.1.14: Create Auth Tests

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-api/tests/test_auth.py` (new) |
| **Verify** | `cd solacore-api && poetry run pytest tests/test_auth.py -v` 全绿 |
| **Depends** | T-2.1.12, T-2.1.13 |

---

## Phase 2: OAuth Integration (Story 2.3 + 2.4)

### T-2.3.1: Add Google OAuth Dependencies

| Item | Value |
|------|-------|
| **Command** | `cd solacore-api && poetry add google-auth` |
| **Files** | `pyproject.toml`, `poetry.lock` |
| **Verify** | `poetry show google-auth` 显示版本 |
| **Depends** | T-2.1.14 |

---

### T-2.3.2: Create OAuth Service

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-api/app/services/oauth_service.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.services.oauth_service import OAuthService; print('OK')"` |
| **Depends** | T-2.3.1, T-2.1.9 |

---

### T-2.3.3: Add OAuth Routes

| Item | Value |
|------|-------|
| **Command** | 更新文件 |
| **Files** | `solacore-api/app/routers/auth.py` (append) |
| **Verify** | `curl http://localhost:8000/docs` 显示 /auth/oauth/google, /auth/oauth/apple |
| **Depends** | T-2.3.2 |

---

## Phase 3: Device Binding (Story 2.5)

### T-2.5.1: Create Auth Middleware

| Item | Value |
|------|-------|
| **Command** | 创建目录和文件 |
| **Files** | `solacore-api/app/middleware/__init__.py`, `solacore-api/app/middleware/auth.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.middleware.auth import get_current_user; print('OK')"` |
| **Depends** | T-2.1.4 |

---

### T-2.5.2: Add Device Management Routes

| Item | Value |
|------|-------|
| **Command** | 更新文件 |
| **Files** | `solacore-api/app/routers/auth.py` (append) |
| **Verify** | `curl http://localhost:8000/docs` 显示 /auth/devices, /auth/me |
| **Depends** | T-2.5.1 |

---

## Phase 4: Mobile Auth UI (Story 2.6)

### T-2.6.1: Install Mobile Auth Dependencies

| Item | Value |
|------|-------|
| **Command** | `cd solacore-mobile && npm install expo-secure-store expo-auth-session expo-apple-authentication expo-crypto zustand react-hook-form @hookform/resolvers zod` |
| **Files** | `package.json`, `package-lock.json` |
| **Verify** | `npm ls expo-secure-store` 显示版本 |
| **Depends** | None |

---

### T-2.6.2: Create Auth Store

| Item | Value |
|------|-------|
| **Command** | 创建目录和文件 |
| **Files** | `solacore-mobile/stores/authStore.ts` (new) |
| **Verify** | `npx tsc --noEmit` 无错误 |
| **Depends** | T-2.6.1 |

---

### T-2.6.3: Create API Service

| Item | Value |
|------|-------|
| **Command** | 创建目录和文件 |
| **Files** | `solacore-mobile/services/api.ts` (new) |
| **Verify** | `npx tsc --noEmit` 无错误 |
| **Depends** | T-2.6.2 |

---

### T-2.6.4: Create Auth Service

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-mobile/services/auth.ts` (new) |
| **Verify** | `npx tsc --noEmit` 无错误 |
| **Depends** | T-2.6.3 |

---

### T-2.6.5: Create Login Screen

| Item | Value |
|------|-------|
| **Command** | 创建目录和文件 |
| **Files** | `solacore-mobile/app/(auth)/login.tsx` (new) |
| **Verify** | `npx tsc --noEmit` 无错误 |
| **Depends** | T-2.6.4 |

---

### T-2.6.6: Create Register Screen

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-mobile/app/(auth)/register.tsx` (new) |
| **Verify** | `npx tsc --noEmit` 无错误 |
| **Depends** | T-2.6.4 |

---

### T-2.6.7: Create Auth Layout

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-mobile/app/(auth)/_layout.tsx` (new) |
| **Verify** | `npx expo start` 无报错 |
| **Depends** | T-2.6.5, T-2.6.6 |

---

## Phase 5: Password Reset (Story 2.7)

### T-2.7.1: Create Password Reset Model

| Item | Value |
|------|-------|
| **Command** | 创建文件 |
| **Files** | `solacore-api/app/models/password_reset.py` (new) |
| **Verify** | `cd solacore-api && python -c "from app.models.password_reset import PasswordReset; print('OK')"` |
| **Depends** | T-2.1.3 |

---

### T-2.7.2: Add Password Reset to Auth Service

| Item | Value |
|------|-------|
| **Command** | 更新文件 |
| **Files** | `solacore-api/app/services/auth_service.py` (append) |
| **Verify** | `cd solacore-api && python -c "from app.services.auth_service import AuthService; print('OK')"` |
| **Depends** | T-2.7.1 |

---

### T-2.7.3: Add Password Reset Routes

| Item | Value |
|------|-------|
| **Command** | 更新文件 |
| **Files** | `solacore-api/app/routers/auth.py` (append) |
| **Verify** | `curl http://localhost:8000/docs` 显示 /auth/forgot-password, /auth/reset-password |
| **Depends** | T-2.7.2 |

---

## Execution Sequence (Topological Order)

```
Wave 1 (Parallel):
├── T-2.1.1  (Add deps)
├── T-2.1.2  (Schemas)
├── T-2.1.3  (User model)
├── T-2.1.11 (Config)
└── T-2.6.1  (Mobile deps)

Wave 2 (Parallel, after Wave 1):
├── T-2.1.4  (Security utils)
├── T-2.1.5  (Device model)
├── T-2.1.7  (Subscription model)
└── T-2.6.2  (Auth store)

Wave 3 (Parallel, after Wave 2):
├── T-2.1.6  (Session model)
├── T-2.7.1  (PasswordReset model)
└── T-2.6.3  (API service)

Wave 4 (Sequential):
├── T-2.1.8  (Models __init__)
└── T-2.6.4  (Auth service mobile)

Wave 5 (Sequential):
├── T-2.1.9  (Auth service)
├── T-2.6.5  (Login screen)
└── T-2.6.6  (Register screen)

Wave 6 (Sequential):
├── T-2.1.10 (Auth router)
├── T-2.5.1  (Auth middleware)
└── T-2.6.7  (Auth layout)

Wave 7 (Sequential):
├── T-2.1.12 (Register in main)
├── T-2.5.2  (Device routes)
└── T-2.7.2  (Password reset service)

Wave 8 (Sequential):
├── T-2.1.13 (Migration)
└── T-2.7.3  (Password reset routes)

Wave 9 (Sequential):
├── T-2.1.14 (Tests)
└── T-2.3.1  (Google deps)

Wave 10 (Sequential):
├── T-2.3.2  (OAuth service)
└── T-2.3.3  (OAuth routes)
```

---

## Git Commit Milestones

| Milestone | Tasks | Commit Message |
|-----------|-------|----------------|
| M1 | T-2.1.1 ~ T-2.1.8 | `feat(auth): add user/device/session models` |
| M2 | T-2.1.9 ~ T-2.1.14 | `feat(auth): implement email registration and login` |
| M3 | T-2.3.1 ~ T-2.3.3 | `feat(auth): add Google and Apple OAuth` |
| M4 | T-2.5.1 ~ T-2.5.2 | `feat(auth): implement device binding` |
| M5 | T-2.6.1 ~ T-2.6.7 | `feat(mobile): add auth UI screens` |
| M6 | T-2.7.1 ~ T-2.7.3 | `feat(auth): implement password reset flow` |

---

## Final Verification Checklist

### Backend

```bash
cd solacore-api

# Lint
poetry run ruff check .
poetry run mypy app --ignore-missing-imports

# Tests
poetry run pytest -v

# Manual API tests
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123","device_fingerprint":"fp-001"}'

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123","device_fingerprint":"fp-001"}'
```

### Mobile

```bash
cd solacore-mobile

# Lint & Type check
npm run lint
npx tsc --noEmit

# Run on simulator
npx expo start
```
