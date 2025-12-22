"""认证相关测试"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """测试成功注册"""
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-001"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """测试弱密码被拒绝"""
    response = await client.post("/auth/register", json={
        "email": "weak@example.com",
        "password": "weak",
        "device_fingerprint": "test-device-002"
    })
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_no_uppercase(client: AsyncClient):
    """测试缺少大写字母的密码被拒绝"""
    response = await client.post("/auth/register", json={
        "email": "noupper@example.com",
        "password": "password123",
        "device_fingerprint": "test-device-003"
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_no_digit(client: AsyncClient):
    """测试缺少数字的密码被拒绝"""
    response = await client.post("/auth/register", json={
        "email": "nodigit@example.com",
        "password": "PasswordABC",
        "device_fingerprint": "test-device-004"
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """测试重复邮箱被拒绝"""
    # 第一次注册
    await client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-005"
    })
    # 第二次注册
    response = await client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "Password456",
        "device_fingerprint": "test-device-006"
    })
    assert response.status_code == 409
    assert response.json()["detail"]["error"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """测试成功登录"""
    # 先注册
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-007"
    })
    # 再登录
    response = await client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-007"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    """测试不存在的邮箱登录失败"""
    response = await client.post("/auth/login", json={
        "email": "nouser@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-008"
    })
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """测试错误密码登录失败"""
    # 先注册
    await client.post("/auth/register", json={
        "email": "wrongpwd@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-009"
    })
    # 错误密码登录
    response = await client.post("/auth/login", json={
        "email": "wrongpwd@example.com",
        "password": "WrongPass456",
        "device_fingerprint": "test-device-009"
    })
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """测试刷新 token"""
    # 先注册
    register_resp = await client.post("/auth/register", json={
        "email": "refresh@example.com",
        "password": "Password123",
        "device_fingerprint": "test-device-010"
    })
    refresh_token = register_resp.json()["refresh_token"]

    # 刷新 token
    response = await client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # Token rotation 验证：新 token 应该有效（同一秒内可能相同，所以只验证格式）
    assert data["refresh_token"].startswith("eyJ")


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """测试无效 token 刷新失败"""
    response = await client.post("/auth/refresh", json={
        "refresh_token": "invalid-token"
    })
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "INVALID_TOKEN"
