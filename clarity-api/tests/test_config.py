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
    settings = _make_settings(debug=False, jwt_secret="secure-secret")
    validate_production_config(settings)
