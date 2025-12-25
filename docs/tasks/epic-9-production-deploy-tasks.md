# Epic 9: Production Deployment - Task Checklist

**Version**: 1.0
**Created**: 2025-12-23
**Status**: Blocked - Waiting for Human Action

---

## ⚠️ BLOCKING NOTICE

**所有 Epic 9 任务都需要老板亲自操作** (购买服务器、域名、注册账号)

### 前置准备已完成 ✅
以下脚本和文档已就绪，等待老板提供生产环境：
- `deploy.sh` - 一键部署脚本
- `scripts/deploy_prod_smoke.sh` - Smoke 测试脚本
- `scripts/setup-ssl.sh` - SSL 配置脚本
- `DEPLOY_MANUAL.md` - 傻瓜式部署手册
- `docs/ENV_VARIABLES.md` - 环境变量文档
- `.github/workflows/deploy.yml` - CI/CD 流水线

### 老板需要做的事
1. **购买云服务器** (阿里云/Railway/Vercel) - ¥50-100/月
2. **购买域名** - ¥50-100/年
3. **注册 Apple Developer** (可选，iOS 上架需要) - $99/年

---

## Phase 1: Infrastructure Setup [HUMAN]

### 1.1 Database Provisioning [HUMAN]
- [ ] **Task 1.1.1 [HUMAN]**: Create PostgreSQL instance
  - Provider: Neon / Supabase / RDS
  - Region: US-East or EU-West
  - **Verification**: `psql $DATABASE_URL -c "SELECT 1"`
  - **Expected**: `1`

- [ ] **Task 1.1.2 [HUMAN]**: Configure connection pooling
  - Enable PgBouncer or equivalent
  - **Verification**: Check max_connections setting

- [ ] **Task 1.1.3 [HUMAN]**: Enable automated backups
  - Schedule: Daily, Retention: 7 days
  - **Verification**: Check backup settings in dashboard

### 1.2 Compute Deployment [HUMAN]
- [ ] **Task 1.2.1 [HUMAN]**: Create project on Vercel/Railway/Fly
  - Link GitHub repository
  - Set root directory: `solacore-api`
  - **Verification**: Project visible in dashboard

- [ ] **Task 1.2.2 [HUMAN]**: Configure build settings
  - Build: `pip install -r requirements.txt`
  - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - **Verification**: Successful build log

### 1.3 Domain & SSL [HUMAN]
- [ ] **Task 1.3.1 [HUMAN]**: Add custom domain `api.solacore.app`
  - **Verification**: `dig api.solacore.app`

- [ ] **Task 1.3.2 [HUMAN]**: Verify SSL certificate
  - **Verification**: `curl -I https://api.solacore.app`
  - **Expected**: HTTP/2 200, valid cert

---

## Phase 2: Environment Configuration [HUMAN]

- [ ] **Task 2.1.1 [HUMAN]**: Generate JWT secret
  - Command: `openssl rand -hex 32`

- [ ] **Task 2.1.2 [HUMAN]**: Set all environment variables
  - See `docs/ENV_VARIABLES.md`

- [ ] **Task 2.1.3 [HUMAN]**: Verify DEBUG=false

---

## Phase 3: Database Migration [HUMAN]

- [ ] **Task 3.1.1 [HUMAN]**: Create pre-migration backup
  - Command: `pg_dump $DATABASE_URL > backup.sql`

- [ ] **Task 3.1.2 [HUMAN]**: Run Alembic migrations
  - Command: `alembic upgrade head`
  - **Verification**: `alembic current`

- [ ] **Task 3.1.3 [HUMAN]**: Verify schema
  - Command: `psql $DATABASE_URL -c "\dt"`

---

## Phase 4: Webhook Configuration [HUMAN]

### 4.1 Stripe Webhook [HUMAN]
- [ ] **Task 4.1.1 [HUMAN]**: Create Stripe webhook endpoint
  - URL: `https://api.solacore.app/webhooks/stripe`

- [ ] **Task 4.1.2 [HUMAN]**: Copy webhook secret to env
  - Variable: `STRIPE_WEBHOOK_SECRET`

- [ ] **Task 4.1.3 [HUMAN]**: Send test event
  - **Verification**: Stripe dashboard → Send test webhook
  - **Expected**: 200 OK

### 4.2 RevenueCat Webhook [HUMAN]
- [ ] **Task 4.2.1 [HUMAN]**: Create RevenueCat webhook endpoint
  - URL: `https://api.solacore.app/webhooks/revenuecat`

- [ ] **Task 4.2.2 [HUMAN]**: Copy webhook secret to env

- [ ] **Task 4.2.3 [HUMAN]**: Send test event
  - **Expected**: 200 OK

---

## Phase 5: Smoke Testing [HUMAN]

- [ ] **Task 5.1.1 [HUMAN]**: Verify /health endpoint
  - Command: `curl https://api.solacore.app/health`
  - **Expected**: `{"status":"healthy","version":"1.0.0","database":"connected"}`

- [ ] **Task 5.1.2 [HUMAN]**: Verify /health/ready endpoint
  - **Expected**: `{"ready":true}`

- [ ] **Task 5.1.3 [HUMAN]**: Verify /health/live endpoint
  - **Expected**: `{"live":true}`

- [ ] **Task 5.2.1 [HUMAN]**: Run smoke script
  - Command: `./scripts/deploy_prod_smoke.sh https://api.solacore.app`

---

## Phase 6: Mobile Build [HUMAN]

- [ ] **Task 6.1.1 [HUMAN]**: Update version numbers in app.config.ts

- [ ] **Task 6.1.2 [HUMAN]**: Trigger production build
  - Command: `eas build --profile production --platform all`

- [ ] **Task 6.2.1 [HUMAN]**: Submit to App Store
  - Command: `eas submit --platform ios`

- [ ] **Task 6.2.2 [HUMAN]**: Submit to Google Play
  - Command: `eas submit --platform android`

---

## Phase 7: Go-Live Verification [HUMAN]

- [ ] **Task 7.1.1 [HUMAN]**: Test Google Sign In
- [ ] **Task 7.1.2 [HUMAN]**: Test Solve session flow
- [ ] **Task 7.1.3 [HUMAN]**: Test subscription UI
- [ ] **Task 7.2.1 [HUMAN]**: Verify Sentry integration
- [ ] **Task 7.2.2 [HUMAN]**: Verify uptime monitoring

---

## Completion Checklist

- [ ] Database provisioned and migrated
- [ ] Backend deployed to production
- [ ] Custom domain with SSL active
- [ ] All environment variables configured
- [ ] Stripe webhook working
- [ ] RevenueCat webhook working
- [ ] All health endpoints green
- [ ] Smoke tests pass
- [ ] Mobile builds submitted
- [ ] Sentry receiving errors
- [ ] PROGRESS.md updated

---

**Total Tasks**: ~30
**Estimated Duration**: 3 days
