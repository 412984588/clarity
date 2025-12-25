# Epic 9: Production Deployment Specification

**Version**: 1.0
**Created**: 2025-12-23
**Status**: In Progress

---

## Overview

Epic 9 covers the complete production deployment of Solacore, including:
- Backend API deployment
- Database provisioning and migration
- Mobile app store submission preparation
- Webhook configuration (Stripe + RevenueCat)
- Monitoring and alerting setup
- Backup and disaster recovery

---

## Infrastructure Requirements

### Backend API

| Component | Provider | Specification |
|-----------|----------|---------------|
| Compute | Vercel / Railway / Fly.io | Auto-scaling, min 1 instance |
| Domain | Custom | `api.solacore.app` |
| SSL | Provider-managed | Auto-renewed TLS 1.3 |
| Region | US-East / EU-West | Low latency to target users |

### Database

| Component | Provider | Specification |
|-----------|----------|---------------|
| PostgreSQL | Neon / Supabase / RDS | PostgreSQL 15+ |
| Connection | Pooled | PgBouncer or equivalent |
| Backup | Automated | Daily snapshots, 7-day retention |
| Size | Starter | 1GB initial, auto-scale |

### Mobile

| Platform | Store | Requirements |
|----------|-------|--------------|
| iOS | App Store | Apple Developer ($99/yr) |
| Android | Google Play | Google Play Console ($25 one-time) |
| Build | EAS Build | Production profile |

---

## Environment Configuration

### Required Production Variables

```bash
# Core
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/solacore_prod
JWT_SECRET=<256-bit-random-hex>

# OAuth
GOOGLE_CLIENT_ID=<production-google-client-id>
APPLE_CLIENT_ID=com.solacore.app

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-prod-xxx
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT=30
LLM_MAX_TOKENS=1024

# Stripe (Production)
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_STANDARD=price_xxx
STRIPE_PRICE_PRO=price_xxx
STRIPE_SUCCESS_URL=https://api.solacore.app/subscriptions/success?session_id={CHECKOUT_SESSION_ID}
STRIPE_CANCEL_URL=https://api.solacore.app/subscriptions/cancel

# RevenueCat
REVENUECAT_WEBHOOK_SECRET=whsec_xxx
REVENUECAT_ENTITLEMENT_STANDARD=standard_access
REVENUECAT_ENTITLEMENT_PRO=pro_access

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
APP_VERSION=1.0.0
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All CI checks green on main
- [ ] Database backup created
- [ ] Environment variables configured
- [ ] DNS records ready (api.solacore.app → provider)
- [ ] SSL certificate provisioned
- [ ] Stripe webhook endpoint registered
- [ ] RevenueCat webhook endpoint registered

### Deployment Steps

1. **Database**: Create production PostgreSQL instance
2. **Migrate**: Run `alembic upgrade head`
3. **Deploy**: Push to production (Vercel/Railway/Fly)
4. **Verify**: Run smoke tests
5. **Webhooks**: Configure and verify
6. **Monitor**: Enable Sentry + alerts

### Post-Deployment

- [ ] `/health` returns `{"status":"healthy","version":"1.0.0","database":"connected"}`
- [ ] `/health/ready` returns `{"ready":true}`
- [ ] `/health/live` returns `{"live":true}`
- [ ] Stripe webhook test event succeeds
- [ ] RevenueCat webhook test event succeeds
- [ ] Error tracking active in Sentry

---

## Webhook Configuration

### Stripe Webhook

**Endpoint**: `https://api.solacore.app/webhooks/stripe`

**Events to subscribe**:
- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`

**Verification**:
```bash
curl -X POST https://api.solacore.app/webhooks/stripe \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: test" \
  -d '{"type":"test"}'
# Expected: 400 (invalid signature) - endpoint is reachable
```

### RevenueCat Webhook

**Endpoint**: `https://api.solacore.app/webhooks/revenuecat`

**Events**:
- `INITIAL_PURCHASE`
- `RENEWAL`
- `CANCELLATION`
- `EXPIRATION`

**Verification**:
```bash
curl -X POST https://api.solacore.app/webhooks/revenuecat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $REVENUECAT_WEBHOOK_SECRET" \
  -d '{"event":{"type":"TEST"}}'
# Expected: 200 or 400 (endpoint is reachable)
```

---

## Rollback Procedure

### Immediate Rollback (< 5 min)

```bash
# 1. Revert deployment
# Vercel: vercel rollback
# Railway: railway rollback
# Fly: fly releases rollback

# 2. Verify health
curl https://api.solacore.app/health

# 3. If database migration issue
cd solacore-api
poetry run alembic downgrade -1
```

### Extended Rollback (> 5 min)

1. Communicate outage to users
2. Restore database from backup if needed
3. Redeploy previous known-good version
4. Run full smoke test suite
5. Post-incident review

---

## Monitoring & Alerts

### Health Checks

| Endpoint | Interval | Timeout | Alert |
|----------|----------|---------|-------|
| `/health` | 30s | 5s | If != healthy for 2 checks |
| `/health/ready` | 30s | 5s | If 503 for 3 checks |
| `/health/live` | 30s | 5s | If non-200 for 5 checks |

### Error Tracking

- **Sentry**: All unhandled exceptions
- **Alert**: > 10 errors/minute
- **P0**: Any error in auth/payment flows

---

## Acceptance Criteria

| Item | Verification Command | Expected Output |
|------|---------------------|-----------------|
| Health | `curl https://api.solacore.app/health` | `{"status":"healthy","version":"1.0.0","database":"connected"}` |
| Ready | `curl https://api.solacore.app/health/ready` | `{"ready":true}` |
| Live | `curl https://api.solacore.app/health/live` | `{"live":true}` |
| Stripe WH | Stripe Dashboard → Send test event | 200 OK |
| RevenueCat WH | RevenueCat Dashboard → Send test event | 200 OK |
| Auth | POST /auth/google with valid token | 200 + JWT |
| Sentry | Trigger test error | Error appears in dashboard |
