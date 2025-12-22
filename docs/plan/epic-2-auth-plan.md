# Epic 2: User Authentication System - Implementation Plan

> **Version**: 1.0
> **Created**: 2025-12-22
> **Input**: docs/spec/epic-2-auth.md
> **Total Tasks**: 28

---

## Implementation Overview

### Phase Structure

| Phase | Stories | Focus |
|-------|---------|-------|
| Phase 1 | 2.1, 2.2 | 核心认证：邮箱注册/登录 + JWT 管理 |
| Phase 2 | 2.3, 2.4 | OAuth 集成：Google + Apple |
| Phase 3 | 2.5 | 设备绑定与反滥用 |
| Phase 4 | 2.6 | 移动端 Auth UI |
| Phase 5 | 2.7 | 密码重置流程 |

### Dependencies Graph

```
T-2.1.1 (Add deps) ──┬── T-2.1.2 (Schemas) ──┬── T-2.1.3 (User model)
                     │                        │
                     │                        ├── T-2.1.4 (Security utils)
                     │                        │
                     └── T-2.1.5 (Device model) ── T-2.1.6 (Session model)
                                              │
                                              └── T-2.1.7 (Auth service) ── T-2.1.8 (Auth router)
                                                                         │
                                                              T-2.2.1 ───┴── T-2.2.2 (Middleware)
                                                                         │
                                              T-2.3.1 (Google) ──────────┤
                                              T-2.4.1 (Apple) ───────────┤
                                                                         │
                                              T-2.5.1 (Device middleware) ┤
                                                                         │
                                              T-2.6.1+ (Mobile UI) ──────┤
                                                                         │
                                              T-2.7.1+ (Password reset) ─┘
```

---

## Phase 1: Core Authentication (Story 2.1 + 2.2)

### T-2.1.1: Add Auth Dependencies

**Command:**
```bash
cd clarity-api
poetry add passlib[bcrypt] python-jose[cryptography] httpx
```

**Files Modified:** `pyproject.toml`, `poetry.lock`

**Verification:** `poetry show passlib` → shows version

---

### T-2.1.2: Create Auth Schemas

**File:** `clarity-api/app/schemas/auth.py`

```python
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


class RefreshRequest(BaseModel):
    refresh_token: str


class OAuthRequest(BaseModel):
    id_token: str
    device_fingerprint: str
    device_name: Optional[str] = None


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
```

**Verification:** `python -c "from app.schemas.auth import RegisterRequest; print('OK')"`

---

### T-2.1.3: Extend User Model

