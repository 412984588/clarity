import os
from http.cookies import SimpleCookie
from typing import AsyncGenerator, Generator

_DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/solacore"
base_db_url = os.getenv("DATABASE_URL", _DEFAULT_DATABASE_URL)
if base_db_url.endswith("/solacore_test"):
    test_db_url = base_db_url
elif base_db_url.endswith("/solacore"):
    test_db_url = base_db_url.replace("/solacore", "/solacore_test")
else:
    test_db_url = base_db_url

os.environ["DATABASE_URL"] = test_db_url

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.middleware.rate_limit import limiter  # noqa: E402
from app.services import stripe_service  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

get_settings.cache_clear()
settings = get_settings()

TEST_DATABASE_URL = test_db_url
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    isolation_level="READ COMMITTED",
)
TestingSessionLocal = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)

__all__ = ["TestingSessionLocal", "TEST_DATABASE_URL"]


async def _add_csrf_header(request) -> None:
    if request.method.upper() not in {"POST", "PUT", "PATCH", "DELETE"}:
        return
    if "x-csrf-token" in request.headers:
        return
    cookie_header = request.headers.get("cookie")
    if not cookie_header:
        return
    cookie = SimpleCookie()
    cookie.load(cookie_header)
    token = cookie.get("csrf_token")
    if token:
        request.headers["X-CSRF-Token"] = token.value


async def _ensure_db_available() -> None:
    from sqlalchemy import text

    try:
        async with engine_test.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        message = (
            "PostgreSQL is unavailable for tests. Start it with "
            "`cd solacore-api && docker compose up -d db redis`. "
            "Set SOLACORE_TEST_SKIP_DB=1 to skip DB-backed tests locally."
        )
        if os.getenv("SOLACORE_TEST_SKIP_DB") == "1":
            pytest.skip(message)
        raise RuntimeError(message) from exc


async def _truncate_tables() -> None:
    """清空所有表数据（保留表结构，避免锁冲突）"""
    from sqlalchemy import text

    async with TestingSessionLocal() as session:
        # 获取所有表名
        tables = [table.name for table in reversed(Base.metadata.sorted_tables)]
        if tables:
            # 使用 DELETE 逐表清空，避免 TRUNCATE 的 ACCESS EXCLUSIVE 锁
            for table in tables:
                await session.execute(text(f"DELETE FROM {table}"))
            await session.commit()


@pytest.fixture(scope="function", autouse=True)
def _configure_payments(request) -> Generator[None, None, None]:
    """Ensure Stripe settings and stubs for subscription tests."""
    if request.node.fspath and request.node.fspath.basename != "test_subscriptions.py":
        yield
        return

    settings = get_settings()
    settings.payments_enabled = True
    settings.stripe_secret_key = "sk_test_dummy"
    settings.stripe_webhook_secret = "whsec_test_dummy"
    settings.stripe_price_standard = "price_standard"
    settings.stripe_price_pro = "price_pro"
    settings.stripe_success_url = "https://example.com/success"
    settings.stripe_cancel_url = "https://example.com/cancel"

    async def _fake_checkout_session(*_args, **_kwargs):
        return "https://example.com/checkout", "cs_test_dummy"

    async def _fake_portal_session(*_args, **_kwargs):
        return "https://example.com/portal"

    original_checkout = stripe_service.create_checkout_session
    original_portal = stripe_service.create_portal_session
    stripe_service.create_checkout_session = _fake_checkout_session
    stripe_service.create_portal_session = _fake_portal_session
    try:
        yield
    finally:
        stripe_service.create_checkout_session = original_checkout
        stripe_service.create_portal_session = original_portal


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """每个测试函数使用独立的数据库状态"""
    await _ensure_db_available()
    # 首次运行时创建表（如果不存在）
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 清空表数据（不删表,避免并发死锁）
    await _truncate_tables()

    # 覆盖依赖
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # 重置 rate limiter 状态，避免测试间累积
    limiter.reset()

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        event_hooks={"request": [_add_csrf_header]},
    ) as c:
        await c.get("/auth/csrf")
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client_no_csrf() -> AsyncGenerator[AsyncClient, None]:
    """不自动注入 CSRF header 的测试客户端"""
    await _ensure_db_available()
    # 首次运行时创建表（如果不存在）
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 清空表数据（不删表,避免并发死锁）
    await _truncate_tables()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
