"""应用生命周期管理 - 启动和关闭事件处理"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.config import Settings, validate_production_config
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
    # 启动时校验生产配置
    validate_production_config(settings)
    yield
    # 关闭时的清理工作（如需要可在此添加）
