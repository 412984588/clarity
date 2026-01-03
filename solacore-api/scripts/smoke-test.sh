#!/bin/bash
# =============================================================================
# Solacore API 部署冒烟测试
# =============================================================================
# 用途：部署后快速验证核心功能是否正常
# 使用：./scripts/smoke-test.sh [API_URL]
# 示例：./scripts/smoke-test.sh https://api.solacore.app
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API URL（默认生产环境）
API_URL="${1:-https://api.solacore.app}"
FRONTEND_URL="${FRONTEND_URL:-https://solacore.app}"

echo "=========================================="
echo "🧪 Solacore API 冒烟测试"
echo "=========================================="
echo "API URL: $API_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# 测试计数器
TESTS_PASSED=0
TESTS_FAILED=0

# 测试结果函数
pass_test() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

fail_test() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    echo -e "${YELLOW}   详情: $2${NC}"
    ((TESTS_FAILED++))
}

# =============================================================================
# 测试 1: 健康检查
# =============================================================================
echo "📍 测试 1: 健康检查端点..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health/live")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    pass_test "健康检查端点返回 200"
else
    fail_test "健康检查端点失败" "HTTP $HEALTH_RESPONSE (期望 200)"
fi

# =============================================================================
# 测试 2: CORS 配置
# =============================================================================
echo "📍 测试 2: CORS 配置..."
CORS_RESPONSE=$(curl -s -I -H "Origin: $FRONTEND_URL" "$API_URL/health/live" | grep -i "access-control-allow-origin")
if echo "$CORS_RESPONSE" | grep -q "$FRONTEND_URL"; then
    pass_test "CORS 允许前端域名访问"
else
    fail_test "CORS 配置错误" "响应头: $CORS_RESPONSE"
fi

CORS_CREDENTIALS=$(curl -s -I -H "Origin: $FRONTEND_URL" "$API_URL/health/live" | grep -i "access-control-allow-credentials")
if echo "$CORS_CREDENTIALS" | grep -qi "true"; then
    pass_test "CORS 允许携带凭证 (credentials)"
else
    fail_test "CORS 凭证配置错误" "响应头: $CORS_CREDENTIALS"
fi

# =============================================================================
# 测试 3: Cookie Domain 配置（通过注册接口）
# =============================================================================
echo "📍 测试 3: Cookie Domain 配置..."
TEST_EMAIL="smoke-test-$(date +%s)@example.com"
REGISTER_RESPONSE=$(curl -s -i -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"TestPassword123!\",
    \"device_fingerprint\": \"smoke-test-device\",
    \"device_name\": \"Smoke Test Device\"
  }")

# 检查 HTTP 状态码
HTTP_STATUS=$(echo "$REGISTER_RESPONSE" | grep -i "HTTP/" | awk '{print $2}')
if [ "$HTTP_STATUS" = "201" ]; then
    pass_test "注册接口返回 201"
else
    fail_test "注册接口失败" "HTTP $HTTP_STATUS (期望 201)"
fi

# 检查 Set-Cookie 中的 Domain 属性
COOKIE_DOMAIN=$(echo "$REGISTER_RESPONSE" | grep -i "set-cookie: access_token" | grep -o "Domain=[^;]*")
if echo "$COOKIE_DOMAIN" | grep -q "Domain=\."; then
    pass_test "Cookie 配置了跨子域名 Domain"
    echo "   Domain: $COOKIE_DOMAIN"
else
    fail_test "Cookie Domain 配置错误" "响应头: $(echo "$REGISTER_RESPONSE" | grep -i "set-cookie")"
fi

# 检查 HttpOnly 属性
if echo "$REGISTER_RESPONSE" | grep -i "set-cookie: access_token" | grep -qi "HttpOnly"; then
    pass_test "Cookie 配置了 HttpOnly 安全属性"
else
    fail_test "Cookie 缺少 HttpOnly 属性" "可能存在 XSS 风险"
fi

# 检查 Secure 属性
if echo "$REGISTER_RESPONSE" | grep -i "set-cookie: access_token" | grep -qi "Secure"; then
    pass_test "Cookie 配置了 Secure 安全属性"
else
    fail_test "Cookie 缺少 Secure 属性" "仅应在 HTTPS 下传输"
fi

# 检查 SameSite 属性
if echo "$REGISTER_RESPONSE" | grep -i "set-cookie: access_token" | grep -qi "SameSite"; then
    pass_test "Cookie 配置了 SameSite 防护"
else
    fail_test "Cookie 缺少 SameSite 属性" "可能存在 CSRF 风险"
fi

# =============================================================================
# 测试 4: API 文档可访问性
# =============================================================================
echo "📍 测试 4: API 文档..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/docs")
if [ "$DOCS_RESPONSE" = "200" ]; then
    pass_test "API 文档 (/docs) 可访问"
else
    fail_test "API 文档不可访问" "HTTP $DOCS_RESPONSE"
fi

# =============================================================================
# 测试 5: 认证流程（带 Cookie）
# =============================================================================
echo "📍 测试 5: 认证流程（带 Cookie）..."
# 提取 access_token
ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | grep -i "set-cookie: access_token" | sed -n 's/.*access_token=\([^;]*\).*/\1/p' | head -1)

if [ -n "$ACCESS_TOKEN" ]; then
    # 使用 Cookie 调用 /auth/me
    ME_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_URL/auth/me" \
      -H "Cookie: access_token=$ACCESS_TOKEN")

    if [ "$ME_RESPONSE" = "200" ]; then
        pass_test "Cookie 认证成功 (/auth/me 返回 200)"
    else
        fail_test "Cookie 认证失败" "HTTP $ME_RESPONSE (期望 200)"
    fi
else
    fail_test "无法提取 access_token" "注册响应中未找到 Cookie"
fi

# =============================================================================
# 测试总结
# =============================================================================
echo ""
echo "=========================================="
echo "📊 测试总结"
echo "=========================================="
echo -e "通过: ${GREEN}$TESTS_PASSED${NC}"
echo -e "失败: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！部署成功！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  有 $TESTS_FAILED 个测试失败，请检查配置！${NC}"
    exit 1
fi
