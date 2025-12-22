# Epic 1: Project Foundation & Infrastructure

**Epic ID**: EPIC-001
**Created**: 2025-12-21
**Status**: Ready for Implementation
**Timeline**: Week 1-2
**Stories**: 1.1 - 1.5

---

## Epic Overview

### Goal

Establish project structure, development environment, CI/CD pipeline, and core backend skeleton that enables the team to develop the Clarity application following the Constitution principles.

### Success Criteria

| ID | Criterion | Measurement |
|----|-----------|-------------|
| SC-01 | Developer can set up local environment in < 30 minutes | Time from git clone to running app |
| SC-02 | Both mobile and backend projects build without errors | CI pipeline green |
| SC-03 | Database migrations run successfully | `alembic upgrade head` exits 0 |
| SC-04 | Health check endpoint responds correctly | `GET /health` returns 200 |
| SC-05 | New developer can understand project structure from docs | Onboarding feedback |

### Definition of Done (DoD) - Epic Level

- [ ] All 5 stories completed and merged to main
- [ ] All CI checks passing
- [ ] Documentation reviewed and accurate
- [ ] No critical security issues
- [ ] Git tags created for milestone

---

## Story 1.1: Initialize Mobile App Project

**Story ID**: STORY-1.1
**Priority**: P1 (Critical Path)
**Estimate**: 4 hours

### User Story

> As a **developer**,
> I want to **set up a React Native + Expo project with proper folder structure**,
> so that **the team has a consistent starting point for mobile development**.

### Why P1

This is a blocking prerequisite. No mobile development can begin without the project scaffold. It establishes patterns (folder structure, linting, navigation) that all subsequent code will follow.

### Acceptance Criteria

| AC ID | Criterion | Verification |
|-------|-----------|--------------|
| AC-1.1.1 | Expo project created with TypeScript template | `npx expo --version` works in project |
| AC-1.1.2 | Folder structure matches architecture doc | Directories exist: `app/`, `components/`, `services/`, `stores/`, `i18n/` |
| AC-1.1.3 | ESLint + Prettier configured | `npm run lint` passes with no errors |
| AC-1.1.4 | Expo Router navigation shell working | App renders with tab/stack navigation |
| AC-1.1.5 | App builds on iOS simulator | `npx expo run:ios` succeeds |
| AC-1.1.6 | App builds on Android emulator | `npx expo run:android` succeeds |
| AC-1.1.7 | README with setup instructions | `clarity-mobile/README.md` exists with install steps |

### Acceptance Scenarios

1. **Given** a fresh git clone, **When** developer runs `npm install && npx expo start`, **Then** the Expo dev server launches without errors

2. **Given** the mobile project initialized, **When** developer runs `npm run lint`, **Then** ESLint checks pass with 0 errors

3. **Given** the project with Expo Router, **When** developer opens on simulator, **Then** a placeholder home screen renders

### Edge Cases

- Node version mismatch: Document required Node version in README
- Missing Expo CLI: Include installation command in setup docs
- iOS simulator not installed: Provide fallback to Expo Go

### DoD - Story Level

- [ ] All acceptance criteria verified
- [ ] Code pushed to feature branch
- [ ] PR approved and merged
- [ ] CI pipeline green

---

## Story 1.2: Initialize Backend API Project

**Story ID**: STORY-1.2
**Priority**: P1 (Critical Path)
**Estimate**: 4 hours

### User Story

> As a **developer**,
> I want to **set up a FastAPI project with proper folder structure and configuration**,
> so that **the team has a consistent starting point for backend development**.

### Why P1

Backend is a blocking prerequisite for all API-dependent features (auth, sessions, subscriptions). Establishes async patterns, middleware structure, and configuration approach.

### Acceptance Criteria

| AC ID | Criterion | Verification |
|-------|-----------|--------------|
| AC-1.2.1 | FastAPI project with Poetry | `poetry install` succeeds |
| AC-1.2.2 | Folder structure matches architecture | Directories: `routers/`, `services/`, `models/`, `middleware/`, `schemas/` |
| AC-1.2.3 | Pydantic Settings with .env support | App loads config from `.env` file |
| AC-1.2.4 | Health check endpoint | `GET /health` returns `{"status": "healthy"}` |
| AC-1.2.5 | OpenAPI docs accessible | `GET /docs` renders Swagger UI |
| AC-1.2.6 | Dockerfile present | `docker build .` succeeds |
| AC-1.2.7 | docker-compose.yml for local dev | `docker-compose up` starts API server |
| AC-1.2.8 | README with setup instructions | `clarity-api/README.md` exists |

