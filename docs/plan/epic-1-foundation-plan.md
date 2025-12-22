# Epic 1: Foundation - Tech Implementation Plan

**Plan ID**: PLAN-EPIC-001
**Source**: `docs/spec/epic-1-foundation.md`
**Created**: 2025-12-21
**Status**: Ready for Execution

---

## Overview

本计划将 Epic 1 的 5 个 Stories 拆解为可执行的技术任务，每个任务包含：
- 具体步骤和命令
- 文件/目录落点
- 验收方式

---

## Story 1.1: Initialize Mobile App Project

**预估**: 4 hours | **优先级**: P1

### Task 1.1.1: Create Expo Project

**步骤**:
```bash
# 进入项目根目录
cd /Users/zhimingdeng/Documents/claude/clarity

# 创建 Expo 项目（TypeScript 模板）
npx create-expo-app@latest clarity-mobile --template blank-typescript

# 进入移动端目录
cd clarity-mobile
```

**产出**: `clarity-mobile/` 目录

**验收**:
```bash
cd clarity-mobile && npx expo --version
# 预期：输出 Expo CLI 版本号
```

### Task 1.1.2: Setup Folder Structure

**步骤**:
```bash
cd clarity-mobile

# 创建标准目录结构
mkdir -p app/{(tabs),auth,chat}
mkdir -p components/{ui,chat,common}
mkdir -p services
mkdir -p stores
mkdir -p i18n
mkdir -p hooks
mkdir -p utils
mkdir -p constants
mkdir -p types
```

**产出目录结构**:
```
clarity-mobile/
├── app/                    # Expo Router 页面
│   ├── (tabs)/            # Tab 导航组
│   ├── auth/              # 认证相关页面
│   └── chat/              # 聊天相关页面
├── components/            # React 组件
│   ├── ui/               # 基础 UI 组件
│   ├── chat/             # 聊天相关组件
│   └── common/           # 通用组件
├── services/             # API 调用层
├── stores/               # 状态管理 (Zustand)
├── i18n/                 # 国际化文件
├── hooks/                # 自定义 Hooks
├── utils/                # 工具函数
├── constants/            # 常量定义
└── types/                # TypeScript 类型
```

**验收**:
```bash
ls -la app components services stores i18n hooks utils constants types
# 预期：所有目录存在
```

### Task 1.1.3: Configure ESLint + Prettier

**步骤**:
```bash
cd clarity-mobile

# 安装 ESLint + Prettier
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
npm install -D eslint-plugin-react eslint-plugin-react-hooks
```

**创建文件**: `clarity-mobile/.eslintrc.js`
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

**创建文件**: `clarity-mobile/.prettierrc`
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

**更新**: `clarity-mobile/package.json` scripts
```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix",
    "format": "prettier --write \"**/*.{ts,tsx,js,json}\""
  }
}
```

**验收**:
```bash
npm run lint
# 预期：0 errors, 0 warnings（或只有可忽略的警告）
```

### Task 1.1.4: Setup Expo Router Navigation

**步骤**:
```bash
cd clarity-mobile

# 安装 Expo Router
npx expo install expo-router expo-linking expo-constants expo-status-bar
```

**创建文件**: `clarity-mobile/app/_layout.tsx`
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

**创建文件**: `clarity-mobile/app/(tabs)/_layout.tsx`
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

**创建文件**: `clarity-mobile/app/(tabs)/index.tsx`
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

**验收**:
```bash
npx expo start
# 预期：Expo Dev Server 启动，扫码可在 Expo Go 中查看
```

### Task 1.1.5: Test iOS/Android Build

**iOS 验收**:
```bash
npx expo run:ios
# 预期：iOS 模拟器启动并显示 Home 页面
```

**Android 验收**:
```bash
npx expo run:android
# 预期：Android 模拟器启动并显示 Home 页面
```

**Fallback（无模拟器时）**:
```bash
npx expo start --go
# 使用 Expo Go 扫码测试
```

### Task 1.1.6: Create Mobile README

**创建文件**: `clarity-mobile/README.md`
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

