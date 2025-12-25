# Epic 4.5: RevenueCat IAP 实施计划

## Phase 1: Backend Webhook (先做后端，方便测试)

### 1.1 配置
- 更新 `app/config.py` 添加 RevenueCat 配置
- 更新 `.env.example`

### 1.2 Webhook Router
- 创建 `app/routers/revenuecat_webhooks.py`
- 实现 Bearer token 认证
- 处理 6 种事件类型

### 1.3 测试
- `tests/test_revenuecat_webhooks.py`
- Mock 各种事件类型

---

## Phase 2: Mobile SDK 集成

### 2.1 安装依赖
```bash
cd solacore-mobile
npx expo install react-native-purchases
```

### 2.2 创建 RevenueCat Service
- `src/services/revenuecat.ts`
- 初始化、登录、购买、恢复

### 2.3 Context/Store 更新
- 扩展 AuthContext 处理 RevenueCat 登录绑定

---

## Phase 3: Paywall 页面

### 3.1 创建页面
- `app/(main)/paywall.tsx`
- 展示 offerings
- 购买按钮

### 3.2 导航
- 从 Settings 或 Usage Limit 触达 Paywall

---

## Phase 4: Settings 增强

### 4.1 新增入口
- Manage Subscription (系统订阅页)
- Restore Purchases

---

## Phase 5: 验收

### Backend
```bash
cd solacore-api
poetry run ruff check app tests
poetry run mypy app --ignore-missing-imports
poetry run pytest -v
```

### Mobile
```bash
cd solacore-mobile
npm run lint
npx tsc --noEmit
```

---

## 风险与注意事项

1. **Expo Go 不支持**: react-native-purchases 需要 native 模块，必须用 EAS Build
2. **Sandbox 测试**: IAP 购买需要 iOS/Android sandbox 账号
3. **双订阅系统**: Stripe (Web) 和 RevenueCat (Mobile) 并存，需防止冲突
4. **appUserId 一致性**: 必须使用 user.id 确保跨平台同步
