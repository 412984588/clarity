import uuid

from app.database import Base
from app.utils.datetime_utils import utc_now
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class PromptTemplate(Base):
    """Prompt template model for pre-defined AI roles."""

    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(100), nullable=False, unique=True)
    role_name_cn = Column(String(100), nullable=True)
    category = Column(String(50), nullable=False, index=True)
    system_prompt = Column(Text, nullable=False)
    welcome_message = Column(Text, nullable=True)
    icon_emoji = Column(String(10), nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: utc_now())
    updated_at = Column(
        DateTime,
        default=lambda: utc_now(),
        onupdate=lambda: utc_now(),
    )

    sessions = relationship("SolveSession", back_populates="template")

    def __repr__(self) -> str:
        return f"<PromptTemplate {self.role_name}>"
