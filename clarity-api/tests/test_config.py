import pytest

from app.config import DEFAULT_JWT_SECRET, Settings, validate_production_config


def _make_settings(**overrides: object) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_validate_allows_debug_default_secret() -> None:
    settings = _make_settings(debug=True, jwt_secret=DEFAULT_JWT_SECRET)
    validate_production_config(settings)


def test_validate_blocks_default_secret_in_production() -> None:
    settings = _make_settings(debug=False, jwt_secret=DEFAULT_JWT_SECRET)
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        validate_production_config(settings)


def test_validate_allows_custom_secret_in_production() -> None:
    """生产环境配置校验 - 所有必需配置都设置时应通过"""
    settings = _make_settings(
        debug=False,
        jwt_secret="secure-secret",
        database_url="postgresql+asyncpg://user:pass@prod-db:5432/clarity",
        openai_api_key="sk-test-key",
        payments_enabled=False,  # 禁用支付则不需要 Stripe 配置
        google_client_id="test-google-client-id",
        frontend_url="https://solacore.app",  # 生产环境 URL
    )
    validate_production_config(settings)
