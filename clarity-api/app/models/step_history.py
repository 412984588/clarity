import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.datetime_utils import utc_now


class StepHistory(Base):
    """步骤历史记录 - 追踪每个 Solve 步骤的开始/结束时间"""

    __tablename__ = "step_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("solve_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    step = Column(String(50), nullable=False)
    started_at = Column(DateTime, default=lambda: utc_now())
    completed_at = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)

    # Relationship
    session = relationship("SolveSession", back_populates="step_history")

    def __repr__(self):
        return f"<StepHistory {self.id} step={self.step}>"
