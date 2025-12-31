"""CSRF Token 端点

提供 CSRF Token 生成和获取功能
"""

from app.middleware.csrf import generate_csrf_token, set_csrf_cookies
from app.schemas.auth import CsrfTokenResponse
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter, Response

router = APIRouter()


@router.get(
    "/csrf",
    response_model=CsrfTokenResponse,
    summary="获取 CSRF Token",
    description=(
        "生成新的 CSRF Token，并写入 `csrf_token` 与 `csrf_token_http` 两个 cookie。"
        "用于 Cookie 认证下的写操作。"
    ),
    responses=COMMON_ERROR_RESPONSES,
)
async def get_csrf_token(response: Response):
    """生成 CSRF Token 并写入双 Cookie，供后续写操作使用。"""
    token = generate_csrf_token()
    set_csrf_cookies(response, token)
    return {"csrf_token": token}
