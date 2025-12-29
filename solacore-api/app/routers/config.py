"""功能开关配置 API"""

from app.config import get_settings
from app.middleware.rate_limit import API_RATE_LIMIT, limiter, user_rate_limit_key
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/config", tags=["config"])
settings = get_settings()


@router.get("/features")
@limiter.limit(API_RATE_LIMIT, key_func=user_rate_limit_key, override_defaults=False)
async def get_features(request: Request):
    """返回前端功能开关"""
    return JSONResponse(
        {
            "payments_enabled": settings.payments_enabled,
            "beta_mode": settings.beta_mode,
            "app_version": settings.app_version,
        }
    )
