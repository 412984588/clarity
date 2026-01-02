"""Prompt templates API routes."""

from uuid import UUID

from app.database import get_db
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import (
    PromptTemplateDetailResponse,
    PromptTemplateListItem,
    PromptTemplateListResponse,
)
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/templates", tags=["Templates"])


@router.get(
    "",
    response_model=PromptTemplateListResponse,
    summary="获取模板列表",
    description="获取所有可用 Prompt 模板，支持按分类筛选。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def list_templates(
    request: Request,
    response: Response,
    category: str | None = Query(
        None,
        description="模板分类筛选",
        examples=["learning"],
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="分页大小（1-100）",
        examples=[20],
    ),
    offset: int = Query(
        0,
        ge=0,
        description="偏移量",
        examples=[0, 20, 40],
    ),
    db: AsyncSession = Depends(get_db),
) -> PromptTemplateListResponse:
    """返回模板列表，默认只展示启用的模板。"""
    filters = [PromptTemplate.is_active.is_(True)]
    if category:
        filters.append(PromptTemplate.category == category)

    total_result = await db.execute(
        select(func.count(PromptTemplate.id)).where(*filters)
    )
    total = total_result.scalar() or 0

    templates_result = await db.execute(
        select(PromptTemplate)
        .where(*filters)
        .order_by(PromptTemplate.usage_count.desc(), PromptTemplate.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    templates = templates_result.scalars().all()

    return PromptTemplateListResponse(
        templates=[
            PromptTemplateListItem.model_validate(template) for template in templates
        ],
        total=total,
    )


@router.get(
    "/{template_id}",
    response_model=PromptTemplateDetailResponse,
    summary="获取单个模板详情",
    description="根据模板 ID 获取完整 Prompt 模板详情。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def get_template(
    request: Request,
    response: Response,
    template_id: UUID = Path(
        ...,
        description="模板 ID",
        examples=["2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f"],
    ),
    db: AsyncSession = Depends(get_db),
) -> PromptTemplateDetailResponse:
    """获取模板详情（仅返回启用模板）。"""
    result = await db.execute(
        select(PromptTemplate).where(
            PromptTemplate.id == template_id,
            PromptTemplate.is_active.is_(True),
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail={"error": "TEMPLATE_NOT_FOUND"})

    return PromptTemplateDetailResponse.model_validate(template)
