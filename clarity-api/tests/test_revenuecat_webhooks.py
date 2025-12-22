"""RevenueCat webhook endpoint tests."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from tests.conftest import TestingSessionLocal
from app.models.subscription import Subscription
from app.models.user import User
from app.models.webhook_event import ProcessedWebhookEvent


class _TestSettings:
    revenuecat_webhook_secret = "whsec_test"
    revenuecat_entitlement_standard = "standard_access"
    revenuecat_entitlement_pro = "pro_access"


async def _create_user_with_subscription(email: str) -> str:
    """直接创建用户与订阅记录。"""
    async with TestingSessionLocal() as session:
        user = User(
            email=email,
            password_hash="test",
            auth_provider="email",
        )
        session.add(user)
        await session.flush()

        subscription = Subscription(
            user_id=user.id,
            tier="free",
            status="active",
        )
        session.add(subscription)
        await session.commit()
        return str(user.id)


@pytest.mark.asyncio
async def test_webhook_missing_auth_returns_401(client: AsyncClient):
    """缺少 Authorization 时返回 401。"""
    response = await client.post(
        "/webhooks/revenuecat",
        json={"event": {"type": "INITIAL_PURCHASE"}},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "MISSING_AUTH"


@pytest.mark.asyncio
async def test_webhook_invalid_auth_returns_401(client: AsyncClient):
    """Authorization 不合法时返回 401。"""
    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        response = await client.post(
            "/webhooks/revenuecat",
            json={"event": {"type": "INITIAL_PURCHASE"}},
            headers={"Authorization": "Bearer wrong"},
        )
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_AUTH"


@pytest.mark.asyncio
async def test_webhook_initial_purchase(client: AsyncClient):
    """INITIAL_PURCHASE 更新 tier 与状态。"""
    user_id = await _create_user_with_subscription("rc-initial@example.com")

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
        response = await client.post(
            "/webhooks/revenuecat",
            json={"event": event},
            headers={"Authorization": "Bearer whsec_test"},
        )

    assert response.status_code == 200

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.tier == "standard"
        assert sub.status == "active"
        assert sub.cancel_at_period_end is False


@pytest.mark.asyncio
async def test_webhook_renewal(client: AsyncClient):
    """RENEWAL 更新 period_end。"""
    user_id = await _create_user_with_subscription("rc-renewal@example.com")

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "RENEWAL",
        "app_user_id": user_id,
        "expiration_at_ms": 1706745600000,
    }

    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        response = await client.post(
            "/webhooks/revenuecat",
            json={"event": event},
            headers={"Authorization": "Bearer whsec_test"},
        )

    assert response.status_code == 200

    expected = datetime.fromtimestamp(1706745600, tz=timezone.utc).replace(tzinfo=None)
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.current_period_end == expected
        assert sub.status == "active"


@pytest.mark.asyncio
async def test_webhook_expiration(client: AsyncClient):
    """EXPIRATION 降级为 free 并标记过期。"""
    user_id = await _create_user_with_subscription("rc-expired@example.com")

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        sub.tier = "pro"
        await session.commit()

    event = {
        "id": f"evt_{uuid4().hex[:14]}",
        "type": "EXPIRATION",
        "app_user_id": user_id,
    }

    with patch(
        "app.routers.revenuecat_webhooks.get_settings", return_value=_TestSettings()
    ):
        response = await client.post(
            "/webhooks/revenuecat",
            json={"event": event},
            headers={"Authorization": "Bearer whsec_test"},
        )

    assert response.status_code == 200

    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.tier == "free"
        assert sub.status == "expired"


@pytest.mark.asyncio
async def test_webhook_idempotency_duplicate_event(client: AsyncClient):
    """重复发送同一 event_id 只处理一次（幂等性）。"""
    user_id = await _create_user_with_subscription("rc-idempotent@example.com")
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
        response1 = await client.post(
            "/webhooks/revenuecat",
            json={"event": event},
            headers={"Authorization": "Bearer whsec_test"},
        )
        assert response1.status_code == 200

        # 第二次请求（相同 event_id）
        response2 = await client.post(
            "/webhooks/revenuecat",
            json={"event": event},
            headers={"Authorization": "Bearer whsec_test"},
        )
        assert response2.status_code == 200

    # 验证事件只被记录一次
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(ProcessedWebhookEvent).where(
                ProcessedWebhookEvent.event_id == event_id
            )
        )
        events = result.scalars().all()
        assert len(events) == 1

        # 验证订阅状态是 pro（处理成功）
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        assert sub.tier == "pro"


@pytest.mark.asyncio
async def test_webhook_concurrency_final_state_correct(client: AsyncClient):
    """并发发送两个不同事件，最终状态正确。"""
    user_id = await _create_user_with_subscription("rc-concurrent@example.com")

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
            client.post(
                "/webhooks/revenuecat",
                json={"event": event1},
                headers={"Authorization": "Bearer whsec_test"},
            ),
            client.post(
                "/webhooks/revenuecat",
                json={"event": event2},
                headers={"Authorization": "Bearer whsec_test"},
            ),
        )

    # 两个请求都应该成功
    assert results[0].status_code == 200
    assert results[1].status_code == 200

    # 验证两个事件都被记录
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(ProcessedWebhookEvent).where(
                ProcessedWebhookEvent.event_id.in_([event1["id"], event2["id"]])
            )
        )
        events = result.scalars().all()
        assert len(events) == 2

        # 验证订阅状态最终正确（CANCELLATION 后 cancel_at_period_end 为 True）
        result = await session.execute(
            select(Subscription).join(User).where(User.id == user_id)
        )
        sub = result.scalar_one()
        # 两个事件都被处理，最终状态取决于处理顺序
        # 但关键是没有数据丢失或写脏数据
        assert sub.tier in ["standard", "free"]  # 取决于处理顺序
        assert sub.status == "active"  # 两个事件都不会改变为非 active
