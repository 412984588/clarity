from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.models.solve_session import SolveStep
from app.schemas.fields import Field
from pydantic import BaseModel, ConfigDict


class UsageResponse(BaseModel):
    sessions_used: int = Field(
        ...,
        description="当前计费周期已使用会话数",
        example=3,
    )
    sessions_limit: int = Field(
        ...,
        description="当前计费周期会话上限（0 表示无限制）",
        example=10,
    )
    tier: str = Field(
        ...,
        description="订阅等级",
        example="free",
    )


class MessageResponse(BaseModel):
    """消息响应"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="消息 ID",
        example="1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e",
    )
    role: str = Field(
        ...,
        description="消息角色（user/assistant/system）",
        example="user",
    )
    content: str = Field(
        ...,
        description="消息内容",
        example="我最近有点焦虑，睡不好。",
    )
    step: Optional[str] = Field(
        default=None,
        description="Solve 当前步骤",
        example="receive",
    )
    created_at: datetime = Field(
        ...,
        description="消息创建时间",
        example="2024-06-01T12:00:00Z",
    )


class SessionListItem(BaseModel):
    """会话列表项（不包含消息，用于列表展示）"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="会话 ID",
        example="2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
    )
    status: str = Field(
        ...,
        description="会话状态",
        example="active",
    )
    current_step: str = Field(
        ...,
        description="当前 Solve 步骤",
        example="receive",
    )
    created_at: datetime = Field(
        ...,
        description="会话创建时间",
        example="2024-06-01T12:00:00Z",
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="会话完成时间",
        example="2024-06-01T12:10:00Z",
    )
    first_message: Optional[str] = Field(
        default=None,
        description="会话的第一条用户消息（用于列表展示）",
        example="我最近有点焦虑，睡不好。",
    )


class SessionResponse(BaseModel):
    """会话详情（消息可选，用于单个会话查询）"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="会话 ID",
        example="2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
    )
    status: str = Field(
        ...,
        description="会话状态",
        example="active",
    )
    current_step: str = Field(
        ...,
        description="当前 Solve 步骤",
        example="clarify",
    )
    created_at: datetime = Field(
        ...,
        description="会话创建时间",
        example="2024-06-01T12:00:00Z",
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="会话完成时间",
        example="2024-06-01T12:10:00Z",
    )
    messages: Optional[List[MessageResponse]] = Field(
        default=None,
        description="会话消息列表（可选）",
        example=[
            {
                "id": "1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e",
                "role": "user",
                "content": "我最近有点焦虑，睡不好。",
                "step": "receive",
                "created_at": "2024-06-01T12:00:00Z",
            }
        ],
    )


class SessionCreateResponse(BaseModel):
    session_id: UUID = Field(
        ...,
        description="新会话 ID",
        example="3d4e5f6a-7b8c-9d0e-1f2a-3b4c5d6e7f8a",
    )
    status: str = Field(
        ...,
        description="会话状态",
        example="active",
    )
    current_step: str = Field(
        ...,
        description="初始 Solve 步骤",
        example="receive",
    )
    created_at: datetime = Field(
        ...,
        description="会话创建时间",
        example="2024-06-01T12:00:00Z",
    )
    usage: UsageResponse = Field(
        ...,
        description="当前使用量信息",
        example={"sessions_used": 1, "sessions_limit": 10, "tier": "free"},
    )


class SessionListResponse(BaseModel):
    """会话列表响应（使用轻量级 SessionListItem）"""

    sessions: List[SessionListItem] = Field(
        ...,
        description="会话列表",
        example=[
            {
                "id": "2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
                "status": "active",
                "current_step": "receive",
                "created_at": "2024-06-01T12:00:00Z",
                "completed_at": None,
            }
        ],
    )
    total: int = Field(
        ...,
        description="总会话数",
        example=1,
    )
    limit: int = Field(
        ...,
        description="分页大小",
        example=20,
    )
    offset: int = Field(
        ...,
        description="分页偏移量",
        example=0,
    )


class MessageRequest(BaseModel):
    content: str = Field(
        ...,
        description="用户消息内容",
        example="我最近情绪有点低落，想找人聊聊。",
    )
    step: SolveStep = Field(
        ...,
        description="当前 Solve 步骤",
        example="receive",
    )


class SSETokenEvent(BaseModel):
    content: str = Field(
        ...,
        description="流式输出的文本片段",
        example="我能理解你的感受，",
    )


class SSEDoneEvent(BaseModel):
    next_step: str = Field(
        ...,
        description="下一步 Solve 步骤",
        example="clarify",
    )
    emotion_detected: str = Field(
        ...,
        description="检测到的情绪",
        example="sadness",
    )


class SessionUpdateRequest(BaseModel):
    status: Optional[str] = Field(
        default=None,
        description="更新会话状态（active/completed）",
        example="completed",
    )
    current_step: Optional[str] = Field(
        default=None,
        description="更新当前步骤（receive/clarify/reframe/options/commit）",
        example="commit",
    )
    locale: Optional[str] = Field(
        default=None,
        description="会话语言",
        example="zh-CN",
    )
    first_step_action: Optional[str] = Field(
        default=None,
        description="用户在第一步决定的行动",
        example="今晚早点睡",
    )
    reminder_time: Optional[datetime] = Field(
        default=None,
        description="提醒时间",
        example="2024-08-01T09:00:00Z",
    )


class SessionUpdateResponse(BaseModel):
    id: str = Field(
        ...,
        description="会话 ID",
        example="2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
    )
    status: str = Field(
        ...,
        description="更新后的会话状态",
        example="completed",
    )
    current_step: str = Field(
        ...,
        description="更新后的当前步骤",
        example="commit",
    )
    updated_at: datetime = Field(
        ...,
        description="更新时间",
        example="2024-06-01T12:15:00Z",
    )
