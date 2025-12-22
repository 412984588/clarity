# Clarity

Universal problem-solving assistant - 跨平台智能问题解决助手

## 项目概述

Clarity 是一款移动优先的 AI 助手应用，帮助用户通过对话解决各种问题。

## 技术栈

| 组件 | 技术 |
|------|------|
| 移动端 | React Native + Expo |
| 后端 API | FastAPI + Python 3.11 |
| 数据库 | PostgreSQL 15 |
| 容器化 | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## 项目结构

```
clarity/
├── clarity-mobile/     # React Native 移动应用
├── clarity-api/        # FastAPI 后端服务
├── docs/               # 项目文档
└── .github/workflows/  # CI/CD 配置
```

## 快速开始

详见 [docs/setup.md](docs/setup.md)

### 后端

```bash
cd clarity-api
poetry install --no-root
cp .env.example .env
docker-compose up -d db
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

### 移动端

```bash
cd clarity-mobile
npm install
npx expo start
```

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发规范

- 后端：`poetry run ruff check .` + `poetry run mypy app`
- 移动端：`npm run lint` + `npx tsc --noEmit`

## 许可证

MIT