```bash
# 安装依赖
npm install

# 启动开发服务器
npx expo start

# iOS 模拟器
npx expo run:ios

# Android 模拟器
npx expo run:android
```

## 目录结构

- `app/` - Expo Router 页面
- `components/` - React 组件
- `services/` - API 调用
- `stores/` - Zustand 状态管理
- `i18n/` - 国际化

## 代码规范

```bash
npm run lint      # ESLint 检查
npm run format    # Prettier 格式化
```
```

**验收**: 文件存在且内容完整

---

## Story 1.2: Initialize Backend API Project

**预估**: 4 hours | **优先级**: P1

### Task 1.2.1: Create FastAPI Project with Poetry

**步骤**:
```bash
cd /Users/zhimingdeng/Documents/claude/clarity

# 创建后端目录
mkdir clarity-api && cd clarity-api

# 初始化 Poetry 项目
poetry init --name clarity-api --python "^3.11" --no-interaction

# 添加核心依赖
poetry add fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv

# 添加开发依赖
poetry add -D pytest pytest-asyncio httpx ruff mypy
```

**验收**:
```bash
poetry install
# 预期：依赖安装成功，生成 poetry.lock
```

### Task 1.2.2: Setup Folder Structure

**步骤**:
```bash
cd clarity-api

# 创建标准目录结构
mkdir -p app/{routers,services,models,middleware,schemas}
touch app/__init__.py
touch app/routers/__init__.py
touch app/services/__init__.py
touch app/models/__init__.py
touch app/middleware/__init__.py
touch app/schemas/__init__.py
```

**产出目录结构**:
```
clarity-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 入口
│   ├── config.py         # Pydantic Settings
│   ├── routers/          # API 路由
│   ├── services/         # 业务逻辑
│   ├── models/           # SQLAlchemy 模型
│   ├── middleware/       # 中间件
│   └── schemas/          # Pydantic 模型
├── alembic/              # 数据库迁移（Story 1.3）
├── tests/                # 测试文件
├── pyproject.toml
└── poetry.lock
```

**验收**:
```bash
ls -la app app/routers app/services app/models app/middleware app/schemas
# 预期：所有目录和 __init__.py 存在
```

### Task 1.2.3: Configure Pydantic Settings

**创建文件**: `clarity-api/app/config.py`
```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置，从环境变量加载"""

    # 应用
    app_name: str = "Clarity API"
    debug: bool = False

    # 数据库
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/clarity"

    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # 服务器
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**创建文件**: `clarity-api/.env.example`
```bash
# Clarity API 环境变量

# 应用
DEBUG=true

# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/clarity

# JWT
JWT_SECRET=your-secret-key-change-in-production

# 服务器
HOST=0.0.0.0
PORT=8000
```

**验收**:
```bash
cp .env.example .env
poetry run python -c "from app.config import get_settings; print(get_settings().app_name)"
# 预期：输出 "Clarity API"
```

### Task 1.2.4: Create Main Application with Health Check

**创建文件**: `clarity-api/app/main.py`
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

# CORS 配置（开发环境允许所有来源）
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

**验收**:
```bash
poetry run uvicorn app.main:app --reload
# 另一个终端：
curl http://localhost:8000/health
# 预期：{"status":"healthy"}
```

### Task 1.2.5: Create Dockerfile

**创建文件**: `clarity-api/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装 Poetry
RUN pip install poetry

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装依赖（不创建虚拟环境）
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction

# 复制应用代码
COPY app ./app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**验收**:
```bash
docker build -t clarity-api .
# 预期：镜像构建成功
```

### Task 1.2.6: Create docker-compose.yml

**创建文件**: `clarity-api/docker-compose.yml`
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
      - ./app:/app/app  # 开发时热重载

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

**验收**:
```bash
docker-compose up -d
curl http://localhost:8000/health
# 预期：{"status":"healthy"}
docker-compose down
```

### Task 1.2.7: Create Backend README

**创建文件**: `clarity-api/README.md`
```markdown
# Clarity API

FastAPI 后端服务

## 环境要求

- Python 3.11+
- Poetry
- Docker + Docker Compose

## 快速开始

### 本地开发

```bash
# 安装依赖
poetry install

# 复制环境变量
cp .env.example .env

# 启动开发服务器
poetry run uvicorn app.main:app --reload
```

### Docker 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down
```

## API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 目录结构

- `app/main.py` - FastAPI 入口
- `app/config.py` - 配置管理
- `app/routers/` - API 路由
- `app/services/` - 业务逻辑
- `app/models/` - SQLAlchemy 模型
- `app/middleware/` - 中间件
- `app/schemas/` - Pydantic 模型

## 代码规范

```bash
poetry run ruff check .     # Lint
poetry run mypy app         # Type check
poetry run pytest           # Test
```
```

**验收**: 文件存在且内容完整

---

## Story 1.3: Set Up PostgreSQL Database

**预估**: 3 hours | **优先级**: P1

### Task 1.3.1: Add Database Dependencies

**步骤**:
```bash
cd clarity-api

# 添加数据库相关依赖
poetry add sqlalchemy[asyncio] asyncpg alembic greenlet
```

**验收**:
```bash
poetry show sqlalchemy
# 预期：显示 SQLAlchemy 版本信息
```

### Task 1.3.2: Configure Async SQLAlchemy Engine

**创建文件**: `clarity-api/app/database.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import get_settings

settings = get_settings()

# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=10,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 声明基类
Base = declarative_base()


async def get_db():
    """依赖注入：获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

