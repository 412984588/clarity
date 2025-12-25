# Production Deployment Runbook

**Version**: 1.0
**Last Updated**: 2025-12-23

Step-by-step guide for deploying Solacore to production.

---

## Prerequisites

- [ ] GitHub repository access
- [ ] Provider account (Vercel/Railway/Fly)
- [ ] PostgreSQL provider account (Neon/Supabase/RDS)
- [ ] Stripe account (live mode enabled)
- [ ] RevenueCat account
- [ ] Apple Developer account ($99/yr)
- [ ] Google Play Console account ($25)
- [ ] Domain: `api.solacore.app` DNS access

---

## Step 1: Database Setup

### 1.1 Create PostgreSQL Instance

**Neon (recommended)**:
```bash
# Via Neon Console: https://console.neon.tech
# 1. Create new project: "solacore-prod"
# 2. Region: us-east-1 or eu-central-1
# 3. Copy connection string
```

**Verification**:
```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@ep-xxx.us-east-1.aws.neon.tech/solacore"
psql $DATABASE_URL -c "SELECT 1"
```
**Expected**: `1`

### 1.2 Enable Backups

```bash
# Neon: Automatic (point-in-time recovery included)
# Supabase: Dashboard → Database → Backups → Enable
# RDS: Enable automated backups in console
```

---

## Step 2: Generate Secrets

### 2.1 JWT Secret

```bash
openssl rand -hex 32
```
**Expected**: 64-character hex string (save this!)

### 2.2 Collect All Secrets

| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Step 1.1 |
| `JWT_SECRET` | Step 2.1 |
| `GOOGLE_CLIENT_ID` | Google Cloud Console |
| `APPLE_CLIENT_ID` | Apple Developer Portal |
| `OPENAI_API_KEY` | OpenAI Platform |
| `STRIPE_SECRET_KEY` | Stripe Dashboard (Live) |
| `STRIPE_WEBHOOK_SECRET` | Step 5.1 |
| `REVENUECAT_WEBHOOK_SECRET` | Step 5.2 |
| `SENTRY_DSN` | Sentry Project |

---

## Step 3: Deploy Backend

### 3.1 Vercel Deployment

```bash
npm i -g vercel
vercel login
cd solacore-api
vercel --prod

# Set environment variables
vercel env add DATABASE_URL production
vercel env add JWT_SECRET production
# ... repeat for all
```

### 3.2 Railway Deployment (Alternative)

```bash
npm i -g @railway/cli
railway login
cd solacore-api
railway init
railway up
```

### 3.3 Fly.io Deployment (Alternative)

```bash
brew install flyctl
fly auth login
cd solacore-api
fly launch
fly deploy
fly secrets set DATABASE_URL="..." JWT_SECRET="..."
```

**Verification**:
```bash
curl https://api.solacore.app/health
```
**Expected**: `{"status":"healthy","version":"1.0.0","database":"connected"}`

---

## Step 4: Run Database Migration

```bash
cd solacore-api
export DATABASE_URL="postgresql+asyncpg://..."
poetry run alembic upgrade head
```

**Verification**:
```bash
poetry run alembic current
```

---

## Step 5: Configure Webhooks

### 5.1 Stripe Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://api.solacore.app/webhooks/stripe`
3. Select events: checkout.session.completed, customer.subscription.*
4. Copy "Signing secret" → `STRIPE_WEBHOOK_SECRET`

**Verification**: Send test event from dashboard
**Expected**: 200 OK

### 5.2 RevenueCat Webhook

1. Go to https://app.revenuecat.com → Settings → Webhooks
2. Add endpoint: `https://api.solacore.app/webhooks/revenuecat`
3. Copy secret → `REVENUECAT_WEBHOOK_SECRET`

**Verification**: Test webhook from dashboard
**Expected**: 200 OK

---

## Step 6: Smoke Test

```bash
./scripts/deploy_prod_smoke.sh https://api.solacore.app
```

**Expected Output**:
```
✅ /health - healthy
✅ /health/ready - ready
✅ /health/live - live
✅ All smoke tests passed!
```

---

## Step 7: Mobile Production Build

```bash
cd solacore-mobile
eas build --profile production --platform all
eas submit --platform ios
eas submit --platform android
```

---

## Step 8: Monitoring Setup

1. Create Sentry project
2. Copy DSN → `SENTRY_DSN`
3. Update env var
4. Verify with test error

---

## Rollback Procedure

### Quick Rollback
```bash
vercel rollback  # or railway rollback / fly releases rollback
```

### Database Rollback
```bash
poetry run alembic downgrade -1
```

---

## Post-Deployment Checklist

- [ ] `/health` returns healthy
- [ ] Stripe webhook test succeeds
- [ ] RevenueCat webhook test succeeds
- [ ] Mobile builds submitted
- [ ] Sentry receiving errors
