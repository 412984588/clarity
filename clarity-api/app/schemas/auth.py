from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID
import re


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    device_fingerprint: str
    device_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_fingerprint: str
    device_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: Optional[UUID] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class OAuthRequest(BaseModel):
    id_token: str
    device_fingerprint: str
    device_name: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    auth_provider: str
    locale: str

    class Config:
        from_attributes = True


class DeviceResponse(BaseModel):
    id: UUID
    device_name: Optional[str]
    platform: Optional[str]
    last_active_at: str
    is_current: bool = False

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    params: Optional[dict] = None
