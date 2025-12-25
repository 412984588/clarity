# Environment Variables Reference

**Version**: 1.0
**Last Updated**: 2025-12-24

This document lists all environment variables used by the Solacore API.

---

## Quick Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DEBUG` | Yes | Enable debug mode (set `false` in production) |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET` | Yes | JWT signing secret |
| `BETA_MODE` | No | Enable free beta mode with relaxed limits |
| `PAYMENTS_ENABLED` | No | Enable payment features (Stripe/RevenueCat) |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth Client ID |
| `APPLE_CLIENT_ID` | Yes | Apple Sign In Client ID |
| `LLM_PROVIDER` | Yes | LLM provider (`openai`, `anthropic`, `openrouter`) |
| `OPENAI_API_KEY` | Conditional | Required if `LLM_PROVIDER=openai` |
| `ANTHROPIC_API_KEY` | Conditional | Required if `LLM_PROVIDER=anthropic` |
| `OPENROUTER_API_KEY` | Conditional | Required if `LLM_PROVIDER=openrouter` |
| `OPENROUTER_REASONING_FALLBACK` | No | Use reasoning tokens if OpenRouter content is empty |
| `STRIPE_SECRET_KEY` | Conditional | Required if `PAYMENTS_ENABLED=true` |
| `STRIPE_WEBHOOK_SECRET` | Conditional | Required if `PAYMENTS_ENABLED=true` |
| `REVENUECAT_WEBHOOK_SECRET` | Conditional | Required if `PAYMENTS_ENABLED=true` |

---

## Detailed Configuration

### Core Settings

#### `DEBUG`
- **Required**: Yes
- **Default**: `true`
- **Production**: Must be `false`
- **Description**: Enables debug mode with detailed error messages and CORS wildcard

```bash
DEBUG=false
```

#### `DATABASE_URL`
- **Required**: Yes
- **Format**: `postgresql+asyncpg://user:password@host:port/database`
- **Description**: PostgreSQL connection string using asyncpg driver

```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/solacore
```

#### `JWT_SECRET`
- **Required**: Yes
- **Description**: Secret key for signing JWT tokens
- **Generate**: `openssl rand -hex 32`

```bash
JWT_SECRET=your-256-bit-secret-key
```

#### `HOST` / `PORT`
- **Required**: No
- **Default**: `0.0.0.0:8000`
- **Description**: Server binding address

---

### Free Beta Mode

#### `BETA_MODE`
- **Required**: No
- **Default**: `false`
- **Description**: Enable free beta mode with relaxed device and session limits
- **When to use**: For testing with friends/early testers before production launch
- **Effects**:
  - Device limit increased from 3 to 10
  - Session limits removed (unlimited sessions)
  - No payment enforcement
- **Production**: Must be `false`

```bash
BETA_MODE=true
```

#### `PAYMENTS_ENABLED`
- **Required**: No
- **Default**: `true`
- **Description**: Enable payment features (Stripe/RevenueCat endpoints)
- **When to use**: Set to `false` for free beta testing without payment infrastructure
- **Effects**:
  - When `false`: All payment endpoints return `501 Not Implemented`
  - When `true`: Full Stripe and RevenueCat integration
- **Production**: Must be `true` for monetization

```bash
PAYMENTS_ENABLED=false
```

**Note**: For free beta testing, typically set `BETA_MODE=true` and `PAYMENTS_ENABLED=false`. This allows early testers to use the app without payment flows while providing relaxed usage limits.

---

### OAuth Configuration

#### `GOOGLE_CLIENT_ID`
- **Required**: Yes
- **Source**: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- **Description**: Client ID for Google Sign-In

```bash
GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
```

