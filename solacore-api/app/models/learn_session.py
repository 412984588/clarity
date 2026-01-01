"""学习会话模型 - 基于方法论引导的学习功能"""

import uuid
from enum import Enum

from app.database import Base
from app.utils.datetime_utils import utc_now
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship


class LearnStep(str, Enum):
    """学习步骤 - 4步学习循环"""

    START = "start"  # 开始：了解学习目标，评估当前水平
    EXPLORE = "explore"  # 探索：深入理解概念
    PRACTICE = "practice"  # 练习：应用和测试
    PLAN = "plan"  # 规划：制定学习计划


class LearnTool(str, Enum):
    """学习工具 - 可组合的学习方法论"""

    PARETO = "pareto"  # 80/20原则
    FEYNMAN = "feynman"  # 费曼学习法
    CHUNKING = "chunking"  # 分块学习法
    DUAL_CODING = "dual_coding"  # 双编码理论
    INTERLEAVING = "interleaving"  # 主题交叉法
    RETRIEVAL = "retrieval"  # 检索练习
    SPACED = "spaced"  # 艾宾浩斯复习
    GROW = "grow"  # GROW模型
    SOCRATIC = "socratic"  # 苏格拉底提问
    ERROR_DRIVEN = "error_driven"  # 错误驱动学习


class LearnSession(Base):
    """学习会话模型

    内置方法论：
    - START: 费曼学习法 + 80/20原则
    - EXPLORE: 分块学习法 + 主题交叉法
    - PRACTICE: 双编码理论 + 费曼教学法
    - PLAN: 艾宾浩斯遗忘曲线 + GROW模型
    """

    __tablename__ = "learn_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    device_id = Column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True
    )
    status = Column(String(50), default="active")  # active, completed, abandoned
    current_step = Column(  # deprecated: 使用 learning_mode + current_tool
        String(50), default=LearnStep.START.value
    )
    learning_mode = Column(String(20), default="quick")  # quick, deep, custom
    current_tool = Column(String(50), default=LearnTool.PARETO.value)
    tool_plan = Column(JSON, default=list)  # 工具计划数组
    locale = Column(String(10), default="zh")  # 默认中文

    # 学习相关字段
    topic = Column(Text, nullable=True)  # 学习主题
    key_concepts = Column(JSON, nullable=True)  # 关键概念列表
    review_schedule = Column(JSON, nullable=True)  # 艾宾浩斯复习计划
    learning_summary = Column(Text, nullable=True)  # 学习总结

    created_at = Column(DateTime, default=lambda: utc_now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="learn_sessions")
    device = relationship("Device")
    messages = relationship(
        "LearnMessage",
        back_populates="session",
        lazy="selectin",
        order_by="LearnMessage.created_at",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<LearnSession {self.id}>"
