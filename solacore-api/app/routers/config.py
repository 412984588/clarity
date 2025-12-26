"""功能开关配置 API"""

from fastapi import APIRouter, Request
from app.config import get_settings
from app.middleware.rate_limit import limiter, DEFAULT_RATE_LIMIT

router = APIRouter(prefix="/config", tags=["config"])
settings = get_settings()


@router.get("/features")
@limiter.limit(DEFAULT_RATE_LIMIT)
async def get_features(request: Request):
    """返回前端功能开关"""
    return {
        "payments_enabled": settings.payments_enabled,
        "beta_mode": settings.beta_mode,
        "app_version": settings.app_version,
    }
