"""应用配置模块 - OpenAPI 文档配置和应用元信息"""

from app.config import Settings
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

OPENAPI_TAGS = [
    {
        "name": "Auth",
        "description": "注册、登录、OAuth 与账户认证相关接口。",
    },
    {
        "name": "Sessions",
        "description": "Solve 会话管理与 SSE 流式消息接口。",
    },
    {
        "name": "Subscriptions",
        "description": "订阅状态、结账与使用量统计接口。",
    },
    {
        "name": "Account",
        "description": "账户导出与删除接口。",
    },
    {
        "name": "Health",
        "description": "健康检查与探针接口。",
    },
]


def get_api_description(settings: Settings) -> str:
    """获取 API 描述文档"""
    return f"""
Solacore API for authentication, Solve sessions, subscriptions, and account management.

## Authentication
- **Bearer Token**: `Authorization: Bearer <access_token>`
- **Cookie**: `access_token` + `refresh_token` httpOnly cookies
- **CSRF**: 使用 Cookie 进行写操作时，需要携带 `X-CSRF-Token`

## Version
当前 API 版本: {settings.app_version}
    """.strip()


def get_contact_info(settings: Settings) -> dict[str, str]:
    """获取联系信息"""
    return {
        "name": settings.smtp_from_name or "Solacore Support",
        "email": settings.smtp_from,
        "url": settings.frontend_url_prod or settings.frontend_url,
    }


def get_license_info() -> dict[str, str]:
    """获取许可证信息"""
    return {"name": "Proprietary"}


def setup_openapi(app: FastAPI, settings: Settings) -> None:
    """配置 OpenAPI 文档

    Args:
        app: FastAPI 应用实例
        settings: 应用配置
    """

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=OPENAPI_TAGS,
            contact=get_contact_info(settings),
            license_info=get_license_info(),
        )
        components = openapi_schema.setdefault("components", {})
        security_schemes = components.setdefault("securitySchemes", {})
        security_schemes.update(
            {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "使用 Authorization: Bearer <token> 进行认证",
                },
                "CookieAuth": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "access_token",
                    "description": "使用 httpOnly cookies 进行认证",
                },
            }
        )
        openapi_schema.setdefault("info", {})["x-api-version"] = settings.app_version
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
