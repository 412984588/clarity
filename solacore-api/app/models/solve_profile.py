import uuid

from app.database import Base
from app.utils.datetime_utils import utc_now
from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class SolveProfile(Base):
    __tablename__ = "solve_profiles"
    __table_args__ = (
        Index("ix_solve_profiles_session_id", "session_id"),
        Index("ix_solve_profiles_schema_version", "schema_version"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("solve_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    schema_version = Column(String(20), nullable=False, default="v1")
    profile = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=lambda: utc_now())
    updated_at = Column(DateTime, default=lambda: utc_now())

    session = relationship("SolveSession", back_populates="profile")

    def __repr__(self):
        return f"<SolveProfile {self.id} session={self.session_id}>"
