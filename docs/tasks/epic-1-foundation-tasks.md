# Epic 1: Foundation - Executable Task List

**Task List ID**: TASKS-EPIC-001
**Source**: `docs/plan/epic-1-foundation-plan.md`
**Created**: 2025-12-21
**Total Tasks**: 27

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Pending |
| 🔄 | In Progress |
| ✅ | Completed |
| ❌ | Blocked |
| 🔗 | Has Dependencies |

---

## Story 1.1: Initialize Mobile App Project

**Tasks**: 6 | **Priority**: P1 | **Can Parallel With**: Story 1.2

### ⬜ Task 1.1.1: Create Expo Project

| Field | Value |
|-------|-------|
| **ID** | T-1.1.1 |
| **Dependencies** | None (Entry Point) |
| **Commands** | `npx create-expo-app@latest clarity-mobile --template blank-typescript` |
| **Files Created** | `clarity-mobile/` (entire directory) |
| **Verification** | `cd clarity-mobile && npx expo --version` → outputs version |

---

### ⬜ Task 1.1.2: Setup Folder Structure 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.1.2 |
| **Dependencies** | T-1.1.1 |
| **Commands** | ```bash
mkdir -p clarity-mobile/app/{(tabs),auth,chat}
mkdir -p clarity-mobile/components/{ui,chat,common}
mkdir -p clarity-mobile/{services,stores,i18n,hooks,utils,constants,types}
``` |
| **Files Created** | 12 directories under `clarity-mobile/` |
| **Verification** | `ls clarity-mobile/app clarity-mobile/components clarity-mobile/services clarity-mobile/stores clarity-mobile/i18n` → all exist |

---

### ⬜ Task 1.1.3: Configure ESLint + Prettier 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.1.3 |
| **Dependencies** | T-1.1.1 |
| **Commands** | ```bash
cd clarity-mobile
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
npm install -D eslint-plugin-react eslint-plugin-react-hooks
``` |
| **Files Created** | `clarity-mobile/.eslintrc.js`, `clarity-mobile/.prettierrc` |
| **Files Modified** | `clarity-mobile/package.json` (add lint/format scripts) |
| **Verification** | `cd clarity-mobile && npm run lint` → exits 0 |

**File: `.eslintrc.js`**
```javascript
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
    ecmaFeatures: { jsx: true },
  },
  plugins: ['@typescript-eslint', 'react', 'react-hooks'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'prettier',
  ],
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
  },
  settings: {
    react: { version: 'detect' },
  },
};
```

**File: `.prettierrc`**
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

**package.json scripts addition:**
```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix",
    "format": "prettier --write \"**/*.{ts,tsx,js,json}\""
  }
}
```

---

### ⬜ Task 1.1.4: Setup Expo Router Navigation 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.1.4 |
| **Dependencies** | T-1.1.2 |
| **Commands** | `cd clarity-mobile && npx expo install expo-router expo-linking expo-constants expo-status-bar` |
| **Files Created** | `clarity-mobile/app/_layout.tsx`, `clarity-mobile/app/(tabs)/_layout.tsx`, `clarity-mobile/app/(tabs)/index.tsx`, `clarity-mobile/app/(tabs)/settings.tsx` |
| **Verification** | `cd clarity-mobile && npx expo start` → Expo Dev Server starts |

**File: `app/_layout.tsx`**
```typescript
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="auth" options={{ headerShown: false }} />
    </Stack>
  );
}
```

**File: `app/(tabs)/_layout.tsx`**
```typescript
import { Tabs } from 'expo-router';

export default function TabLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: 'Home' }} />
      <Tabs.Screen name="settings" options={{ title: 'Settings' }} />
    </Tabs>
  );
}
```

**File: `app/(tabs)/index.tsx`**
```typescript
import { View, Text, StyleSheet } from 'react-native';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Clarity</Text>
      <Text style={styles.subtitle}>Your universal problem-solving assistant</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 32, fontWeight: 'bold' },
  subtitle: { fontSize: 16, color: '#666', marginTop: 8 },
});
```

**File: `app/(tabs)/settings.tsx`**
```typescript
import { View, Text, StyleSheet } from 'react-native';

export default function SettingsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Settings</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: 'bold' },
});
```

---

