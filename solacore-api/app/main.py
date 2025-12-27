from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings, validate_production_config
from app.database import get_db
from app.logging_config import setup_logging
from app.middleware.rate_limit import limiter
from app.routers import auth
from app.routers import sessions
from app.routers import subscriptions
from app.routers import webhooks
from app.routers import revenuecat_webhooks
from app.routers import account
from app.routers import config

settings = get_settings()

# 初始化结构化日志
setup_logging(debug=settings.debug)

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        integrations=[FastApiIntegration()],
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # 启动时校验生产配置
    validate_production_config(settings)
    yield


def get_cors_origins() -> list[str]:
    """获取 CORS 白名单 - 生产环境不包含 localhost"""
    origins: list[str] = []

    # 仅在 debug 模式下允许 localhost（开发环境）
    if settings.debug:
        origins.extend(
            [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
            ]
        )

    # 使用 frontend_url
    if settings.frontend_url:
        origins.append(settings.frontend_url)

    # 使用 cors_allowed_origins（生产环境主要靠这个）
    if settings.cors_allowed_origins:
        origins.extend(
            o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()
        )

    return origins


app = FastAPI(
    title=settings.app_name,
    description="Universal problem-solving assistant API",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册限流器
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# 注册路由
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(subscriptions.router)
app.include_router(webhooks.router)
app.include_router(revenuecat_webhooks.router)
app.include_router(account.router)
app.include_router(config.router)


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查端点 - 生产环境仅返回基本状态，debug 模式返回详细配置"""
    # 数据库检查
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    # 基础状态判断
    llm_ok = bool(
        (settings.llm_provider == "openai" and settings.openai_api_key)
        or (settings.llm_provider == "anthropic" and settings.anthropic_api_key)
        or settings.openrouter_api_key
    )
    health_status = "healthy" if (db_ok and llm_ok) else "degraded"

    # 生产环境：仅返回基本状态（不暴露内部配置）
    if not settings.debug:
        return {
            "status": health_status,
            "version": settings.app_version,
        }

    # Debug 模式：返回详细配置信息（便于开发调试）
    checks = {
        "database": "connected" if db_ok else "error",
        "llm_configured": "unknown",
        "stripe_configured": "unknown",
        "sentry_configured": "unknown",
    }

    if settings.llm_provider == "openai" and settings.openai_api_key:
        checks["llm_configured"] = "openai"
    elif settings.llm_provider == "anthropic" and settings.anthropic_api_key:
        checks["llm_configured"] = "anthropic"
    elif settings.openrouter_api_key:
        checks["llm_configured"] = "openrouter"
    else:
        checks["llm_configured"] = "missing"

    if settings.payments_enabled:
        checks["stripe_configured"] = (
            "configured" if settings.stripe_secret_key else "missing"
        )
    else:
        checks["stripe_configured"] = "disabled"

    checks["sentry_configured"] = "configured" if settings.sentry_dsn else "disabled"

    return {
        "status": health_status,
        "version": settings.app_version,
        "environment": "debug",
        "checks": checks,
    }


@app.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe - 检查数据库连接"""
    try:
        await db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"ready": False},
        )


@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe - 检查进程存活"""
    return {"live": True}


@app.get("/")
async def root():
    """根端点"""
    return {"message": "Welcome to Solacore API", "docs": "/docs"}
