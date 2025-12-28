#!/bin/bash

# Rate Limit Testing Script
# 测试 SolaCore API 的限流功能

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BASE_URL="${API_BASE_URL:-http://139.180.223.98}"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="TestPass123!"
LOG_FILE="/tmp/rate_limit_test.log"

# 清空日志
> "$LOG_FILE"

# 工具函数：打印标题
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# 工具函数：打印成功
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 工具函数：打印失败
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 工具函数：打印警告
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 工具函数：发送 HTTP 请求并记录
http_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local headers=$4

    local url="${BASE_URL}${endpoint}"
    local status_code

    if [ -n "$data" ]; then
        status_code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            ${headers:+-H "$headers"} \
            -d "$data" 2>&1)
    else
        status_code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
            ${headers:+-H "$headers"} 2>&1)
    fi

    echo "$status_code"
}

# 测试函数：测试端点限流
test_endpoint_limit() {
    local endpoint=$1
    local method=$2
    local data=$3
    local limit=$4
    local test_name=$5
    local headers=$6

    print_header "测试: $test_name"
    echo "端点: $method $endpoint"
    echo "限制: $limit 次/分钟"
    echo ""

    local success_count=0
    local rate_limited_count=0
    local request_count=$((limit + 2))  # 超过限制

    echo "发送 $request_count 个请求..."

    for i in $(seq 1 $request_count); do
        status_code=$(http_request "$method" "$endpoint" "$data" "$headers")

        echo "[$i/$request_count] 状态码: $status_code" >> "$LOG_FILE"

        if [ "$status_code" = "429" ]; then
            ((rate_limited_count++))
            echo -n "R"  # Rate limited
        elif [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
            ((success_count++))
            echo -n "."  # Success
        else
            echo -n "X"  # Error
        fi

        # 快速连续请求
        sleep 0.05
    done

    echo ""
    echo ""
    echo "结果统计:"
    echo "  成功请求: $success_count"
    echo "  限流拦截: $rate_limited_count"
    echo ""

    # 判断限流是否生效
    if [ $rate_limited_count -gt 0 ]; then
        print_success "端点 $endpoint - 限流生效 (${request_count}次请求，${rate_limited_count}次返回429)"
        return 0
    else
        print_error "端点 $endpoint - 限流未生效 (所有${request_count}次请求都未被拦截)"
        return 1
    fi
}

# 测试函数：无限流端点
test_unlimited_endpoint() {
    local endpoint=$1
    local test_name=$2

    print_header "测试: $test_name (应无限流)"

    local request_count=10
    local success_count=0

    for i in $(seq 1 $request_count); do
        status_code=$(http_request "GET" "$endpoint" "" "")

        if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
            ((success_count++))
            echo -n "."
        else
            echo -n "X"
        fi

        sleep 0.05
    done

    echo ""
    echo ""

    if [ $success_count -eq $request_count ]; then
        print_success "端点 $endpoint - 无限流限制 (${request_count}次请求全部成功)"
        return 0
    else
        print_warning "端点 $endpoint - 部分请求失败 (${success_count}/${request_count})"
        return 1
    fi
}

# 检查 Redis 连接
check_redis() {
    print_header "检查 Redis 连接状态"

    # 尝试通过健康检查端点验证 Redis
    result=$(curl -s "$BASE_URL/health/ready" 2>&1)

    if echo "$result" | grep -q '"redis"'; then
        if echo "$result" | grep -q '"status":"up"'; then
            print_success "Redis 连接正常"
            return 0
        else
            print_warning "Redis 状态异常"
            echo "$result" | python3 -m json.tool 2>/dev/null || echo "$result"
            return 1
        fi
    else
        print_error "无法获取 Redis 状态"
        echo "$result"
        return 1
    fi
}

# 主测试流程
main() {
    print_header "SolaCore API 限流功能测试"
    echo "目标服务器: $BASE_URL"
    echo "日志文件: $LOG_FILE"
    echo ""

    # 等待用户确认
    read -p "按 Enter 开始测试... " -r

    # 1. 检查 Redis
    check_redis
    echo ""

    # 2. 测试无限流端点（健康检查）
    test_unlimited_endpoint "/health" "健康检查端点"
    echo ""

    # 3. 测试注册端点限流 (5/min)
    register_data=$(cat <<EOF
{"email": "$TEST_EMAIL", "password": "$TEST_PASSWORD", "confirm_password": "$TEST_PASSWORD"}
EOF
)
    test_endpoint_limit "/auth/register" "POST" "$register_data" 5 "注册端点限流 (5/min)"
    register_result=$?
    echo ""

    # 等待限流窗口重置
    if [ $register_result -eq 0 ]; then
        print_warning "限流生效，等待 60 秒让限流窗口重置..."
        sleep 60
    else
        print_warning "等待 5 秒后继续..."
        sleep 5
    fi

    # 4. 测试登录端点限流 (5/min)
    login_data=$(cat <<EOF
{"email": "$TEST_EMAIL", "password": "$TEST_PASSWORD"}
EOF
)
    test_endpoint_limit "/auth/login" "POST" "$login_data" 5 "登录端点限流 (5/min)"
    login_result=$?
    echo ""

    # 5. 测试配置端点限流 (60/min)
    print_warning "准备测试配置端点 (需要发送 62 个请求)..."
    sleep 2
    test_endpoint_limit "/config" "GET" "" 60 "配置端点限流 (60/min)"
    config_result=$?
    echo ""

    # 生成测试报告
    print_header "测试总结"

    total_tests=3
    passed_tests=0

    [ $register_result -eq 0 ] && ((passed_tests++))
    [ $login_result -eq 0 ] && ((passed_tests++))
    [ $config_result -eq 0 ] && ((passed_tests++))

    echo "通过测试: $passed_tests / $total_tests"
    echo ""

    if [ $passed_tests -eq $total_tests ]; then
        print_success "所有限流测试通过！"
    else
        print_error "部分限流测试失败！"
        echo ""
        print_header "诊断建议"

        if [ $register_result -ne 0 ] || [ $login_result -ne 0 ]; then
            echo "认证端点限流失败，检查以下配置："
            echo ""
            echo "1. app/routers/auth.py 中的装饰器配置:"
            echo "   @limiter.limit(AUTH_RATE_LIMIT, ...)"
            echo ""
            echo "2. .env 环境变量:"
            echo "   AUTH_RATE_LIMIT=5/minute"
            echo ""
            echo "3. Redis 中的限流键:"
            echo "   docker exec -it clarity-redis redis-cli KEYS \"*LIMITER*\""
            echo ""
            echo "4. API 日志:"
            echo "   docker logs clarity-api -n 50 | grep -i 'rate\\|limit'"
        fi

        if [ $config_result -ne 0 ]; then
            echo "全局限流失败，检查以下配置："
            echo ""
            echo "1. app/middleware/rate_limit.py 中 limiter 初始化"
            echo ""
            echo "2. .env 环境变量:"
            echo "   API_RATE_LIMIT=60/minute"
            echo ""
            echo "3. Redis 存储后端是否配置:"
            echo "   limiter = Limiter(..., storage_uri=\"redis://...\")"
        fi

        echo ""
        echo "详细日志: $LOG_FILE"
    fi

    echo ""
    print_header "快速诊断命令"
    echo "# 检查 Redis 键"
    echo "docker exec -it clarity-redis redis-cli KEYS \"*LIMITER*\""
    echo ""
    echo "# 检查 API 日志"
    echo "docker logs clarity-api -n 100 | grep -i rate"
    echo ""
    echo "# 手动测试限流"
    echo "for i in {1..10}; do curl -s -o /dev/null -w \"%{http_code} \" http://139.180.223.98/config; done"
}

# 运行主函数
main "$@"
