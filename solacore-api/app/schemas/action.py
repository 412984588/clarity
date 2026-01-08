from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    id: UUID
    action: str
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    session_id: UUID

    class Config:
        from_attributes = True


class ActionStats(BaseModel):
    total: int
    completed: int
    pending: int
    completion_rate: float = Field(ge=0, le=100)


class Pagination(BaseModel):
    limit: int
    offset: int
    total: int


class ActionListResponse(BaseModel):
    actions: list[ActionItem]
    stats: ActionStats
    pagination: Pagination


class CompleteActionRequest(BaseModel):
    pass
