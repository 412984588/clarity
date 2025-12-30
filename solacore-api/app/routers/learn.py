"""学习功能路由 - 基于方法论引导的学习助手

内置方法论：
- 费曼学习法：用简单语言解释，测试真正理解程度
- 分块学习法：把大主题拆成小块，逐个攻克
- 主题交叉法：建立知识连接，启发跨界思考
- 艾宾浩斯遗忘曲线：科学的复习时间安排
- 双编码理论：文字+图像双重编码
- 80/20原则：找到20%的核心内容
- GROW模型：Goal→Reality→Options→Will
"""

import json
import logging
from datetime import datetime, timedelta
from typing import AsyncGenerator
from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    SSE_RATE_LIMIT,
    limiter,
    user_rate_limit_key,
)
from app.models.device import Device
from app.models.learn_message import LearnMessage, LearnMessageRole
from app.models.learn_session import LearnSession, LearnStep
from app.models.user import User
from app.services.ai_service import AIService
from app.services.content_filter import sanitize_user_input, strip_pii
from app.utils.datetime_utils import utc_now
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/learn", tags=["Learn"])

# ==================== 方法论提示词模板 ====================

LEARN_STEP_PROMPTS = {
    LearnStep.START.value: """你是 Solacore 学习助手，一位温暖、专业的学习教练。

当前阶段：开始 (Start)

你的任务：
- 了解用户想学习什么主题
- 评估用户当前对这个主题的理解程度
- 识别学习目标和现有知识差距

内置方法论：
📚 **费曼学习法**：让用户用自己的话描述对这个主题的了解。如果讲不清楚，说明还没真正理解。
📊 **80/20原则**：帮助识别这个主题最核心的20%内容，这20%往往能带来80%的价值。

引导策略：
1. 热情欢迎，询问用户想学什么
2. 让用户用简单的话描述他们对这个主题已经知道什么
3. 通过追问评估当前理解程度（不要让用户感到被考试）
4. 总结学习目标和需要突破的点

语言要求：必须用中文回复，语气温暖鼓励，像朋友聊天。
回复长度：2-4句话，简洁有引导性。""",
    LearnStep.EXPLORE.value: """你是 Solacore 学习助手，一位温暖、专业的学习教练。

当前阶段：探索 (Explore)

你的任务：
- 帮助用户深入理解核心概念
- 用通俗易懂的方式解释复杂内容
- 建立知识之间的连接

内置方法论：
📚 **费曼学习法**：用最简单的语言解释概念。如果能让一个小学生听懂，说明你真的理解了。
🧩 **分块学习法**：把大概念拆成小块，一次只讲1-2个要点，避免信息过载。
🔗 **主题交叉法**：关联其他领域的类似概念，问"这个和XX有什么相似之处？"

引导策略：
1. 把复杂概念用比喻和类比来解释（比如：数据库像图书馆，API像餐厅菜单）
2. 每讲完一个要点，让用户用自己的话复述
3. 如果用户讲不清楚，换一个角度或更简单的比喻重新解释
4. 适时问"这个概念让你想到了什么？"启发跨界联想

语言要求：必须用中文回复，解释要通俗易懂，避免专业术语。
回复长度：根据概念复杂度调整，但一次只讲1-2个要点。""",
    LearnStep.PRACTICE.value: """你是 Solacore 学习助手，一位温暖、专业的学习教练。

当前阶段：练习 (Practice)

你的任务：
- 通过实际练习巩固用户的理解
- 让用户"教出来"验证是否真的学会
- 及时反馈，帮助纠正误解

内置方法论：
🎨 **双编码理论**：同时使用文字描述和图表/流程图来强化记忆。
📚 **费曼教学法**：让用户假装教给一个10岁的小朋友，用最简单的语言解释。
🔗 **主题交叉法**：设计跨领域的应用场景，加深理解。

引导策略：
1. 设计一个简单的应用场景或小问题
2. 让用户尝试用学到的知识来解答
3. 提供鼓励性反馈，不要让用户感到挫败
4. 如果有误解，温和地纠正并解释为什么
5. 逐步增加难度，但保持可达成感

语言要求：必须用中文回复，鼓励为主，纠错要温和。
回复长度：2-4句话。""",
    LearnStep.PLAN.value: """你是 Solacore 学习助手，一位温暖、专业的学习教练。

当前阶段：规划 (Plan)

你的任务：
- 总结本次学习的核心收获
- 制定科学的复习计划
- 明确下一步学习行动

内置方法论：
📈 **艾宾浩斯遗忘曲线**：科学的复习节点：1天后、3天后、7天后、15天后、30天后。
📊 **80/20原则**：提炼出最值得记住的20%核心内容。
🎯 **GROW模型**：
  - Goal（目标）：你想达到什么水平？
  - Reality（现状）：现在掌握到什么程度？
  - Options（选项）：有哪些继续学习的方式？
  - Will（行动）：下一步具体做什么？

引导策略：
1. 总结本次学习的3个核心收获（80/20提炼）
2. 按艾宾浩斯曲线制定复习提醒：
   - 明天回顾一次
   - 3天后再回顾
   - 一周后巩固
3. 用GROW模型帮用户明确下一步：
   - "你希望在这个主题上达到什么水平？"
   - "接下来你打算怎么继续学习？"
4. 给出1-2个具体可行的学习资源建议

语言要求：必须用中文回复，语气温暖鼓励。
回复长度：可以稍长，因为要给出具体的复习计划。""",
}

