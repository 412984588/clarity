"""统计数据路由 - 提供会话统计、标签分析、时间趋势等数据洞察"""

import csv
import io
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.solve_session import SessionStatus, SolveSession, SolveStep
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
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


def generate_stats_csv(stats: dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Statistics Export Report"])
    writer.writerow(["Export Time", datetime.utcnow().isoformat()])
    writer.writerow([])

    writer.writerow(["Total Sessions", stats["total_sessions"]])
    writer.writerow([])

    writer.writerow(["Status Distribution"])
    writer.writerow(["Status", "Count"])
    for status, count in stats["status_distribution"].items():
        writer.writerow([status, count])
    writer.writerow([])

    writer.writerow(["Step Distribution"])
    writer.writerow(["Step", "Count"])
    for step, count in stats["step_distribution"].items():
        writer.writerow([step, count])
    writer.writerow([])

    writer.writerow(["Action Completion"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Actions", stats["action_completion"]["total"]])
    writer.writerow(["Completed Actions", stats["action_completion"]["completed"]])
    writer.writerow(
        ["Completion Rate (%)", stats["action_completion"]["completion_rate"]]
    )
    writer.writerow([])

    writer.writerow(["Top Tags"])
    writer.writerow(["Tag", "Count"])
    for tag_info in stats["top_tags"]:
        writer.writerow([tag_info["tag"], tag_info["count"]])
    writer.writerow([])

    writer.writerow(["Daily Trend (Last 30 Days)"])
    writer.writerow(["Date", "Count"])
    for trend_info in stats["daily_trend"]:
        writer.writerow([trend_info["date"], trend_info["count"]])

    return output.getvalue()


@router.get(
    "/export",
    summary="导出统计报告",
    description="""
    导出用户的统计数据报告。

    **功能特性**:
    - 支持 JSON 和 CSV 两种格式
    - JSON 格式：与 /stats/overview 相同的结构化数据
    - CSV 格式：分段展示各项统计指标，适合 Excel 查看

    **使用场景**:
    - 定期数据备份
    - 数据分析和可视化
    - 向第三方工具导入
    - 生成报告文档
    """,
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def export_stats(
    request: Request,
    format: Literal["json", "csv"] = Query("json", description="导出格式"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stats = await get_stats_overview(current_user=current_user, db=db)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    if format == "csv":
        content = generate_stats_csv(stats)
        filename = f"stats_report_{timestamp}.csv"
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "text/csv; charset=utf-8",
            },
        )

    else:
        stats_with_meta = {
            "export_time": datetime.utcnow().isoformat(),
            **stats,
        }
        content = json.dumps(stats_with_meta, ensure_ascii=False, indent=2)
        filename = f"stats_report_{timestamp}.json"
        return Response(
            content=content,
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/json; charset=utf-8",
            },
        )
