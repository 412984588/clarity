import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base, get_db
from app.config import get_settings
from app.middleware.rate_limit import limiter

settings = get_settings()

# 使用测试数据库，禁用连接池避免并发问题
# CI 中 DATABASE_URL 已是 solacore_test，本地是 solacore 需替换
if settings.database_url.endswith("/solacore_test"):
    TEST_DATABASE_URL = settings.database_url
else:
    TEST_DATABASE_URL = settings.database_url.replace("/solacore", "/solacore_test")
engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)

# 导出供其他测试文件使用
__all__ = ["TestingSessionLocal", "TEST_DATABASE_URL"]


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """每个测试函数使用独立的数据库状态"""
    # 创建表
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 覆盖依赖
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # 重置 rate limiter 状态，避免测试间累积
    limiter.reset()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