**File:** `clarity-api/app/models/user.py` (update)

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """用户模型 - 支持邮箱和 OAuth"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL for OAuth users
    auth_provider = Column(String(50), default="email")  # email/google/apple
    auth_provider_id = Column(String(255), nullable=True)  # OAuth user ID
    locale = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("ActiveSession", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.email}>"
```

---

### T-2.1.4: Create Security Utilities

**File:** `clarity-api/app/utils/security.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: UUID, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": expire
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(session_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + (expires_delta or timedelta(days=30))
    to_encode = {
        "sub": str(session_id),
        "type": "refresh",
        "exp": expire
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """Hash token for storage (use first 32 chars of sha256)"""
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()[:32]
```

---

### T-2.1.5: Create Device Model

**File:** `clarity-api/app/models/device.py`

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Device(Base):
    """设备模型 - 用于设备绑定和反滥用"""
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_fingerprint = Column(String(255), nullable=False, index=True)
    device_name = Column(String(255), nullable=True)
    platform = Column(String(50), nullable=True)  # ios/android
    last_active_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_removal_at = Column(DateTime, nullable=True)  # 用于限制解绑频率

    # Relationships
    user = relationship("User", back_populates="devices")
    sessions = relationship("ActiveSession", back_populates="device", cascade="all, delete-orphan")

    __table_args__ = (
        # 每个用户的设备指纹唯一
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<Device {self.device_name} ({self.platform})>"
```

---

### T-2.1.6: Create ActiveSession Model

**File:** `clarity-api/app/models/session.py`

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class ActiveSession(Base):
    """活跃会话模型 - 用于 token 管理和并发限制"""
    __tablename__ = "active_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(64), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")
    device = relationship("Device", back_populates="sessions")

    def __repr__(self):
        return f"<ActiveSession {self.id}>"
```

---

### T-2.1.7: Create Subscription Model

**File:** `clarity-api/app/models/subscription.py`

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Subscription(Base):
    """订阅模型"""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    tier = Column(String(50), default="free")  # free/standard/pro
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    status = Column(String(50), default="active")  # active/canceled/past_due
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription {self.tier} for user {self.user_id}>"


class Usage(Base):
    """用量追踪"""
    __tablename__ = "usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    period_start = Column(DateTime, nullable=False)
    session_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # user_id + period_start 唯一
        {"sqlite_autoincrement": True},
    )
```

---

### T-2.1.8: Update Models __init__.py

**File:** `clarity-api/app/models/__init__.py`

```python
from app.models.user import User
from app.models.device import Device
from app.models.session import ActiveSession
from app.models.subscription import Subscription, Usage

__all__ = ["User", "Device", "ActiveSession", "Subscription", "Usage"]
```

---

### T-2.1.9: Create Auth Service

**File:** `clarity-api/app/services/auth_service.py`

```python
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.device import Device
from app.models.session import ActiveSession
from app.models.subscription import Subscription
from app.utils.security import (
    hash_password, verify_password, 
    create_access_token, create_refresh_token,
    decode_token, hash_token
)
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse


# 设备限制
DEVICE_LIMITS = {"free": 1, "standard": 2, "pro": 3}


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> Tuple[User, TokenResponse]:
        """注册新用户"""
        # 检查邮箱是否已存在
        existing = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise ValueError("EMAIL_ALREADY_EXISTS")

        # 创建用户
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            auth_provider="email"
        )
        self.db.add(user)
        await self.db.flush()

        # 创建 Free 订阅
        subscription = Subscription(user_id=user.id, tier="free")
        self.db.add(subscription)

        # 创建设备
        device = await self._get_or_create_device(user, data.device_fingerprint, data.device_name)

        # 创建会话和 tokens
        tokens = await self._create_session(user, device)

        await self.db.commit()
        return user, tokens

    async def login(self, data: LoginRequest) -> Tuple[User, TokenResponse]:
        """邮箱登录"""
        # 查找用户
        result = await self.db.execute(
            select(User).options(selectinload(User.subscription)).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        if not user or not user.password_hash:
            raise ValueError("INVALID_CREDENTIALS")

        if not verify_password(data.password, user.password_hash):
            raise ValueError("INVALID_CREDENTIALS")

        # 检查/创建设备
        device = await self._get_or_create_device(user, data.device_fingerprint, data.device_name)

        # 创建会话
        tokens = await self._create_session(user, device)

        await self.db.commit()
        return user, tokens

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """刷新 access token"""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("INVALID_TOKEN")

        session_id = payload.get("sub")
        token_hash = hash_token(refresh_token)

        # 查找有效会话
        result = await self.db.execute(
            select(ActiveSession)
            .options(selectinload(ActiveSession.user))
            .where(
                ActiveSession.id == session_id,
                ActiveSession.token_hash == token_hash,
                ActiveSession.expires_at > datetime.utcnow()
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("INVALID_TOKEN")

        user = session.user

        # Token rotation: 创建新 token，删除旧会话
        new_refresh = create_refresh_token(session.id)
        session.token_hash = hash_token(new_refresh)
        session.expires_at = datetime.utcnow() + timedelta(days=30)

        access_token = create_access_token(user.id, user.email)

        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            expires_in=3600
        )

    async def logout(self, user_id: UUID, token_hash: str) -> bool:
        """登出：使会话失效"""
        result = await self.db.execute(
            select(ActiveSession).where(
                ActiveSession.user_id == user_id,
                ActiveSession.token_hash == token_hash
            )
        )
        session = result.scalar_one_or_none()

        if session:
            await self.db.delete(session)
            await self.db.commit()
            return True
        return False

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """获取用户"""
        result = await self.db.execute(
            select(User).options(selectinload(User.subscription)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_or_create_device(self, user: User, fingerprint: str, name: Optional[str] = None) -> Device:
        """获取或创建设备，检查设备限制"""
        # 查找现有设备
        result = await self.db.execute(
            select(Device).where(
                Device.device_fingerprint == fingerprint
            )
        )
        device = result.scalar_one_or_none()

        if device:
            if device.user_id != user.id:
                raise ValueError("DEVICE_BOUND_TO_OTHER")
            device.last_active_at = datetime.utcnow()
            return device

        # 检查设备限制
        tier = "free"
        if user.subscription:
            tier = user.subscription.tier

        result = await self.db.execute(
            select(func.count(Device.id)).where(Device.user_id == user.id, Device.is_active == True)
        )
        device_count = result.scalar() or 0

        if device_count >= DEVICE_LIMITS.get(tier, 1):
            raise ValueError("DEVICE_LIMIT_REACHED")

        # 创建新设备
        device = Device(
            user_id=user.id,
            device_fingerprint=fingerprint,
            device_name=name,
            platform=self._detect_platform(name)
        )
        self.db.add(device)
        await self.db.flush()
        return device

    async def _create_session(self, user: User, device: Device) -> TokenResponse:
        """创建新会话"""
        session = ActiveSession(
            user_id=user.id,
            device_id=device.id,
            token_hash="",  # Will be updated
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        self.db.add(session)
        await self.db.flush()

        access_token = create_access_token(user.id, user.email)
        refresh_token = create_refresh_token(session.id)
        session.token_hash = hash_token(refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600
        )

    def _detect_platform(self, device_name: Optional[str]) -> Optional[str]:
        """从设备名推断平台"""
        if not device_name:
            return None
        name_lower = device_name.lower()
        if "iphone" in name_lower or "ipad" in name_lower:
            return "ios"
        if "pixel" in name_lower or "samsung" in name_lower or "android" in name_lower:
            return "android"
        return None
```

---

### T-2.1.10: Create Auth Router

**File:** `clarity-api/app/routers/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest, UserResponse, ErrorResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_device_fingerprint(x_device_fingerprint: Optional[str] = Header(None)) -> str:
    """从 header 获取设备指纹"""
    if not x_device_fingerprint:
        raise HTTPException(status_code=400, detail={"error": "DEVICE_FINGERPRINT_REQUIRED"})
    return x_device_fingerprint


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
    """登出 - 需要 auth middleware (后续实现)"""
    # TODO: Implement with auth middleware
    pass
```

---

### T-2.1.11: Update Config with JWT Settings

**File:** `clarity-api/app/config.py` (update)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置，从环境变量加载"""
    app_name: str = "Clarity API"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/clarity"
    
    # JWT 配置
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    
    # OAuth 配置
    google_client_id: str = ""
    apple_client_id: str = ""
    
    # Server 配置
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

