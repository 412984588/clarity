from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """注册新用户"""
    service = AuthService(db)
    try:
        user, tokens = await service.register(data)
        return tokens
    except ValueError as e:
        error_code = str(e)
        if error_code == "EMAIL_ALREADY_EXISTS":
            raise HTTPException(status_code=409, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """邮箱登录"""
    service = AuthService(db)
    try:
        user, tokens = await service.login(data)
        return tokens
    except ValueError as e:
        error_code = str(e)
        if error_code == "INVALID_CREDENTIALS":
            raise HTTPException(status_code=401, detail={"error": error_code})
        if error_code == "DEVICE_LIMIT_REACHED":
            raise HTTPException(status_code=403, detail={"error": error_code})
        if error_code == "DEVICE_BOUND_TO_OTHER":
            raise HTTPException(status_code=403, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """刷新 access token"""
    service = AuthService(db)
    try:
        tokens = await service.refresh_token(data.refresh_token)
        return tokens
    except ValueError as e:
        error_code = str(e)
        if error_code == "INVALID_TOKEN":
            raise HTTPException(status_code=401, detail={"error": error_code})
        if error_code == "TOKEN_EXPIRED":
            raise HTTPException(status_code=401, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})


@router.post("/logout", status_code=204)
async def logout():
    """登出 - 需要 auth middleware (M4 实现)"""
    # TODO: Implement with auth middleware in M4
    pass
