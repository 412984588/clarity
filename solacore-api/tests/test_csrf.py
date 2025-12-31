import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_csrf_missing_token_rejected(client_no_csrf: AsyncClient):
    """测试缺少 CSRF token 时请求被拒绝"""
    # 注册用户
    register_resp = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "csrf-missing@example.com",
            "password": "Pass123!",  # 短密码避免 bcrypt 72字节限制
            "device_fingerprint": "csrf-device-001",
        },
    )
    assert register_resp.status_code == 201

    # 获取认证 token
    access_token = register_resp.cookies.get("access_token")
    assert access_token, "注册应该返回 access_token cookie"

    # 获取 CSRF token（但不使用）
    csrf_resp = await client_no_csrf.get("/auth/csrf")
    assert csrf_resp.status_code == 200

    # 尝试删除账户（需要 CSRF 保护的端点），不带 CSRF token
    response = await client_no_csrf.delete(
        "/account",
        cookies={"access_token": access_token},
    )
    assert response.status_code == 403
    assert response.json()["error"] == "CSRF_TOKEN_MISSING"


@pytest.mark.asyncio
async def test_csrf_invalid_token_rejected(client_no_csrf: AsyncClient):
    """测试无效 CSRF token 时请求被拒绝"""
    # 注册用户
    register_resp = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "csrf-invalid@example.com",
            "password": "Pass123!",
            "device_fingerprint": "csrf-device-002",
        },
    )
    assert register_resp.status_code == 201

    # 获取认证 token
    access_token = register_resp.cookies.get("access_token")
    assert access_token

    # 获取 CSRF token
    csrf_resp = await client_no_csrf.get("/auth/csrf")
    assert csrf_resp.status_code == 200

    # 尝试删除账户，使用无效的 CSRF token
    response = await client_no_csrf.delete(
        "/account",
        cookies={"access_token": access_token},
        headers={"X-CSRF-Token": "invalid-token-12345"},
    )
    assert response.status_code == 403
    assert response.json()["error"] == "CSRF_TOKEN_INVALID"


@pytest.mark.asyncio
async def test_csrf_valid_token_accepted(client_no_csrf: AsyncClient):
    """测试有效 CSRF token 时请求被接受"""
    # 注册用户
    register_resp = await client_no_csrf.post(
        "/auth/register",
        json={
            "email": "csrf-valid@example.com",
            "password": "Pass123!",
            "device_fingerprint": "csrf-device-003",
        },
    )
    assert register_resp.status_code == 201

    # 获取认证 token
    access_token = register_resp.cookies.get("access_token")
    assert access_token

    # 获取 CSRF token
    csrf_resp = await client_no_csrf.get("/auth/csrf")
    assert csrf_resp.status_code == 200
    csrf_token = csrf_resp.cookies.get("csrf_token")
    csrf_http_token = csrf_resp.cookies.get("csrf_token_http")
    assert csrf_token, "应该返回 csrf_token cookie"
    assert csrf_http_token, "应该返回 csrf_token_http cookie"

    # 删除账户，使用正确的 CSRF token
    response = await client_no_csrf.delete(
        "/account",
        cookies={
            "access_token": access_token,
            "csrf_token": csrf_token,
            "csrf_token_http": csrf_http_token,
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    # 删除账户应该返回 204 No Content
    assert response.status_code == 204