# 步骤顺序定义
LEARN_STEP_ORDER = [
    LearnStep.START,
    LearnStep.EXPLORE,
    LearnStep.PRACTICE,
    LearnStep.PLAN,
]


def get_next_learn_step(current: LearnStep) -> LearnStep | None:
    """获取下一个学习步骤"""
    try:
        idx = LEARN_STEP_ORDER.index(current)
        if idx < len(LEARN_STEP_ORDER) - 1:
            return LEARN_STEP_ORDER[idx + 1]
        return None  # 已是最后一步
    except ValueError:
        return None


def is_final_learn_step(step: LearnStep) -> bool:
    """是否是最后一步"""
    return step == LearnStep.PLAN


# ==================== Pydantic Schemas ====================


class LearnSessionCreateResponse(BaseModel):
    """创建学习会话响应"""

    session_id: UUID = Field(..., description="会话ID")
    status: str = Field(..., description="会话状态")
    current_step: str = Field(..., description="当前步骤")
    created_at: datetime = Field(..., description="创建时间")


class LearnMessageRequest(BaseModel):
    """发送消息请求"""

    content: str = Field(..., min_length=1, max_length=4000, description="消息内容")
    step: str = Field(..., description="当前步骤")


class LearnMessageResponse(BaseModel):
    """消息响应"""

    id: UUID
    role: str
    content: str
    step: str | None
    created_at: datetime


class LearnSessionResponse(BaseModel):
    """会话详情响应"""

    id: UUID
    status: str
    current_step: str
    topic: str | None
    key_concepts: list | None
    review_schedule: dict | None
    created_at: datetime
    completed_at: datetime | None
    messages: list[LearnMessageResponse] = []


class LearnSessionListItem(BaseModel):
    """会话列表项"""

    id: UUID
    status: str
    current_step: str
    topic: str | None
    created_at: datetime
    first_message: str | None = None


class LearnSessionListResponse(BaseModel):
    """会话列表响应"""

    sessions: list[LearnSessionListItem]
    total: int
    limit: int
    offset: int


# ==================== API 端点 ====================


