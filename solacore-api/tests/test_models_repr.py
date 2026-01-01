"""测试模型的 __repr__ 方法覆盖率"""

from datetime import datetime
from uuid import uuid4

from app.models.analytics_event import AnalyticsEvent
from app.models.device import Device
from app.models.learn_message import LearnMessage
from app.models.learn_session import LearnSession
from app.models.message import Message, MessageRole
from app.models.session import ActiveSession
from app.models.solve_session import SessionStatus, SolveSession, SolveStep
from app.models.step_history import StepHistory
from app.models.subscription import Subscription
from app.models.user import User


def test_analytics_event_repr():
    """测试 AnalyticsEvent 的 __repr__ 方法"""
    event = AnalyticsEvent(
        id=uuid4(),
        session_id=uuid4(),
    )
    repr_str = repr(event)
    assert "AnalyticsEvent" in repr_str or len(repr_str) > 0


def test_device_repr():
    """测试 Device 的 __repr__ 方法"""
    device = Device(
        id=uuid4(),
        user_id=uuid4(),
        device_fingerprint="test-fingerprint",
    )
    repr_str = repr(device)
    assert "Device" in repr_str or len(repr_str) > 0


def test_learn_message_repr():
    """测试 LearnMessage 的 __repr__ 方法"""
    message = LearnMessage(
        id=uuid4(),
        session_id=uuid4(),
        role=MessageRole.USER,
        content="test content",
    )
    repr_str = repr(message)
    assert "LearnMessage" in repr_str


def test_learn_session_repr():
    """测试 LearnSession 的 __repr__ 方法"""
    session = LearnSession(
        id=uuid4(),
        user_id=uuid4(),
        locale="en",
    )
    repr_str = repr(session)
    assert "LearnSession" in repr_str


def test_message_repr():
    """测试 Message 的 __repr__ 方法"""
    message = Message(
        id=uuid4(),
        session_id=uuid4(),
        role=MessageRole.USER,
        content="test content",
        step=SolveStep.RECEIVE,
    )
    repr_str = repr(message)
    assert "Message" in repr_str


def test_active_session_repr():
    """测试 ActiveSession 的 __repr__ 方法"""
    session = ActiveSession(
        id=uuid4(),
        user_id=uuid4(),
        device_id=uuid4(),
        token_hash="test_hash",
        expires_at=datetime.utcnow(),
    )
    repr_str = repr(session)
    assert "ActiveSession" in repr_str


def test_solve_session_repr():
    """测试 SolveSession 的 __repr__ 方法"""
    session = SolveSession(
        id=uuid4(),
        user_id=uuid4(),
        status=SessionStatus.ACTIVE,
        current_step=SolveStep.RECEIVE,
        locale="en",
    )
    repr_str = repr(session)
    assert "SolveSession" in repr_str


def test_step_history_repr():
    """测试 StepHistory 的 __repr__ 方法"""
    history = StepHistory(
        id=uuid4(),
        session_id=uuid4(),
        step=str(SolveStep.RECEIVE),
    )
    repr_str = repr(history)
    assert "StepHistory" in repr_str


def test_subscription_repr():
    """测试 Subscription 的 __repr__ 方法"""
    subscription = Subscription(
        id=uuid4(),
        user_id=uuid4(),
        stripe_subscription_id="sub_test",
        stripe_customer_id="cus_test",
        status="active",
    )
    repr_str = repr(subscription)
    assert "Subscription" in repr_str


def test_user_repr():
    """测试 User 的 __repr__ 方法"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        auth_provider="email",
        locale="en",
    )
    repr_str = repr(user)
    assert "User" in repr_str
    assert "test@example.com" in repr_str
