from datetime import datetime
from typing import Literal
from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.message import Message
from app.models.solve_session import SolveSession
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def sanitize_filename(text: str | None, max_length: int = 50) -> str:
    if not text:
        return "session"
    safe = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in text)
    return safe[:max_length].strip()


def generate_markdown(session: SolveSession, messages: list[Message]) -> str:
    lines = [
        f"# {session.first_step_action or '会话记录'}",
        "",
        "## 元数据",
        f"- **创建时间**: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **状态**: {session.status}",
        f"- **当前步骤**: {session.current_step}",
    ]

    if session.tags:
        lines.append(f"- **标签**: {', '.join(session.tags)}")

    if session.completed_at:
        lines.append(
            f"- **完成时间**: {session.completed_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    if session.first_step_action:
        lines.extend(
            [
                "",
                "## 行动计划",
                "",
                session.first_step_action,
            ]
        )

        if session.action_completed:
            completed_time = (
                session.action_completed_at.strftime("%Y-%m-%d %H:%M:%S")
                if session.action_completed_at
                else "未知"
            )
            lines.append(f"\n✅ **已完成** ({completed_time})")

    lines.extend(
        [
            "",
            "## 对话历史",
            "",
        ]
    )

    for msg in messages:
        role_name = "👤 用户" if msg.role.value == "user" else "🤖 助手"
        timestamp = msg.created_at.strftime("%H:%M:%S")
        lines.extend(
            [
                f"### {role_name} ({timestamp})",
                "",
                msg.content,
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "",
            f"*导出时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*",
        ]
    )

    return "\n".join(lines)


@router.get(
    "/{session_id}/export",
    summary="导出会话",
    description="导出会话为 Markdown 或 JSON 格式",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def export_session(
    request: Request,
    session_id: UUID = Path(..., description="会话 ID"),
    format: Literal["markdown", "json"] = Query(
        "markdown", description="导出格式：markdown 或 json"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SolveSession).where(
            SolveSession.id == session_id, SolveSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    messages_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()

    first_message = next((m.content for m in messages if m.role.value == "user"), None)
    filename_base = sanitize_filename(first_message)
    date_str = session.created_at.strftime("%Y%m%d")

    if format == "markdown":
        content = generate_markdown(session, list(messages))
        filename = f"{filename_base}_{date_str}.md"
        return Response(
            content=content,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "text/markdown; charset=utf-8",
            },
        )
    else:
        import json

        data = {
            "id": str(session.id),
            "status": str(session.status),
            "current_step": str(session.current_step),
            "created_at": session.created_at.isoformat(),
            "completed_at": (
                session.completed_at.isoformat() if session.completed_at else None
            ),
            "tags": session.tags,
            "first_step_action": session.first_step_action,
            "action_completed": session.action_completed,
            "action_completed_at": (
                session.action_completed_at.isoformat()
                if session.action_completed_at
                else None
            ),
            "messages": [
                {
                    "id": str(m.id),
                    "role": str(m.role.value),
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ],
        }
        filename = f"{filename_base}_{date_str}.json"
        return Response(
            content=json.dumps(data, ensure_ascii=False, indent=2),
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/json; charset=utf-8",
            },
        )
