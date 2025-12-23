from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，从环境变量加载"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Clarity API"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/clarity"
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # OAuth 配置
    google_client_id: str = ""
    apple_client_id: str = ""

    # Server 配置
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM 配置
    llm_provider: str = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_app_name: str = ""
    openrouter_referer: str = ""
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
