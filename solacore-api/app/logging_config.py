"""结构化日志配置"""

import logging
import re
import sys
from typing import Any

import structlog


def redact_sensitive_data(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """脱敏敏感信息（密码、token、API keys）"""
    # 定义敏感字段（不区分大小写）
    sensitive_fields = {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "authorization",
        "auth",
        "stripe_secret_key",
        "openai_api_key",
        "anthropic_api_key",
        "openrouter_api_key",
        "sentry_dsn",
    }

    # 脱敏字段值
    for key in list(event_dict.keys()):
        if key.lower() in sensitive_fields:
            event_dict[key] = "***REDACTED***"

    # 脱敏消息内容中的敏感模式
    if "event" in event_dict and isinstance(event_dict["event"], str):
        message = event_dict["event"]
        # 脱敏 JWT token (eyJ 开头的长字符串)
        message = re.sub(r"eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*", "***JWT_REDACTED***", message)
        # 脱敏看起来像 API key 的字符串 (sk_live_, pk_live_ 等)
        message = re.sub(r"(sk|pk)_(live|test)_[A-Za-z0-9]{24,}", "***API_KEY_REDACTED***", message)
        # 脱敏 Bearer token
        message = re.sub(r"Bearer\s+[A-Za-z0-9_-]+", "Bearer ***REDACTED***", message)
        event_dict["event"] = message

    return event_dict


def setup_logging(debug: bool = False) -> None:
    """配置结构化日志"""

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        redact_sensitive_data,  # 脱敏敏感信息
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if debug:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,  # type: ignore[arg-type]
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if debug else logging.INFO,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """获取 logger 实例"""
    return structlog.get_logger(name)
