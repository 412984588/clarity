"""FastAPI 应用创建和配置

这个模块提供了 create_app() 工厂函数，用于创建和配置 FastAPI 应用实例。
它整合了中间件、路由、生命周期事件和 OpenAPI 配置。
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.config import get_settings
from app.logging_config import setup_logging
from app.startup.config import (
    OPENAPI_TAGS,
    get_api_description,
    get_contact_info,
    get_license_info,
    setup_openapi,
)
from app.startup.lifespan import lifespan_handler
from app.startup.middleware import setup_middlewares
from app.startup.routes import register_routes
from fastapi import FastAPI


def create_app() -> FastAPI:
    """创建和配置 FastAPI 应用实例

    Returns:
        FastAPI: 完全配置好的应用实例
    """
    # 加载配置
    settings = get_settings()

    # 初始化结构化日志
    setup_logging(debug=settings.debug)

    # 创建生命周期管理器
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with lifespan_handler(app, settings):
            yield

    # 创建 FastAPI 应用
    app = FastAPI(
        title=settings.app_name,
        description=get_api_description(settings),
        version=settings.app_version,
        contact=get_contact_info(settings),
        license_info=get_license_info(),
        openapi_tags=OPENAPI_TAGS,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # 配置 OpenAPI 文档
    setup_openapi(app, settings)

    # 配置中间件
    setup_middlewares(app, settings)

    # 注册路由
    register_routes(app, settings)

    return app