### ⬜ Task 1.1.5: Test iOS/Android Build 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.1.5 |
| **Dependencies** | T-1.1.4 |
| **Commands** | iOS: `npx expo run:ios`<br>Android: `npx expo run:android`<br>Fallback: `npx expo start --go` |
| **Files Created** | None |
| **Verification** | App renders Home screen on simulator/Expo Go |

---

### ⬜ Task 1.1.6: Create Mobile README 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.1.6 |
| **Dependencies** | T-1.1.5 |
| **Commands** | None (file creation only) |
| **Files Created** | `clarity-mobile/README.md` |
| **Verification** | File exists with setup instructions |
| **Story Completion Check** | `cd clarity-mobile && npm run lint && npx tsc --noEmit` → exits 0 |

**File: `clarity-mobile/README.md`**
```markdown
# Clarity Mobile

React Native + Expo 移动端应用

## 环境要求

- Node.js 18+
- npm 9+
- Expo CLI (`npx expo`)
- iOS: Xcode 15+ (macOS only)
- Android: Android Studio + Emulator

## 快速开始

# 安装依赖
npm install

# 启动开发服务器
npx expo start

# iOS 模拟器
npx expo run:ios

# Android 模拟器
npx expo run:android

## 目录结构

- `app/` - Expo Router 页面
- `components/` - React 组件
- `services/` - API 调用
- `stores/` - Zustand 状态管理
- `i18n/` - 国际化

## 代码规范

npm run lint      # ESLint 检查
npm run format    # Prettier 格式化
```

---

## Story 1.2: Initialize Backend API Project

**Tasks**: 7 | **Priority**: P1 | **Can Parallel With**: Story 1.1

### ⬜ Task 1.2.1: Create FastAPI Project with Poetry

| Field | Value |
|-------|-------|
| **ID** | T-1.2.1 |
| **Dependencies** | None (Entry Point) |
| **Commands** | ```bash
mkdir clarity-api && cd clarity-api
poetry init --name clarity-api --python "^3.11" --no-interaction
poetry add fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv
poetry add -D pytest pytest-asyncio httpx ruff mypy
``` |
| **Files Created** | `clarity-api/pyproject.toml`, `clarity-api/poetry.lock` |
| **Verification** | `cd clarity-api && poetry install` → succeeds |

---

### ⬜ Task 1.2.2: Setup Backend Folder Structure 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.2.2 |
| **Dependencies** | T-1.2.1 |
| **Commands** | ```bash
cd clarity-api
mkdir -p app/{routers,services,models,middleware,schemas}
mkdir -p tests
touch app/__init__.py app/routers/__init__.py app/services/__init__.py
touch app/models/__init__.py app/middleware/__init__.py app/schemas/__init__.py
``` |
| **Files Created** | 6 directories, 6 `__init__.py` files |
| **Verification** | `ls clarity-api/app/routers clarity-api/app/models` → directories exist |

---

### ⬜ Task 1.2.3: Configure Pydantic Settings 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.2.3 |
| **Dependencies** | T-1.2.2 |
| **Commands** | None (file creation) |
| **Files Created** | `clarity-api/app/config.py`, `clarity-api/.env.example` |
| **Verification** | `cd clarity-api && cp .env.example .env && poetry run python -c "from app.config import get_settings; print(get_settings().app_name)"` → outputs "Clarity API" |

