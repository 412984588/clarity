from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.solve_session import SolveSession
from app.models.user import User
from app.schemas.action import ActionItem, ActionListResponse, ActionStats, Pagination
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/actions", tags=["Actions"])


@router.get("/", response_model=ActionListResponse)
async def list_actions(
    status: Literal["pending", "completed", "all"] = "all",
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SolveSession).where(
        SolveSession.user_id == current_user.id,
        SolveSession.first_step_action.isnot(None),
    )

    if status == "pending":
        query = query.where(~SolveSession.action_completed)
    elif status == "completed":
        query = query.where(SolveSession.action_completed)

    query = (
        query.order_by(
            SolveSession.action_completed.asc(), SolveSession.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    sessions = result.scalars().all()

    stats_query = select(
        func.count(SolveSession.id).label("total"),
        func.sum(func.cast(SolveSession.action_completed, Integer)).label("completed"),
    ).where(
        SolveSession.user_id == current_user.id,
        SolveSession.first_step_action.isnot(None),
    )

    stats_result = await db.execute(stats_query)
    stats = stats_result.one()

    total = stats.total or 0
    completed = stats.completed or 0
    pending = total - completed

    return ActionListResponse(
        actions=[
            ActionItem(
                id=s.id,
                action=s.first_step_action or "",
                completed=s.action_completed,
                completed_at=s.action_completed_at,
                created_at=s.created_at,
                session_id=s.id,
            )
            for s in sessions
        ],
        stats=ActionStats(
            total=total,
            completed=completed,
            pending=pending,
            completion_rate=(completed / total * 100) if total else 0,
        ),
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )


@router.patch("/{session_id}/complete")
async def complete_action(
    session_id: UUID,
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
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.first_step_action:
        raise HTTPException(status_code=400, detail="No action plan in this session")

    session.action_completed = True
    session.action_completed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await db.commit()
    await db.refresh(session)

    return {
        "id": session.id,
        "action_completed": session.action_completed,
        "action_completed_at": session.action_completed_at,
    }


@router.patch("/{session_id}/uncomplete")
async def uncomplete_action(
    session_id: UUID,
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
        raise HTTPException(status_code=404, detail="Session not found")

    session.action_completed = False
    session.action_completed_at = None

    await db.commit()
    await db.refresh(session)

    return {
        "id": session.id,
        "action_completed": session.action_completed,
        "action_completed_at": session.action_completed_at,
    }
