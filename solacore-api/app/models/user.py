import uuid

from app.database import Base
from app.utils.datetime_utils import utc_now
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class User(Base):
    """用户模型 - 支持邮箱和 OAuth"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL for OAuth users
    auth_provider = Column(String(50), default="email")  # email/google/apple
    auth_provider_id = Column(String(255), nullable=True)  # OAuth user ID
    locale = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: utc_now(), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: utc_now(),
        onupdate=lambda: utc_now(),
    )

    # Relationships
    devices = relationship(
        "Device", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "ActiveSession", back_populates="user", cascade="all, delete-orphan"
    )
    solve_sessions = relationship(
        "SolveSession", back_populates="user", cascade="all, delete-orphan"
    )
    learn_sessions = relationship(
        "LearnSession", back_populates="user", cascade="all, delete-orphan"
    )
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"
