"""用户信息和设备管理端点

提供用户信息查询、设备管理、会话管理功能
"""

from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from app.models.device import Device
from app.models.session import ActiveSession
from app.models.user import User
from app.schemas.auth import ActiveSessionResponse, DeviceResponse, UserResponse
from app.services.cache_service import CacheService
from app.utils.datetime_utils import utc_now
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Depends, Header, HTTPException, Path, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

cache_service = CacheService()

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="返回当前登录用户的基础信息。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def get_current_user_info(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
):
    """获取当前登录用户的基础资料。"""
    return JSONResponse(
        content={
            "id": str(current_user.id),
            "email": current_user.email,
            "auth_provider": current_user.auth_provider,
            "locale": current_user.locale,
        }
    )


@router.get(
    "/devices",
    response_model=list[DeviceResponse],
    summary="获取活跃设备列表",
    description="返回当前用户的活跃设备列表。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def list_devices(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的活跃设备列表。"""
    # 只查询需要的字段，不加载关联数据
    result = await db.execute(
        select(Device)
        .where(Device.user_id == current_user.id, Device.is_active.is_(True))
        .order_by(Device.created_at.asc())
    )
    devices = result.scalars().all()
    devices_list: list[dict[str, object]] = []
    for device in devices:
        cached_device = await cache_service.get_device(device.id)
        if isinstance(cached_device, dict):
            devices_list.append(cached_device)
            continue
        payload = {
            "id": str(device.id),
            "device_name": device.device_name,
            "platform": device.platform,
            "last_active_at": device.last_active_at.isoformat()
            if device.last_active_at
            else None,
            "is_active": device.is_active,
        }
        devices_list.append(payload)
        await cache_service.set_device(device.id, payload)
    return devices_list


@router.delete(
    "/devices/{device_id}",
    status_code=204,
    summary="解绑设备",
    description="撤销指定设备的登录授权，并终止该设备的活跃会话。",
    responses={
        **COMMON_ERROR_RESPONSES,
        204: {"description": "No Content"},
    },
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def revoke_device(
    request: Request,
    response: Response,
    device_id: UUID = Path(
        ...,
        description="设备 ID",
        example="1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e6f",
    ),
    device_fingerprint: str = Header(
        ...,
        alias="X-Device-Fingerprint",
        description="当前设备指纹，用于避免解绑自己",
        example="ios-4f3e9b2c",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """解绑设备并清理相关会话。"""
    result = await db.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail={"error": "DEVICE_NOT_FOUND"})

    if device.device_fingerprint == device_fingerprint:
        raise HTTPException(
            status_code=400, detail={"error": "CANNOT_REMOVE_CURRENT_DEVICE"}
        )

    # 使用 SQL 日期过滤，避免内存加载所有记录
    today = utc_now().date()
    removal_check = await db.execute(
        select(func.count())
        .select_from(Device)
        .where(
            Device.user_id == current_user.id,
            func.date(Device.last_removal_at) == today,
        )
    )
    if (removal_check.scalar() or 0) > 0:
        raise HTTPException(status_code=429, detail={"error": "REMOVAL_LIMIT_EXCEEDED"})

    device.is_active = False  # type: ignore[assignment]
    device.last_removal_at = utc_now()  # type: ignore[assignment]

    # 批量删除会话，避免 N+1 问题
    await db.execute(delete(ActiveSession).where(ActiveSession.device_id == device_id))

    await db.commit()
    await cache_service.invalidate_device(device_id)
    await cache_service.invalidate_sessions(current_user.id)
    return None


@router.get(
    "/sessions",
    response_model=list[ActiveSessionResponse],
    summary="获取活跃会话列表",
    description="返回当前用户的活跃登录会话。",
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def list_sessions(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的活跃会话列表。"""
    cached_sessions = await cache_service.get_sessions(current_user.id)
    if isinstance(cached_sessions, list):
        return cached_sessions
    # 只查询需要的字段，不加载 device 关联
    result = await db.execute(
        select(ActiveSession)
        .where(
            ActiveSession.user_id == current_user.id,
            ActiveSession.expires_at > utc_now(),
        )
        .order_by(ActiveSession.created_at.asc())
    )
    sessions = result.scalars().all()
    response = [
        {
            "id": str(session.id),
            "device_id": str(session.device_id) if session.device_id else None,
            "created_at": session.created_at.isoformat()
            if session.created_at
            else None,
            "expires_at": session.expires_at.isoformat()
            if session.expires_at
            else None,
        }
        for session in sessions
    ]
    await cache_service.set_sessions(current_user.id, response)
    return response


@router.delete(
    "/sessions/{session_id}",
    status_code=204,
    summary="终止单个会话",
    description="终止指定会话并使其立即失效。",
    responses={
        **COMMON_ERROR_RESPONSES,
        204: {"description": "No Content"},
    },
)
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def revoke_session(
    request: Request,
    response: Response,
    session_id: UUID = Path(
        ...,
        description="会话 ID",
        example="5f1c9b3e-7c2a-4d1a-9a1d-0b8f7c5f2c10",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """终止指定活跃会话。"""
    result = await db.execute(
        select(ActiveSession).where(
            ActiveSession.id == session_id, ActiveSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail={"error": "SESSION_NOT_FOUND"})

    await db.delete(session)
    await db.commit()
    await cache_service.invalidate_sessions(current_user.id)
    return None