**File: `app/config.py`**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置，从环境变量加载"""
    app_name: str = "Clarity API"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/clarity"
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**File: `.env.example`**
```bash
DEBUG=true
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/clarity
JWT_SECRET=your-secret-key-change-in-production
HOST=0.0.0.0
PORT=8000
```

---

### ⬜ Task 1.2.4: Create Main Application with Health Check 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.2.4 |
| **Dependencies** | T-1.2.3 |
| **Commands** | None (file creation) |
| **Files Created** | `clarity-api/app/main.py` |
| **Verification** | ```bash
cd clarity-api
poetry run uvicorn app.main:app --reload &
sleep 3 && curl http://localhost:8000/health
``` → returns `{"status":"healthy"}` |

**File: `app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Universal problem-solving assistant API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """根端点"""
    return {"message": "Welcome to Clarity API", "docs": "/docs"}
```

---

### ⬜ Task 1.2.5: Create Dockerfile 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.2.5 |
| **Dependencies** | T-1.2.4 |
| **Commands** | None (file creation) |
| **Files Created** | `clarity-api/Dockerfile` |
| **Verification** | `cd clarity-api && docker build -t clarity-api .` → builds successfully |

**File: `Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### ⬜ Task 1.2.6: Create docker-compose.yml 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.2.6 |
| **Dependencies** | T-1.2.5 |
| **Commands** | None (file creation) |
| **Files Created** | `clarity-api/docker-compose.yml` |
| **Verification** | `cd clarity-api && docker-compose up -d && curl http://localhost:8000/health && docker-compose down` → returns healthy |

**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/clarity
    depends_on:
      - db
    volumes:
      - ./app:/app/app

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=clarity
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

### ⬜ Task 1.2.7: Create Backend README 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.2.7 |
| **Dependencies** | T-1.2.6 |
| **Commands** | None (file creation) |
| **Files Created** | `clarity-api/README.md` |
| **Verification** | File exists with complete instructions |
| **Story Completion Check** | `cd clarity-api && poetry run ruff check . && poetry run mypy app --ignore-missing-imports` → exits 0 |

---

## Story 1.3: Set Up PostgreSQL Database

**Tasks**: 6 | **Priority**: P1 | **Depends On**: Story 1.2

### ⬜ Task 1.3.1: Add Database Dependencies 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.3.1 |
| **Dependencies** | T-1.2.6 (docker-compose with db) |
| **Commands** | `cd clarity-api && poetry add sqlalchemy[asyncio] asyncpg alembic greenlet` |
| **Files Modified** | `clarity-api/pyproject.toml`, `clarity-api/poetry.lock` |
| **Verification** | `poetry show sqlalchemy` → shows version |

---

### ⬜ Task 1.3.2: Configure Async SQLAlchemy Engine 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.3.2 |
| **Dependencies** | T-1.3.1 |
| **Commands** | None (file creation) |
| **Files Created** | `clarity-api/app/database.py` |
| **Verification** | `poetry run python -c "from app.database import engine; print(engine)"` → outputs Engine |

**File: `app/database.py`**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    """依赖注入：获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

### ⬜ Task 1.3.3: Initialize Alembic 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.3.3 |
| **Dependencies** | T-1.3.2 |
| **Commands** | `cd clarity-api && poetry run alembic init alembic` |
| **Files Created** | `clarity-api/alembic/`, `clarity-api/alembic.ini` |
| **Files Modified** | `clarity-api/alembic/env.py` (async config) |
| **Verification** | `ls clarity-api/alembic/` → env.py, versions/, script.py.mako exist |

**File: `alembic/env.py` (replace content)**
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.config import get_settings
from app.database import Base
from app.models import *

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

### ⬜ Task 1.3.4: Create User Model and Initial Migration 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.3.4 |
| **Dependencies** | T-1.3.3 |
| **Commands** | ```bash
cd clarity-api
docker-compose up -d db
poetry run alembic revision --autogenerate -m "create users table"
``` |
| **Files Created** | `clarity-api/app/models/user.py`, `clarity-api/alembic/versions/*_create_users_table.py` |
| **Files Modified** | `clarity-api/app/models/__init__.py` |
| **Verification** | `ls clarity-api/alembic/versions/` → migration file exists |

**File: `app/models/user.py`**
```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class User(Base):
    """用户模型 - 初始版本"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"
```

**File: `app/models/__init__.py`**
```python
from app.models.user import User

__all__ = ["User"]
```

---

### ⬜ Task 1.3.5: Run Migration 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.3.5 |
| **Dependencies** | T-1.3.4 |
| **Commands** | `cd clarity-api && poetry run alembic upgrade head` |
| **Files Modified** | Database (creates tables) |
| **Verification** | `docker exec -it clarity-api-db-1 psql -U postgres -d clarity -c "\dt"` → shows users, alembic_version |

---

### ⬜ Task 1.3.6: Update Health Check with Database Status 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.3.6 |
| **Dependencies** | T-1.3.5 |
| **Commands** | None (file modification) |
| **Files Modified** | `clarity-api/app/main.py` |
| **Verification** | `curl http://localhost:8000/health` → `{"status":"healthy","database":"ok"}` |
| **Story Completion Check** | `poetry run alembic upgrade head` exits 0 + `/health` returns `{"database":"ok"}` |

**File: `app/main.py` (updated)**
```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import get_db

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Universal problem-solving assistant API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查端点（含数据库状态）"""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    status = "healthy" if db_status == "ok" else "degraded"
    return {"status": status, "database": db_status}


@app.get("/")
async def root():
    return {"message": "Welcome to Clarity API", "docs": "/docs"}
```

