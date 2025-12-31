"""配置端点

提供前端功能开关和版本信息
"""

from app.config import get_settings
from app.schemas.auth import FeatureConfigResponse
from app.utils.docs import COMMON_ERROR_RESPONSES
from fastapi import APIRouter

settings = get_settings()

router = APIRouter()


@router.get(
    "/config/features",
    response_model=FeatureConfigResponse,
    summary="获取前端功能开关",
    description="返回前端需要的功能开关与版本信息。",
    responses=COMMON_ERROR_RESPONSES,
)
async def get_features():
    """返回前端功能开关配置与版本信息。"""
    return {
        "payments_enabled": settings.payments_enabled,
        "beta_mode": settings.beta_mode,
        "app_version": settings.app_version,
    }
