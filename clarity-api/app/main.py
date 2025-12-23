from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import get_db
from app.routers import auth
from app.routers import sessions
from app.routers import subscriptions
from app.routers import webhooks
from app.routers import revenuecat_webhooks
from app.routers import account

settings = get_settings()

if (
    not settings.debug
    and settings.jwt_secret in {"", "your-secret-key-change-in-production"}
):
    raise RuntimeError("JWT_SECRET must be set to a secure value in production")

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

# 注册路由
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(subscriptions.router)
app.include_router(webhooks.router)
app.include_router(revenuecat_webhooks.router)
app.include_router(account.router)


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