---

## Story 1.4: Configure CI/CD Pipeline

**Tasks**: 4 | **Priority**: P2 | **Depends On**: Story 1.1, 1.2, 1.3

### ⬜ Task 1.4.1: Create Backend CI Workflow 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.4.1 |
| **Dependencies** | T-1.3.6 |
| **Commands** | `mkdir -p .github/workflows` |
| **Files Created** | `.github/workflows/backend.yml` |
| **Verification** | Push to GitHub → CI runs, lint/test jobs pass |

**File: `.github/workflows/backend.yml`**
```yaml
name: Backend CI

on:
  push:
    branches: [main]
    paths: ['clarity-api/**', '.github/workflows/backend.yml']
  pull_request:
    branches: [main]
    paths: ['clarity-api/**', '.github/workflows/backend.yml']

defaults:
  run:
    working-directory: clarity-api

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install poetry
      - run: poetry install
      - run: poetry run ruff check .
      - run: poetry run mypy app --ignore-missing-imports

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: clarity_test
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install poetry
      - run: poetry install
      - run: poetry run alembic upgrade head
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/clarity_test
      - run: poetry run pytest -v
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/clarity_test
```

---

### ⬜ Task 1.4.2: Create Mobile CI Workflow 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.4.2 |
| **Dependencies** | T-1.1.6 |
| **Commands** | None (file creation) |
| **Files Created** | `.github/workflows/mobile.yml` |
| **Verification** | Push to GitHub → CI runs, lint job passes |

**File: `.github/workflows/mobile.yml`**
```yaml
name: Mobile CI

on:
  push:
    branches: [main]
    paths: ['clarity-mobile/**', '.github/workflows/mobile.yml']
  pull_request:
    branches: [main]
    paths: ['clarity-mobile/**', '.github/workflows/mobile.yml']

defaults:
  run:
    working-directory: clarity-mobile

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: clarity-mobile/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit

  eas-build-dry:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: npm ci
      - run: eas build --platform all --non-interactive --dry-run || true
```

---

### ⬜ Task 1.4.3: Configure Branch Protection 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.4.3 |
| **Dependencies** | T-1.4.1, T-1.4.2 |
| **Commands** | GitHub Web UI: Settings → Branches → Add rule |
| **Configuration** | Branch: `main`, Require PR, Require status checks (lint, test) |
| **Verification** | Direct push to main is rejected |

---

### ⬜ Task 1.4.4: Setup EAS Build 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.4.4 |
| **Dependencies** | T-1.1.6 |
| **Commands** | ```bash
cd clarity-mobile
npx eas login
npx eas build:configure
``` |
| **Files Created** | `clarity-mobile/eas.json` |
| **Verification** | `npx eas build --platform all --non-interactive --dry-run` → shows config |
| **Story Completion Check** | All CI workflows exist in `.github/workflows/` + Branch protection configured |

**File: `eas.json`**
```json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": { "developmentClient": true, "distribution": "internal" },
    "preview": { "distribution": "internal" },
    "production": {}
  },
  "submit": { "production": {} }
}
```

---

## Story 1.5: Set Up Development Environment Documentation

**Tasks**: 4 | **Priority**: P2 | **Depends On**: Story 1.1, 1.2, 1.3

### ⬜ Task 1.5.1: Create Root README 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.5.1 |
| **Dependencies** | T-1.3.6 |
| **Commands** | None (file creation) |
| **Files Created** | `README.md` |
| **Verification** | File exists with project overview |

---

### ⬜ Task 1.5.2: Create Setup Guide 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.5.2 |
| **Dependencies** | T-1.5.1 |
| **Commands** | None (file creation) |
| **Files Created** | `docs/setup.md` |
| **Verification** | Developer can follow guide and run project in < 30 min |

---

### ⬜ Task 1.5.3: Create Troubleshooting Guide 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.5.3 |
| **Dependencies** | T-1.5.2 |
| **Commands** | None (file creation) |
| **Files Created** | `docs/troubleshooting.md` |
| **Verification** | Common issues documented with solutions |

---

### ⬜ Task 1.5.4: Add Architecture Diagram 🔗

