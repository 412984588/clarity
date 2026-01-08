"""统计数据路由 - 提供会话统计、标签分析、时间趋势等数据洞察"""

from datetime import datetime, timedelta, timezone
from typing import Any

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.solve_session import SessionStatus, SolveSession, SolveStep
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get(
    "/overview",
    summary="获取统计概览",
    description="返回用户的会话统计数据，包括状态分布、标签频率、时间趋势、行动完成率等。",
    responses={
        **COMMON_ERROR_RESPONSES,
        200: {
            "description": "统计数据",
            "content": {
                "application/json": {
                    "example": {
                        "total_sessions": 150,
                        "status_distribution": {
                            "active": 45,
                            "completed": 95,
                            "abandoned": 10,
                        },
                        "top_tags": [
                            {"tag": "工作", "count": 50},
                            {"tag": "学习", "count": 35},
                        ],
                        "daily_trend": [
                            {"date": "2026-01-01", "count": 5},
                            {"date": "2026-01-02", "count": 8},
                        ],
                        "action_completion": {
                            "total": 80,
                            "completed": 60,
                            "completion_rate": 75.0,
                        },
                        "step_distribution": {
                            "receive": 20,
                            "clarify": 15,
                            "reframe": 10,
                            "options": 8,
                            "commit": 7,
                        },
                    }
                }
            },
        },
    },
)
async def get_stats_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """获取用户的统计概览数据"""

    # 1. 总会话数
    total_query = select(func.count(SolveSession.id)).where(
        SolveSession.user_id == current_user.id
    )
    total_result = await db.execute(total_query)
    total_sessions = total_result.scalar() or 0

    # 2. 状态分布
    status_query = (
        select(SolveSession.status, func.count(SolveSession.id).label("count"))
        .where(SolveSession.user_id == current_user.id)
        .group_by(SolveSession.status)
    )
    status_result = await db.execute(status_query)
    status_distribution: dict[str, int] = {
        SessionStatus.ACTIVE.value: 0,
        SessionStatus.COMPLETED.value: 0,
        SessionStatus.ABANDONED.value: 0,
    }
    for row in status_result:
        status_distribution[row.status] = row.count  # type: ignore[assignment]

    # 3. 标签频率（Top 10）
    # PostgreSQL ARRAY 需要使用 unnest 展开
    tag_query = (
        select(
            func.unnest(SolveSession.tags).label("tag"),
            func.count().label("count"),
        )
        .where(SolveSession.user_id == current_user.id)
        .where(func.array_length(SolveSession.tags, 1) > 0)  # type: ignore[arg-type]
        .group_by("tag")
        .order_by(func.count().desc())
        .limit(10)
    )
    tag_result = await db.execute(tag_query)
    top_tags = [{"tag": row.tag, "count": row.count} for row in tag_result]  # type: ignore[misc]

    # 4. 时间趋势（最近 30 天）
    thirty_days_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        days=30
    )
    trend_query = (
        select(
            func.date(SolveSession.created_at).label("date"),
            func.count(SolveSession.id).label("count"),
        )
        .where(SolveSession.user_id == current_user.id)
        .where(SolveSession.created_at >= thirty_days_ago)
        .group_by(func.date(SolveSession.created_at))
        .order_by(func.date(SolveSession.created_at))
    )
    trend_result = await db.execute(trend_query)
    daily_trend = [
        {"date": row.date.isoformat(), "count": row.count} for row in trend_result
    ]

    # 5. 行动完成率
    action_total_query = select(func.count(SolveSession.id)).where(
        SolveSession.user_id == current_user.id,
        SolveSession.first_step_action.isnot(None),
    )
    action_total_result = await db.execute(action_total_query)
    action_total = action_total_result.scalar() or 0

    action_completed_query = select(func.count(SolveSession.id)).where(
        SolveSession.user_id == current_user.id,
        SolveSession.action_completed.is_(True),
    )
    action_completed_result = await db.execute(action_completed_query)
    action_completed = action_completed_result.scalar() or 0

    completion_rate = (
        round((action_completed / action_total) * 100, 1) if action_total > 0 else 0.0
    )

    # 6. 步骤分布
    step_query = (
        select(SolveSession.current_step, func.count(SolveSession.id).label("count"))
        .where(SolveSession.user_id == current_user.id)
        .group_by(SolveSession.current_step)
    )
    step_result = await db.execute(step_query)
    step_distribution: dict[str, int] = {
        SolveStep.RECEIVE.value: 0,
        SolveStep.CLARIFY.value: 0,
        SolveStep.REFRAME.value: 0,
        SolveStep.OPTIONS.value: 0,
        SolveStep.COMMIT.value: 0,
    }
    for row in step_result:
        step_distribution[row.current_step] = row.count  # type: ignore[assignment]

    return {
        "total_sessions": total_sessions,
        "status_distribution": status_distribution,
        "top_tags": top_tags,
        "daily_trend": daily_trend,
        "action_completion": {
            "total": action_total,
            "completed": action_completed,
            "completion_rate": completion_rate,
        },
        "step_distribution": step_distribution,
    }
