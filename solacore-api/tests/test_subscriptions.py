"""Subscription endpoint tests."""

import pytest
from httpx import AsyncClient


async def _register_user(client: AsyncClient, email: str, fingerprint: str) -> str:
    """Helper to register user and get access token."""
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "Password123",
            "device_fingerprint": fingerprint,
        },
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_subscriptions_unauthenticated_returns_401(client: AsyncClient):
    """Unauthenticated request returns 401."""
    response = await client.get("/subscriptions/current")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_subscription(client: AsyncClient):
    """Get current subscription returns user's subscription."""
    token = await _register_user(client, "sub-current@example.com", "sub-device-001")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/subscriptions/current", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "free"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_usage(client: AsyncClient):
    """Get usage returns current usage stats."""
    token = await _register_user(client, "sub-usage@example.com", "sub-device-002")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/subscriptions/usage", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "free"
    assert data["sessions_used"] == 0
    assert data["sessions_limit"] == 10
    assert data["is_lifetime"] is True


@pytest.mark.asyncio
async def test_checkout_invalid_price_id(client: AsyncClient):
    """Checkout with invalid price_id returns 400."""
    token = await _register_user(client, "sub-checkout@example.com", "sub-device-003")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/subscriptions/checkout", json={"price_id": "invalid_price"}, headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "INVALID_PRICE_ID"


@pytest.mark.asyncio
async def test_portal_no_customer_returns_404(client: AsyncClient):
    """Portal without stripe_customer_id returns 404."""
    token = await _register_user(client, "sub-portal@example.com", "sub-device-005")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/subscriptions/portal", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "NO_SUBSCRIPTION"