### Acceptance Scenarios

1. **Given** a fresh git clone, **When** developer runs `poetry install && poetry run uvicorn app.main:app`, **Then** server starts on port 8000

2. **Given** the API running, **When** user visits `/health`, **Then** response is `{"status": "healthy"}` with 200 status

3. **Given** the API running, **When** user visits `/docs`, **Then** Swagger UI renders with available endpoints

4. **Given** docker-compose.yml, **When** developer runs `docker-compose up api`, **Then** API container starts and responds on port 8000

### Edge Cases

- Python version mismatch: Document Python 3.11+ requirement
- Port 8000 in use: Document how to change port via env var
- Missing Poetry: Include installation command

### DoD - Story Level

- [ ] All acceptance criteria verified
- [ ] Code pushed to feature branch
- [ ] PR approved and merged
- [ ] CI pipeline green

---

## Story 1.3: Set Up PostgreSQL Database

**Story ID**: STORY-1.3
**Priority**: P1 (Critical Path)
**Estimate**: 3 hours

### User Story

> As a **developer**,
> I want to **configure PostgreSQL with SQLAlchemy and Alembic migrations**,
> so that **we have a reliable and versioned database schema**.

### Why P1

Database is required for all data persistence. Migration system ensures schema changes are tracked and reproducible across environments.

### Acceptance Criteria

| AC ID | Criterion | Verification |
|-------|-----------|--------------|
| AC-1.3.1 | PostgreSQL in docker-compose | `docker-compose up db` starts Postgres on 5432 |
| AC-1.3.2 | SQLAlchemy async engine configured | `create_async_engine()` in database.py |
| AC-1.3.3 | Alembic initialized | `alembic/` directory with `env.py` |
| AC-1.3.4 | Initial migration for users table | Migration file creates `users` table |
| AC-1.3.5 | Migration runs successfully | `alembic upgrade head` exits 0 |
| AC-1.3.6 | Health check includes DB | `/health` checks database connection |

### Acceptance Scenarios

1. **Given** docker-compose with db service, **When** developer runs `docker-compose up db`, **Then** PostgreSQL accepts connections on port 5432

2. **Given** Alembic configured, **When** developer runs `alembic upgrade head`, **Then** `users` table exists with columns: id, email, created_at

3. **Given** database connection, **When** `/health` is called, **Then** response includes `{"database": "ok"}`

4. **Given** database is down, **When** `/health` is called, **Then** response includes `{"database": "error"}` with status 503

### Key Entities

- **User** (initial schema):
  - `id`: UUID, primary key
  - `email`: VARCHAR(255), unique, not null
  - `created_at`: TIMESTAMP, default now()

### Edge Cases

- Database not running: Health check returns degraded status
- Migration conflict: Document rollback procedure
- Connection pool exhaustion: Configure pool size in settings

### DoD - Story Level

- [ ] All acceptance criteria verified
- [ ] Migration tested (up and down)
- [ ] Code pushed to feature branch
- [ ] PR approved and merged

---

## Story 1.4: Configure CI/CD Pipeline

**Story ID**: STORY-1.4
**Priority**: P2 (Important)
**Estimate**: 4 hours

### User Story

> As a **developer**,
> I want to **set up GitHub Actions for linting, testing, and building**,
> so that **code quality is automatically enforced on every PR**.

### Why P2

CI is critical for quality but doesn't block initial development. Can be set up in parallel with other stories.

### Acceptance Criteria

| AC ID | Criterion | Verification |
|-------|-----------|--------------|
| AC-1.4.1 | Backend workflow: lint (ruff) | `ruff check` runs in CI |
| AC-1.4.2 | Backend workflow: type check (mypy) | `mypy` runs in CI |
| AC-1.4.3 | Backend workflow: test (pytest) | `pytest` runs in CI |
| AC-1.4.4 | Mobile workflow: lint (eslint) | `eslint` runs in CI |
| AC-1.4.5 | Mobile workflow: type check (tsc) | `tsc --noEmit` runs in CI |
| AC-1.4.6 | Trigger on push to main | Workflow runs on main push |
| AC-1.4.7 | Trigger on PR | Workflow runs on PR |
| AC-1.4.8 | Branch protection | PRs require passing checks |
| AC-1.4.9 | Expo EAS Build setup | `eas build` configured (dry run) |

### Acceptance Scenarios

