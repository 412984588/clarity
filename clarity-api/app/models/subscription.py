from app.utils.datetime_utils import utc_now
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Subscription(Base):
    """订阅模型"""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    tier = Column(String(50), default="free")  # free/standard/pro
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    status = Column(String(50), default="active")  # active/canceled/past_due
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: utc_now())
    updated_at = Column(
        DateTime,
        default=lambda: utc_now(),
        onupdate=lambda: utc_now(),
    )

    # Relationships
    user = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription {self.tier} for user {self.user_id}>"


class Usage(Base):
    """用量追踪"""
    __tablename__ = "usage"
    __table_args__ = (
        # 唯一约束防止并发重复创建同月 usage
        UniqueConstraint("user_id", "period_start", name="uq_usage_user_period"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    session_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: utc_now())
    updated_at = Column(
        DateTime,
        default=lambda: utc_now(),
        onupdate=lambda: utc_now(),
    )
