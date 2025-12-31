from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# ⚠️ 仅用于开发环境和测试环境，生产环境必须从环境变量设置
DEFAULT_JWT_SECRET = "dev-secret-key-DO-NOT-USE-IN-PRODUCTION"


class Settings(BaseSettings):
    """应用配置，从环境变量加载"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Solacore API"
    app_version: str = "0.1.0"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/solacore"
    redis_url: str = "redis://localhost:6379/0"

    # JWT 配置 - 生产环境必须从环境变量设置
    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Rate limiting 配置
    rate_limit_global: str = "100/minute"
    rate_limit_auth: str = "5/minute"
    rate_limit_oauth: str = "10/minute"
    rate_limit_forgot_password: str = "3/hour"
    rate_limit_api: str = "60/minute"
    rate_limit_sse: str = "5/minute"
    rate_limit_ip_whitelist: str = ""  # 逗号分隔的 IP 白名单
    rate_limit_redis_url: str = ""  # 默认使用 redis_url

    # OAuth 配置
    google_client_id: str = ""
    google_client_secret: str = ""  # Code exchange flow 需要
    apple_client_id: str = ""

    # Server 配置
    host: str = "0.0.0.0"
    port: int = 8000
    frontend_url: str = "http://localhost:3000"  # 前端开发地址
    frontend_url_prod: str = "https://solacore.app"  # 生产环境域名

    # AI 功能开关
    enable_reasoning_output: bool = False  # 默认禁用思考过程输出

    # CORS 配置
    cors_allowed_origins: str = ""  # 逗号分隔的域名列表

    # Cookie 配置（跨子域名共享）
    cookie_domain: str = ""  # 生产环境设置为 ".solacore.app"

    # Sentry 配置
    sentry_dsn: str = ""  # 生产环境从环境变量读取
    sentry_environment: str = "production"
    sentry_traces_sample_rate: float = 0.1

    # Free Beta 配置
    beta_mode: bool = False
    payments_enabled: bool = True

    # LLM 配置
    llm_provider: str = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_app_name: str = ""
    openrouter_referer: str = ""
    openrouter_reasoning_fallback: bool = False
    llm_model: str = "gpt-4o-mini"
    llm_timeout: int = 30
    llm_max_tokens: int = 1024

    # Stripe 配置
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_standard: str = ""
    stripe_price_pro: str = ""
    stripe_success_url: str = ""
    stripe_cancel_url: str = ""

    # RevenueCat 配置
    revenuecat_webhook_secret: str = ""
    revenuecat_entitlement_standard: str = "standard_access"
    revenuecat_entitlement_pro: str = "pro_access"

    # 邮件服务配置
    smtp_enabled: bool = False
    smtp_host: str = "smtp.sendgrid.net"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@solacore.app"
    smtp_from_name: str = "Solacore Support"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _validate_jwt_config(settings: Settings) -> list[str]:
    """校验 JWT 配置"""
    errors = []
    if settings.jwt_secret in {
        "",
        DEFAULT_JWT_SECRET,
        "your-secret-key-change-in-production",
    }:
        errors.append(
            "🔥 CRITICAL: JWT_SECRET must be set to a secure random value in production. "
            "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )
    return errors


def _validate_database_config(settings: Settings) -> list[str]:
    """校验数据库配置"""
    errors = []
    if not settings.database_url or "localhost" in settings.database_url:
        errors.append("DATABASE_URL must be set to production database (not localhost)")
    return errors


def _validate_llm_config(settings: Settings) -> list[str]:
    """校验 LLM 配置"""
    errors = []
    if settings.llm_provider == "openai" and not settings.openai_api_key:
        errors.append("OPENAI_API_KEY is required when llm_provider=openai")
    if settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        errors.append("ANTHROPIC_API_KEY is required when llm_provider=anthropic")
    return errors


def _validate_payment_config(settings: Settings) -> list[str]:
    """校验支付配置"""
    errors: list[str] = []
    if not settings.payments_enabled:
        return errors

    if not settings.stripe_secret_key:
        errors.append("STRIPE_SECRET_KEY is required when payments_enabled=true")
    if not settings.stripe_webhook_secret:
        errors.append("STRIPE_WEBHOOK_SECRET is required when payments_enabled=true")
    if not settings.revenuecat_webhook_secret:
        errors.append(
            "REVENUECAT_WEBHOOK_SECRET is required when payments_enabled=true"
        )
    return errors


def _validate_oauth_config(settings: Settings) -> list[str]:
    """校验 OAuth 配置"""
    errors = []
    if not settings.google_client_id:
        errors.append("GOOGLE_CLIENT_ID is required for Google OAuth")
    return errors


def _validate_frontend_config(settings: Settings) -> list[str]:
    """校验前端 URL 配置"""
    errors = []
    if not settings.frontend_url or "localhost" in settings.frontend_url:
        errors.append("FRONTEND_URL must be set to production URL (not localhost)")
    return errors


def _validate_beta_mode(settings: Settings) -> list[str]:
    """校验 Beta 模式配置"""
    errors = []
    if settings.beta_mode:
        errors.append(
            "BETA_MODE must be disabled in production (security risk: shared account bypass)"
        )
    return errors


def validate_production_config(settings: Settings | None = None) -> None:
    """生产环境配置校验 - 启动时检查所有关键配置"""
    active_settings = settings or get_settings()

    if active_settings.debug:
        return  # Debug 模式跳过校验

    # 收集所有验证函数的错误
    validators = [
        _validate_jwt_config,
        _validate_database_config,
        _validate_llm_config,
        _validate_payment_config,
        _validate_oauth_config,
        _validate_frontend_config,
        _validate_beta_mode,
    ]

    errors = []
    for validator in validators:
        errors.extend(validator(active_settings))

    if errors:
        error_msg = "🚨 Production configuration errors:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        raise RuntimeError(error_msg)
