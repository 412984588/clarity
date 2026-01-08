"""批量导出会话数据模块"""

import csv
import io
import json
from datetime import date, datetime
from typing import Literal, Sequence

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.message import Message
from app.models.solve_session import SessionStatus, SolveSession
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy import and_, func, or_, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def generate_csv(sessions: Sequence[Row[tuple[SolveSession, int]]]) -> str:
    """生成 CSV 格式的会话数据"""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "Session ID",
            "Status",
            "Current Step",
            "Created At",
            "Completed At",
            "Tags",
            "First Step Action",
            "Action Completed",
            "Action Completed At",
            "Message Count",
        ]
    )

    for row in sessions:
        session = row[0]
        message_count = row[1]
        writer.writerow(
            [
                str(session.id),
                session.status.value
                if hasattr(session.status, "value")
                else session.status,
                session.current_step.value
                if hasattr(session.current_step, "value")
                else session.current_step,
                session.created_at.isoformat(),
                session.completed_at.isoformat() if session.completed_at else "",
                ", ".join(session.tags) if session.tags else "",
                session.first_step_action or "",
                str(session.action_completed),
                session.action_completed_at.isoformat()
                if session.action_completed_at
                else "",
                message_count,
            ]
        )

    return output.getvalue()


def generate_json(
    sessions: Sequence[Row[tuple[SolveSession, int]]],
    messages_by_session: dict[str, list[Message]],
) -> str:
    """生成 JSON 格式的会话数据（包含完整消息）"""
    data = {
        "export_time": datetime.utcnow().isoformat(),
        "total_sessions": len(sessions),
        "sessions": [
            {
                "id": str(row[0].id),
                "status": row[0].status.value
                if hasattr(row[0].status, "value")
                else row[0].status,
                "current_step": row[0].current_step.value
                if hasattr(row[0].current_step, "value")
                else row[0].current_step,
                "created_at": row[0].created_at.isoformat(),
                "completed_at": row[0].completed_at.isoformat()
                if row[0].completed_at
                else None,
                "tags": row[0].tags,
                "first_step_action": row[0].first_step_action,
                "action_completed": row[0].action_completed,
                "action_completed_at": (
                    row[0].action_completed_at.isoformat()
                    if row[0].action_completed_at
                    else None
                ),
                "message_count": row[1],
                "messages": [
                    {
                        "id": str(m.id),
                        "role": m.role.value,
                        "content": m.content,
                        "created_at": m.created_at.isoformat(),
                    }
                    for m in messages_by_session.get(str(row[0].id), [])
                ],
            }
            for row in sessions
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


@router.get(
    "/all/export",
    summary="批量导出会话",
    description="""
    批量导出用户的所有会话数据。

    **功能特性**:
    - 支持 JSON 和 CSV 两种格式
    - 可选时间范围过滤（start_date, end_date）
    - 可选状态过滤（active, completed, abandoned）
    - 可选标签过滤（tags，逗号分隔）
    - JSON 格式包含完整消息内容
    - CSV 格式仅包含会话元数据和消息数量

    **使用场景**:
    - 数据备份
    - 数据分析
    - 数据迁移
    - 合规导出
    """,
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def batch_export_sessions(
    request: Request,
    format: Literal["json", "csv"] = Query("json", description="导出格式"),
    start_date: date | None = Query(None, description="开始日期（含）"),
    end_date: date | None = Query(None, description="结束日期（含）"),
    status: SessionStatus | None = Query(None, description="会话状态过滤"),
    tags: str | None = Query(None, description="标签过滤（逗号分隔）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """批量导出会话数据"""

    conditions = [SolveSession.user_id == current_user.id]

    if start_date:
        conditions.append(
            SolveSession.created_at >= datetime.combine(start_date, datetime.min.time())
        )

    if end_date:
        conditions.append(
            SolveSession.created_at <= datetime.combine(end_date, datetime.max.time())
        )

    if status:
        conditions.append(SolveSession.status == status.value)

    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            tag_conditions = [
                func.array_to_string(SolveSession.tags, ",").ilike(f"%{tag}%")
                for tag in tag_list
            ]
            conditions.append(or_(*tag_conditions))

    sessions_query = (
        select(SolveSession, func.count(Message.id).label("message_count"))
        .outerjoin(Message, Message.session_id == SolveSession.id)
        .where(and_(*conditions))
        .group_by(SolveSession.id)
        .order_by(SolveSession.created_at.desc())
    )

    result = await db.execute(sessions_query)
    sessions = result.all()

    if format == "csv":
        content = generate_csv(sessions)
        filename = f"sessions_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "text/csv; charset=utf-8",
            },
        )

    else:
        session_ids = [str(row[0].id) for row in sessions]

        if session_ids:
            messages_query = (
                select(Message)
                .where(Message.session_id.in_(session_ids))
                .order_by(Message.created_at)
            )
            messages_result = await db.execute(messages_query)
            all_messages = messages_result.scalars().all()

            messages_by_session: dict[str, list[Message]] = {}
            for msg in all_messages:
                session_id_str = str(msg.session_id)
                if session_id_str not in messages_by_session:
                    messages_by_session[session_id_str] = []
                messages_by_session[session_id_str].append(msg)
        else:
            messages_by_session = {}

        content = generate_json(sessions, messages_by_session)
        filename = f"sessions_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        return Response(
            content=content,
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/json; charset=utf-8",
            },
        )
