"""测试 AnalyticsService - 事件追踪服务"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from app.models.analytics_event import AnalyticsEvent
from app.services.analytics_service import AnalyticsService


@pytest.mark.asyncio
async def test_emit_success_with_flush() -> None:
    """测试成功发送事件并立即刷新到数据库"""
    # 准备 Mock 数据库
    fake_db = MagicMock()
    fake_db.add = MagicMock()
    fake_db.flush = AsyncMock()

    service = AnalyticsService(fake_db)
    session_id = uuid4()
    payload = {"action": "button_click", "target": "submit"}

    # 执行
    result = await service.emit(
        event_type="user_action", session_id=session_id, payload=payload, flush=True
    )

    # 验证
    assert result is not None
    assert isinstance(result, AnalyticsEvent)
    assert result.event_type == "user_action"
    assert result.session_id == session_id
    assert result.payload == payload

    # 验证数据库操作
    fake_db.add.assert_called_once()
    fake_db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_emit_success_without_flush() -> None:
    """测试成功发送事件但不立即刷新"""
    fake_db = MagicMock()
    fake_db.add = MagicMock()
    fake_db.flush = AsyncMock()

    service = AnalyticsService(fake_db)

    result = await service.emit(
        event_type="page_view", session_id=None, payload={"page": "/home"}, flush=False
    )

    assert result is not None
    assert result.event_type == "page_view"
    assert result.session_id is None
    assert result.payload == {"page": "/home"}

    # 验证没有调用 flush
    fake_db.add.assert_called_once()
    fake_db.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_emit_minimal_params() -> None:
    """测试最小参数调用（只传 event_type）"""
    fake_db = MagicMock()
    fake_db.add = MagicMock()
    fake_db.flush = AsyncMock()

    service = AnalyticsService(fake_db)

    result = await service.emit(event_type="app_start")

    assert result is not None
    assert result.event_type == "app_start"
    assert result.session_id is None
    assert result.payload is None

    fake_db.add.assert_called_once()
    fake_db.flush.assert_awaited_once()  # 默认 flush=True


@pytest.mark.asyncio
async def test_emit_failure_returns_none() -> None:
    """测试数据库异常时返回 None（失败不影响主业务）"""
    fake_db = MagicMock()
    fake_db.add = MagicMock(side_effect=Exception("数据库连接失败"))
    fake_db.flush = AsyncMock()

    service = AnalyticsService(fake_db)

    # 应该返回 None 而不是抛出异常
    result = await service.emit(event_type="error_event", payload={"error": "test"})

    assert result is None
    fake_db.add.assert_called_once()
    # 因为 add 已经失败，不应该调用 flush
    fake_db.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_emit_flush_failure_returns_none() -> None:
    """测试 flush 失败时返回 None"""
    fake_db = MagicMock()
    fake_db.add = MagicMock()
    fake_db.flush = AsyncMock(side_effect=Exception("Flush 超时"))

    service = AnalyticsService(fake_db)

    result = await service.emit(event_type="flush_test", flush=True)

    assert result is None


@pytest.mark.asyncio
async def test_emit_logs_warning_on_failure() -> None:
    """测试失败时记录警告日志"""
    fake_db = MagicMock()
    fake_db.add = MagicMock(side_effect=Exception("Mock 错误"))

    service = AnalyticsService(fake_db)

    with patch("app.services.analytics_service.logger") as mock_logger:
        result = await service.emit(event_type="test_event")

        assert result is None
        # 验证记录了警告日志
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Failed to emit analytics event" in call_args
        assert "test_event" in call_args


@pytest.mark.asyncio
async def test_emit_with_complex_payload() -> None:
    """测试复杂 payload 数据"""
    fake_db = MagicMock()
    fake_db.add = MagicMock()
    fake_db.flush = AsyncMock()

    service = AnalyticsService(fake_db)

    complex_payload = {
        "user_id": str(uuid4()),
        "metadata": {
            "browser": "Chrome",
            "version": "120.0",
            "screen": {"width": 1920, "height": 1080},
        },
        "tags": ["mobile", "ios"],
        "timestamp": "2024-12-31T12:00:00Z",
        "count": 42,
        "is_premium": True,
    }

    result = await service.emit(event_type="complex_event", payload=complex_payload)

    assert result is not None
    assert result.payload == complex_payload
    # 验证复杂嵌套结构被正确保存
    assert result.payload["metadata"]["browser"] == "Chrome"
    assert result.payload["tags"] == ["mobile", "ios"]


@pytest.mark.asyncio
async def test_emit_multiple_events_batch() -> None:
    """测试批量发送多个事件（不 flush）"""
    fake_db = MagicMock()
    fake_db.add = MagicMock()
    fake_db.flush = AsyncMock()

    service = AnalyticsService(fake_db)

    # 批量发送 5 个事件，都不 flush
    events = []
    for i in range(5):
        event = await service.emit(
            event_type=f"batch_event_{i}", payload={"index": i}, flush=False
        )
        events.append(event)

    # 验证所有事件都创建成功
    assert len(events) == 5
    assert all(e is not None for e in events)

    # 验证 add 被调用 5 次
    assert fake_db.add.call_count == 5

    # 验证没有任何 flush
    fake_db.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_emit_preserves_session_id_association() -> None:
    """测试会话 ID 关联正确"""
    fake_db = MagicMock()
    fake_db.add = MagicMock()
    fake_db.flush = AsyncMock()

    service = AnalyticsService(fake_db)
    session_id = uuid4()

    # 同一个会话的多个事件
    event1 = await service.emit(event_type="session_start", session_id=session_id)
    event2 = await service.emit(event_type="user_message", session_id=session_id)
    event3 = await service.emit(event_type="session_end", session_id=session_id)

    assert event1.session_id == session_id
    assert event2.session_id == session_id
    assert event3.session_id == session_id

    # 无会话的事件
    event4 = await service.emit(event_type="global_event")
    assert event4.session_id is None
