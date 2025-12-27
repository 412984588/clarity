"""
OAuth Service - Google & Apple Sign-in
验证第三方 ID token，创建/绑定用户

修复 Gemini 审查指出的问题：
1. Apple 登录支持后续登录（通过 sub 查找用户）
2. Google 验证使用 run_in_executor 避免阻塞
3. Apple 公钥缓存（TTL 24小时）
4. 提取通用登录流程减少代码重复
"""

import asyncio
from typing import Tuple, Optional
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
import httpx
from cachetools import TTLCache  # type: ignore[import-untyped]

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.auth import OAuthRequest, TokenResponse
from app.services.auth_service import AuthService
from app.config import get_settings


settings = get_settings()

# Apple 公钥缓存，TTL 24小时
_apple_key_cache: TTLCache = TTLCache(maxsize=1, ttl=86400)


class OAuthService:
    """OAuth 登录服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)

    async def google_auth_with_code(
        self, code: str, device_fingerprint: str, device_name: Optional[str]
    ) -> Tuple[User, TokenResponse]:
        """Google OAuth code 交换（标准 authorization code flow）"""
        id_token_str = await self._exchange_google_code(code)
        user_info = await self._verify_google_token(id_token_str)
        return await self._process_oauth_login(
            email=user_info["email"],
            provider="google",
            provider_id=user_info["sub"],
            device_fingerprint=device_fingerprint,
            device_name=device_name,
        )

    async def google_auth(self, data: OAuthRequest) -> Tuple[User, TokenResponse]:
        """Google OAuth 登录（兼容旧的 id_token 直接验证）"""
        user_info = await self._verify_google_token(data.id_token)
        return await self._process_oauth_login(
            email=user_info["email"],
            provider="google",
            provider_id=user_info["sub"],
            device_fingerprint=data.device_fingerprint,
            device_name=data.device_name,
        )

    async def apple_auth(self, data: OAuthRequest) -> Tuple[User, TokenResponse]:
        """Apple Sign-in 登录"""
        user_info = await self._verify_apple_token(data.id_token)
        return await self._process_oauth_login(
            email=user_info.get("email"),  # Apple 后续登录可能无 email
            provider="apple",
            provider_id=user_info["sub"],
            device_fingerprint=data.device_fingerprint,
            device_name=data.device_name,
        )

    async def _process_oauth_login(
        self,
        email: Optional[str],
        provider: str,
        provider_id: str,
        device_fingerprint: str,
        device_name: Optional[str],
    ) -> Tuple[User, TokenResponse]:
        """
        通用 OAuth 登录流程
        1. 先通过 provider_id 查找用户（支持后续登录）
        2. 再通过 email 查找/创建用户
        3. 创建设备和会话
        """
        # 优先通过 provider_id 查找现有用户（支持 Apple 后续登录无 email 场景）
        user = await self._get_user_by_provider(provider, provider_id)

        if not user:
            # 新用户或首次 OAuth 登录
            if not email:
                # Apple 后续登录但找不到用户记录（数据异常）
                raise ValueError("OAUTH_ACCOUNT_NOT_LINKED")
            user = await self._get_or_create_user(email, provider, provider_id)
        elif provider_id:
            # 已存在用户，记录 provider_id 以支持后续登录
            if not user.auth_provider_id or user.auth_provider == provider:
                user.auth_provider = provider  # type: ignore[assignment]
                user.auth_provider_id = provider_id  # type: ignore[assignment]

        # 获取 tier 用于设备限制检查
        tier = user.subscription.tier if user.subscription else "free"

        # 创建设备和会话（使用 AuthService 的公共方法）
        device = await self.auth_service._get_or_create_device(
            user, device_fingerprint, device_name, tier=tier
        )
        tokens = await self.auth_service._create_session(user, device)

        await self.db.commit()
        return user, tokens

    async def _exchange_google_code(self, code: str) -> str:
        """使用 authorization code 交换 Google tokens"""
        if not settings.google_client_secret:
            raise ValueError("GOOGLE_CLIENT_SECRET_NOT_CONFIGURED")

        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = f"{settings.frontend_url}/callback"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )

            if response.status_code != 200:
                raise ValueError(f"GOOGLE_CODE_EXCHANGE_FAILED: {response.text}")

            data = response.json()
            return data["id_token"]

    async def _verify_google_token(self, token: str) -> dict:
        """
        验证 Google ID token 并提取用户信息
        使用 run_in_executor 避免阻塞事件循环
        """
        loop = asyncio.get_running_loop()
        try:
            # 在线程池中运行阻塞代码
            idinfo = await loop.run_in_executor(
                None,
                lambda: id_token.verify_oauth2_token(
                    token, google_requests.Request(), settings.google_client_id
                ),
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
            "picture": idinfo.get("picture"),
        }

    async def _verify_apple_token(self, token: str) -> dict:
        """验证 Apple ID token 并提取用户信息"""
        try:
            # 获取 Apple 公钥（带缓存）
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
                issuer="https://appleid.apple.com",
            )

            # Apple 首次登录返回 email，后续登录只有 sub
            return {
                "sub": payload["sub"],
                "email": payload.get("email"),  # 可能为 None
                "email_verified": payload.get("email_verified", "true") == "true",
            }
        except jwt.ExpiredSignatureError:
            raise ValueError("APPLE_TOKEN_EXPIRED")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"APPLE_TOKEN_INVALID: {e}")
        except Exception as e:
            raise ValueError(f"APPLE_TOKEN_INVALID: {e}")

    async def _get_apple_public_keys(self) -> dict:
        """获取 Apple 公钥（带 24 小时缓存）"""
        if "keys" in _apple_key_cache:
            return _apple_key_cache["keys"]

        async with httpx.AsyncClient() as client:
            response = await client.get("https://appleid.apple.com/auth/keys")
            response.raise_for_status()
            keys = response.json()
            _apple_key_cache["keys"] = keys
            return keys

    async def _get_user_by_provider(
        self, provider: str, provider_id: str
    ) -> Optional[User]:
        """通过 OAuth provider_id 查找用户"""
        if not provider_id:
            return None
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.subscription))
            .where(
                User.auth_provider == provider,
                User.auth_provider_id == provider_id,
            )
        )
        return result.scalar_one_or_none()

    async def _get_or_create_user(
        self, email: str, provider: str, provider_id: Optional[str] = None
    ) -> User:
        """
        查找或创建用户
        - 如果 email 已存在，link 到现有账户
        - 如果不存在，创建新用户
        """
        # 查找现有用户（预加载 subscription）
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.subscription))
            .where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if user:
            # 已存在的用户，尝试记录 provider_id 以支持后续登录
            if provider_id and (
                not user.auth_provider_id or user.auth_provider == provider
            ):
                user.auth_provider = provider  # type: ignore[assignment]
                user.auth_provider_id = provider_id  # type: ignore[assignment]
            return user

        # 创建新用户（OAuth 用户没有密码）
        user = User(
            email=email,
            password_hash=None,
            auth_provider=provider,
            auth_provider_id=provider_id,
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
