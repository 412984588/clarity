"""功能开关配置 API"""
from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(prefix="/config", tags=["config"])
settings = get_settings()


@router.get("/features")
async def get_features():
    """返回前端功能开关"""
    return {
        "payments_enabled": settings.payments_enabled,
        "beta_mode": settings.beta_mode,
        "app_version": settings.app_version,
    }
