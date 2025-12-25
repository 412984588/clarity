# Production Deployment Pre-Flight Checklist

**Version**: 1.0
**Created**: 2025-12-23
**Status**: Ready for Execution

---

## 1. Environment Variables (Production Required)

All variables below must be set before deployment.

### 1.1 Core (必填)

| Variable | Format | 获取方式 |
|----------|--------|---------|
| `DEBUG` | `false` | 固定值 |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/db` | Neon/Supabase 控制台 |
| `JWT_SECRET` | 64 字符 hex | `openssl rand -hex 32` |
| `APP_VERSION` | `1.0.0` | 固定值 |

### 1.2 OAuth (必填)

| Variable | Format | 获取方式 |
|----------|--------|---------|
| `GOOGLE_CLIENT_ID` | `xxx.apps.googleusercontent.com` | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `APPLE_CLIENT_ID` | `com.solacore.app` | [Apple Developer Portal](https://developer.apple.com/account/resources/identifiers) |

### 1.3 LLM (必填)

| Variable | Format | 获取方式 |
|----------|--------|---------|
| `LLM_PROVIDER` | `openai` | 固定值 |
| `OPENAI_API_KEY` | `sk-xxx` | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `LLM_MODEL` | `gpt-4o-mini` | 默认值 |
| `LLM_TIMEOUT` | `30` | 默认值 |
| `LLM_MAX_TOKENS` | `1024` | 默认值 |

### 1.4 Stripe (必填 - 使用 Live 密钥)

| Variable | Format | 获取方式 |
|----------|--------|---------|
| `STRIPE_SECRET_KEY` | `sk_live_xxx` | [Stripe Dashboard](https://dashboard.stripe.com/apikeys) |
| `STRIPE_WEBHOOK_SECRET` | `whsec_xxx` | 部署后从 Stripe Webhook 配置获取 |
| `STRIPE_PRICE_STANDARD` | `price_xxx` | [Stripe Products](https://dashboard.stripe.com/products) |
| `STRIPE_PRICE_PRO` | `price_xxx` | [Stripe Products](https://dashboard.stripe.com/products) |
| `STRIPE_SUCCESS_URL` | `https://api.solacore.app/subscriptions/success?session_id={CHECKOUT_SESSION_ID}` | 固定格式 |
| `STRIPE_CANCEL_URL` | `https://api.solacore.app/subscriptions/cancel` | 固定格式 |

### 1.5 RevenueCat (必填)

