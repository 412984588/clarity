import time

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings
from app.utils.metrics import metrics

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=10,
)


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def before_cursor_execute(
    conn, cursor, statement, parameters, context, executemany
) -> None:
    conn.info.setdefault("query_start_time", []).append(time.perf_counter())


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def after_cursor_execute(
    conn, cursor, statement, parameters, context, executemany
) -> None:
    start_times = conn.info.get("query_start_time")
    if not start_times:
        return
    start_time = start_times.pop()
    metrics.record_db_query(time.perf_counter() - start_time)


@event.listens_for(engine.sync_engine, "handle_error")
def handle_error(exception_context) -> None:
    conn = exception_context.connection
    if not conn:
        return
    start_times = conn.info.get("query_start_time")
    if not start_times:
        return
    start_time = start_times.pop()
    metrics.record_db_query(time.perf_counter() - start_time)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    """依赖注入：获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_db_pool_stats() -> dict[str, int]:
    pool = engine.sync_engine.pool
    return {
        "size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
    }
