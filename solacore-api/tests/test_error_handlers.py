"""
测试统一错误处理工具函数
"""

import json
from unittest.mock import AsyncMock, patch

import pytest
from app.utils.error_handlers import handle_sse_error, log_and_sanitize_error
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_handle_sse_error_rollback_transaction():
    """测试 SSE 错误处理时正确回滚事务"""
    # 模拟数据库会话
    db_mock = AsyncMock(spec=AsyncSession)

    # 模拟异常
    test_error = ValueError("Test database error")

    # 上下文信息
    context = {
        "session_id": "test-session-id",
        "step": "receive",
        "user_id": "test-user-id",
    }

    # 收集生成的事件
    events = []
    async for event in handle_sse_error(db_mock, test_error, context):
        events.append(event)

    # 验证：1. 回滚了事务
    db_mock.rollback.assert_awaited_once()

    # 验证：2. 返回了错误事件
    assert len(events) == 1
    assert "event: error" in events[0]
    assert "STREAM_ERROR" in events[0]

    # 验证：3. 不暴露内部错误细节
    assert "ValueError" not in events[0]
    assert "Test database error" not in events[0]


@pytest.mark.asyncio
async def test_handle_sse_error_logs_context():
    """测试 SSE 错误处理时记录详细上下文"""
    db_mock = AsyncMock(spec=AsyncSession)
    test_error = RuntimeError("Critical error")
    context = {
        "session_id": "session-123",
        "step": "clarify",
        "user_id": "user-456",
    }

    with patch("app.utils.error_handlers.logger") as logger_mock:
        async for _ in handle_sse_error(db_mock, test_error, context):
            pass

        # 验证日志调用
        logger_mock.error.assert_called_once()
        call_kwargs = logger_mock.error.call_args[1]

        # 验证包含错误信息
        assert call_kwargs["error"] == "Critical error"
        assert call_kwargs["error_type"] == "RuntimeError"

        # 验证包含上下文信息
        assert call_kwargs["session_id"] == "session-123"
        assert call_kwargs["step"] == "clarify"
        assert call_kwargs["user_id"] == "user-456"

        # 验证包含堆栈跟踪
        assert call_kwargs["exc_info"] is True


def test_log_and_sanitize_error_default_code():
    """测试日志并清理错误 - 默认错误码"""
    test_error = Exception("Internal failure")
    context = {"user_id": "user-789", "operation": "create_session"}

    with patch("app.utils.error_handlers.logger") as logger_mock:
        result = log_and_sanitize_error(test_error, context)

        # 验证返回通用错误码
        assert result == {"error": "INTERNAL_ERROR"}

        # 验证日志调用
        logger_mock.error.assert_called_once()
        call_kwargs = logger_mock.error.call_args[1]

        # 验证包含错误信息
        assert call_kwargs["error"] == "Internal failure"
        assert call_kwargs["error_type"] == "Exception"

        # 验证包含上下文
        assert call_kwargs["user_id"] == "user-789"
        assert call_kwargs["operation"] == "create_session"


def test_log_and_sanitize_error_custom_code():
    """测试日志并清理错误 - 自定义错误码"""
    test_error = KeyError("missing_key")
    context = {"session_id": "session-abc"}

    with patch("app.utils.error_handlers.logger") as logger_mock:
        result = log_and_sanitize_error(
            test_error, context, client_error_code="SESSION_CREATE_FAILED"
        )

        # 验证返回自定义错误码
        assert result == {"error": "SESSION_CREATE_FAILED"}

        # 验证日志调用
        logger_mock.error.assert_called_once()


@pytest.mark.asyncio
async def test_handle_sse_error_json_format():
    """测试 SSE 错误事件的 JSON 格式正确"""
    db_mock = AsyncMock(spec=AsyncSession)
    test_error = Exception("Test")
    context = {"session_id": "test"}

    events = []
    async for event in handle_sse_error(db_mock, test_error, context):
        events.append(event)

    # 解析事件数据
    event_str = events[0]
    assert event_str.startswith("event: error\ndata: ")
    assert event_str.endswith("\n\n")

    # 提取 JSON 部分
    json_part = event_str.split("data: ")[1].strip()
    data = json.loads(json_part)

    # 验证 JSON 结构
    assert "error" in data
    assert data["error"] == "STREAM_ERROR"


@pytest.mark.asyncio
async def test_handle_sse_error_with_different_exception_types():
    """测试不同类型异常的处理"""
    db_mock = AsyncMock(spec=AsyncSession)
    context = {"session_id": "test"}

    # 测试多种异常类型
    exceptions = [
        ValueError("value error"),
        KeyError("key error"),
        RuntimeError("runtime error"),
        Exception("generic error"),
    ]

    for exc in exceptions:
        db_mock.rollback.reset_mock()

        events = []
        async for event in handle_sse_error(db_mock, exc, context):
            events.append(event)

        # 验证：每种异常都正确处理
        db_mock.rollback.assert_awaited_once()
        assert len(events) == 1
        assert "STREAM_ERROR" in events[0]
        # 验证：不暴露异常类型
        assert type(exc).__name__ not in events[0]
