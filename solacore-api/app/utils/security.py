from datetime import timedelta
from typing import Optional
from uuid import UUID

import anyio
from app.config import get_settings
from app.utils.datetime_utils import utc_now
from jose import JWTError, jwt
from passlib.context import CryptContext

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt (同步版本，用于测试)"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash (同步版本，用于测试)"""
    return pwd_context.verify(plain_password, hashed_password)


async def hash_password_async(password: str) -> str:
    """Hash password using bcrypt (异步版本，避免阻塞事件循环)"""
    return await anyio.to_thread.run_sync(pwd_context.hash, password)


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash (异步版本，避免阻塞事件循环)"""
    return await anyio.to_thread.run_sync(
        pwd_context.verify, plain_password, hashed_password
    )


def create_access_token(
    user_id: UUID,
    email: str,
    session_id: UUID,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token"""
    expire = utc_now() + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "sid": str(session_id),
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    session_id: UUID, expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token"""
    expire = utc_now() + (expires_delta or timedelta(days=30))
    to_encode = {
        "sub": str(session_id),
        "sid": str(session_id),
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """Hash token for storage (use first 32 chars of sha256)"""
    import hashlib

    return hashlib.sha256(token.encode()).hexdigest()[:32]
