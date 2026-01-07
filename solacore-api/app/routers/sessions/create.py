# 会话创建路由：处理创建 Solve 会话与使用量统计

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.device import Device
from app.models.message import Message, MessageRole
from app.models.prompt_template import PromptTemplate
from app.models.solve_session import SessionStatus, SolveSession, SolveStep
from app.models.step_history import StepHistory
from app.models.subscription import Subscription, Usage
from app.models.user import User
from app.schemas.session import SessionCreateRequest, SessionCreateResponse
from app.services.analytics_service import AnalyticsService
from app.utils.datetime_utils import utc_now
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, Response
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import SESSION_LIMITS, _get_or_create_usage, _period_start_for_tier

router = APIRouter()


@router.post(
    "/",
    response_model=SessionCreateResponse,
    status_code=201,
    summary="创建 Solve 会话",
    description="""
    创建一个新的 5 步 Solve 会话。

    **需要认证**: 是（Bearer Token / Cookie）

    **Headers 必须**:
    - `X-Device-Fingerprint`: 设备指纹

    **返回**: 新建会话的 ID 和初始状态
    """,
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def create_session(
    request: Request,
    response: Response,
    payload: SessionCreateRequest | None = Body(default=None),
    current_user: User = Depends(get_current_user),
    device_fingerprint: str = Header(
        ...,
        alias="X-Device-Fingerprint",
        description="设备指纹，用于识别当前设备",
        examples=["ios-4f3e9b2c"],
    ),
    db: AsyncSession = Depends(get_db),
):
    """创建新的 Solve 会话并返回会话基础信息与使用量。"""
    template: PromptTemplate | None = None
    if payload and payload.template_id:
        template_result = await db.execute(
            select(PromptTemplate).where(
                PromptTemplate.id == payload.template_id,
                PromptTemplate.is_active.is_(True),
            )
        )
        template = template_result.scalar_one_or_none()
        if not template:
            raise HTTPException(status_code=404, detail={"error": "TEMPLATE_NOT_FOUND"})

    device_result = await db.execute(
        select(Device).where(
            Device.user_id == current_user.id,
            Device.device_fingerprint == device_fingerprint,
        )
    )
    # 使用 .first() 容错重复记录（数据库可能存在历史重复数据）
    device = device_result.scalars().first()
    if not device:
        raise HTTPException(status_code=403, detail={"error": "DEVICE_NOT_FOUND"})

    subscription_result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = subscription_result.scalar_one_or_none()
    if not subscription:
        subscription = Subscription(user_id=current_user.id, tier="free")
        db.add(subscription)
        await db.flush()

    tier: str = str(subscription.tier)
    sessions_limit: int = SESSION_LIMITS.get(tier, SESSION_LIMITS["free"])

    # Beta 模式移除 session 限制
    settings = get_settings()
    if settings.beta_mode:
        sessions_limit = 0  # 0 表示无限制

    usage = await _get_or_create_usage(db, subscription)

    # 原子递增 session_count，避免并发丢失更新
    period_start = _period_start_for_tier(
        tier, subscription.created_at, subscription.current_period_start
    )
    stmt = (
        update(Usage)
        .where(Usage.user_id == current_user.id, Usage.period_start == period_start)
        .values(session_count=Usage.session_count + 1)
    )
    await db.execute(stmt)
    result = await db.execute(
        select(Usage.session_count).where(
            Usage.user_id == current_user.id, Usage.period_start == period_start
        )
    )
    new_count = result.scalar_one()

    # 检查是否超限（递增后再检查，避免竞态条件）
    if sessions_limit > 0 and new_count > sessions_limit:
        # 超限则回滚递增
        rollback_stmt = (
            update(Usage)
            .where(Usage.user_id == current_user.id, Usage.period_start == period_start)
            .values(session_count=Usage.session_count - 1)
        )
        await db.execute(rollback_stmt)
        raise HTTPException(
            status_code=403,
            detail={
                "error": "QUOTA_EXCEEDED",
                "usage": {
                    "used": new_count - 1,
                    "limit": sessions_limit,
                    "tier": tier,
                },
                "upgrade_url": "/subscriptions/checkout",
            },
        )

    usage.session_count = new_count  # keep response in sync with DB

    session = SolveSession(
        user_id=current_user.id,
        device_id=device.id,
        status=SessionStatus.ACTIVE.value,
        current_step=SolveStep.RECEIVE.value,
    )
    if template:
        session.template_id = template.id  # type: ignore[assignment]
    db.add(session)
    await db.flush()

    # 创建初始 StepHistory
    step_history = StepHistory(
        session_id=session.id,
        step=SolveStep.RECEIVE.value,
        started_at=utc_now(),
    )
    db.add(step_history)
    if template:
        system_message = Message(
            session_id=session.id,
            role=MessageRole.SYSTEM.value,
            content=template.system_prompt,
        )
        db.add(system_message)

        if template.welcome_message:
            welcome_message = Message(
                session_id=session.id,
                role=MessageRole.ASSISTANT.value,
                content=template.welcome_message,
            )
            db.add(welcome_message)

        # 原子更新 usage_count，避免高并发下的丢失更新问题
        await db.execute(
            update(PromptTemplate)
            .where(PromptTemplate.id == template.id)
            .values(usage_count=PromptTemplate.usage_count + 1)
        )

    # 记录 session_started 事件
    analytics_service = AnalyticsService(db)
    await analytics_service.emit(
        "session_started",
        session.id,  # type: ignore[arg-type]
        {"user_id": str(current_user.id), "device_id": str(device.id)},
    )

    await db.commit()

    return SessionCreateResponse(
        session_id=session.id,
        status=str(session.status),
        current_step=str(session.current_step),
        created_at=session.created_at,  # type: ignore[arg-type]
        usage={
            "sessions_used": int(usage.session_count or 0),
            "sessions_limit": sessions_limit,
            "tier": tier,
        },
    )
