# Epic 4: Subscription & Payment System - Tasks

> **Based on**: docs/plan/epic-4-payments-plan.md
> **Created**: 2025-12-22

---

## Task Checklist

### Phase 1: Configuration & Dependencies

- [ ] **T1.1** Add `stripe>=11.0.0` to `pyproject.toml`
- [ ] **T1.2** Run `poetry lock && poetry install`
- [ ] **T1.3** Add Stripe settings to `app/config.py`:
  - `stripe_secret_key`
  - `stripe_webhook_secret`
  - `stripe_price_standard`
  - `stripe_price_pro`
  - `stripe_success_url`
  - `stripe_cancel_url`
- [ ] **T1.4** Update `.env.example` with Stripe variables

### Phase 2: Schemas

- [ ] **T2.1** Create `app/schemas/subscription.py`:
  - `CheckoutRequest(price_id: str)`
  - `CheckoutResponse(checkout_url: str, session_id: str)`
  - `PortalResponse(portal_url: str)`
  - `SubscriptionResponse(tier, status, period_start, period_end, cancel_at_period_end)`
  - `UsageResponse(tier, sessions_used, sessions_limit, period_start, period_end, is_lifetime)`

### Phase 3: Stripe Service

- [ ] **T3.1** Create `app/services/stripe_service.py`
- [ ] **T3.2** Implement `create_checkout_session(user, price_id)`:
  - Get or create Stripe customer
  - Create checkout session (mode=subscription)
  - Return checkout URL
- [ ] **T3.3** Implement `create_portal_session(customer_id)`:
  - Create billing portal session
  - Return portal URL
- [ ] **T3.4** Implement `verify_webhook(payload, signature)`:
  - Use `stripe.Webhook.construct_event()`
  - Return parsed event or raise

### Phase 4: Subscription Router

- [ ] **T4.1** Create `app/routers/subscriptions.py`
- [ ] **T4.2** Implement `POST /subscriptions/checkout`:
  - Validate price_id
  - Check not already subscribed at tier
  - Create checkout session
  - Return URL
- [ ] **T4.3** Implement `GET /subscriptions/portal`:
  - Check user has stripe_customer_id
  - Create portal session
  - Return URL
- [ ] **T4.4** Implement `GET /subscriptions/current`:
  - Return subscription details
- [ ] **T4.5** Implement `GET /subscriptions/usage`:
  - Return usage stats with tier context
- [ ] **T4.6** Register router in `app/main.py`

### Phase 5: Webhook Handler

- [ ] **T5.1** Create `app/routers/webhooks.py`
- [ ] **T5.2** Implement `POST /webhooks/stripe`:
  - Read raw body
  - Verify signature
  - Route to handler by event type
- [ ] **T5.3** Handle `checkout.session.completed`:
  - Extract customer_id, subscription_id
  - Update user subscription in DB
- [ ] **T5.4** Handle `invoice.paid`:
  - Update period dates
  - Reset usage counter (if not free tier)
- [ ] **T5.5** Handle `invoice.payment_failed`:
  - Mark subscription as `past_due`
- [ ] **T5.6** Handle `customer.subscription.deleted`:
  - Downgrade to free tier
- [ ] **T5.7** Register router in `app/main.py`

### Phase 6: Integration

- [ ] **T6.1** Update quota check in `app/routers/sessions.py`:
  - Return structured QUOTA_EXCEEDED error
  - Include upgrade info in response

### Phase 7: Testing

- [ ] **T7.1** Create `tests/test_subscriptions.py`:
  - Test checkout endpoint (mock Stripe)
  - Test portal endpoint
  - Test current subscription endpoint
  - Test usage endpoint
- [ ] **T7.2** Create `tests/test_webhooks.py`:
  - Test signature verification
  - Test checkout.session.completed handling
  - Test invoice.paid handling
  - Test payment_failed handling
  - Test subscription.deleted handling

### Phase 8: Validation

- [ ] **T8.1** Run `poetry run ruff check .`
- [ ] **T8.2** Run `poetry run mypy app --ignore-missing-imports`
- [ ] **T8.3** Run `poetry run pytest -v`
- [ ] **T8.4** Run mobile `npm run lint && npx tsc --noEmit`

---

## Estimated Complexity

| Phase | Tasks | Complexity |
|-------|-------|------------|
| Config | 4 | Low |
| Schemas | 1 | Low |
| Stripe Service | 4 | Medium |
| Subscription Router | 6 | Medium |
| Webhook Handler | 7 | Medium |
| Integration | 1 | Low |
| Testing | 2 | Medium |
| Validation | 4 | Low |

**Total**: 29 tasks
