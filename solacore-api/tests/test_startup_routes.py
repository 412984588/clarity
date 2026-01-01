"""测试 app/startup/routes.py 中的健康检查端点和异常处理"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


# ==================== /health 端点测试 ====================


@pytest.mark.asyncio
async def test_health_check_basic(client: AsyncClient):
    """测试健康检查端点基本功能"""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # 必须包含的基础字段
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data

    # 测试环境通常是 debug 模式，应该有详细信息
    if "environment" in data and data["environment"] == "debug":
        assert "checks" in data
        checks = data["checks"]
        assert "database" in checks
        assert "llm_configured" in checks
        assert "stripe_configured" in checks
        assert "sentry_configured" in checks


@pytest.mark.asyncio
async def test_health_check_database_connected(client: AsyncClient):
    """测试数据库连接正常的健康检查"""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # 数据库应该是连接状态
    if "checks" in data:
        assert data["checks"]["database"] == "connected"


@pytest.mark.asyncio
async def test_health_check_llm_configured(client: AsyncClient):
    """测试 LLM 配置检测"""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # 如果有 checks，LLM 应该被配置了某个提供商
    if "checks" in data:
        assert data["checks"]["llm_configured"] in [
            "openai",
            "anthropic",
            "openrouter",
            "missing",
        ]


# ==================== /health/ready 端点测试 ====================


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient):
    """测试 Readiness 探针：返回系统就绪状态"""
    response = await client.get("/health/ready")

    # 应返回 200 (healthy/degraded) 或 503 (unhealthy)
    assert response.status_code in [200, 503]
    data = response.json()

    # 必须包含的字段
    assert "status" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "timestamp" in data
    assert "checks" in data


# ==================== /health/live 端点测试 ====================


@pytest.mark.asyncio
async def test_liveness_check(client: AsyncClient):
    """测试 Liveness 探针：检查进程存活"""
    response = await client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "checks" in data
    assert data["checks"]["service"]["status"] == "up"


# ==================== /health/metrics 端点测试 ====================


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    """测试 Prometheus 指标端点"""
    response = await client.get("/health/metrics")

    assert response.status_code == 200
    # Prometheus 格式是纯文本
    assert "text/plain" in response.headers["content-type"]
    # 应包含一些基本指标
    assert len(response.text) > 0


# ==================== / Root 端点测试 ====================


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """测试根端点：返回欢迎消息和文档链接"""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Solacore" in data["message"]
    assert data["docs"] == "/docs"


# ==================== 异常处理器测试 ====================


@pytest.mark.asyncio
async def test_auth_error_handler(client: AsyncClient):
    """测试 AuthError 异常处理器：未认证访问需认证的端点"""
    # 不提供 Authorization Header，触发 AuthError
    response = await client.get("/sessions")

    assert response.status_code == 401
    data = response.json()
    # 错误响应格式：{"detail": {"error": "INVALID_TOKEN"}}
    assert "detail" in data
    assert "error" in data["detail"]
    # 可能的错误码：INVALID_TOKEN 或 SESSION_NOT_FOUND 等
    assert data["detail"]["error"] in ["INVALID_TOKEN", "SESSION_NOT_FOUND", "SESSION_REVOKED"]


# ==================== OpenAPI 配置测试 ====================


@pytest.mark.asyncio
async def test_openapi_schema(client: AsyncClient):
    """测试 OpenAPI schema 配置：验证自定义安全认证配置"""
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    # 验证基本结构
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    assert "components" in data

    # 验证安全认证配置
    assert "securitySchemes" in data["components"]
    security_schemes = data["components"]["securitySchemes"]

    # 应该有 BearerAuth 和 CookieAuth
    assert "BearerAuth" in security_schemes
    assert "CookieAuth" in security_schemes

    # 验证 BearerAuth 配置
    bearer_auth = security_schemes["BearerAuth"]
    assert bearer_auth["type"] == "http"
    assert bearer_auth["scheme"] == "bearer"
    assert bearer_auth["bearerFormat"] == "JWT"

    # 验证 CookieAuth 配置
    cookie_auth = security_schemes["CookieAuth"]
    assert cookie_auth["type"] == "apiKey"
    assert cookie_auth["in"] == "cookie"
    assert cookie_auth["name"] == "access_token"

    # 验证自定义版本信息
    assert "x-api-version" in data["info"]
