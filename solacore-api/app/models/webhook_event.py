from uuid import uuid4

from app.database import Base
from app.utils.datetime_utils import utc_now
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID


class ProcessedWebhookEvent(Base):
    """已处理的 Webhook 事件记录（用于幂等性去重）"""

    __tablename__ = "processed_webhook_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_id = Column(String(255), unique=True, nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False, default="revenuecat")
    payload_hash = Column(String(64), nullable=True)
    processed_at = Column(DateTime, default=utc_now, nullable=False)
    result = Column(Text, nullable=True)
