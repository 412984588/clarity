"""认证路由模块

拆分自原 app/routers/auth.py，按功能划分为多个子模块：
- utils: 辅助函数（set_auth_cookies, set_session_cookies, create_auth_response）
- csrf: CSRF 保护（GET /csrf）
- register: 用户注册（POST /register）
- login: 用户登录（POST /login, POST /beta-login）
- oauth: OAuth 认证（POST /oauth/google, POST /oauth/apple, POST /oauth/google/code）
- password_reset: 密码重置（POST /forgot-password, POST /reset-password）
- tokens: Token 管理（POST /refresh, POST /logout）
- user: 用户信息（GET /me, GET /devices, DELETE /devices/{id}, GET /sessions, DELETE /sessions/{id}）
- config: 配置信息（GET /config/features）
"""

from fastapi import APIRouter

from . import config, csrf, login, oauth, password_reset, register, tokens, user

# 创建主路由（设置统一的 prefix 和 tags）
router = APIRouter(prefix="/auth", tags=["Auth"])

# 注册所有子路由（按功能分组）
router.include_router(csrf.router)
router.include_router(register.router)
router.include_router(login.router)
router.include_router(oauth.router)
router.include_router(password_reset.router)
router.include_router(tokens.router)
router.include_router(user.router)
router.include_router(config.router)

__all__ = ["router"]
