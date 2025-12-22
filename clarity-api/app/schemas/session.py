from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.solve_session import SolveStep


class UsageResponse(BaseModel):
    sessions_used: int
    sessions_limit: int
    tier: str


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    current_step: str
    created_at: datetime
    completed_at: Optional[datetime] = None


class SessionCreateResponse(BaseModel):
    session_id: UUID
    status: str
    current_step: str
    created_at: datetime
    usage: UsageResponse


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
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
