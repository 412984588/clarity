# 会话读取路由：提供会话列表与单个会话详情

from datetime import datetime
from typing import Optional, cast
from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.message import Message, MessageRole
from app.models.solve_session import SessionStatus, SolveSession
from app.models.user import User
from app.schemas.session import (
    MessageResponse,
    SessionListItem,
    SessionListResponse,
    SessionResponse,
)
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from sqlalchemy import Column, func, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

router = APIRouter()


@router.get(
    "/",
    response_model=SessionListResponse,
    summary="获取会话列表",
    description="获取当前用户的所有会话列表，支持分页和搜索过滤。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def list_sessions(
    request: Request,
    response: Response,
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
        description="分页偏移量",
        examples=[0],
    ),
    q: Optional[str] = Query(
        None,
        description="搜索关键词（搜索第一条消息内容）",
        examples=["如何学习编程"],
    ),
    tags: Optional[str] = Query(
        None,
        description="标签过滤（逗号分隔，匹配任意一个标签）",
        examples=["工作,重要"],
    ),
    status: Optional[SessionStatus] = Query(
        None,
        description="状态过滤",
        examples=["active"],
    ),
    from_date: Optional[datetime] = Query(
        None,
        description="开始时间（ISO 8601 格式）",
        examples=["2026-01-01T00:00:00Z"],
    ),
    to_date: Optional[datetime] = Query(
        None,
        description="结束时间（ISO 8601 格式）",
        examples=["2026-01-31T23:59:59Z"],
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分页返回当前用户的 Solve 会话列表，包含第一条用户消息，支持搜索和过滤。"""
    # 构建基础查询条件
    base_conditions = [SolveSession.user_id == current_user.id]

    # 状态过滤
    if status:
        base_conditions.append(SolveSession.status == status)

    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            tags_column = cast(Column[ARRAY], SolveSession.tags)  # type: ignore[misc]
            base_conditions.append(tags_column.overlap(tag_list))  # type: ignore[attr-defined]

    # 时间范围过滤
    if from_date:
        base_conditions.append(SolveSession.created_at >= from_date)
    if to_date:
        base_conditions.append(SolveSession.created_at <= to_date)

    # 计算总数
    total_result = await db.execute(
        select(func.count(SolveSession.id)).where(*base_conditions)
    )
    total = total_result.scalar() or 0

    # 子查询：获取每个会话的第一条用户消息
    first_message_subq = (
        select(
            Message.session_id,
            Message.content,
        )
        .where(Message.role == MessageRole.USER)
        .distinct(Message.session_id)
        .order_by(Message.session_id, Message.created_at.asc())
        .subquery()
    )

    # 主查询：会话列表 + 第一条消息
    query = (
        select(SolveSession, first_message_subq.c.content)
        .outerjoin(
            first_message_subq,
            SolveSession.id == first_message_subq.c.session_id,
        )
        .where(*base_conditions)
    )

    # 关键词搜索（搜索第一条消息内容）
    if q:
        query = query.where(first_message_subq.c.content.ilike(f"%{q}%"))

    # 排序和分页
    query = query.order_by(SolveSession.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    rows = result.all()

    # 手动组装数据
    session_items = []
    for session, first_msg_content in rows:
        item_data = {
            "id": session.id,
            "status": str(session.status),
            "current_step": str(session.current_step),
            "created_at": session.created_at,
            "completed_at": session.completed_at,
            "first_message": first_msg_content[:50] + "..."
            if first_msg_content and len(first_msg_content) > 50
            else first_msg_content,
        }
        session_items.append(SessionListItem(**item_data))

    response = SessionListResponse(
        sessions=session_items,
        total=total,
        limit=limit,
        offset=offset,
    )
    return response


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    response_model_exclude_none=True,
    summary="获取单个会话详情",
    description=(
        "获取指定会话的详细信息。默认不返回消息历史，"
        "需要时可通过 include_messages=true 返回分页消息。"
    ),
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def get_session(
    request: Request,
    response: Response,
    session_id: UUID = Path(
        ...,
        description="会话 ID",
        examples=["2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f"],
    ),
    include_messages: bool = Query(
        False,
        description="是否返回会话消息（默认不返回）",
        examples=[False],
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="消息分页大小，仅 include_messages=true 生效",
        examples=[20],
    ),
    offset: int = Query(
        0,
        ge=0,
        description="消息分页偏移，仅 include_messages=true 生效",
        examples=[0],
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单个 Solve 会话详情，可选返回消息列表。"""
    result = await db.execute(
        select(SolveSession)
        .options(noload(SolveSession.messages))
        .where(SolveSession.id == session_id, SolveSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})
    messages = None
    if include_messages:
        messages_result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
            .limit(limit)
            .offset(offset)
        )
        message_rows = messages_result.scalars().all()
        messages = [MessageResponse.model_validate(message) for message in message_rows]

    response = SessionResponse(
        id=session.id,
        status=str(session.status),
        current_step=str(session.current_step),
        created_at=session.created_at,
        completed_at=session.completed_at,
        messages=messages,
    )
    return response
