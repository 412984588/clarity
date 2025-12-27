from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.solve_session import SolveStep


class UsageResponse(BaseModel):
    sessions_used: int
    sessions_limit: int
    tier: str


class MessageResponse(BaseModel):
    """消息响应"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    step: Optional[str] = None
    created_at: datetime


class SessionListItem(BaseModel):
    """会话列表项（不包含消息，用于列表展示）"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    current_step: str
    created_at: datetime
    completed_at: Optional[datetime] = None


class SessionResponse(BaseModel):
    """会话详情（消息可选，用于单个会话查询）"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    current_step: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    messages: Optional[List[MessageResponse]] = None


class SessionCreateResponse(BaseModel):
    session_id: UUID
    status: str
    current_step: str
    created_at: datetime
    usage: UsageResponse


class SessionListResponse(BaseModel):
    """会话列表响应（使用轻量级 SessionListItem）"""

    sessions: List[SessionListItem]
    total: int
    limit: int
    offset: int


class MessageRequest(BaseModel):
    content: str
    step: SolveStep


class SSETokenEvent(BaseModel):
    content: str


class SSEDoneEvent(BaseModel):
    next_step: str
    emotion_detected: str


class SessionUpdateRequest(BaseModel):
    status: Optional[str] = Field(default=None)
    current_step: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None)
    first_step_action: Optional[str] = Field(default=None)
    reminder_time: Optional[datetime] = Field(default=None)


class SessionUpdateResponse(BaseModel):
    id: str
    status: str
    current_step: str
    updated_at: datetime