**验收**:
```bash
poetry run python -c "from app.database import engine; print(engine)"
# 预期：输出 Engine 对象信息
```

### Task 1.3.3: Initialize Alembic

**步骤**:
```bash
cd clarity-api

# 初始化 Alembic
poetry run alembic init alembic
```

**修改文件**: `clarity-api/alembic/env.py`
```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.config import get_settings
from app.database import Base
from app.models import *  # 导入所有模型

config = context.config
settings = get_settings()

# 动态设置数据库 URL
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式迁移"""
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
    """异步模式迁移"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """在线模式迁移"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**验收**:
```bash
ls alembic/
# 预期：env.py, versions/, script.py.mako 存在
```

### Task 1.3.4: Create User Model and Initial Migration

**创建文件**: `clarity-api/app/models/user.py`
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

**更新文件**: `clarity-api/app/models/__init__.py`
```python
from app.models.user import User

__all__ = ["User"]
```

**生成迁移**:
```bash
# 确保数据库已启动
docker-compose up -d db

# 生成迁移文件
poetry run alembic revision --autogenerate -m "create users table"
```

**验收**:
```bash
ls alembic/versions/
# 预期：存在 *_create_users_table.py 文件
```

### Task 1.3.5: Run Migration

**步骤**:
```bash
# 执行迁移
poetry run alembic upgrade head
```

**验收**:
```bash
# 连接数据库检查
docker exec -it clarity-api-db-1 psql -U postgres -d clarity -c "\dt"
# 预期：显示 users 表和 alembic_version 表
```

### Task 1.3.6: Update Health Check with Database Status

**更新文件**: `clarity-api/app/main.py`
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
    status_code = 200 if db_status == "ok" else 503

    return {"status": status, "database": db_status}


@app.get("/")
async def root():
    return {"message": "Welcome to Clarity API", "docs": "/docs"}
```

**验收**:
```bash
# 数据库正常时
curl http://localhost:8000/health
# 预期：{"status":"healthy","database":"ok"}

# 数据库关闭时
docker-compose stop db
curl http://localhost:8000/health
# 预期：{"status":"degraded","database":"error"} 或连接错误
docker-compose start db
```

---

## Story 1.4: Configure CI/CD Pipeline

**预估**: 4 hours | **优先级**: P2

### Task 1.4.1: Create Backend CI Workflow

**创建目录**:
```bash
mkdir -p .github/workflows
```

