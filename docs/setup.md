# 开发环境配置指南

## 环境要求

| 工具 | 版本 | 用途 |
|------|------|------|
| Node.js | 18+ | 移动端开发 |
| Python | 3.11+ | 后端开发 |
| Poetry | 1.7+ | Python 依赖管理 |
| Docker | 24+ | 数据库容器 |
| Expo CLI | latest | React Native 开发 |

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  clarity-mobile │────▶│   clarity-api   │────▶│   PostgreSQL    │
│  (React Native) │     │    (FastAPI)    │     │    (Docker)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        ▼                       ▼
   Expo Router              /health
   Tab Navigation           /docs (Swagger)
```

## 后端配置 (clarity-api)

### 1. 安装依赖

```bash
cd clarity-api
poetry install --no-root
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 修改数据库连接等配置
```

### 3. 启动 PostgreSQL

```bash
docker-compose up -d db
```

### 4. 运行数据库迁移

```bash
poetry run alembic upgrade head
```

### 5. 启动开发服务器

```bash
poetry run uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档

## 移动端配置 (clarity-mobile)

### 1. 安装依赖

```bash
cd clarity-mobile
npm install
```

### 2. 环境变量配置

| 环境 | 文件 | API URL |
|------|------|---------|
| dev | `.env.development` | `http://localhost:8000` |
| staging | `.env.staging` | `https://staging-api.clarity.app` |
| prod | `.env.production` | `https://api.clarity.app` |

```bash
# 开发环境（默认）
cp .env.example .env.development
```

### 3. 启动开发服务器

```bash
npx expo start
```

### 4. 运行应用

- iOS 模拟器：按 `i`
- Android 模拟器：按 `a`
- Expo Go：扫描二维码

## iOS 本地调试

### 环境要求
- macOS 12+
- Xcode 14+ (从 App Store 安装)
- CocoaPods (`sudo gem install cocoapods`)

### 模拟器调试
```bash
cd clarity-mobile
npx expo start --ios
```

### 真机调试
1. 注册 Apple Developer Account
2. 在 Xcode 中配置 Signing & Capabilities
3. 连接 iPhone，运行 `npx expo run:ios --device`

## Android 本地调试

### 环境要求
- Android Studio (最新稳定版)
- Android SDK (API 33+)
- JDK 17+

### 模拟器调试
```bash
cd clarity-mobile
npx expo start --android
```

### 真机调试
1. 手机开启 "开发者选项" → "USB 调试"
2. 连接 USB，运行 `npx expo run:android --device`

## 验证安装

### 后端健康检查

```bash
curl http://localhost:8000/health
# 应返回 {"status":"healthy","version":"1.0.0","database":"connected"}
```

### 代码质量检查

```bash
# 后端
cd clarity-api
poetry run ruff check .
poetry run mypy app --ignore-missing-imports

# 移动端
cd clarity-mobile
npm run lint
npx tsc --noEmit
```

## 订阅同步验证（本地/测试环境）

### 1. 模拟 RevenueCat Webhook 事件

```bash
# 获取测试用户 ID（从数据库或创建新用户）
USER_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# 模拟 INITIAL_PURCHASE 事件
curl -X POST http://localhost:8000/webhooks/revenuecat \
  -H "Authorization: Bearer $REVENUECAT_WEBHOOK_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "event": {
      "id": "evt_test_001",
      "type": "INITIAL_PURCHASE",
      "app_user_id": "'"$USER_ID"'",
      "entitlement_ids": ["standard_access"],
      "expiration_at_ms": 1735689600000
    }
  }'
# 应返回 {"received": true}
```

### 2. 验证后端订阅状态

```bash
# 获取 access token（通过登录或注册）
ACCESS_TOKEN="eyJ..."

# 查询当前订阅
curl http://localhost:8000/subscriptions/current \
  -H "Authorization: Bearer $ACCESS_TOKEN"
# 应返回 {"tier": "standard", "status": "active", ...}
```

### 3. 验证 App 端同步

1. 登录 App，进入 Settings 页面
2. 订阅状态应显示 "Standard" 或 "Pro"
3. 点击 "Manage Subscription" 应能跳转系统订阅管理页

### 4. 测试幂等性

```bash
# 发送相同 event.id 两次
curl -X POST http://localhost:8000/webhooks/revenuecat \
  -H "Authorization: Bearer $REVENUECAT_WEBHOOK_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"event": {"id": "evt_test_001", "type": "INITIAL_PURCHASE", "app_user_id": "'"$USER_ID"'"}}'

# 第二次应该立即返回 {"received": true} 但不会重复处理
# 查询 processed_webhook_events 表确认只有一条记录
```

### RevenueCat Webhook Event Types

| Event | 触发场景 | 订阅状态变化 |
|-------|---------|-------------|
| `INITIAL_PURCHASE` | 首次购买 | tier → standard/pro, status → active |
| `RENEWAL` | 自动续费 | current_period_end 更新 |
| `CANCELLATION` | 取消续订 | cancel_at_period_end → true |
| `EXPIRATION` | 订阅到期 | tier → free, status → expired |
| `BILLING_ISSUE` | 付款失败 | status → past_due |
| `PRODUCT_CHANGE` | 升级/降级 | tier 变化 |

> 参考: [RevenueCat Webhook Events](https://www.revenuecat.com/docs/webhooks)

## Safety 行为与危机检测

### Crisis Detector 概述

后端集成了危机检测器 (`CrisisDetector`)，在处理用户输入时自动检测可能表示心理危机的内容。

### 触发关键词

检测器支持英语和西班牙语关键词（使用正则词边界匹配）：

| 语言 | 关键词示例 |
|------|-----------|
| English | `suicide`, `kill myself`, `want to die`, `end my life`, `self-harm` |
| Spanish | `suicidio`, `matarme`, `quiero morir`, `terminar con mi vida`, `autolesión` |

### API 响应

当检测到危机内容时，API 返回：

```json
{
  "blocked": true,
  "reason": "CRISIS",
  "resources": {
    "US": "988",
    "ES": "717 003 717"
  }
}
```

### 热线号码

| 国家/地区 | 热线 | 描述 |
|----------|------|------|
| 🇺🇸 United States | **988** | Suicide & Crisis Lifeline (24/7) |
| 🇪🇸 Spain | **717 003 717** | Teléfono de la Esperanza (24/7) |

### 测试危机检测

```bash
# 测试危机检测（应返回 blocked=true）
curl -X POST http://localhost:8000/sessions/{session_id}/stream \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_text": "I want to end my life"}'

# 预期响应：
# {"blocked": true, "reason": "CRISIS", "resources": {"US": "988", "ES": "717 003 717"}}
```

### Analytics 事件

危机检测会触发 `crisis_detected` 分析事件，记录：
- `session_id`: 会话 ID
- `user_id`: 用户 ID
- `timestamp`: 检测时间

> ⚠️ **隐私说明**: 系统不会记录触发危机检测的具体文本内容。

## 常见问题

详见 [troubleshooting.md](troubleshooting.md)
