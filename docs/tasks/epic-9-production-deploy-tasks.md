# Epic 9: Production Deployment - Task Checklist

**Version**: 1.0
**Created**: 2025-12-23
**Status**: In Progress

---

## Phase 1: Infrastructure Setup

### 1.1 Database Provisioning
- [ ] **Task 1.1.1**: Create PostgreSQL instance
  - Provider: Neon / Supabase / RDS
  - Region: US-East or EU-West
  - **Verification**: `psql $DATABASE_URL -c "SELECT 1"`
  - **Expected**: `1`

- [ ] **Task 1.1.2**: Configure connection pooling
  - Enable PgBouncer or equivalent
  - **Verification**: Check max_connections setting

- [ ] **Task 1.1.3**: Enable automated backups
  - Schedule: Daily, Retention: 7 days
  - **Verification**: Check backup settings in dashboard

### 1.2 Compute Deployment
- [ ] **Task 1.2.1**: Create project on Vercel/Railway/Fly
  - Link GitHub repository
  - Set root directory: `clarity-api`
  - **Verification**: Project visible in dashboard

- [ ] **Task 1.2.2**: Configure build settings
  - Build: `pip install -r requirements.txt`
  - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - **Verification**: Successful build log

### 1.3 Domain & SSL
- [ ] **Task 1.3.1**: Add custom domain `api.clarity.app`
  - **Verification**: `dig api.clarity.app`

- [ ] **Task 1.3.2**: Verify SSL certificate
  - **Verification**: `curl -I https://api.clarity.app`
  - **Expected**: HTTP/2 200, valid cert

---

## Phase 2: Environment Configuration

- [ ] **Task 2.1.1**: Generate JWT secret
  - Command: `openssl rand -hex 32`

- [ ] **Task 2.1.2**: Set all environment variables
  - See `docs/ENV_VARIABLES.md`

- [ ] **Task 2.1.3**: Verify DEBUG=false

---

## Phase 3: Database Migration

- [ ] **Task 3.1.1**: Create pre-migration backup
  - Command: `pg_dump $DATABASE_URL > backup.sql`

- [ ] **Task 3.1.2**: Run Alembic migrations
  - Command: `alembic upgrade head`
  - **Verification**: `alembic current`

- [ ] **Task 3.1.3**: Verify schema
  - Command: `psql $DATABASE_URL -c "\dt"`

---

## Phase 4: Webhook Configuration

### 4.1 Stripe Webhook
- [ ] **Task 4.1.1**: Create Stripe webhook endpoint
  - URL: `https://api.clarity.app/webhooks/stripe`

- [ ] **Task 4.1.2**: Copy webhook secret to env
  - Variable: `STRIPE_WEBHOOK_SECRET`

- [ ] **Task 4.1.3**: Send test event
  - **Verification**: Stripe dashboard → Send test webhook
  - **Expected**: 200 OK

### 4.2 RevenueCat Webhook
- [ ] **Task 4.2.1**: Create RevenueCat webhook endpoint
  - URL: `https://api.clarity.app/webhooks/revenuecat`

- [ ] **Task 4.2.2**: Copy webhook secret to env

- [ ] **Task 4.2.3**: Send test event
  - **Expected**: 200 OK

---

## Phase 5: Smoke Testing

- [ ] **Task 5.1.1**: Verify /health endpoint
  - Command: `curl https://api.clarity.app/health`
  - **Expected**: `{"status":"healthy","version":"1.0.0","database":"connected"}`

- [ ] **Task 5.1.2**: Verify /health/ready endpoint
  - **Expected**: `{"ready":true}`

- [ ] **Task 5.1.3**: Verify /health/live endpoint
  - **Expected**: `{"live":true}`

- [ ] **Task 5.2.1**: Run smoke script
  - Command: `./scripts/deploy_prod_smoke.sh https://api.clarity.app`

---

## Phase 6: Mobile Build

- [ ] **Task 6.1.1**: Update version numbers in app.config.ts

- [ ] **Task 6.1.2**: Trigger production build
  - Command: `eas build --profile production --platform all`

- [ ] **Task 6.2.1**: Submit to App Store
  - Command: `eas submit --platform ios`

- [ ] **Task 6.2.2**: Submit to Google Play
  - Command: `eas submit --platform android`

---

## Phase 7: Go-Live Verification

- [ ] **Task 7.1.1**: Test Google Sign In
- [ ] **Task 7.1.2**: Test Solve session flow
- [ ] **Task 7.1.3**: Test subscription UI
- [ ] **Task 7.2.1**: Verify Sentry integration
- [ ] **Task 7.2.2**: Verify uptime monitoring

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
