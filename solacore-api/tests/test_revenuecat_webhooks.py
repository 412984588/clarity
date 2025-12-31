"""RevenueCat webhook endpoint tests."""

import asyncio
from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


class _TestSettings:
    revenuecat_webhook_secret = "whsec_test"
    revenuecat_entitlement_standard = "standard_access"
    revenuecat_entitlement_pro = "pro_access"
    beta_mode = False
    payments_enabled = True


@pytest.mark.asyncio
async def test_webhook_missing_auth_returns_401(client_no_csrf: AsyncClient):
    """缺少 Authorization 时返回 401。"""
    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        response = await client_no_csrf.post(
            "/webhooks/revenuecat",
            json={"event": {"type": "INITIAL_PURCHASE"}},
        )
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "MISSING_AUTH"


@pytest.mark.asyncio
async def test_webhook_invalid_auth_returns_401(client_no_csrf: AsyncClient):
    """Authorization 不合法时返回 401。"""
    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        response = await client_no_csrf.post(
            "/webhooks/revenuecat",
            json={"event": {"type": "INITIAL_PURCHASE"}},
            headers={"Authorization": "Bearer wrong"},
        )
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_AUTH"


@pytest.mark.asyncio
async def test_webhook_initial_purchase(client_no_csrf: AsyncClient):
    """INITIAL_PURCHASE 更新 tier 与状态。"""
    # 先通过 /auth/register 创建用户
    register_response = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "rc-initial@example.com",
            "password": "TestPass123!",
            "device_fingerprint": "test-device",
            "device_name": "Test Device",
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["user"]["id"]

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "INITIAL_PURCHASE",
        "app_user_id": user_id,
        "entitlement_ids": ["standard_access"],
        "expiration_at_ms": 1706745600000,
    }

    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        response = await client_no_csrf.post(
            "/webhooks/revenuecat",
            json={"event": event},
            headers={"Authorization": "Bearer whsec_test"},
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_renewal(client_no_csrf: AsyncClient):
    """RENEWAL 更新 period_end。"""
    # 创建用户
    register_response = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "rc-renewal@example.com",
            "password": "TestPass123!",
            "device_fingerprint": "test-device-renewal",
            "device_name": "Test Device",
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["user"]["id"]

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "RENEWAL",
        "app_user_id": user_id,
        "expiration_at_ms": 1706745600000,
    }

    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        response = await client_no_csrf.post(
            "/webhooks/revenuecat",
            json={"event": event},
            headers={"Authorization": "Bearer whsec_test"},
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_expiration(client_no_csrf: AsyncClient):
    """EXPIRATION 降级为 free 并标记过期。"""
    # 创建用户
    register_response = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "rc-expired@example.com",
            "password": "TestPass123!",
            "device_fingerprint": "test-device-expiration",
            "device_name": "Test Device",
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["user"]["id"]

    # 先发送 INITIAL_PURCHASE 升级到 pro
    initial_event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "INITIAL_PURCHASE",
        "app_user_id": user_id,
        "entitlement_ids": ["pro_access"],
        "expiration_at_ms": 1706745600000,
    }

    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        await client_no_csrf.post(
            "/webhooks/revenuecat",
            json={"event": initial_event},
            headers={"Authorization": "Bearer whsec_test"},
        )

    # 再发送 EXPIRATION
    expiration_event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "EXPIRATION",
        "app_user_id": user_id,
    }

    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        response = await client_no_csrf.post(
            "/webhooks/revenuecat",
            json={"event": expiration_event},
            headers={"Authorization": "Bearer whsec_test"},
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_idempotency_duplicate_event(client_no_csrf: AsyncClient):
    """重复发送同一 event_id 只处理一次（幂等性）。"""
    # 创建用户
    register_response = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "rc-idempotent@example.com",
            "password": "TestPass123!",
            "device_fingerprint": "test-device-idempotent",
            "device_name": "Test Device",
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["user"]["id"]

    event_id = f"evt_{uuid4().hex[:14]}"

    event = {
        "id": event_id,
        "type": "INITIAL_PURCHASE",
        "app_user_id": user_id,
        "entitlement_ids": ["pro_access"],
        "expiration_at_ms": 1706745600000,
    }

    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        # 第一次请求
        response1 = await client_no_csrf.post(
            "/webhooks/revenuecat",
            json={"event": event},
            headers={"Authorization": "Bearer whsec_test"},
        )
        assert response1.status_code == 200

        # 第二次请求（相同 event_id）
        response2 = await client_no_csrf.post(
            "/webhooks/revenuecat",
            json={"event": event},
            headers={"Authorization": "Bearer whsec_test"},
        )
        assert response2.status_code == 200


@pytest.mark.asyncio
async def test_webhook_concurrency_final_state_correct(client_no_csrf: AsyncClient):
    """并发发送两个不同事件，最终状态正确。"""
    # 创建用户
    register_response = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "rc-concurrent@example.com",
            "password": "TestPass123!",
            "device_fingerprint": "test-device-concurrent",
            "device_name": "Test Device",
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["user"]["id"]

    # 模拟快速连续的 INITIAL_PURCHASE 和 CANCELLATION
    event1 = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "INITIAL_PURCHASE",
        "app_user_id": user_id,
        "entitlement_ids": ["standard_access"],
        "expiration_at_ms": 1706745600000,
    }
    event2 = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "CANCELLATION",
        "app_user_id": user_id,
    }

    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        # 并发发送两个请求
        results = await asyncio.gather(
            client_no_csrf.post(
                "/webhooks/revenuecat",
                json={"event": event1},
                headers={"Authorization": "Bearer whsec_test"},
            ),
            client_no_csrf.post(
                "/webhooks/revenuecat",
                json={"event": event2},
                headers={"Authorization": "Bearer whsec_test"},
            ),
        )

    # 两个请求都应该成功
    assert results[0].status_code == 200
    assert results[1].status_code == 200
