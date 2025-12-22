import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Device(Base):
    """设备模型 - 用于设备绑定和反滥用"""
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_fingerprint = Column(String(255), nullable=False, index=True)
    device_name = Column(String(255), nullable=True)
    platform = Column(String(50), nullable=True)  # ios/android
    last_active_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_removal_at = Column(DateTime, nullable=True)  # 用于限制解绑频率

    # Relationships
    user = relationship("User", back_populates="devices")
    sessions = relationship("ActiveSession", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Device {self.device_name} ({self.platform})>"
