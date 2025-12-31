import pytest
from app.database import Base, get_db
from app.main import app
from app.middleware.rate_limit import limiter
from httpx import ASGITransport, AsyncClient
from tests.conftest import TestingSessionLocal, engine_test


@pytest.mark.asyncio
async def test_debug_register_cookies():
    # 创建表
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 覆盖依赖
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 先获取CSRF token
        csrf_resp = await client.get("/auth/csrf")
        print(f"\nCSRF Response cookies: {dict(csrf_resp.cookies)}")

        # 注册
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "Password123",
                "device_fingerprint": "test-001",
            },
        )

        print(f"\nRegister status: {response.status_code}")
        print(f"Register cookies: {dict(response.cookies)}")
        print(f"Register response.cookies object: {response.cookies}")

        # 检查Set-Cookie header
        set_cookie_headers = response.headers.get_list("set-cookie")
        print(f"\nSet-Cookie headers count: {len(set_cookie_headers)}")
        for idx, cookie in enumerate(set_cookie_headers):
            print(f"Set-Cookie {idx}: {cookie[:100]}...")

        assert response.status_code == 201

    app.dependency_overrides.clear()
