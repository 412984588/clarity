"""路由注册模块 - 注册所有 API 路由和健康检查端点"""

from app.database import get_db, get_db_pool_stats
from app.logging_config import get_logger
from app.routers import (
    account,
    auth,
    config,
    learn,
    revenuecat_webhooks,
    sessions,
    subscriptions,
    webhooks,
)
from app.utils.docs import COMMON_ERROR_RESPONSES
from app.utils.exceptions import AuthError
from app.utils.health import (
    get_active_sessions_count,
    get_active_users_count,
    get_liveness_report,
    get_readiness_report,
)
from app.utils.metrics import format_prometheus_metrics, metrics
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(AuthError)
    async def auth_error_handler(request: Request, exc: AuthError):
        auth_context = getattr(request.state, "auth_context", None)
        logger.warning(
            "auth.error",
            error_type=exc.__class__.__name__,
            error_code=exc.code,
            error_detail=exc.detail,
            status_code=exc.status_code,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            auth_context=auth_context,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code, "detail": exc.detail},
        )


def register_health_routes(app: FastAPI, settings: Settings) -> None:
    """注册健康检查端点"""

    @app.get(
        "/health",
        tags=["Health"],
        summary="服务健康检查",
        description="检查数据库与 LLM 配置状态，debug 模式返回更详细的检查信息。",
        responses={
            **COMMON_ERROR_RESPONSES,
            200: {
                "description": "健康状态",
                "content": {
                    "application/json": {
                        "examples": {
                            "production": {
                                "summary": "生产环境响应",
                                "value": {"status": "healthy", "version": "0.1.0"},
                            },
                            "debug": {
                                "summary": "Debug 响应",
                                "value": {
                                    "status": "healthy",
                                    "version": "0.1.0",
                                    "environment": "debug",
                                    "checks": {
                                        "database": "connected",
                                        "llm_configured": "openai",
                                        "stripe_configured": "configured",
                                        "sentry_configured": "configured",
                                    },
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def health_check(db: AsyncSession = Depends(get_db)):
        """健康检查端点，生产环境仅返回基础状态，debug 模式返回详细信息。"""
        # 数据库检查
        db_ok = False
        try:
            await db.execute(text("SELECT 1"))
            db_ok = True
        except Exception as e:
            logger.warning(
                "health_check.database_failed",
                error=str(e),
                error_type=type(e).__name__,
            )

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

        checks["sentry_configured"] = (
            "configured" if settings.sentry_dsn else "disabled"
        )

        return {
            "status": health_status,
            "version": settings.app_version,
            "environment": "debug",
            "checks": checks,
        }

    @app.get(
        "/health/ready",
        tags=["Health"],
        summary="Readiness 探针",
        description="用于 Kubernetes readiness probe，检查依赖服务是否就绪。",
        responses={
            **COMMON_ERROR_RESPONSES,
            200: {
                "description": "服务已就绪",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "healthy",
                            "timestamp": "2025-12-27T00:00:00+00:00",
                            "checks": {
                                "database": {"status": "up", "latency_ms": 5},
                                "redis": {"status": "up", "latency_ms": 2},
                                "disk": {"status": "up", "usage_percent": 45},
                                "memory": {"status": "up", "usage_percent": 60},
                            },
                        }
                    }
                },
            },
            503: {
                "description": "服务未就绪",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "unhealthy",
                            "timestamp": "2025-12-27T00:00:00+00:00",
                            "checks": {
                                "database": {"status": "down"},
                                "redis": {"status": "up", "latency_ms": 2},
                                "disk": {"status": "up", "usage_percent": 45},
                                "memory": {"status": "up", "usage_percent": 60},
                            },
                        }
                    }
                },
            },
        },
    )
    async def readiness_check():
        """Kubernetes readiness probe，检查依赖服务就绪状态。"""
        report = await get_readiness_report()
        status_code = (
            status.HTTP_200_OK
            if report["status"] in {"healthy", "degraded"}
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return JSONResponse(status_code=status_code, content=report)

    @app.get(
        "/health/live",
        tags=["Health"],
        summary="Liveness 探针",
        description="用于 Kubernetes liveness probe，检查进程存活。",
        responses={
            **COMMON_ERROR_RESPONSES,
            200: {
                "description": "服务存活",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "healthy",
                            "timestamp": "2025-12-27T00:00:00+00:00",
                            "checks": {"service": {"status": "up"}},
                        }
                    }
                },
            },
        },
    )
    async def liveness_check():
        """Kubernetes liveness probe，检查进程存活。"""
        return await get_liveness_report()

    @app.get(
        "/health/metrics",
        tags=["Health"],
        summary="Prometheus 指标",
        description="输出 Prometheus 格式的运行指标。",
        responses={
            **COMMON_ERROR_RESPONSES,
            200: {
                "description": "Prometheus metrics",
                "content": {"text/plain": {"example": "request_count 1"}},
            },
        },
    )
    async def metrics_endpoint():
        snapshot = metrics.snapshot()
        active_sessions = await get_active_sessions_count()
        active_users = await get_active_users_count()
        db_pool_stats = get_db_pool_stats()
        payload = format_prometheus_metrics(
            snapshot,
            active_sessions=active_sessions,
            active_users=active_users,
            db_pool=db_pool_stats,
        )
        return PlainTextResponse(payload, media_type="text/plain; version=0.0.4")

    @app.get("/")
    async def root():
        """根端点"""
        return {"message": "Welcome to Solacore API", "docs": "/docs"}


def register_routes(app: FastAPI, settings: Settings) -> None:
    """注册所有路由

    Args:
        app: FastAPI 应用实例
        settings: 应用配置
    """
    # 注册业务路由
    app.include_router(auth.router)
    app.include_router(sessions.router)
    app.include_router(learn.router)
    app.include_router(subscriptions.router)
    app.include_router(webhooks.router)
    app.include_router(revenuecat_webhooks.router)
    app.include_router(account.router)
    app.include_router(config.router)

    # 注册健康检查路由
    register_health_routes(app, settings)

    # 注册异常处理器
    register_exception_handlers(app)