| Field | Value |
|-------|-------|
| **ID** | T-1.5.4 |
| **Dependencies** | T-1.5.3 |
| **Commands** | None (file modification) |
| **Files Modified** | `docs/setup.md` |
| **Description** | Copy/embed the ASCII architecture diagram from `docs/architecture.md` into `docs/setup.md` under a new "## Architecture Overview" section |
| **Verification** | `docs/setup.md` contains ASCII diagram showing Mobile → API → PostgreSQL flow |
| **Story Completion Check** | All docs exist: `README.md`, `docs/setup.md`, `docs/troubleshooting.md` with architecture diagram |

**Content to add in `docs/setup.md`:**
```markdown
## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  clarity-mobile │────▶│   clarity-api   │────▶│   PostgreSQL    │
│  (React Native) │     │    (FastAPI)    │     │    (Docker)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        ▼                       ▼
   Expo Router              /health
   Tab Navigation           /docs (Swagger)
```

For detailed architecture, see [docs/architecture.md](architecture.md).
```

---

## Dependency Graph

```
                    T-1.1.1 ──────────────────────────┐
                       │                              │
              ┌────────┼────────┐                     │
              ▼        ▼        │                     │
          T-1.1.2  T-1.1.3      │                     │
              │                 │                     │
              ▼                 │                     │
          T-1.1.4               │                     │
              │                 │                     │
              ▼                 │                     │
          T-1.1.5               │                     │
              │                 │                     │
              ▼                 │                     │
          T-1.1.6 ─────────────►├─────────► T-1.4.2   │
                                │               │     │
                                │               ▼     │
T-1.2.1                         │           T-1.4.3 ◄─┤
    │                           │               │     │
    ▼                           │               │     │
T-1.2.2                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.2.3                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.2.4                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.2.5                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.2.6                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.2.7                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.3.1                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.3.2                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.3.3                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.3.4                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.3.5                         │               │     │
    │                           │               │     │
    ▼                           │               │     │
T-1.3.6 ────────────────────────┴─────► T-1.4.1     │
    │                                       │       │
    │                                       ▼       │
    │                                   T-1.4.3 ◄───┤
    │                                       │       │
    ▼                                       │       │
T-1.5.1                                     │       │
    │                                       │       │
    ▼                                       │       │
T-1.5.2                                     │       │
    │                                       │       │
    ▼                                       │       │
T-1.5.3                             T-1.4.4 ◄───────┘
    │
    ▼
T-1.5.4
```

---

## Parallel Execution Strategy

### Wave 1 (Entry Points)
- **T-1.1.1** (Create Expo Project)
- **T-1.2.1** (Create FastAPI Project)

### Wave 2 (After Wave 1)
- **T-1.1.2, T-1.1.3** (parallel)
- **T-1.2.2** → **T-1.2.3** → **T-1.2.4** → **T-1.2.5** → **T-1.2.6** → **T-1.2.7**

### Wave 3 (After Backend Ready)
- **T-1.1.4** → **T-1.1.5** → **T-1.1.6**
- **T-1.3.1** → **T-1.3.2** → **T-1.3.3** → **T-1.3.4** → **T-1.3.5** → **T-1.3.6**

### Wave 4 (After Database Ready)
- **T-1.4.1** (Backend CI)
- **T-1.4.2** (Mobile CI) - can run with T-1.1.6
- **T-1.5.1** → **T-1.5.2** → **T-1.5.3** → **T-1.5.4**
- **T-1.4.4** (EAS Setup)

### Wave 5 (Final)
- **T-1.4.3** (Branch Protection) - requires T-1.4.1 + T-1.4.2

---

## Summary

| Story | Tasks | Status |
|-------|-------|--------|
| 1.1 Mobile Init | 6 | ⬜ 0/6 |
| 1.2 Backend Init | 7 | ⬜ 0/7 |
| 1.3 Database | 6 | ⬜ 0/6 |
| 1.4 CI/CD | 4 | ⬜ 0/4 |
| 1.5 Documentation | 4 | ⬜ 0/4 |
| **Total** | **27** | **⬜ 0/27** |

---

## Change Log

| Date | Version | Description |
|------|---------|-------------|
| 2025-12-21 | 1.0 | Initial task list from Epic 1 plan |
| 2025-12-21 | 1.1 | Fix gaps: add T-1.5.4 (Architecture Diagram), add Story Completion Checks, correct task count to 27 |

---

*This task list is derived from `docs/plan/epic-1-foundation-plan.md` and follows the Constitution principles.*
