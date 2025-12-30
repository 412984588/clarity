import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.config import get_settings, validate_production_config
from app.database import get_db, get_db_pool_stats
from app.logging_config import setup_logging
from app.middleware.csrf import validate_csrf
from app.middleware.rate_limit import limiter
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
from app.utils.sentry import setup_sentry
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, PlainTextResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

settings = get_settings()

# 初始化结构化日志
setup_logging(debug=settings.debug)

OPENAPI_TAGS = [
    {
        "name": "Auth",
        "description": "注册、登录、OAuth 与账户认证相关接口。",
    },
    {
        "name": "Sessions",
        "description": "Solve 会话管理与 SSE 流式消息接口。",
    },
    {
        "name": "Subscriptions",
        "description": "订阅状态、结账与使用量统计接口。",
    },
    {
        "name": "Account",
        "description": "账户导出与删除接口。",
    },
    {
        "name": "Health",
        "description": "健康检查与探针接口。",
    },
]

API_DESCRIPTION = f"""
Solacore API for authentication, Solve sessions, subscriptions, and account management.

## Authentication
- **Bearer Token**: `Authorization: Bearer <access_token>`
- **Cookie**: `access_token` + `refresh_token` httpOnly cookies
- **CSRF**: 使用 Cookie 进行写操作时，需要携带 `X-CSRF-Token`

## Version
当前 API 版本: {settings.app_version}
""".strip()

CONTACT_INFO = {
    "name": settings.smtp_from_name or "Solacore Support",
    "email": settings.smtp_from,
    "url": settings.frontend_url_prod or settings.frontend_url,
}

LICENSE_INFO = {"name": "Proprietary"}


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
    description=API_DESCRIPTION,
    version=settings.app_version,
    contact=CONTACT_INFO,
    license_info=LICENSE_INFO,
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=OPENAPI_TAGS,
        contact=CONTACT_INFO,
        license_info=LICENSE_INFO,
    )
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes.update(
        {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "使用 Authorization: Bearer <token> 进行认证",
            },
            "CookieAuth": {
                "type": "apiKey",
                "in": "cookie",
                "name": "access_token",
                "description": "使用 httpOnly cookies 进行认证",
            },
        }
    )
    openapi_schema.setdefault("info", {})["x-api-version"] = settings.app_version
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        metrics.record_request(
            time.perf_counter() - start,
            method=request.method,
            path=path,
            status_code=status_code,
        )


@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    try:
        validate_csrf(request)
    except HTTPException as exc:
        # CSRF 验证失败，返回 JSON 错误响应
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    return await call_next(request)


# 暂时禁用限流中间件，避免 ASGI 协议冲突
# TODO: 修复 SlowAPI 与 Starlette 的兼容性问题
# app.add_middleware(SlowAPIASGIMiddleware)
# app.add_middleware(RateLimitContextMiddleware)

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

setup_sentry(app, settings)


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.code, "detail": exc.detail},
    )


# 注册路由
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(learn.router)
app.include_router(subscriptions.router)
app.include_router(webhooks.router)
app.include_router(revenuecat_webhooks.router)
app.include_router(account.router)
app.include_router(config.router)


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