#### `APPLE_CLIENT_ID`
- **Required**: Yes
- **Source**: [Apple Developer Portal](https://developer.apple.com/account/resources/identifiers)
- **Description**: Bundle ID for Apple Sign In

```bash
APPLE_CLIENT_ID=com.yourcompany.solacore
```

---

### LLM Configuration

#### `LLM_PROVIDER`
- **Required**: Yes
- **Values**: `openai` | `anthropic` | `openrouter`
- **Description**: Which LLM provider to use

#### `OPENAI_API_KEY`
- **Required**: If `LLM_PROVIDER=openai`
- **Source**: [OpenAI Platform](https://platform.openai.com/api-keys)

#### `ANTHROPIC_API_KEY`
- **Required**: If `LLM_PROVIDER=anthropic`
- **Source**: [Anthropic Console](https://console.anthropic.com/settings/keys)

#### `OPENROUTER_API_KEY`
- **Required**: If `LLM_PROVIDER=openrouter`
- **Source**: [OpenRouter Keys](https://openrouter.ai/keys)

#### `OPENROUTER_BASE_URL`
- **Required**: No
- **Default**: `https://openrouter.ai/api/v1`
- **Description**: OpenRouter base URL

#### `OPENROUTER_APP_NAME`
- **Required**: No
- **Description**: Optional app name header for OpenRouter

#### `OPENROUTER_REFERER`
- **Required**: No
- **Description**: Optional HTTP referer header for OpenRouter

#### `OPENROUTER_REASONING_FALLBACK`
- **Required**: No
- **Default**: `false`
- **Description**: If OpenRouter streaming returns only reasoning tokens, emit them as content
- **Note**: This may surface model reasoning text; enable only when you accept that behavior

#### `LLM_MODEL`
- **Required**: No
- **Default**: `gpt-4o-mini`
- **Description**: Model identifier
- **OpenRouter**: For DeepSeek, prefer `deepseek/deepseek-chat` unless you enable `OPENROUTER_REASONING_FALLBACK`

#### `LLM_TIMEOUT`
- **Required**: No
- **Default**: `30`
- **Description**: API timeout in seconds

#### `LLM_MAX_TOKENS`
- **Required**: No
- **Default**: `1024`
- **Description**: Maximum response tokens

---

### Stripe Configuration (Web Subscriptions)

#### `STRIPE_SECRET_KEY`
- **Required**: Yes
- **Source**: [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
- **Format**: `sk_test_...` (test) or `sk_live_...` (production)

#### `STRIPE_WEBHOOK_SECRET`
- **Required**: Yes
- **Source**: [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
- **Format**: `whsec_...`

#### `STRIPE_PRICE_STANDARD` / `STRIPE_PRICE_PRO`
- **Required**: Yes
- **Source**: [Stripe Products](https://dashboard.stripe.com/products)
- **Description**: Price IDs for subscription tiers

#### `STRIPE_SUCCESS_URL` / `STRIPE_CANCEL_URL`
- **Required**: No
- **Description**: Redirect URLs after checkout

---

### RevenueCat Configuration (Mobile Subscriptions)

#### `REVENUECAT_WEBHOOK_SECRET`
- **Required**: Yes
- **Source**: [RevenueCat Dashboard](https://app.revenuecat.com)
- **Description**: Webhook authentication secret

#### `REVENUECAT_ENTITLEMENT_STANDARD` / `REVENUECAT_ENTITLEMENT_PRO`
- **Required**: Yes
- **Description**: Entitlement identifiers matching RevenueCat config

---

### Monitoring (Optional)

#### `SENTRY_DSN`
- **Required**: No
- **Source**: [Sentry Settings](https://sentry.io)
- **Description**: Error tracking DSN

#### `APP_VERSION`
- **Required**: No
- **Default**: `1.0.0`
- **Description**: Version returned by `/health` endpoint

---

## Production Checklist

Before deploying to production, verify:

- [ ] `DEBUG=false`
- [ ] `BETA_MODE=false` (disable free beta mode)
- [ ] `PAYMENTS_ENABLED=true` (enable payment features)
- [ ] `JWT_SECRET` is a unique, random 256-bit key
- [ ] `DATABASE_URL` points to production database
- [ ] All OAuth credentials are production keys
- [ ] All Stripe keys are `sk_live_*` (not `sk_test_*`)
- [ ] `SENTRY_DSN` is configured for error tracking
- [ ] No secrets are committed to version control

### Free Beta Checklist

For free beta testing deployment, verify:

- [ ] `BETA_MODE=true` (enable relaxed limits)
- [ ] `PAYMENTS_ENABLED=false` (disable payment endpoints)
- [ ] All other core settings configured correctly
- [ ] Mobile app has `EXPO_PUBLIC_BILLING_ENABLED=false`

---

## Setting Variables

### Local Development
```bash
cp .env.example .env
# Edit .env with your values
```

### Docker
```bash
docker run -e DEBUG=false -e DATABASE_URL=... solacore-api
```

### Railway / Render / Fly.io
Use the platform's environment variable settings in the dashboard.

### Kubernetes
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: solacore-api-secrets
type: Opaque
stringData:
  DATABASE_URL: postgresql+asyncpg://...
  JWT_SECRET: ...
```

---

## Production Provider Examples

### Neon (PostgreSQL)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.us-east-1.aws.neon.tech/solacore?sslmode=require
```

### Vercel
```bash
vercel env add DATABASE_URL production
vercel env add JWT_SECRET production
```

### Railway
```bash
railway variables set DATABASE_URL="postgresql+asyncpg://..."
railway variables set JWT_SECRET="..."
```

### Fly.io
```bash
fly secrets set DATABASE_URL="postgresql+asyncpg://..."
fly secrets set JWT_SECRET="..."
```

---

## Verification Commands

```bash
# Health check
curl https://api.solacore.app/health
# Expected: {"status":"healthy","version":"1.0.0","database":"connected"}

# Readiness
curl https://api.solacore.app/health/ready
# Expected: {"ready":true}

# Liveness
curl https://api.solacore.app/health/live
# Expected: {"live":true}
```