1. **Given** a PR with linting errors, **When** CI runs, **Then** workflow fails and PR cannot merge

2. **Given** a PR with all checks passing, **When** CI runs, **Then** workflow succeeds and PR can merge

3. **Given** push to main branch, **When** CI runs, **Then** both backend and mobile workflows execute

### Edge Cases

- Flaky tests: Implement retry logic (max 2 retries)
- Long-running tests: Set timeout (10 minutes)
- Secrets exposure: Use GitHub secrets for sensitive config

### DoD - Story Level

- [ ] All acceptance criteria verified
- [ ] Test PR created to validate CI
- [ ] Branch protection rules enabled
- [ ] PR approved and merged

---

## Story 1.5: Set Up Development Environment Documentation

**Story ID**: STORY-1.5
**Priority**: P2 (Important)
**Estimate**: 2 hours

### User Story

> As a **developer**,
> I want to **comprehensive setup documentation**,
> so that **new team members can onboard quickly**.

### Why P2

Documentation is critical for team scale but doesn't block solo development. Should be done alongside or after infrastructure setup.

### Acceptance Criteria

| AC ID | Criterion | Verification |
|-------|-----------|--------------|
| AC-1.5.1 | Root README.md | Exists with project overview |
| AC-1.5.2 | docs/setup.md | Step-by-step local dev setup |
| AC-1.5.3 | Environment variables documented | All required env vars listed |
| AC-1.5.4 | Troubleshooting section | Common issues and solutions |
| AC-1.5.5 | Architecture diagram | Visual overview (ASCII or image) |

### Acceptance Scenarios

1. **Given** a new developer, **When** they follow docs/setup.md, **Then** they can run both mobile and backend locally in < 30 minutes

2. **Given** setup documentation, **When** developer encounters common error, **Then** troubleshooting section has solution

3. **Given** architecture diagram, **When** developer views it, **Then** they understand system components and data flow

### Documentation Structure

```
/
├── README.md                 # Project overview, quick start
├── docs/
│   ├── setup.md             # Detailed setup guide
│   ├── architecture.md      # (already exists)
│   └── troubleshooting.md   # Common issues
├── clarity-mobile/
│   └── README.md            # Mobile-specific setup
└── clarity-api/
    └── README.md            # Backend-specific setup
```

### Edge Cases

- Outdated documentation: Include "last verified" date
- OS-specific instructions: Cover macOS, Windows, Linux
- Version drift: Link to specific tool versions

### DoD - Story Level

- [ ] All acceptance criteria verified
- [ ] Documentation reviewed by second person
- [ ] PR approved and merged

---

## Dependencies & Assumptions

### Dependencies

| Story | Depends On | Notes |
|-------|------------|-------|
| 1.2 | 1.1 (partial) | Can work in parallel, share linting config |
| 1.3 | 1.2 | Needs backend project structure |
| 1.4 | 1.1, 1.2 | Needs both projects to configure CI |
| 1.5 | 1.1, 1.2, 1.3 | Documents completed setup |

### Assumptions

1. **macOS primary dev environment**: Windows/Linux as secondary
2. **Node.js 18+ available**: For Expo/React Native
3. **Python 3.11+ available**: For FastAPI
4. **Docker Desktop installed**: For PostgreSQL and containerization
5. **GitHub repository created**: For CI/CD and version control
6. **Expo account exists**: For EAS Build (can use free tier)

### Risks

| Risk | Mitigation |
|------|------------|
| Expo version incompatibility | Pin Expo SDK version in package.json |
| Poetry/Python version issues | Use pyenv, document in setup |
| Docker resource constraints | Document minimum system requirements |

---

## Functional Requirements Summary

| FR ID | Requirement | Story |
|-------|-------------|-------|
| FR-001 | System MUST provide a mobile app scaffold with TypeScript | 1.1 |
| FR-002 | System MUST provide a backend API scaffold with FastAPI | 1.2 |
| FR-003 | System MUST provide a PostgreSQL database with migrations | 1.3 |
| FR-004 | System MUST run automated checks on every PR | 1.4 |
| FR-005 | System MUST provide documentation for local development setup | 1.5 |
| FR-006 | System MUST have a health check endpoint | 1.2, 1.3 |
| FR-007 | System MUST support Docker-based local development | 1.2, 1.3 |

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-21 | 1.0 | Initial spec from Epic 1 stories | AI |

---

*This specification is derived from docs/prd.md, docs/architecture.md, and docs/epics.md*
