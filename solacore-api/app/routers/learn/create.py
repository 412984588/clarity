"""学习功能路由 - 创建学习会话"""

import logging

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.device import Device
from app.models.learn_session import LearnSession, LearnStep
from app.models.user import User
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import Depends, Header, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import LearnSessionCreateResponse, router

logger = logging.getLogger(__name__)


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
    response: Response,
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
                Device.device_fingerprint == x_device_fingerprint,
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

    return LearnSessionCreateResponse(
        session_id=session.id,
        status=str(session.status),
        current_step=str(session.current_step),
        created_at=session.created_at,  # type: ignore[arg-type]
    )