@router.post(
    "",
    response_model=LearnSessionCreateResponse,
    status_code=201,
    summary="创建学习会话",
    description="创建一个新的学习会话，开始基于方法论的学习引导。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def create_learn_session(
    request: Request,
    x_device_fingerprint: str | None = Header(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建学习会话"""
    # 查找设备
    device = None
    if x_device_fingerprint:
        result = await db.execute(
            select(Device).where(
                Device.user_id == current_user.id,
                Device.fingerprint == x_device_fingerprint,
            )
        )
        device = result.scalar_one_or_none()

    # 创建学习会话
    session = LearnSession(
        user_id=current_user.id,
        device_id=device.id if device else None,
        status="active",
        current_step=LearnStep.START.value,
        locale="zh",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    logger.info(
        f"Learn session {session.id} created for user {current_user.id}",
        extra={"session_id": str(session.id), "user_id": str(current_user.id)},
    )

    return JSONResponse(
        status_code=201,
        content={
            "session_id": str(session.id),
            "status": session.status,
            "current_step": session.current_step,
            "created_at": session.created_at.isoformat(),
        },
    )


@router.get(
    "",
    response_model=LearnSessionListResponse,
    summary="获取学习会话列表",
    description="获取当前用户的所有学习会话列表。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def list_learn_sessions(
    request: Request,
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取学习会话列表"""
    # 子查询：获取每个会话的第一条用户消息
    first_message_subq = (
        select(
            LearnMessage.session_id,
            LearnMessage.content.label("first_message"),
        )
        .where(LearnMessage.role == LearnMessageRole.USER.value)
        .distinct(LearnMessage.session_id)
        .order_by(LearnMessage.session_id, LearnMessage.created_at.asc())
        .subquery()
    )

    # 主查询
    query = (
        select(LearnSession, first_message_subq.c.first_message)
        .outerjoin(
            first_message_subq,
            LearnSession.id == first_message_subq.c.session_id,
        )
        .where(LearnSession.user_id == current_user.id)
        .order_by(LearnSession.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    # 获取总数
    count_result = await db.execute(
        select(func.count(LearnSession.id)).where(
            LearnSession.user_id == current_user.id
        )
    )
    total = count_result.scalar() or 0

    sessions = []
    for session, first_message in rows:
        # 截断第一条消息
        truncated_message = None
        if first_message:
            truncated_message = (
                first_message[:50] + "..." if len(first_message) > 50 else first_message
            )

        sessions.append(
            {
                "id": str(session.id),
                "status": session.status,
                "current_step": session.current_step,
                "topic": session.topic,
                "created_at": session.created_at.isoformat(),
                "first_message": truncated_message,
            }
        )

    return JSONResponse(
        content={
            "sessions": sessions,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


@router.get(
    "/{session_id}",
    response_model=LearnSessionResponse,
    summary="获取学习会话详情",
    description="获取指定学习会话的详细信息，包括消息历史。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def get_learn_session(
    request: Request,
    session_id: UUID = Path(..., description="会话ID"),
    include_messages: bool = Query(True, description="是否包含消息历史"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取学习会话详情"""
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    response_data = {
        "id": str(session.id),
        "status": session.status,
        "current_step": session.current_step,
        "topic": session.topic,
        "key_concepts": session.key_concepts,
        "review_schedule": session.review_schedule,
        "created_at": session.created_at.isoformat(),
        "completed_at": session.completed_at.isoformat()
        if session.completed_at
        else None,
        "messages": [],
    }

    if include_messages:
        response_data["messages"] = [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "step": msg.step,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in session.messages
        ]

    return JSONResponse(content=response_data)


@router.post(
    "/{session_id}/messages",
    summary="发送学习消息",
    description="向学习会话发送消息，获取 AI 基于方法论的引导回复。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(SSE_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def send_learn_message(
    request: Request,
    message_request: LearnMessageRequest,
    session_id: UUID = Path(..., description="会话ID"),
    x_device_fingerprint: str | None = Header(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息并获取流式回复"""
    # 查询会话
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    if session.status != "active":
        raise HTTPException(status_code=400, detail={"error": "SESSION_NOT_ACTIVE"})

    # 内容过滤
    sanitized_content = sanitize_user_input(message_request.content)
    sanitized_content = strip_pii(sanitized_content)

    # 保存用户消息
    user_message = LearnMessage(
        session_id=session.id,
        role=LearnMessageRole.USER.value,
        content=sanitized_content,
        step=message_request.step,
    )
    db.add(user_message)

    # 如果是第一条消息，提取学习主题
    if not session.topic and message_request.step == LearnStep.START.value:
        # 简单提取主题：取前30个字符
        session.topic = sanitized_content[:30] + (
            "..." if len(sanitized_content) > 30 else ""
        )

    await db.commit()

    # 获取历史消息用于上下文
    history_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in session.messages
        if msg.id != user_message.id  # 排除刚添加的消息
    ]

    # 构建包含历史的用户提示
    if history_messages:
        history_text = "Previous conversation:\n"
        for msg in history_messages[-6:]:  # 只保留最近 6 条消息
            role_label = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role_label}: {msg['content']}\n"
        user_prompt_with_history = (
            f"{history_text}\nCurrent message: {sanitized_content}"
        )
    else:
        user_prompt_with_history = sanitized_content

    # 获取系统提示词
    current_step = LearnStep(session.current_step)
    system_prompt = LEARN_STEP_PROMPTS.get(
        current_step.value,
        LEARN_STEP_PROMPTS[LearnStep.START.value],
    )

    # AI 服务
    ai_service = AIService()

    async def event_generator() -> AsyncGenerator[str, None]:
        """SSE 事件生成器"""
        accumulated_content = ""

        try:
            async for token in ai_service.stream(
                system_prompt, user_prompt_with_history
            ):
                accumulated_content += token
                yield f"event: token\ndata: {json.dumps({'content': token})}\n\n"

            # 保存 AI 回复
            ai_message = LearnMessage(
                session_id=session.id,
                role=LearnMessageRole.ASSISTANT.value,
                content=accumulated_content,
                step=current_step.value,
            )
            db.add(ai_message)

            # 检查是否可以进入下一步
            next_step = get_next_learn_step(current_step)
            step_completed = (
                len(accumulated_content) > 50
            )  # 简单判断：回复足够长则可进入下一步

            # 如果是最后一步，生成复习计划
            if is_final_learn_step(current_step):
                session.status = "completed"
                session.completed_at = utc_now()
                # 生成艾宾浩斯复习计划
                now = utc_now()
                session.review_schedule = {
                    "day_1": (now + timedelta(days=1)).isoformat(),
                    "day_3": (now + timedelta(days=3)).isoformat(),
                    "day_7": (now + timedelta(days=7)).isoformat(),
                    "day_15": (now + timedelta(days=15)).isoformat(),
                    "day_30": (now + timedelta(days=30)).isoformat(),
                }

            await db.commit()
            await db.refresh(ai_message)

            # 发送完成事件
            done_data = json.dumps(
                {
                    "message_id": str(ai_message.id),
                    "next_step": next_step.value if next_step else None,
                    "step_completed": step_completed,
                    "session_completed": session.status == "completed",
                }
            )
            yield f"event: done\ndata: {done_data}\n\n"

        except Exception as e:
            logger.error(f"Error in learn stream: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.patch(
    "/{session_id}",
    summary="更新学习会话",
    description="更新学习会话的状态或当前步骤。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def update_learn_session(
    request: Request,
    session_id: UUID = Path(..., description="会话ID"),
    current_step: str | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新学习会话"""
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    if current_step:
        # 验证步骤值
        try:
            new_step = LearnStep(current_step)
            session.current_step = new_step.value
        except ValueError:
            raise HTTPException(status_code=400, detail={"error": "INVALID_STEP"})

    if status:
        if status not in ["active", "completed", "abandoned"]:
            raise HTTPException(status_code=400, detail={"error": "INVALID_STATUS"})
        session.status = status
        if status == "completed":
            session.completed_at = utc_now()

    await db.commit()
    await db.refresh(session)

    return JSONResponse(
        content={
            "id": str(session.id),
            "status": session.status,
            "current_step": session.current_step,
            "topic": session.topic,
        }
    )


@router.delete(
    "/{session_id}",
    status_code=204,
    summary="删除学习会话",
    description="删除指定的学习会话及其所有消息。",
    responses={**COMMON_ERROR_RESPONSES},
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def delete_learn_session(
    request: Request,
    session_id: UUID = Path(..., description="会话ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除学习会话"""
    result = await db.execute(
        select(LearnSession).where(
            LearnSession.id == session_id,
            LearnSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    await db.delete(session)
    await db.commit()

    logger.info(
        f"Learn session {session_id} deleted by user {current_user.id}",
        extra={"session_id": str(session_id), "user_id": str(current_user.id)},
    )

    return JSONResponse(content=None, status_code=204)