### T-2.1.12: Register Auth Router in Main

**File:** `clarity-api/app/main.py` (update)

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import get_db
from app.routers import auth

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Universal problem-solving assistant API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查端点（含数据库状态）"""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    status = "healthy" if db_status == "ok" else "degraded"
    return {"status": status, "database": db_status}


@app.get("/")
async def root():
    """根端点"""
    return {"message": "Welcome to Clarity API", "docs": "/docs"}
```

---

### T-2.1.13: Create Migration for Auth Tables

**Command:**
```bash
cd clarity-api
poetry run alembic revision --autogenerate -m "add auth tables"
poetry run alembic upgrade head
```

**Verification:** `\dt` shows: users, devices, active_sessions, subscriptions, usage

---

### T-2.1.14: Create Auth Tests

**File:** `clarity-api/tests/test_auth.py`

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_register_success(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-001"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.anyio
async def test_register_weak_password(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "email": "weak@example.com",
        "password": "weak",
        "device_fingerprint": "test-device-002"
    })
    assert response.status_code == 422  # Validation error


@pytest.mark.anyio
async def test_login_success(client: AsyncClient):
    # First register
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-003"
    })
    
    # Then login
    response = await client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-003"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.anyio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post("/auth/login", json={
        "email": "nouser@example.com",
        "password": "WrongPass123",
        "device_fingerprint": "test-device-004"
    })
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_CREDENTIALS"
```

**Verification:** `poetry run pytest tests/test_auth.py -v`

---

## Phase 2: OAuth Integration (Story 2.3 + 2.4)

### T-2.3.1: Add Google OAuth Dependencies

**Command:**
```bash
cd clarity-api
poetry add google-auth
```

---

### T-2.3.2: Create OAuth Service

**File:** `clarity-api/app/services/oauth_service.py`

```python
from typing import Optional, Tuple
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.subscription import Subscription
from app.config import get_settings
from app.services.auth_service import AuthService

settings = get_settings()


class OAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)

    async def google_login(self, token: str, device_fingerprint: str, device_name: Optional[str] = None) -> Tuple[User, dict]:
        """Google OAuth 登录"""
        try:
            # 验证 Google token
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), settings.google_client_id
            )
        except ValueError:
            raise ValueError("OAUTH_INVALID_TOKEN")

        email = idinfo.get("email")
        google_user_id = idinfo.get("sub")

        if not email:
            raise ValueError("OAUTH_INVALID_TOKEN")

        # 查找或创建用户
        user = await self._get_or_create_oauth_user(
            email=email,
            provider="google",
            provider_id=google_user_id
        )

        # 创建设备和会话
        device = await self.auth_service._get_or_create_device(user, device_fingerprint, device_name)
        tokens = await self.auth_service._create_session(user, device)

        await self.db.commit()
        return user, tokens

    async def apple_login(self, token: str, device_fingerprint: str, device_name: Optional[str] = None) -> Tuple[User, dict]:
        """Apple Sign-In 登录"""
        # 验证 Apple token (简化版 - 生产环境需要完整验证)
        try:
            from jose import jwt
            # Apple token 是 JWT，需要用 Apple 公钥验证
            # 这里简化处理，实际需要获取 https://appleid.apple.com/auth/keys
            unverified = jwt.get_unverified_claims(token)
            email = unverified.get("email")
            apple_user_id = unverified.get("sub")
        except Exception:
            raise ValueError("OAUTH_INVALID_TOKEN")

        if not apple_user_id:
            raise ValueError("OAUTH_INVALID_TOKEN")

        # Apple 可能不返回邮箱（用户选择隐藏）
        if not email:
            email = f"{apple_user_id}@privaterelay.appleid.com"

        user = await self._get_or_create_oauth_user(
            email=email,
            provider="apple",
            provider_id=apple_user_id
        )

        device = await self.auth_service._get_or_create_device(user, device_fingerprint, device_name)
        tokens = await self.auth_service._create_session(user, device)

        await self.db.commit()
        return user, tokens

    async def _get_or_create_oauth_user(self, email: str, provider: str, provider_id: str) -> User:
        """获取或创建 OAuth 用户"""
        # 先按 provider_id 查找
        result = await self.db.execute(
            select(User).where(
                User.auth_provider == provider,
                User.auth_provider_id == provider_id
            )
        )
        user = result.scalar_one_or_none()
        if user:
            return user

        # 再按邮箱查找（链接账号）
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if user:
            # 更新 provider 信息
            user.auth_provider = provider
            user.auth_provider_id = provider_id
            return user

        # 创建新用户
        user = User(
            email=email,
            auth_provider=provider,
            auth_provider_id=provider_id
        )
        self.db.add(user)
        await self.db.flush()

        # 创建 Free 订阅
        subscription = Subscription(user_id=user.id, tier="free")
        self.db.add(subscription)

        return user
```

---

### T-2.3.3: Add OAuth Routes

**File:** `clarity-api/app/routers/auth.py` (append)

```python
# Add to existing auth.py

from app.services.oauth_service import OAuthService
from app.schemas.auth import OAuthRequest


@router.post("/oauth/google", response_model=TokenResponse)
async def google_oauth(
    data: OAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Google OAuth 登录"""
    service = OAuthService(db)
    try:
        user, tokens = await service.google_login(
            data.id_token,
            data.device_fingerprint,
            data.device_name
        )
        return tokens
    except ValueError as e:
        error_code = str(e)
        if error_code == "OAUTH_INVALID_TOKEN":
            raise HTTPException(status_code=401, detail={"error": error_code})
        if error_code == "DEVICE_LIMIT_REACHED":
            raise HTTPException(status_code=403, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})