**创建文件**: `.github/workflows/backend.yml`
```yaml
name: Backend CI

on:
  push:
    branches: [main]
    paths:
      - 'clarity-api/**'
      - '.github/workflows/backend.yml'
  pull_request:
    branches: [main]
    paths:
      - 'clarity-api/**'
      - '.github/workflows/backend.yml'

defaults:
  run:
    working-directory: clarity-api

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run Ruff (lint)
        run: poetry run ruff check .

      - name: Run MyPy (type check)
        run: poetry run mypy app --ignore-missing-imports

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: clarity_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run migrations
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/clarity_test
        run: poetry run alembic upgrade head

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/clarity_test
        run: poetry run pytest -v
```

**验收**: Push 到 GitHub 后 CI 执行成功

### Task 1.4.2: Create Mobile CI Workflow

**创建文件**: `.github/workflows/mobile.yml`
```yaml
name: Mobile CI

on:
  push:
    branches: [main]
    paths:
      - 'clarity-mobile/**'
      - '.github/workflows/mobile.yml'
  pull_request:
    branches: [main]
    paths:
      - 'clarity-mobile/**'
      - '.github/workflows/mobile.yml'

defaults:
  run:
    working-directory: clarity-mobile

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: clarity-mobile/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Run TypeScript check
        run: npx tsc --noEmit

  eas-build-dry:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Setup Expo
        uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}

      - name: Install dependencies
        run: npm ci

      - name: EAS Build (dry run)
        run: eas build --platform all --non-interactive --dry-run || true
```

**验收**: Push 到 GitHub 后 CI 执行成功

### Task 1.4.3: Configure Branch Protection

**步骤**（GitHub Web UI）:
1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. 勾选:
   - Require a pull request before merging
   - Require status checks to pass before merging
   - Select: `lint`, `test`
4. Save changes

**验收**: 尝试直接 push 到 main 被拒绝

### Task 1.4.4: Setup EAS Build

**步骤**:
```bash
cd clarity-mobile

# 登录 Expo
npx eas login

# 初始化 EAS 配置
npx eas build:configure
```

**创建/更新文件**: `clarity-mobile/eas.json`
```json
{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {}
  },
  "submit": {
    "production": {}
  }
}
```

**验收**:
```bash
npx eas build --platform all --non-interactive --dry-run
# 预期：显示构建配置摘要（不实际构建）
```

---

## Story 1.5: Set Up Development Environment Documentation

**预估**: 2 hours | **优先级**: P2

### Task 1.5.1: Create Root README

**创建文件**: `README.md`
```markdown
# Clarity

Universal problem-solving and decision-making assistant.

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker Desktop
- Poetry (`pip install poetry`)

### Setup

```bash
# Clone repository
git clone <repo-url>
cd clarity

# Start backend
cd clarity-api
poetry install
cp .env.example .env
docker-compose up -d db
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload

# Start mobile (in another terminal)
cd clarity-mobile
npm install
npx expo start
```

## Project Structure

```
clarity/
├── clarity-mobile/    # React Native + Expo 移动端
├── clarity-api/       # FastAPI 后端
├── docs/              # 文档
│   ├── prd.md        # 产品需求文档
│   ├── architecture.md
│   └── epics.md
└── .github/           # CI/CD
```

## Documentation

- [Setup Guide](docs/setup.md)
- [Architecture](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Mobile | React Native + Expo |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Auth | JWT + OAuth2 |
```

**验收**: 文件存在且格式正确

### Task 1.5.2: Create Setup Guide

**创建文件**: `docs/setup.md`
```markdown
# Development Setup Guide

**Last verified**: 2025-12-21

## System Requirements

| Tool | Version | Check Command |
|------|---------|---------------|
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Python | 3.11+ | `python3 --version` |
| Poetry | 1.6+ | `poetry --version` |
| Docker | 24+ | `docker --version` |

## Step 1: Clone Repository

```bash
git clone <repo-url>
cd clarity
```

## Step 2: Backend Setup

```bash
cd clarity-api

# Install dependencies
poetry install

# Copy environment variables
cp .env.example .env

# Start PostgreSQL
docker-compose up -d db

# Wait for database to be ready
sleep 5

# Run migrations
poetry run alembic upgrade head

