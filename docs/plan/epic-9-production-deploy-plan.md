# Epic 9: Production Deployment Plan

**Version**: 1.0
**Created**: 2025-12-23

---

## Implementation Phases

### Phase 1: Infrastructure Setup (Day 1)

**Goal**: Provision production infrastructure

1. **Database**
   - Create PostgreSQL instance (Neon/Supabase/RDS)
   - Configure connection pooling
   - Set up automated backups
   - Note connection string for `DATABASE_URL`

2. **Compute**
   - Create Vercel/Railway/Fly project
   - Link to GitHub repository
   - Configure build command: `cd clarity-api && pip install -r requirements.txt`
   - Configure start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Domain & SSL**
   - Add custom domain `api.clarity.app`
   - Verify SSL certificate provisioned
   - Test HTTPS access

---

### Phase 2: Environment Configuration (Day 1)

**Goal**: Configure all production secrets

1. **Core Secrets**
   ```bash
   # Generate JWT secret
   openssl rand -hex 32
   ```

2. **Set Environment Variables**
   - Via provider dashboard or CLI
   - All variables from `docs/ENV_VARIABLES.md`
   - Double-check `DEBUG=false`

3. **Verify Configuration**
   ```bash
   # Deploy should pick up new env vars
   # Verify via /health endpoint
   ```

---

### Phase 3: Database Migration (Day 1)

**Goal**: Initialize production database

1. **Pre-Migration Backup**
   ```bash
   # For existing data (if any)
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
   ```

2. **Run Migrations**
   ```bash
   cd clarity-api
   DATABASE_URL=$PROD_DATABASE_URL poetry run alembic upgrade head
   ```

3. **Verify Schema**
   ```bash
   # Connect to prod DB and verify tables
   psql $DATABASE_URL -c "\dt"
   ```

---

### Phase 4: Webhook Configuration (Day 2)

**Goal**: Set up payment webhooks

1. **Stripe Webhook**
   - Go to: https://dashboard.stripe.com/webhooks
   - Add endpoint: `https://api.clarity.app/webhooks/stripe`
   - Select events (see spec)
   - Copy webhook secret → `STRIPE_WEBHOOK_SECRET`

2. **RevenueCat Webhook**
   - Go to: https://app.revenuecat.com → Settings → Webhooks
   - Add endpoint: `https://api.clarity.app/webhooks/revenuecat`
   - Copy secret → `REVENUECAT_WEBHOOK_SECRET`

3. **Test Webhooks**
   - Stripe: Send test event from dashboard
   - RevenueCat: Send test event from dashboard

---

### Phase 5: Smoke Testing (Day 2)

**Goal**: Verify production deployment

1. **Run Smoke Script**
   ```bash
   ./scripts/deploy_prod_smoke.sh https://api.clarity.app
   ```

2. **Manual Verification**
   - [ ] `/health` returns healthy
   - [ ] `/health/ready` returns ready
   - [ ] `/health/live` returns live
   - [ ] Auth endpoints respond (401 without token)
   - [ ] Webhook endpoints respond

3. **Error Tracking**
   - Trigger test error
   - Verify appears in Sentry

---

### Phase 6: Mobile Build (Day 3)

**Goal**: Build production mobile apps

1. **Update Version**
   ```bash
   cd clarity-mobile
   # Update app.config.ts version
   ```

2. **Production Build**
   ```bash
   eas build --profile production --platform all
   ```

3. **Submit to Stores**
   ```bash
   eas submit --platform ios
   eas submit --platform android
   ```

---

### Phase 7: Go-Live Verification (Day 3)

**Goal**: Final production verification

1. **Full User Flow Test**
   - Sign in with Google
   - Create solve session
   - Complete 5-step flow
   - Verify subscription UI

2. **Monitoring Active**
   - Sentry receiving events
   - Health checks green
   - No error spikes

3. **Documentation**
   - Update PROGRESS.md
   - Mark Epic 9 complete

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Database migration fails | Test on staging first, have rollback ready |
| Webhook signature mismatch | Verify secret copied correctly, test before go-live |
| SSL certificate issues | Use provider-managed SSL, verify before DNS switch |
| LLM API rate limits | Start with conservative limits, monitor usage |
| App store rejection | Review guidelines, have backup submission plan |

---

## Success Criteria

- [ ] All health endpoints return expected responses
- [ ] Stripe webhook test succeeds
- [ ] RevenueCat webhook test succeeds
- [ ] Auth flow works end-to-end
- [ ] Solve session flow works end-to-end
- [ ] Error tracking captures test error
- [ ] Mobile builds submitted to stores
