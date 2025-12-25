# Epic 4.5: RevenueCat IAP 集成规格

## 概述

在 iOS/Android 原生应用中通过 RevenueCat 实现 In-App Purchase (IAP)，与现有 Stripe 订阅系统并行运行

## 技术栈

- **Mobile**: react-native-purchases (RevenueCat SDK)
- **Backend**: FastAPI webhook endpoint
- **Expo/EAS**: 需要 development build（非 Expo Go）

---

## A. Mobile 端 (solacore-mobile)

### A1. RevenueCat SDK 集成

```bash
npx expo install react-native-purchases
```

**配置要求**:
- iOS: 需要 StoreKit 配置
- Android: 需要 Google Play Billing
- 初始化时机: App 启动时，登录后绑定 appUserId

**appUserId 策略**:
- 使用现有 user.id (UUID) 作为 RevenueCat appUserId
- 确保跨设备同步订阅状态

### A2. Paywall 页面

**路由**: `/paywall`

**UI 组件**:
```
┌─────────────────────────────────┐
│  🚀 Upgrade to Pro              │
├─────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐│
│  │  Standard   │ │    Pro      ││
│  │  $9.99/mo   │ │  $19.99/mo  ││
│  │  100/month  │ │  Unlimited  ││
│  │ [Subscribe] │ │ [Subscribe] ││
│  └─────────────┘ └─────────────┘│
├─────────────────────────────────┤
│  [Restore Purchases]            │
│  Already have a subscription?   │
└─────────────────────────────────┘
```

**功能**:
1. 展示 RevenueCat offerings
2. 购买按钮触发 native IAP 流程
3. 恢复购买功能
4. 购买成功后刷新本地订阅状态

### A3. Settings 订阅管理

**新增入口**:
- "Manage Subscription" → 打开系统订阅管理页面
  - iOS: `itms-apps://apps.apple.com/account/subscriptions`
  - Android: `https://play.google.com/store/account/subscriptions`
- "Restore Purchases" → 调用 `Purchases.restorePurchases()`

### A4. 登录态绑定

```typescript
// 登录成功后
await Purchases.logIn(user.id);

// 登出时
await Purchases.logOut();
```

---

## B. Backend 端 (solacore-api)

### B1. RevenueCat Webhook Endpoint

**路由**: `POST /webhooks/revenuecat`

**认证**: Bearer Token (RevenueCat webhook secret)

**事件类型处理**:
| 事件 | 动作 |
|------|------|
| `INITIAL_PURCHASE` | 创建/更新订阅为 active |
| `RENEWAL` | 更新 period_end |
| `CANCELLATION` | 标记 cancel_at_period_end=true |
| `EXPIRATION` | tier→free, status→expired |
| `BILLING_ISSUE` | status→past_due |
| `PRODUCT_CHANGE` | 更新 tier |

**Payload 结构** (简化):
```json
{
  "event": {
    "type": "INITIAL_PURCHASE",
    "app_user_id": "user-uuid",
    "product_id": "pro_monthly",
    "entitlement_ids": ["pro_access"],
    "expiration_at_ms": 1735689600000
  }
}
```

### B2. Entitlement → Tier 映射

**.env.example**:
```
REVENUECAT_WEBHOOK_SECRET=whsec_xxx
REVENUECAT_ENTITLEMENT_STANDARD=standard_access
REVENUECAT_ENTITLEMENT_PRO=pro_access
```

**映射逻辑**:
```python
ENTITLEMENT_TO_TIER = {
    settings.revenuecat_entitlement_standard: "standard",
    settings.revenuecat_entitlement_pro: "pro",
}
```

### B3. 幂等性

- 使用 `event.id` 作为幂等键
- 复用 Epic 4 的 LRU 缓存机制

---

## C. 数据流

```
┌──────────┐    ┌────────────┐    ┌─────────────┐    ┌──────────┐
│  Mobile  │───▶│ RevenueCat │───▶│   Webhook   │───▶│    DB    │
│  (IAP)   │    │  (Server)  │    │  /revenuecat│    │ subscrip │
└──────────┘    └────────────┘    └─────────────┘    └──────────┘
      │                                                    │
      │              ┌──────────────────────────────────────┘
      │              ▼
      └─────────────▶ GET /subscriptions/current
                     (验证订阅状态)
```

---

## D. 验收标准

### Mobile
- [ ] RevenueCat SDK 初始化成功
- [ ] Paywall 展示 offerings
- [ ] 购买流程完整（需真机 + sandbox）
- [ ] 恢复购买功能正常
- [ ] Settings 订阅管理入口正常
- [ ] lint + tsc 通过

### Backend
- [ ] Webhook 端点接收事件
- [ ] 正确解析 entitlement → tier
- [ ] 更新 subscriptions 表
- [ ] 幂等性处理
- [ ] ruff + mypy + pytest 通过
