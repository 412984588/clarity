"""
OAuth Service - Google & Apple Sign-in
验证第三方 ID token，创建/绑定用户
"""
from typing import Tuple, Optional
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.auth import OAuthRequest, TokenResponse
from app.services.auth_service import AuthService
from app.config import get_settings


settings = get_settings()


class OAuthService:
    """OAuth 登录服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)

    async def google_auth(self, data: OAuthRequest) -> Tuple[User, TokenResponse]:
        """
        Google OAuth 登录
        1. 验证 Google ID token
        2. 提取 email
        3. 查找现有用户或创建新用户
        4. 创建设备和会话
        """
        # 验证 Google ID token
        user_info = await self._verify_google_token(data.id_token)
        email = user_info["email"]

        # 查找或创建用户
        user = await self._get_or_create_user(
            email=email,
            provider="google",
            provider_id=user_info.get("sub")
        )

        # 获取 tier 用于设备限制检查
        tier = user.subscription.tier if user.subscription else "free"

        # 创建设备
        device = await self.auth_service._get_or_create_device(
            user, data.device_fingerprint, data.device_name, tier=tier
        )

        # 创建会话
        tokens = await self.auth_service._create_session(user, device)

        await self.db.commit()
        return user, tokens

    async def apple_auth(self, data: OAuthRequest) -> Tuple[User, TokenResponse]:
        """
        Apple Sign-in 登录
        1. 验证 Apple ID token
        2. 提取 email
        3. 查找现有用户或创建新用户
        4. 创建设备和会话
        """
        # 验证 Apple ID token
        user_info = await self._verify_apple_token(data.id_token)
        email = user_info["email"]

        # 查找或创建用户
        user = await self._get_or_create_user(
            email=email,
            provider="apple",
            provider_id=user_info.get("sub")
        )

        # 获取 tier 用于设备限制检查
        tier = user.subscription.tier if user.subscription else "free"

        # 创建设备
        device = await self.auth_service._get_or_create_device(
            user, data.device_fingerprint, data.device_name, tier=tier
        )

        # 创建会话
        tokens = await self.auth_service._create_session(user, device)

        await self.db.commit()
        return user, tokens

    async def _verify_google_token(self, token: str) -> dict:
        """验证 Google ID token 并提取用户信息"""
        try:
            # 使用 Google 官方库验证 token
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.google_client_id
            )
        except ValueError as e:
            raise ValueError(f"GOOGLE_TOKEN_INVALID: {e}")

        # 确保 token 是由 Google 签发的
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("INVALID_TOKEN_ISSUER")

        # 确保 email 已验证
        if not idinfo.get("email_verified", False):
            raise ValueError("EMAIL_NOT_VERIFIED")

        return {
            "sub": idinfo["sub"],
            "email": idinfo["email"],
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture")
        }

    async def _verify_apple_token(self, token: str) -> dict:
        """验证 Apple ID token 并提取用户信息"""
        try:
            # 获取 Apple 公钥
            apple_keys = await self._get_apple_public_keys()

            # 解码 token header 获取 kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            # 找到对应的公钥
            key = None
            for k in apple_keys["keys"]:
                if k["kid"] == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(k)
                    break

            if not key:
                raise ValueError("APPLE_KEY_NOT_FOUND")

            # 验证并解码 token
            payload = jwt.decode(
                token,
                key,  # type: ignore[arg-type]
                algorithms=["RS256"],
                audience=settings.apple_client_id,
                issuer="https://appleid.apple.com"
            )

            # Apple 首次登录可能没有 email（用户选择隐藏）
            # 后续登录可以通过 sub 匹配
            email = payload.get("email")
            if not email:
                raise ValueError("EMAIL_NOT_PROVIDED")

            return {
                "sub": payload["sub"],
                "email": email,
                "email_verified": payload.get("email_verified", "true") == "true"
            }
        except jwt.ExpiredSignatureError:
            raise ValueError("APPLE_TOKEN_EXPIRED")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"APPLE_TOKEN_INVALID: {e}")
        except Exception as e:
            raise ValueError(f"APPLE_TOKEN_INVALID: {e}")

    async def _get_apple_public_keys(self) -> dict:
        """获取 Apple 公钥（用于验证 ID token）"""
        async with httpx.AsyncClient() as client:
            response = await client.get("https://appleid.apple.com/auth/keys")
            response.raise_for_status()
            return response.json()

    async def _get_or_create_user(
        self,
        email: str,
        provider: str,
        provider_id: Optional[str] = None
    ) -> User:
        """
        查找或创建用户
        - 如果 email 已存在，link 到现有账户（更新 auth_provider）
        - 如果不存在，创建新用户
        """
        # 查找现有用户（预加载 subscription）
        result = await self.db.execute(
            select(User).options(selectinload(User.subscription)).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if user:
            # 已存在的用户，可以选择更新 provider 或保留原有
            # 这里保留原有 provider，不覆盖
            return user

        # 创建新用户（OAuth 用户没有密码）
        user = User(
            email=email,
            password_hash=None,  # OAuth 用户无密码
            auth_provider=provider
        )
        self.db.add(user)
        await self.db.flush()

        # 创建 Free 订阅
        subscription = Subscription(user_id=user.id, tier="free")
        self.db.add(subscription)
        await self.db.flush()

        # 重新加载用户以获取 subscription 关联
        await self.db.refresh(user, ["subscription"])

        return user
