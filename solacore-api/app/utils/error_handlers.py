"""
统一错误处理工具函数

提供标准化的错误处理逻辑，确保：
1. 所有异常都有日志记录
2. 不暴露内部细节给客户端
3. 事务一致性（该回滚的回滚）
"""

import json
from typing import Any, AsyncGenerator

from app.logging_config import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


async def handle_sse_error(
    db: AsyncSession,
    error: Exception,
    context: dict[str, Any],
) -> AsyncGenerator[str, None]:
    """
    统一的 SSE 错误处理函数

    参数:
        db: 数据库会话
        error: 捕获的异常
        context: 错误上下文信息（session_id, step, user_id 等）

    返回:
        生成包含错误事件的 SSE 流

    行为:
        1. 回滚数据库事务
        2. 记录详细错误日志（包含堆栈跟踪和上下文）
        3. 返回通用错误码给客户端（不泄露内部细节）
    """
    # 回滚事务，防止连接状态不一致
    await db.rollback()

    # 记录详细错误到日志（包含堆栈跟踪），用于服务器端排查
    logger.error(
        "sse_stream_error",
        error=str(error),
        error_type=type(error).__name__,
        **context,  # session_id, step, user_id 等上下文信息
        exc_info=True,  # 包含完整堆栈跟踪
    )

    # 客户端只返回通用错误码，不泄露内部详情（如数据库路径、内部变量）
    error_payload = json.dumps({"error": "STREAM_ERROR"})
    yield f"event: error\ndata: {error_payload}\n\n"


def log_and_sanitize_error(
    error: Exception,
    context: dict[str, Any],
    client_error_code: str = "INTERNAL_ERROR",
) -> dict[str, Any]:
    """
    记录错误并返回安全的客户端错误响应

    参数:
        error: 捕获的异常
        context: 错误上下文信息
        client_error_code: 返回给客户端的错误码

    返回:
        安全的错误响应字典（不包含敏感信息）

    示例:
        try:
            await some_operation()
        except Exception as e:
            return log_and_sanitize_error(
                e,
                {"user_id": user.id, "operation": "create_session"},
                "SESSION_CREATE_FAILED"
            )
    """
    # 记录详细错误到日志
    logger.error(
        "operation_failed",
        error=str(error),
        error_type=type(error).__name__,
        **context,
        exc_info=True,
    )

    # 返回通用错误响应
    return {"error": client_error_code}
