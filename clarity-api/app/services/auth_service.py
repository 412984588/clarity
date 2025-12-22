from app.utils.datetime_utils import utc_now
from datetime import timedelta
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

        # 创建设备（新用户默认 free tier）
        device = await self._get_or_create_device(user, data.device_fingerprint, data.device_name, tier="free")

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

        if not verify_password(data.password, user.password_hash):  # type: ignore[arg-type]
            raise ValueError("INVALID_CREDENTIALS")

        # 检查/创建设备（subscription 已通过 selectinload 预加载）
        tier = user.subscription.tier if user.subscription else "free"
        device = await self._get_or_create_device(user, data.device_fingerprint, data.device_name, tier=tier)

        # 创建会话
        tokens = await self._create_session(user, device)

        await self.db.commit()
        return user, tokens

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """刷新 access token"""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("INVALID_TOKEN")

        session_id = payload.get("sid") or payload.get("sub")
        try:
            session_uuid = UUID(str(session_id))
        except (TypeError, ValueError):
            raise ValueError("INVALID_TOKEN")
        token_hash = hash_token(refresh_token)

        # 查找有效会话
        result = await self.db.execute(
            select(ActiveSession)
            .options(selectinload(ActiveSession.user))
            .where(
                ActiveSession.id == session_uuid,
                ActiveSession.token_hash == token_hash,
                ActiveSession.expires_at > utc_now()
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("INVALID_TOKEN")

        user = session.user

        # Token rotation: 创建新 token，更新会话
        new_refresh = create_refresh_token(session.id)  # type: ignore[arg-type]
        session.token_hash = hash_token(new_refresh)  # type: ignore[assignment]
        session.expires_at = utc_now() + timedelta(days=30)  # type: ignore[assignment]

        access_token = create_access_token(user.id, user.email, session.id)  # type: ignore[arg-type]

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

    async def _get_or_create_device(
        self, user: User, fingerprint: str, name: Optional[str] = None, tier: str = "free"
    ) -> Device:
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
            device.last_active_at = utc_now()  # type: ignore[assignment]
            return device

        # 检查设备限制（tier 由调用方传入，避免懒加载）
        result = await self.db.execute(
            select(func.count(Device.id)).where(Device.user_id == user.id, Device.is_active.is_(True))
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
            expires_at=utc_now() + timedelta(days=30)
        )
        self.db.add(session)
        await self.db.flush()

        access_token = create_access_token(user.id, user.email, session.id)  # type: ignore[arg-type]
        refresh_token = create_refresh_token(session.id)  # type: ignore[arg-type]
        session.token_hash = hash_token(refresh_token)  # type: ignore[assignment]

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
