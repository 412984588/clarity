"""Solacore API 主入口

这个文件是应用的入口点，负责创建 FastAPI 应用实例。
所有的配置、中间件、路由注册都在 startup 模块中完成。

使用方式:
    uvicorn app.main:app --reload
"""

from app.startup import create_app

# 创建应用实例
app = create_app()
