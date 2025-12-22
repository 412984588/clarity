# Epic 4.5: RevenueCat IAP 任务清单

## Backend (clarity-api)

### 配置
- [ ] 更新 `app/config.py` 添加 RevenueCat 配置项
- [ ] 更新 `.env.example` 添加环境变量说明

### Webhook 端点
- [ ] 创建 `app/routers/revenuecat_webhooks.py`
- [ ] 实现 Bearer token 认证中间件
- [ ] 处理 INITIAL_PURCHASE 事件
- [ ] 处理 RENEWAL 事件
- [ ] 处理 CANCELLATION 事件
- [ ] 处理 EXPIRATION 事件
- [ ] 处理 BILLING_ISSUE 事件
- [ ] 处理 PRODUCT_CHANGE 事件
- [ ] 实现 entitlement → tier 映射
- [ ] 实现幂等性 (复用 LRU 缓存)
- [ ] 注册路由到 main.py

### 测试
- [ ] `tests/test_revenuecat_webhooks.py`
- [ ] 测试缺失 Authorization 返回 401
- [ ] 测试无效 token 返回 401
- [ ] 测试 INITIAL_PURCHASE 创建订阅
- [ ] 测试 RENEWAL 更新 period_end
- [ ] 测试 EXPIRATION 降级到 free

### 验收
- [ ] ruff check 通过
- [ ] mypy 通过
- [ ] pytest 全部通过

---

## Mobile (clarity-mobile)

### SDK 集成
- [ ] 安装 react-native-purchases
- [ ] 创建 `src/services/revenuecat.ts`
- [ ] 实现 configure() 初始化
- [ ] 实现 login(userId) 绑定用户
- [ ] 实现 logout() 解绑
- [ ] 实现 getOfferings() 获取产品
- [ ] 实现 purchasePackage() 购买
- [ ] 实现 restorePurchases() 恢复

### Paywall 页面
- [ ] 创建 `app/(main)/paywall.tsx`
- [ ] 展示 Standard/Pro 两个选项
- [ ] 展示价格和功能对比
- [ ] 购买按钮触发 IAP
- [ ] 恢复购买按钮
- [ ] 购买成功后刷新状态并返回

### Settings 增强
- [ ] 添加 "Manage Subscription" 入口
- [ ] iOS 跳转到系统订阅页
- [ ] Android 跳转到 Play Store 订阅页
- [ ] 添加 "Restore Purchases" 入口

### 登录态绑定
- [ ] 登录成功后调用 RevenueCat.login()
- [ ] 登出时调用 RevenueCat.logout()

### 验收
- [ ] npm run lint 通过
- [ ] npx tsc --noEmit 通过

---

## PR
- [ ] 创建 PR
- [ ] 设置 auto-merge (squash)
