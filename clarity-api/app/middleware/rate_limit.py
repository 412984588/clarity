"""API 限流中间件 - 防止 DDoS 和滥用"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# 创建限流器实例，使用客户端 IP 作为标识
limiter = Limiter(key_func=get_remote_address)

# 限流规则说明：
# - "10/minute" = 每分钟最多 10 次请求
# - "100/hour" = 每小时最多 100 次请求
# - "5/second" = 每秒最多 5 次请求

# 默认限流规则（适用于大多数 API）
DEFAULT_RATE_LIMIT = "60/minute"

# 敏感操作限流规则（登录、注册等）
AUTH_RATE_LIMIT = "10/minute"

# AI 生成限流规则（成本较高）
AI_RATE_LIMIT = "20/minute"

# 订阅相关限流规则
SUBSCRIPTION_RATE_LIMIT = "30/minute"
