"""应用生命周期管理 - 启动和关闭事件处理"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.config import Settings, validate_production_config
from app.tasks.scheduler import shutdown_scheduler, start_scheduler
from fastapi import FastAPI


@asynccontextmanager
async def lifespan_handler(app: FastAPI, settings: Settings) -> AsyncIterator[None]:
    """应用生命周期管理

    Args:
        app: FastAPI 应用实例
        settings: 应用配置

    Yields:
        None: 生命周期上下文
    """
    validate_production_config(settings)
    start_scheduler()
    yield
    shutdown_scheduler()
