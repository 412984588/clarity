# Epic 4: Subscription & Payment System - Specification

> **Version**: 1.0
> **Last Updated**: 2025-12-22
> **Status**: Draft
> **Scope**: Stripe Checkout + Webhooks + Subscription Management

---

## Overview

Epic 4 implements Stripe integration for subscription-based payments with tiered plans, webhook synchronization, and usage quota enforcement.

---

## Subscription Tiers

| Tier | Sessions | Price | Device Limit |
|------|----------|-------|--------------|
| **Free** | 10 lifetime | $0 | 1 |
| **Standard** | 100/month | $9.99/mo | 2 |
| **Pro** | Unlimited | $19.99/mo | 3 |

---

## API Endpoints

### 1. POST /subscriptions/checkout

Create a Stripe Checkout session for subscription.

**Request Headers:**
- `Authorization: Bearer <access_token>` (required)

**Request Body:**
```json
{
  "price_id": "price_standard_monthly"
}
```

**Response (200):**
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_xxx",
  "session_id": "cs_xxx"
}
```

**Error Codes:**
- `400 INVALID_PRICE_ID` - Unknown price ID
- `400 ALREADY_SUBSCRIBED` - User already has active subscription at this tier or higher

---

### 2. GET /subscriptions/portal

Get Stripe Customer Portal URL for managing subscription.

**Request Headers:**
- `Authorization: Bearer <access_token>` (required)

**Response (200):**
```json
{
  "portal_url": "https://billing.stripe.com/p/session/xxx"
}
```

**Error Codes:**
- `404 NO_SUBSCRIPTION` - User has no paid subscription history

---

### 3. GET /subscriptions/current

Get current subscription status.

**Request Headers:**
- `Authorization: Bearer <access_token>` (required)

**Response (200):**
```json
{
  "tier": "standard",
  "status": "active",
  "current_period_start": "2025-12-01T00:00:00Z",
  "current_period_end": "2026-01-01T00:00:00Z",
  "cancel_at_period_end": false
}
```

---

### 4. GET /subscriptions/usage

Get current usage statistics.

**Request Headers:**
- `Authorization: Bearer <access_token>` (required)

**Response (200):**
```json
{
  "tier": "free",
  "sessions_used": 7,
  "sessions_limit": 10,
  "period_start": "2025-12-01T00:00:00Z",
  "period_end": null,
  "is_lifetime": true
}
```

For paid tiers:
```json
{
  "tier": "standard",
  "sessions_used": 45,
  "sessions_limit": 100,
  "period_start": "2025-12-01T00:00:00Z",
  "period_end": "2026-01-01T00:00:00Z",
  "is_lifetime": false
}
```

---

### 5. POST /webhooks/stripe

Stripe webhook endpoint (no auth, signature verified).

**Request Headers:**
- `Stripe-Signature: t=xxx,v1=xxx` (required)

**Handled Events:**

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Create/upgrade subscription |
| `invoice.paid` | Renew subscription, reset usage counter |
| `invoice.payment_failed` | Mark subscription as `past_due` |
| `customer.subscription.deleted` | Downgrade to free tier |

**Response (200):**
```json
{"received": true}
```

---

## Data Model Updates

### Subscription Table (Update)

```sql
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS cancel_at_period_end BOOLEAN DEFAULT FALSE;
```

Already has: tier, status, stripe_customer_id, stripe_subscription_id, current_period_start, current_period_end

### Usage Table

Already exists with: user_id, period_start, session_count

---

## Stripe Configuration

### Environment Variables

```bash
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_STANDARD=price_xxx
STRIPE_PRICE_PRO=price_xxx
STRIPE_SUCCESS_URL=https://api.solacore.app/subscriptions/success?session_id={CHECKOUT_SESSION_ID}
STRIPE_CANCEL_URL=https://api.solacore.app/subscriptions/cancel
```

### Stripe Products (Dashboard Setup)

1. **Standard Plan** - $9.99/month recurring
2. **Pro Plan** - $19.99/month recurring

---

## Webhook Security

1. Verify `Stripe-Signature` header using `stripe.Webhook.construct_event()`
2. Reject requests with invalid signatures (400)
3. Idempotency: Track processed event IDs to prevent duplicate handling
4. Log all webhook events for debugging

---

## Usage Quota Logic

### Free Tier
- 10 sessions **lifetime** (not per month)
- No reset on any event
- Block at limit with upgrade prompt

### Standard Tier
- 100 sessions per **billing period**
- Reset to 0 on `invoice.paid` webhook
- Warn at 80%, soft block at 100% (allow finish current session)

### Pro Tier
- Unlimited sessions
- No tracking needed (but still track for analytics)

---

## Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `INVALID_PRICE_ID` | 400 | Price ID not recognized |
| `ALREADY_SUBSCRIBED` | 400 | Already has this tier or higher |
| `NO_SUBSCRIPTION` | 404 | No paid subscription history |
| `QUOTA_EXCEEDED` | 403 | Session limit reached |
| `PAYMENT_FAILED` | 402 | Subscription payment failed |
| `SUBSCRIPTION_CANCELED` | 403 | Subscription was canceled |

---

## Upgrade Flow

```
User creates session → Check quota →
  If exceeded → Return 403 QUOTA_EXCEEDED with:
    {
      "error": "QUOTA_EXCEEDED",
      "usage": {"used": 10, "limit": 10, "tier": "free"},
      "upgrade_url": "/subscriptions/checkout"
    }
```

---

## Testing Strategy

1. **Checkout Session Creation** - Mock Stripe API
2. **Webhook Handling** - Send mock events with valid structure
3. **Usage Tracking** - Verify counts increment correctly
4. **Quota Enforcement** - Test blocking at limit

---

## Out of Scope (Future)

- Org/Team seats billing
- Annual plans
- Promo codes
- Usage-based billing (per AI token)
- Mobile in-app purchases (Apple/Google)

---

## Change Log

| Date | Version | Description |
|------|---------|-------------|
| 2025-12-22 | 1.0 | Initial specification |
