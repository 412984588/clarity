from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.schemas.fields import Field
from pydantic import BaseModel, ConfigDict


class PromptTemplateListItem(BaseModel):
    """模板列表项（不包含 system_prompt）"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="模板 ID",
        examples=["2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f"],
    )
    role_name: str = Field(
        ...,
        description="角色名称",
        examples=["English Teacher"],
    )
    role_name_cn: Optional[str] = Field(
        default=None,
        description="角色中文名称",
        examples=["英语老师"],
    )
    category: str = Field(
        ...,
        description="模板分类",
        examples=["learning"],
    )
    welcome_message: Optional[str] = Field(
        default=None,
        description="欢迎语",
        examples=["Hello! I'm your English teacher..."],
    )
    icon_emoji: Optional[str] = Field(
        default=None,
        description="图标 emoji",
        examples=["🎓"],
    )
    usage_count: int = Field(
        ...,
        description="使用次数",
        examples=[1523],
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="创建时间",
        examples=["2024-06-01T12:00:00Z"],
    )


class PromptTemplateListResponse(BaseModel):
    """模板列表响应"""

    templates: List[PromptTemplateListItem] = Field(
        ...,
        description="模板列表",
    )
    total: int = Field(
        ...,
        description="模板总数",
        examples=[20],
    )


class PromptTemplateDetailResponse(BaseModel):
    """模板详情响应"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="模板 ID",
        examples=["2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f"],
    )
    role_name: str = Field(
        ...,
        description="角色名称",
        examples=["Life Coach"],
    )
    role_name_cn: Optional[str] = Field(
        default=None,
        description="角色中文名称",
        examples=["生活教练"],
    )
    category: str = Field(
        ...,
        description="模板分类",
        examples=["life"],
    )
    system_prompt: str = Field(
        ...,
        description="系统提示词",
        examples=["I want you to act as a life coach..."],
    )
    welcome_message: Optional[str] = Field(
        default=None,
        description="欢迎语",
        examples=["你好！我是你的生活教练..."],
    )
    icon_emoji: Optional[str] = Field(
        default=None,
        description="图标 emoji",
        examples=["❤️"],
    )
    usage_count: int = Field(
        ...,
        description="使用次数",
        examples=[856],
    )