| Variable | Format | 获取方式 |
|----------|--------|---------|
| `REVENUECAT_WEBHOOK_SECRET` | `whsec_xxx` | [RevenueCat Dashboard](https://app.revenuecat.com) |
| `REVENUECAT_ENTITLEMENT_STANDARD` | `standard_access` | RevenueCat Entitlements |
| `REVENUECAT_ENTITLEMENT_PRO` | `pro_access` | RevenueCat Entitlements |

### 1.6 Monitoring (可选但强烈推荐)

| Variable | Format | 获取方式 |
|----------|--------|---------|
| `SENTRY_DSN` | `https://xxx@sentry.io/xxx` | [Sentry Project](https://sentry.io) |

---

## 2. Deployment Steps Checklist

### Phase 1: Database Setup

```bash
# 1.1 创建 Neon 数据库（登录 https://console.neon.tech）
# - 项目名: solacore-prod
# - 区域: us-east-1
# - 复制连接字符串

# 1.2 验证连接
export DATABASE_URL="postgresql+asyncpg://user:pass@ep-xxx.us-east-1.aws.neon.tech/solacore"
psql "${DATABASE_URL/+asyncpg/}" -c "SELECT 1"
# 预期输出: 1
```

- [ ] **1.1** 创建 Neon 数据库实例
- [ ] **1.2** 验证数据库连接成功

### Phase 2: Generate Secrets

```bash
# 2.1 生成 JWT Secret
openssl rand -hex 32
# 保存输出（64 字符 hex）
```

- [ ] **2.1** 生成并保存 JWT_SECRET

### Phase 3: Deploy Backend

```bash
# 3.1 Vercel 部署
npm i -g vercel
cd solacore-api
vercel --prod

# 3.2 设置环境变量（逐个设置）
vercel env add DEBUG production        # 输入: false
vercel env add DATABASE_URL production # 输入: postgresql+asyncpg://...
vercel env add JWT_SECRET production   # 输入: <64-char-hex>
# ... 继续设置所有变量

# 3.3 重新部署以应用新变量
vercel --prod
```

- [ ] **3.1** 部署到 Vercel
- [ ] **3.2** 设置所有环境变量
- [ ] **3.3** 重新部署

### Phase 4: Database Migration

```bash
# 4.1 运行迁移
cd solacore-api
export DATABASE_URL="postgresql+asyncpg://..."
poetry run alembic upgrade head

# 4.2 验证迁移
poetry run alembic current
# 预期输出: 显示最新 revision
```

- [ ] **4.1** 运行 Alembic 迁移
- [ ] **4.2** 验证迁移成功

### Phase 5: Domain Setup

```bash
# 5.1 添加自定义域名（在 Vercel Dashboard）
# Project Settings → Domains → Add → api.solacore.app

# 5.2 验证 SSL
curl -I https://api.solacore.app
# 预期: HTTP/2 200, 有效证书
```

- [ ] **5.1** 配置自定义域名
- [ ] **5.2** 验证 SSL 证书

### Phase 6: Smoke Test

```bash
# 6.1 健康检查
curl https://api.solacore.app/health
# 预期: {"status":"healthy","version":"1.0.0","database":"connected"}

# 6.2 就绪检查
curl https://api.solacore.app/health/ready
# 预期: {"ready":true}

# 6.3 存活检查
curl https://api.solacore.app/health/live
# 预期: {"live":true}

# 6.4 运行完整 smoke 脚本
./scripts/deploy_prod_smoke.sh https://api.solacore.app
# 预期: All smoke tests passed!
```

- [ ] **6.1** /health 返回 healthy
- [ ] **6.2** /health/ready 返回 ready
- [ ] **6.3** /health/live 返回 live
- [ ] **6.4** Smoke 脚本全部通过

### Phase 7: Webhook Configuration

```bash
# 7.1 Stripe Webhook
# - 登录 https://dashboard.stripe.com/webhooks
# - Add endpoint: https://api.solacore.app/webhooks/stripe
# - 选择事件: checkout.session.completed, customer.subscription.*
# - 复制 Signing secret → 更新 STRIPE_WEBHOOK_SECRET

# 7.2 RevenueCat Webhook
# - 登录 https://app.revenuecat.com → Settings → Webhooks
# - Add endpoint: https://api.solacore.app/webhooks/revenuecat
# - 复制 secret → 更新 REVENUECAT_WEBHOOK_SECRET

# 7.3 测试 Webhook
# Stripe: Dashboard → Send test event
# RevenueCat: Dashboard → Test webhook
```

- [ ] **7.1** 配置 Stripe Webhook
- [ ] **7.2** 配置 RevenueCat Webhook
- [ ] **7.3** 测试 Webhook 成功

### Phase 8: Final Verification

```bash
# 8.1 端到端测试
# - 使用测试 Google 账号登录
# - 创建 Solve session
# - 完成 5 步流程

# 8.2 验证 Sentry
# - 触发测试错误
# - 确认 Sentry 收到
```

- [ ] **8.1** 端到端流程测试通过
- [ ] **8.2** Sentry 错误追踪正常

---

## 3. Rollback Steps Checklist

### 3.1 Quick Rollback (部署问题)

```bash
# Vercel 回滚到上一版本
vercel rollback

# 验证
curl https://api.solacore.app/health
```

- [ ] 执行 `vercel rollback`
- [ ] 验证 /health 正常

### 3.2 Database Rollback (迁移问题)

```bash
# 回滚最近一次迁移
cd solacore-api
export DATABASE_URL="postgresql+asyncpg://..."
poetry run alembic downgrade -1

# 验证
poetry run alembic current
```

- [ ] 执行 `alembic downgrade -1`
- [ ] 验证当前 revision

### 3.3 Full Restore (严重问题)

```bash
# 1. 暂停服务（Vercel Dashboard → Pause）
# 2. 从 Neon 恢复到指定时间点
# 3. 重新部署已知正常版本
# 4. 恢复服务
# 5. 运行 smoke 测试
```

- [ ] 暂停服务
- [ ] 恢复数据库
- [ ] 重新部署
- [ ] 恢复服务
- [ ] 验证正常

---

## 4. Pre-Flight Summary

| 检查项 | 状态 |
|-------|------|
| Main 分支 CI 全绿 | ⬜ |
| 所有环境变量已准备 | ⬜ |
| 数据库实例已创建 | ⬜ |
| 域名 DNS 已配置 | ⬜ |
| Stripe/RevenueCat 账号就绪 | ⬜ |
| Sentry 项目已创建 | ⬜ |
| 团队已通知部署窗口 | ⬜ |

---

## 5. Smoke Test Results (本次验证)

**执行时间**: 2025-12-23 09:45 UTC+8
**环境**: 本地（无生产服务器）

| 测试项 | 结果 | 备注 |
|-------|------|------|
| 本地服务器检测 | ❌ | 服务器未运行 |
| /health | ⏭️ | 跳过（无服务器） |
| /health/ready | ⏭️ | 跳过（无服务器） |
| /health/live | ⏭️ | 跳过（无服务器） |

**结论**: 本地 smoke 无法执行，需在实际部署后运行 `./scripts/deploy_prod_smoke.sh https://api.solacore.app`

---

**下一步**: 按 Phase 1-8 顺序执行部署
