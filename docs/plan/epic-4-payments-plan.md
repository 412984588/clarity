# Epic 4: Subscription & Payment System - Implementation Plan

> **Based on**: docs/spec/epic-4-payments.md
> **Created**: 2025-12-22

---

## Implementation Phases

### Phase 1: Configuration & Dependencies

1. Add `stripe` to Poetry dependencies
2. Update `app/config.py` with Stripe settings
3. Update `.env.example` with Stripe environment variables
4. Add `cancel_at_period_end` column to subscriptions table (if not exists)

### Phase 2: Stripe Service

1. Create `app/services/stripe_service.py`:
   - `create_checkout_session(user_id, price_id)` → checkout URL
   - `create_portal_session(customer_id)` → portal URL
   - `verify_webhook_signature(payload, signature)` → event
   - `sync_subscription(event)` → update DB

### Phase 3: Subscription Router

1. Create `app/routers/subscriptions.py`:
   - `POST /subscriptions/checkout` - Create checkout session
   - `GET /subscriptions/portal` - Get portal URL
   - `GET /subscriptions/current` - Get subscription status
   - `GET /subscriptions/usage` - Get usage stats

2. Register router in `app/main.py`

### Phase 4: Webhook Handler

1. Create `app/routers/webhooks.py`:
   - `POST /webhooks/stripe` - Handle Stripe events
   - Verify signature before processing
   - Handle: checkout.session.completed, invoice.paid, invoice.payment_failed, customer.subscription.deleted

2. Register router in `app/main.py`

### Phase 5: Usage Integration

1. Update usage tracking in `app/routers/sessions.py`:
   - Check quota before session creation
   - Return QUOTA_EXCEEDED with upgrade info

2. Reset usage counter on `invoice.paid` event

### Phase 6: Testing

1. Create `tests/test_subscriptions.py`:
   - Checkout session creation (mock Stripe)
   - Portal URL generation
   - Current subscription endpoint
   - Usage endpoint

2. Create `tests/test_webhooks.py`:
   - Webhook signature verification
   - Event handling for each type
   - Subscription state transitions

---

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` | Modify | Add stripe dependency |
| `app/config.py` | Modify | Add Stripe settings |
| `.env.example` | Modify | Add Stripe env vars |
| `app/services/stripe_service.py` | Create | Stripe integration |
| `app/routers/subscriptions.py` | Create | Subscription endpoints |
| `app/routers/webhooks.py` | Create | Webhook handler |
| `app/schemas/subscription.py` | Create | Request/Response schemas |
| `app/main.py` | Modify | Register new routers |
| `app/routers/sessions.py` | Modify | Quota check integration |
| `tests/test_subscriptions.py` | Create | Subscription tests |
| `tests/test_webhooks.py` | Create | Webhook tests |

---

## Technical Decisions

### Stripe API Version
Use latest stable: `2024-12-18.acacia`

### Webhook Idempotency
Store processed event IDs in memory (single server) or use Stripe's built-in idempotency.

### Price IDs
Map config price IDs to tiers:
```python
PRICE_TO_TIER = {
    settings.stripe_price_standard: "standard",
    settings.stripe_price_pro: "pro",
}
```

### Usage Reset Logic
- Free: Never reset (lifetime)
- Standard/Pro: Reset on `invoice.paid` event

---

## Error Handling

1. Stripe API errors → Log and return 500
2. Invalid webhook signature → Return 400
3. Unknown price ID → Return 400 INVALID_PRICE_ID
4. No Stripe customer → Create one on first checkout

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Webhook delivery failure | High | Stripe retries, log for manual sync |
| Race condition on checkout | Medium | Idempotency key in checkout call |
| Usage counter drift | Low | Reconcile on invoice.paid |

---

## Success Criteria

- [ ] Checkout session creates valid Stripe URL
- [ ] Webhook processes all 4 event types correctly
- [ ] Subscription status syncs to DB
- [ ] Usage resets on renewal
- [ ] Quota enforcement blocks at limit
- [ ] All tests pass (ruff, mypy, pytest)
