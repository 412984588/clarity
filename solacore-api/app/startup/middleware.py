"""中间件配置模块 - 配置 CORS、CSRF、限流、指标收集等中间件"""

import time

from app.config import Settings
from app.middleware.csrf import validate_csrf
from app.middleware.rate_limit import limiter
from app.utils.metrics import metrics
from app.utils.sentry import setup_sentry
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


def get_cors_origins(settings: Settings) -> list[str]:
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

    # 生产环境默认允许正式域名（主域 + www）
    if not settings.debug:
        origins.extend(["https://solacore.app", "https://www.solacore.app"])

    deduped: list[str] = []
    seen: set[str] = set()
    for origin in origins:
        if not origin or origin in seen:
            continue
        seen.add(origin)
        deduped.append(origin)

    return deduped


def setup_middlewares(app: FastAPI, settings: Settings) -> None:
    """配置所有中间件

    Args:
        app: FastAPI 应用实例
        settings: 应用配置
    """

    # 1. 指标收集中间件
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

    # 2. CSRF 保护中间件
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

    # 3. CORS 中间件
    # SlowAPI 限流中间件已禁用，使用 @limiter.limit() 装饰器替代
    # 原因：SlowAPIASGIMiddleware 与 Starlette 的 ASGI 协议存在兼容性问题
    # 当前方案：在每个endpoint手动添加 @limiter.limit() 装饰器（见 verify_rate_limits.py 验证脚本）
    # 长期方案：等待 SlowAPI 修复兼容性问题，或迁移到其他限流库（如 fastapi-limiter）
    # app.add_middleware(SlowAPIASGIMiddleware)
    # app.add_middleware(RateLimitContextMiddleware)

    # CORS 中间件：仅在开发环境启用（生产环境由 nginx 统一处理 CORS，避免 header 重复）
    if settings.debug:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=get_cors_origins(settings),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 4. 注册限流器
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # 5. Sentry 错误追踪
    setup_sentry(app, settings)
