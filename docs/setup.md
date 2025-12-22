# 开发环境配置指南

## 环境要求

| 工具 | 版本 | 用途 |
|------|------|------|
| Node.js | 18+ | 移动端开发 |
| Python | 3.11+ | 后端开发 |
| Poetry | 1.7+ | Python 依赖管理 |
| Docker | 24+ | 数据库容器 |
| Expo CLI | latest | React Native 开发 |

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

## 后端配置 (clarity-api)

### 1. 安装依赖

```bash
cd clarity-api
poetry install --no-root
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 修改数据库连接等配置
```

### 3. 启动 PostgreSQL

```bash
docker-compose up -d db
```

### 4. 运行数据库迁移

```bash
poetry run alembic upgrade head
```

### 5. 启动开发服务器

```bash
poetry run uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档

## 移动端配置 (clarity-mobile)

### 1. 安装依赖

```bash
cd clarity-mobile
npm install
```

### 2. 启动开发服务器

```bash
npx expo start
```

### 3. 运行应用

- iOS 模拟器：按 `i`
- Android 模拟器：按 `a`
- Expo Go：扫描二维码

## 验证安装

### 后端健康检查

```bash
curl http://localhost:8000/health
# 应返回 {"status":"healthy","database":"ok"}
```

### 代码质量检查

```bash
# 后端
cd clarity-api
poetry run ruff check .
poetry run mypy app --ignore-missing-imports

# 移动端
cd clarity-mobile
npm run lint
npx tsc --noEmit
```

## 常见问题

详见 [troubleshooting.md](troubleshooting.md)
