"""学习消息模型 - 保存学习对话内容"""

import uuid
from enum import Enum

from app.database import Base
from app.utils.datetime_utils import utc_now
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class LearnMessageRole(str, Enum):
    """消息角色"""

    USER = "user"
    ASSISTANT = "assistant"


class LearnMessage(Base):
    """学习消息模型 - 保存学习会话中的每条消息"""

    __tablename__ = "learn_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("learn_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # user 或 assistant
    content = Column(Text, nullable=False)
    step = Column(String(50), nullable=True)  # 消息所属的步骤
    created_at = Column(DateTime, default=lambda: utc_now())

    # Relationships
    session = relationship("LearnSession", back_populates="messages")

    def __repr__(self):
        return f"<LearnMessage {self.id} role={self.role}>"
