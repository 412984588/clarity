"""消息模型 - 保存用户和 AI 的对话内容"""

import uuid
from enum import Enum

from app.database import Base
from app.utils.datetime_utils import utc_now
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class MessageRole(str, Enum):
    """消息角色"""

    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    """消息模型 - 保存会话中的每条消息"""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("solve_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # user 或 assistant
    content = Column(Text, nullable=False)
    step = Column(String(50), nullable=True)  # 消息所属的步骤
    created_at = Column(DateTime, default=lambda: utc_now())

    # Relationships
    session = relationship("SolveSession", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id} role={self.role}>"
