import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.schemas.fields import Field


def _validate_password_strength(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one digit")
    return value


class RegisterRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="用户邮箱，用于注册和登录",
        example="user@example.com",
    )
    password: str = Field(
        ...,
        description="登录密码（至少 8 位，包含大写字母和数字）",
        example="SecurePass1",
    )
    device_fingerprint: str = Field(
        ...,
        description="设备指纹，用于识别登录设备",
        example="ios-4f3e9b2c",
    )
    device_name: Optional[str] = Field(
        default=None,
        description="设备名称（用于展示登录设备）",
        example="iPhone 15",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="用户邮箱",
        example="user@example.com",
    )
    password: str = Field(
        ...,
        description="登录密码",
        example="SecurePass1",
    )
    device_fingerprint: str = Field(
        ...,
        description="设备指纹",
        example="web-2f1a8c7d",
    )
    device_name: Optional[str] = Field(
        default=None,
        description="设备名称",
        example="Chrome on macOS",
    )


class BetaLoginRequest(BaseModel):
    device_fingerprint: Optional[str] = Field(
        default=None,
        description="设备指纹（未提供时将自动生成）",
        example="beta-5b7c9a1d",
    )
    device_name: Optional[str] = Field(
        default=None,
        description="设备名称（未提供时使用默认值）",
        example="Beta Device",
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="短期访问令牌（JWT）",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    refresh_token: str = Field(
        ...,
        description="刷新令牌（用于续期 access token）",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    token_type: str = Field(
        default="bearer",
        description="令牌类型",
        example="bearer",
    )
    expires_in: int = Field(
        default=3600,
        description="access token 有效期（秒）",
        example=3600,
    )
    user_id: Optional[UUID] = Field(
        default=None,
        description="用户 ID（可选）",
        example="2f1c9b3e-7c2a-4d1a-9a1d-0b8f7c5f2c10",
    )


class RefreshRequest(BaseModel):
    refresh_token: str = Field(
        ...,
        description="刷新令牌",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )


class OAuthRequest(BaseModel):
    id_token: str = Field(
        ...,
        description="第三方 OAuth 提供的 ID Token",
        example="eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2...",
    )
    device_fingerprint: str = Field(
        ...,
        description="设备指纹",
        example="web-2f1a8c7d",
    )
    device_name: Optional[str] = Field(
        default=None,
        description="设备名称",
        example="Chrome on macOS",
    )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="用户邮箱",
        example="user@example.com",
    )


class ResetPasswordRequest(BaseModel):
    token: str = Field(
        ...,
        description="重置密码 token（从邮件链接获取）",
        example="r-2f1a8c7d9e5b",
    )
    new_password: str = Field(
        ...,
        description="新密码（至少 8 位，包含大写字母和数字）",
        example="NewSecure1",
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="用户 ID",
        example="2f1c9b3e-7c2a-4d1a-9a1d-0b8f7c5f2c10",
    )
    email: str = Field(
        ...,
        description="用户邮箱",
        example="user@example.com",
    )
    auth_provider: str = Field(
        ...,
        description="认证提供方（email/google/apple）",
        example="email",
    )
    locale: str = Field(
        ...,
        description="用户语言偏好",
        example="en",
    )


class AuthSuccessResponse(BaseModel):
    """认证成功响应（httpOnly cookies 模式）"""

    user: UserResponse = Field(
        ...,
        description="已认证用户信息",
        example={
            "id": "2f1c9b3e-7c2a-4d1a-9a1d-0b8f7c5f2c10",
            "email": "user@example.com",
            "auth_provider": "email",
            "locale": "en",
        },
    )
    message: str = Field(
        default="Authentication successful",
        description="认证结果提示",
        example="Authentication successful",
    )


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="设备 ID",
        example="1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e6f",
    )
    device_name: Optional[str] = Field(
        default=None,
        description="设备名称",
        example="iPhone 15",
    )
    platform: Optional[str] = Field(
        default=None,
        description="设备平台",
        example="ios",
    )
    last_active_at: Optional[datetime] = Field(
        default=None,
        description="上次活跃时间",
        example="2024-07-01T12:34:56Z",
    )
    is_active: bool = Field(
        default=True,
        description="设备是否有效",
        example=True,
    )


class ErrorResponse(BaseModel):
    error: str = Field(
        ...,
        description="错误码",
        example="INVALID_TOKEN",
    )
    detail: Optional[str] = Field(
        default=None,
        description="错误详情说明",
        example="Token is missing or invalid",
    )
    params: Optional[dict[str, object]] = Field(
        default=None,
        description="错误上下文参数",
        example={"field": "email"},
    )


class CsrfTokenResponse(BaseModel):
    csrf_token: str = Field(
        ...,
        description="CSRF Token（同时写入 cookie）",
        example="p2gq5q1oY2B2b0vZ5d9dJq8w5uQ0j3nX1y9uK1dG7a0",
    )


class StatusMessageResponse(BaseModel):
    message: str = Field(
        ...,
        description="操作结果信息",
        example="Operation completed successfully",
    )


class FeatureConfigResponse(BaseModel):
    payments_enabled: bool = Field(
        ...,
        description="支付功能是否启用",
        example=True,
    )
    beta_mode: bool = Field(
        ...,
        description="是否开启 Beta 模式",
        example=False,
    )
    app_version: str = Field(
        ...,
        description="应用版本号",
        example="0.1.0",
    )


class ActiveSessionResponse(BaseModel):
    id: UUID = Field(
        ...,
        description="会话 ID",
        example="5f1c9b3e-7c2a-4d1a-9a1d-0b8f7c5f2c10",
    )
    device_id: Optional[UUID] = Field(
        default=None,
        description="设备 ID",
        example="1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e6f",
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="会话创建时间",
        example="2024-06-01T12:00:00Z",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="会话过期时间",
        example="2024-06-02T12:00:00Z",
    )
