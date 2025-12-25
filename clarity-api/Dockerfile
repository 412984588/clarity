# =============================================================================
# Clarity API - 生产级 Dockerfile
# =============================================================================
# 多阶段构建，优化镜像体积和安全性
# =============================================================================

FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=2.1.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# 构建阶段安装 Poetry 并安装依赖
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./

# 使用 Poetry 安装生产依赖（排除 dev 组，不安装项目本身）
RUN poetry install --only main --no-interaction --no-ansi --no-root

# =============================================================================
# 生产镜像
# =============================================================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# 安全最佳实践：非 root 用户运行
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# 复制虚拟环境和应用代码
COPY --from=builder /app/.venv /app/.venv
COPY --chown=app:app app /app/app
COPY --chown=app:app alembic /app/alembic
COPY --chown=app:app alembic.ini /app/alembic.ini

USER app

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live').read()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
