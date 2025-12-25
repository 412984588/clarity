from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings, validate_production_config
from app.database import get_db
from app.routers import auth
from app.routers import sessions
from app.routers import subscriptions
from app.routers import webhooks
from app.routers import revenuecat_webhooks
from app.routers import account
from app.routers import config

settings = get_settings()

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
    """获取 CORS 白名单"""
    if settings.debug:
        return ["*"]  # Debug 模式允许所有来源

    origins = []

    # 使用 frontend_url
    if settings.frontend_url and "localhost" not in settings.frontend_url:
        origins.append(settings.frontend_url)

    # 使用 cors_allowed_origins
    if settings.cors_allowed_origins:
        origins.extend(o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip())

    # 兜底：至少允许本地开发
    if not origins:
        origins = ["http://localhost:3000", "http://localhost:8000"]

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
    """健康检查端点（含数据库状态和版本号）"""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"

    health_status = "healthy" if db_status == "connected" else "degraded"

    return {
        "status": health_status,
        "version": settings.app_version,
        "database": db_status,
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
    return {"message": "Welcome to Clarity API", "docs": "/docs"}