# Start API server
poetry run uvicorn app.main:app --reload
```

Verify: http://localhost:8000/health should return `{"status":"healthy","database":"ok"}`

## Step 3: Mobile Setup

```bash
cd clarity-mobile

# Install dependencies
npm install

# Start Expo dev server
npx expo start
```

Options:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR with Expo Go app

## Environment Variables

### Backend (`clarity-api/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Enable debug mode | `true` |
| DATABASE_URL | PostgreSQL connection string | `postgresql+asyncpg://...` |
| JWT_SECRET | JWT signing key | (change in production!) |

## Common Issues

See [Troubleshooting Guide](troubleshooting.md)
```

**验收**: 文件存在且步骤可执行

### Task 1.5.3: Create Troubleshooting Guide

**创建文件**: `docs/troubleshooting.md`
```markdown
# Troubleshooting Guide

## Backend Issues

### Port 8000 already in use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
PORT=8001 poetry run uvicorn app.main:app --reload --port 8001
```

### Database connection refused

```bash
# Check if PostgreSQL is running
docker-compose ps

# Start database
docker-compose up -d db

# Check logs
docker-compose logs db
```

### Migration failed

```bash
# Check current migration status
poetry run alembic current

# Rollback one step
poetry run alembic downgrade -1

# Re-run migration
poetry run alembic upgrade head
```

### Poetry not found

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH (macOS/Linux)
export PATH="$HOME/.local/bin:$PATH"
```

## Mobile Issues

### Expo CLI not found

```bash
# Use npx (recommended)
npx expo start

# Or install globally
npm install -g expo-cli
```

### Metro bundler stuck

```bash
# Clear cache
npx expo start --clear
```

### iOS simulator not opening

```bash
# Check Xcode installation
xcode-select --install

# Open simulator manually
open -a Simulator

# Then run
npx expo run:ios
```

### Android emulator issues

```bash
# Check ANDROID_HOME
echo $ANDROID_HOME

# Should be: ~/Library/Android/sdk (macOS)

# Start emulator manually
emulator -list-avds
emulator -avd <avd_name>
```

## General Issues

### Node version mismatch

```bash
# Use nvm to switch versions
nvm install 18
nvm use 18
```

### Python version mismatch

```bash
# Use pyenv to switch versions
pyenv install 3.11
pyenv local 3.11
```
```

**验收**: 文件存在且内容覆盖常见问题

---

## Execution Order

```
1.1.1 → 1.1.2 → 1.1.3 → 1.1.4 → 1.1.5 → 1.1.6  (Mobile Init)
                    ↓
1.2.1 → 1.2.2 → 1.2.3 → 1.2.4 → 1.2.5 → 1.2.6 → 1.2.7  (Backend Init)
                    ↓
         1.3.1 → 1.3.2 → 1.3.3 → 1.3.4 → 1.3.5 → 1.3.6  (Database)
                              ↓
                    1.4.1 → 1.4.2 → 1.4.3 → 1.4.4  (CI/CD)
                              ↓
                    1.5.1 → 1.5.2 → 1.5.3  (Documentation)
```

**可并行执行**:
- Story 1.1 和 Story 1.2 可以并行
- Story 1.4 和 Story 1.5 可以并行（在 1.3 完成后）

---

## Verification Checklist

完成 Epic 1 后的最终验收：

- [ ] `npm install && npx expo start` 成功启动移动端
- [ ] `poetry install && poetry run uvicorn app.main:app` 成功启动后端
- [ ] `curl localhost:8000/health` 返回 `{"status":"healthy","database":"ok"}`
- [ ] `curl localhost:8000/docs` 返回 Swagger UI
- [ ] `docker-compose up` 成功启动所有服务
- [ ] `alembic upgrade head` 成功执行迁移
- [ ] GitHub Actions CI 全部通过
- [ ] 新开发者按 `docs/setup.md` 可在 30 分钟内启动项目

---

## Change Log

| Date | Version | Description |
|------|---------|-------------|
| 2025-12-21 | 1.0 | Initial plan from Epic 1 spec |

---

*This plan is derived from `docs/spec/epic-1-foundation.md` and follows the Constitution principles.*
