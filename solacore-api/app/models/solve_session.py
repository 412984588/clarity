from app.utils.datetime_utils import utc_now
import uuid
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SolveStep(str, Enum):
    RECEIVE = "receive"
    CLARIFY = "clarify"
    REFRAME = "reframe"
    OPTIONS = "options"
    COMMIT = "commit"


class SolveSession(Base):
    """Solve 会话模型"""

    __tablename__ = "solve_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    device_id = Column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True
    )
    status = Column(String(50), default=SessionStatus.ACTIVE.value)
    current_step = Column(String(50), default=SolveStep.RECEIVE.value)
    locale = Column(String(10), default="en")
    first_step_action = Column(Text, nullable=True)
    reminder_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: utc_now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="solve_sessions")
    device = relationship("Device")
    step_history = relationship(
        "StepHistory", back_populates="session", lazy="selectin"
    )

    def __repr__(self):
        return f"<SolveSession {self.id}>"
