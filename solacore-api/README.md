# Solacore API

FastAPI 后端服务

## 环境要求

- Python 3.11+
- Poetry 1.7+
- PostgreSQL 15+（或使用 Docker）
- Docker + Docker Compose（可选）

## 快速开始

### 本地开发

```bash
# 安装依赖
poetry install --no-root

# 复制环境变量配置
cp .env.example .env

# 启动开发服务器
poetry run uvicorn app.main:app --reload

# 访问 API 文档
open http://localhost:8000/docs
```

### Docker 部署

```bash
# 启动所有服务（API + PostgreSQL）
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down
```

## 目录结构

- `app/` - 应用代码
  - `routers/` - API 路由
  - `services/` - 业务逻辑
  - `models/` - SQLAlchemy 模型
  - `schemas/` - Pydantic 数据模型
  - `middleware/` - 中间件
  - `config.py` - 配置管理
  - `database.py` - 数据库连接
  - `main.py` - FastAPI 应用入口
- `tests/` - 测试文件
- `alembic/` - 数据库迁移脚本

## 代码规范

```bash
# 代码检查
poetry run ruff check .

# 类型检查
poetry run mypy app --ignore-missing-imports

# 运行测试
poetry run pytest
```

## API 端点

- `GET /` - 根端点
- `GET /health` - 健康检查
- `GET /docs` - Swagger UI 文档
- `GET /redoc` - ReDoc 文档

## 环境变量

查看 `.env.example` 获取完整配置说明

- `DEBUG` - 调试模式
- `DATABASE_URL` - 数据库连接字符串
- `JWT_SECRET` - JWT 密钥
- `HOST` - 服务器地址
- `PORT` - 服务器端口
