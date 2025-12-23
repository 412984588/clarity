# Local Demo Runbook

**Version**: 1.0
**Created**: 2025-12-23

---

## Purpose & Scope

This runbook provides the **shortest path** to run Clarity locally for demonstration and verification purposes.

**Use Cases**:
- Demo to stakeholders
- Verify code changes work end-to-end
- Test before committing

**Not For**:
- Production deployment (see `docs/PROD_DEPLOY.md`)
- Full development setup (see `docs/setup.md`)

---

## Prerequisites

| Tool | Minimum Version | Check Command |
|------|-----------------|---------------|
| Docker | 20.x | `docker --version` |
| Docker Compose | 2.x | `docker compose version` |
| Poetry | 1.x | `poetry --version` |
| Node.js | 18.x | `node --version` |
| npm | 9.x | `npm --version` |

> For installation instructions, see `docs/setup.md`

---

## Quick Start (5 minutes)

### 1. Start Backend

```bash
# Terminal 1: Backend
cd clarity-api
cp .env.example .env          # First time only
docker compose up -d db       # Start PostgreSQL
poetry install --no-root      # First time only
poetry run alembic upgrade head
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Start Mobile (Optional)

```bash
# Terminal 2: Mobile
cd clarity-mobile
npm install                   # First time only
npx expo start
```

### 3. Verify

```bash
# Terminal 3: Smoke test
./scripts/deploy_prod_smoke.sh http://localhost:8000
```

**Expected**: All endpoints return PASS

---

## Demo Paths

### Path 1: Health Endpoints (1 min)

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/ready
curl http://localhost:8000/health/live
```

**Shows**: Backend is running, database connected

### Path 2: API Documentation (1 min)

Open in browser: http://localhost:8000/docs

**Shows**: Full OpenAPI spec, all endpoints documented

### Path 3: User Registration (2 min)

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"Demo1234!"}'
```

**Shows**: User authentication works

### Path 4: Mobile App (3 min)

1. Run `npx expo start` in `clarity-mobile/`
2. Press `i` for iOS simulator or `a` for Android emulator
3. Navigate through login/register screens

**Shows**: Full mobile UI

### Path 5: Full Solve Flow (5 min)

1. Register/login via mobile or API
2. Create solve session
3. Walk through 5 steps: Receive → Clarify → Reframe → Options → Commit

**Shows**: Core product functionality

---

## Known Limitations

### Blocked (Requires External Accounts)

| Feature | Blocker | Workaround |
|---------|---------|------------|
| iOS build | Apple Developer Account | Use Android or simulator |
| Stripe payments | Production Stripe keys | Use test mode |
| RevenueCat | Production setup | Mock subscription |
| Google OAuth | Production client ID | Use email/password |
| Apple Sign-In | Apple Developer Account | Use email/password |

### Local-Only Limitations

| Limitation | Reason |
|------------|--------|
| No push notifications | Requires production setup |
| No real LLM responses | Requires OpenAI/Anthropic API key |
| No email sending | SMTP not configured |

### Configuring LLM (Optional)

To enable AI responses, add to `.env`:

```bash
OPENAI_API_KEY=sk-your-key-here
# or
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## Shutdown & Cleanup

### Stop Services

```bash
# Stop API server
# Press Ctrl+C in Terminal 1

# Stop database
cd clarity-api
docker compose down
```

### Full Cleanup (Reset Everything)

```bash
# Remove database data
cd clarity-api
docker compose down -v        # -v removes volumes

# Remove node_modules (if needed)
cd clarity-mobile
rm -rf node_modules

# Remove Python venv (if needed)
poetry env remove python
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then `kill <PID>` |
| Database connection refused | `docker compose up -d db` |
| Alembic migration fails | Check `DATABASE_URL` in `.env` |
| Expo won't start | `npx expo start --clear` |

> For more details, see `docs/setup.md` troubleshooting section

---

## Related Documents

- Full setup guide: `docs/setup.md`
- Production deployment: `docs/PROD_DEPLOY.md`
- Environment variables: `docs/ENV_VARIABLES.md`
- Local deploy verification: `docs/release/local-deploy-verify.md`

