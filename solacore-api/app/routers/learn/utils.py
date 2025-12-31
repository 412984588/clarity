"""学习功能路由 - 辅助函数"""

from datetime import timedelta

from app.models.learn_session import LearnSession
from app.utils.datetime_utils import utc_now
from fastapi import HTTPException


def _validate_session(session: LearnSession | None) -> LearnSession:
    """验证会话是否存在且处于活跃状态"""
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})
    if session.status != "active":
        raise HTTPException(status_code=400, detail={"error": "SESSION_NOT_ACTIVE"})
    return session


def _build_context_prompt(
    history_messages: list[dict[str, str]], sanitized_content: str
) -> str:
    """构建包含历史上下文的用户提示"""
    if not history_messages:
        return sanitized_content

    history_text = "Previous conversation:\n"
    for msg in history_messages[-6:]:  # 只保留最近 6 条消息
        role_label = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role_label}: {msg['content']}\n"
    return f"{history_text}\nCurrent message: {sanitized_content}"


def _generate_review_schedule() -> dict[str, str]:
    """生成艾宾浩斯复习计划"""
    now = utc_now()
    return {
        "day_1": (now + timedelta(days=1)).isoformat(),
        "day_3": (now + timedelta(days=3)).isoformat(),
        "day_7": (now + timedelta(days=7)).isoformat(),
        "day_15": (now + timedelta(days=15)).isoformat(),
        "day_30": (now + timedelta(days=30)).isoformat(),
    }
