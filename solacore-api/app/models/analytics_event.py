import uuid

from app.database import Base
from app.utils.datetime_utils import utc_now
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID


class AnalyticsEvent(Base):
    """分析事件 - 追踪用户行为和会话状态"""

    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("solve_sessions.id", ondelete="CASCADE"),
        nullable=True,
    )
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=lambda: utc_now())

    def __repr__(self):
        return f"<AnalyticsEvent {self.id} type={self.event_type}>"