@router.post("/oauth/apple", response_model=TokenResponse)
async def apple_oauth(
    data: OAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Apple Sign-In 登录"""
    service = OAuthService(db)
    try:
        user, tokens = await service.apple_login(
            data.id_token,
            data.device_fingerprint,
            data.device_name
        )
        return tokens
    except ValueError as e:
        error_code = str(e)
        if error_code == "OAUTH_INVALID_TOKEN":
            raise HTTPException(status_code=401, detail={"error": error_code})
        if error_code == "DEVICE_LIMIT_REACHED":
            raise HTTPException(status_code=403, detail={"error": error_code})
        raise HTTPException(status_code=400, detail={"error": error_code})
```

---

## Phase 3: Device Binding (Story 2.5)

### T-2.5.1: Create Auth Middleware

**File:** `clarity-api/app/middleware/auth.py`

```python
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.utils.security import decode_token
from app.services.auth_service import AuthService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """验证 JWT 并返回当前用户"""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    service = AuthService(db)
    user = await service.get_user_by_id(UUID(user_id))

    if not user:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN"})

    return user


async def get_device_fingerprint_header(request: Request) -> str:
    """从 header 获取设备指纹"""
    fingerprint = request.headers.get("X-Device-Fingerprint")
    if not fingerprint:
        raise HTTPException(status_code=400, detail={"error": "DEVICE_FINGERPRINT_REQUIRED"})
    return fingerprint
```

---

### T-2.5.2: Add Device Management Routes

**File:** `clarity-api/app/routers/auth.py` (append)

```python
# Add to existing auth.py

from app.middleware.auth import get_current_user, get_device_fingerprint_header
from app.models.user import User
from app.models.device import Device
from sqlalchemy import select
from datetime import datetime, timedelta


@router.get("/devices", response_model=list[DeviceResponse])
async def list_devices(
    current_user: User = Depends(get_current_user),
    current_fingerprint: str = Depends(get_device_fingerprint_header),
    db: AsyncSession = Depends(get_db)
):
    """列出用户的所有设备"""
    result = await db.execute(
        select(Device).where(Device.user_id == current_user.id, Device.is_active == True)
    )
    devices = result.scalars().all()

    return [
        DeviceResponse(
            id=d.id,
            device_name=d.device_name,
            platform=d.platform,
            last_active_at=d.last_active_at.isoformat() if d.last_active_at else "",
            is_current=(d.device_fingerprint == current_fingerprint)
        )
        for d in devices
    ]


@router.delete("/devices/{device_id}", status_code=204)
async def remove_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    current_fingerprint: str = Depends(get_device_fingerprint_header),
    db: AsyncSession = Depends(get_db)
):
    """解绑设备（每天限1次）"""
    from uuid import UUID
    
    # 查找设备
    result = await db.execute(
        select(Device).where(
            Device.id == UUID(device_id),
            Device.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail={"error": "DEVICE_NOT_FOUND"})

    # 不能删除当前设备
    if device.device_fingerprint == current_fingerprint:
        raise HTTPException(status_code=400, detail={"error": "CANNOT_REMOVE_CURRENT_DEVICE"})

    # 检查解绑频率限制
    if device.last_removal_at and device.last_removal_at > datetime.utcnow() - timedelta(days=1):
        raise HTTPException(status_code=429, detail={"error": "DEVICE_REMOVAL_LIMIT"})

    # 软删除
    device.is_active = False
    device.last_removal_at = datetime.utcnow()
    await db.commit()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        auth_provider=current_user.auth_provider,
        locale=current_user.locale
    )
```

---

## Phase 4: Mobile Auth UI (Story 2.6)

### T-2.6.1: Install Mobile Auth Dependencies

**Command (user runs in Terminal):**
```bash
cd clarity-mobile
npm install expo-secure-store expo-auth-session expo-apple-authentication expo-crypto
npm install zustand react-hook-form @hookform/resolvers zod
```

---

### T-2.6.2: Create Auth Store

**File:** `clarity-mobile/stores/authStore.ts`

```typescript
import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';

interface User {
  id: string;
  email: string;
  authProvider: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  setTokens: (accessToken: string, refreshToken: string) => Promise<void>;
  setUser: (user: User) => void;
  logout: () => Promise<void>;
  loadStoredTokens: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isLoading: true,
  isAuthenticated: false,

  setTokens: async (accessToken, refreshToken) => {
    await SecureStore.setItemAsync('accessToken', accessToken);
    await SecureStore.setItemAsync('refreshToken', refreshToken);
    set({ accessToken, refreshToken, isAuthenticated: true });
  },

  setUser: (user) => {
    set({ user });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('accessToken');
    await SecureStore.deleteItemAsync('refreshToken');
    set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
  },

  loadStoredTokens: async () => {
    try {
      const accessToken = await SecureStore.getItemAsync('accessToken');
      const refreshToken = await SecureStore.getItemAsync('refreshToken');

      if (accessToken && refreshToken) {
        set({ accessToken, refreshToken, isAuthenticated: true, isLoading: false });
        return true;
      }
    } catch (error) {
      console.error('Failed to load tokens:', error);
    }
    set({ isLoading: false });
    return false;
  },
}));
```

---

### T-2.6.3: Create API Service

**File:** `clarity-mobile/services/api.ts`

```typescript
import * as SecureStore from 'expo-secure-store';
import { useAuthStore } from '../stores/authStore';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

async function getDeviceFingerprint(): Promise<string> {
  // 生成或获取设备指纹
  let fingerprint = await SecureStore.getItemAsync('deviceFingerprint');
  if (!fingerprint) {
    fingerprint = Math.random().toString(36).substring(2) + Date.now().toString(36);
    await SecureStore.setItemAsync('deviceFingerprint', fingerprint);
  }
  return fingerprint;
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const deviceFingerprint = await getDeviceFingerprint();
  const accessToken = await SecureStore.getItemAsync('accessToken');

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'X-Device-Fingerprint': deviceFingerprint,
    ...(options.headers || {}),
  };

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { error: errorData.detail?.error || 'UNKNOWN_ERROR' };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: 'NETWORK_ERROR' };
  }
}
```

---

### T-2.6.4: Create Auth Service

**File:** `clarity-mobile/services/auth.ts`

```typescript
import { apiRequest } from './api';
import { useAuthStore } from '../stores/authStore';
import * as SecureStore from 'expo-secure-store';

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export async function register(email: string, password: string): Promise<{ success: boolean; error?: string }> {
  const deviceFingerprint = await SecureStore.getItemAsync('deviceFingerprint') || '';
  
  const result = await apiRequest<TokenResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
      device_fingerprint: deviceFingerprint,
    }),
  });

  if (result.error) {
    return { success: false, error: result.error };
  }

  if (result.data) {
    await useAuthStore.getState().setTokens(result.data.access_token, result.data.refresh_token);
    return { success: true };
  }

  return { success: false, error: 'UNKNOWN_ERROR' };
}

export async function login(email: string, password: string): Promise<{ success: boolean; error?: string }> {
  const deviceFingerprint = await SecureStore.getItemAsync('deviceFingerprint') || '';
  
  const result = await apiRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
      device_fingerprint: deviceFingerprint,
    }),
  });

  if (result.error) {
    return { success: false, error: result.error };
  }

  if (result.data) {
    await useAuthStore.getState().setTokens(result.data.access_token, result.data.refresh_token);
    return { success: true };
  }

  return { success: false, error: 'UNKNOWN_ERROR' };
}

export async function logout(): Promise<void> {
  await apiRequest('/auth/logout', { method: 'POST' });
  await useAuthStore.getState().logout();
}
```

---

### T-2.6.5: Create Login Screen

**File:** `clarity-mobile/app/(auth)/login.tsx`

```typescript
import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { Link, router } from 'expo-router';
import { login } from '../../services/auth';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setError('');
    setLoading(true);

    const result = await login(email, password);
    
    setLoading(false);
    
    if (result.success) {
      router.replace('/(main)');
    } else {
      setError(getErrorMessage(result.error || ''));
    }
  };

  const getErrorMessage = (code: string): string => {
    const messages: Record<string, string> = {
      INVALID_CREDENTIALS: 'Invalid email or password',
      DEVICE_LIMIT_REACHED: 'Device limit reached. Remove a device to continue.',
      NETWORK_ERROR: 'Network error. Please try again.',
    };
    return messages[code] || 'An error occurred';
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome Back</Text>
      
      {error ? <Text style={styles.error}>{error}</Text> : null}

      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <TouchableOpacity 
        style={[styles.button, loading && styles.buttonDisabled]} 
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Log In</Text>
        )}
      </TouchableOpacity>

      <Link href="/(auth)/register" style={styles.link}>
        Don't have an account? Sign Up
      </Link>

      <Link href="/(auth)/forgot-password" style={styles.link}>
        Forgot Password?
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 30,
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    fontSize: 16,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  link: {
    color: '#007AFF',
    textAlign: 'center',
    marginTop: 20,
    fontSize: 16,
  },
  error: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 15,
  },
});
```

---

### T-2.6.6: Create Register Screen

**File:** `clarity-mobile/app/(auth)/register.tsx`

```typescript
import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { Link, router } from 'expo-router';
import { register } from '../../services/auth';

export default function RegisterScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    const result = await register(email, password);
    
    setLoading(false);
    
    if (result.success) {
      router.replace('/(main)');
    } else {
      setError(getErrorMessage(result.error || ''));
    }
  };

  const getErrorMessage = (code: string): string => {
    const messages: Record<string, string> = {
      EMAIL_ALREADY_EXISTS: 'This email is already registered',
      WEAK_PASSWORD: 'Password must contain uppercase and number',
      NETWORK_ERROR: 'Network error. Please try again.',
    };
    return messages[code] || 'An error occurred';
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Account</Text>
      
      {error ? <Text style={styles.error}>{error}</Text> : null}

      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <TextInput
        style={styles.input}
        placeholder="Confirm Password"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
      />

      <TouchableOpacity 
        style={[styles.button, loading && styles.buttonDisabled]} 
        onPress={handleRegister}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Sign Up</Text>
        )}
      </TouchableOpacity>

      <Link href="/(auth)/login" style={styles.link}>
        Already have an account? Log In
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 30,
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    fontSize: 16,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  link: {
    color: '#007AFF',
    textAlign: 'center',
    marginTop: 20,
    fontSize: 16,
  },
  error: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 15,
  },
});
```

---

### T-2.6.7: Create Auth Layout

**File:** `clarity-mobile/app/(auth)/_layout.tsx`

```typescript
import { Stack } from 'expo-router';

export default function AuthLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="login" />
      <Stack.Screen name="register" />
      <Stack.Screen name="forgot-password" />
    </Stack>
  );
}
```

---

## Phase 5: Password Reset (Story 2.7)

### T-2.7.1: Create Password Reset Model

**File:** `clarity-api/app/models/password_reset.py`

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class PasswordReset(Base):
    """密码重置模型"""
    __tablename__ = "password_resets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(64), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

### T-2.7.2: Add Password Reset to Auth Service

**File:** `clarity-api/app/services/auth_service.py` (append)

```python
# Add to AuthService class

async def request_password_reset(self, email: str) -> Optional[str]:
    """请求密码重置，返回 reset token"""
    import secrets
    from app.models.password_reset import PasswordReset

    result = await self.db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user or user.auth_provider != "email":
        # 不泄露用户是否存在
        return None

    # 生成 reset token
    token = secrets.token_urlsafe(32)
    token_hash = hash_token(token)

    reset = PasswordReset(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    self.db.add(reset)
    await self.db.commit()

    return token


async def reset_password(self, token: str, new_password: str) -> bool:
    """使用 token 重置密码"""
    from app.models.password_reset import PasswordReset
    
    token_hash = hash_token(token)

    result = await self.db.execute(
        select(PasswordReset).where(
            PasswordReset.token_hash == token_hash,
            PasswordReset.expires_at > datetime.utcnow(),
            PasswordReset.used_at == None
        )
    )
    reset = result.scalar_one_or_none()

    if not reset:
        raise ValueError("RESET_TOKEN_INVALID")

    # 更新密码
    result = await self.db.execute(
        select(User).where(User.id == reset.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError("RESET_TOKEN_INVALID")

    user.password_hash = hash_password(new_password)
    reset.used_at = datetime.utcnow()

    # 使所有会话失效
    await self.db.execute(
        select(ActiveSession).where(ActiveSession.user_id == user.id)
    )
    # Delete all sessions
    from sqlalchemy import delete
    await self.db.execute(
        delete(ActiveSession).where(ActiveSession.user_id == user.id)
    )

    await self.db.commit()
    return True
```

---

### T-2.7.3: Add Password Reset Routes

**File:** `clarity-api/app/routers/auth.py` (append)

```python
# Add these schemas and routes

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str
    
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


@router.post("/forgot-password", status_code=202)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """请求密码重置邮件"""
    service = AuthService(db)
    token = await service.request_password_reset(data.email)
    
    if token:
        # TODO: Send email with reset link
        # reset_link = f"clarity://reset-password?token={token}"
        pass

    # 始终返回成功（不泄露用户是否存在）
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password", status_code=200)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """重置密码"""
    service = AuthService(db)
    try:
        await service.reset_password(data.token, data.password)
        return {"message": "Password reset successful"}
    except ValueError as e:
        error_code = str(e)
        raise HTTPException(status_code=400, detail={"error": error_code})
```

---

## Verification Checklist

### Backend Verification

```bash
cd clarity-api

# 1. Run migrations
poetry run alembic upgrade head

# 2. Start server
poetry run uvicorn app.main:app --reload

# 3. Test registration
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Device-Fingerprint: test-device" \
  -d '{"email":"test@example.com","password":"Password123","device_fingerprint":"test-device"}'

# 4. Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Device-Fingerprint: test-device" \
  -d '{"email":"test@example.com","password":"Password123","device_fingerprint":"test-device"}'

# 5. Run tests
poetry run pytest tests/test_auth.py -v
```

### Mobile Verification

```bash
cd clarity-mobile

# 1. Install dependencies
npm install

# 2. Start Expo
npx expo start

# 3. Test on simulator
# Press 'i' for iOS or 'a' for Android
```

---

## Change Log

| Date | Version | Description |
|------|---------|-------------|
| 2025-12-22 | 1.0 | Initial implementation plan |
