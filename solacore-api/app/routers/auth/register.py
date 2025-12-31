"""用户注册端点

提供邮箱注册功能
"""

from app.database import get_db
from app.middleware.rate_limit import AUTH_RATE_LIMIT, ip_rate_limit_key, limiter
from app.schemas.auth import AuthSuccessResponse, RegisterRequest
from app.services.auth_service import AuthService
from app.utils.docs import COMMON_ERROR_RESPONSES
from app.utils.exceptions import raise_auth_error
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import create_auth_response

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthSuccessResponse,
    status_code=201,
    summary="注册新用户",
    description=(
        "使用邮箱与密码注册新账号，成功后写入 httpOnly 的 access/refresh cookies。"
        "注册接口免 CSRF 校验。"
    ),
    responses=COMMON_ERROR_RESPONSES,
)
@limiter.limit(AUTH_RATE_LIMIT, key_func=ip_rate_limit_key, override_defaults=False)
async def register(
    request: Request,
    response: Response,
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """注册新用户并写入认证 Cookie，返回用户基础信息。"""
    service = AuthService(db)
    try:
        user, tokens = await service.register(data)
        return await create_auth_response(response, user, tokens, db)
    except ValueError as e:
        raise_auth_error(e, context="register")
