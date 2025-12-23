# Clarity - Epic & User Story Breakdown

> **Version**: 1.0
> **Last Updated**: 2025-12-21
> **Status**: Draft

---

## Overview

| Phase | Epics | Timeline |
|-------|-------|----------|
| **MVP** | Epic 1-5 | Week 1-8 |
| **V1** | Epic 6-9 | Week 9-12 |

---

# MVP Phase (Week 1-8)

---

## Epic 1: Project Foundation & Infrastructure

**Goal**: Establish project structure, development environment, CI/CD pipeline, and core backend skeleton.

**Timeline**: Week 1-2

### Story 1.1: Initialize Mobile App Project

> As a **developer**,
> I want to **set up a React Native + Expo project with proper folder structure**,
> so that **the team has a consistent starting point for mobile development**.

**Acceptance Criteria:**
1. Expo project created with TypeScript template
2. Folder structure matches architecture doc (`app/`, `components/`, `services/`, `stores/`, `i18n/`)
3. ESLint + Prettier configured with shared config
4. Basic navigation shell working (Expo Router)
5. App builds and runs on iOS simulator and Android emulator
6. README with setup instructions

---

### Story 1.2: Initialize Backend API Project

> As a **developer**,
> I want to **set up a FastAPI project with proper folder structure and configuration**,
> so that **the team has a consistent starting point for backend development**.

**Acceptance Criteria:**
1. FastAPI project created with Poetry for dependency management
2. Folder structure matches architecture doc (`routers/`, `services/`, `models/`, `middleware/`)
3. Environment configuration via Pydantic Settings (`.env` support)
4. Health check endpoint (`GET /health`) returns `{"status":"healthy","version":"1.0.0","database":"connected"}`
5. OpenAPI docs accessible at `/docs`
6. Dockerfile and docker-compose.yml for local development
7. README with setup instructions

---

### Story 1.3: Set Up PostgreSQL Database

> As a **developer**,
> I want to **configure PostgreSQL with SQLAlchemy and Alembic migrations**,
> so that **we have a reliable and versioned database schema**.

**Acceptance Criteria:**
1. PostgreSQL runs in Docker (docker-compose)
2. SQLAlchemy async engine configured
3. Alembic initialized with migration directory
4. Initial migration creates `users` table (id, email, created_at)
5. `alembic upgrade head` runs without errors
6. Database connection test in health check endpoint

---

### Story 1.4: Configure CI/CD Pipeline

> As a **developer**,
> I want to **set up GitHub Actions for linting, testing, and building**,
> so that **code quality is automatically enforced on every PR**.

**Acceptance Criteria:**
1. GitHub Actions workflow for backend: lint (ruff), type check (mypy), test (pytest)
2. GitHub Actions workflow for mobile: lint (eslint), type check (tsc)
3. Workflows trigger on push to `main` and on PRs
4. PR cannot merge if checks fail
5. Build artifacts for mobile (Expo EAS Build setup)

---

### Story 1.5: Set Up Development Environment Documentation

> As a **developer**,
> I want to **comprehensive setup documentation**,
> so that **new team members can onboard quickly**.

**Acceptance Criteria:**
1. Root `README.md` with project overview
2. `docs/setup.md` with step-by-step local development setup
3. Required environment variables documented
4. Troubleshooting section for common issues
5. Architecture diagram included (can be ASCII or image)

---

## Epic 2: User Authentication System

**Goal**: Implement complete authentication flow with email, Google, and Apple sign-in, including device binding.

**Timeline**: Week 3-4

### Story 2.1: Email Registration & Login (Backend)

> As a **user**,
> I want to **register and log in with my email and password**,
> so that **I can create an account and access my sessions**.

**Acceptance Criteria:**
1. `POST /auth/register` creates user with hashed password (bcrypt)
2. `POST /auth/login` validates credentials and returns JWT tokens
3. Access token expires in 1 hour, refresh token in 30 days
4. Password requirements enforced (min 8 chars, 1 number, 1 uppercase)
5. Email uniqueness validated with proper error message
6. Rate limiting on login endpoint (5 attempts per minute)
7. Unit tests for all auth endpoints

---

### Story 2.2: JWT Token Management

> As a **user**,
> I want to **my session to stay active without frequent re-login**,
> so that **I have a seamless experience**.

**Acceptance Criteria:**
1. `POST /auth/refresh` exchanges refresh token for new access token
2. Refresh token rotation implemented (old token invalidated)
3. `POST /auth/logout` invalidates refresh token
4. Token blacklist or session table for revocation
5. Middleware extracts and validates JWT on protected routes
6. 401 returned for expired/invalid tokens with clear error code

---

### Story 2.3: Google OAuth Integration

> As a **user**,
> I want to **sign in with my Google account**,
> so that **I don't need to remember another password**.

**Acceptance Criteria:**
1. `POST /auth/oauth/google` accepts Google ID token
2. Token verified against Google's public keys
3. New user created if email doesn't exist (auth_provider='google')
4. Existing user linked if email matches
5. JWT tokens returned on success
6. Works with Expo AuthSession for mobile

---

### Story 2.4: Apple Sign-In Integration

> As a **user**,
> I want to **sign in with my Apple ID**,
> so that **I can use secure authentication on iOS**.

**Acceptance Criteria:**
1. `POST /auth/oauth/apple` accepts Apple identity token
2. Token verified against Apple's public keys
3. Handles Apple's private relay email
4. New user created or existing user linked
5. JWT tokens returned on success
6. Works with Expo Apple Authentication

---

### Story 2.5: Device Registration & Binding

> As the **system**,
> I want to **track and limit devices per user**,
> so that **account sharing is prevented**.

**Acceptance Criteria:**
1. `X-Device-Fingerprint` header required on auth endpoints
2. Device fingerprint generated client-side (vendor ID + install ID)
3. Device record created on first login from new device
4. Device limit enforced per tier (Free: 1, Standard: 2, Pro: 3)
5. `GET /auth/devices` lists user's registered devices
6. `DELETE /auth/devices/{id}` allows user to unlink device (max 1/day)
7. Clear error message when device limit reached

---

### Story 2.6: Auth UI (Mobile)

> As a **user**,
> I want to **a clean login and signup experience in the app**,
> so that **I can easily create an account or sign in**.

**Acceptance Criteria:**
1. Login screen with email/password fields
2. Sign up screen with email/password + confirmation
3. Google Sign-In button (uses Expo AuthSession)
4. Apple Sign-In button (iOS only, uses expo-apple-authentication)
5. Form validation with inline error messages
6. Loading states during API calls
7. Tokens stored securely (expo-secure-store)
8. Auto-login if valid refresh token exists

---

### Story 2.7: Password Reset Flow

> As a **user**,
> I want to **reset my password if I forget it**,
> so that **I can regain access to my account**.

**Acceptance Criteria:**
1. `POST /auth/forgot-password` sends reset email
2. Reset token valid for 1 hour
3. `POST /auth/reset-password` sets new password with valid token
4. Mobile: "Forgot Password" link on login screen
5. Mobile: Deep link handling for reset links
6. Email template is professional and branded

---

## Epic 3: Chat Core & AI Integration

**Goal**: Implement the core chat interface and AI service integration with streaming responses.

**Timeline**: Week 5

### Story 3.1: Session Management (Backend)

> As a **user**,
> I want to **create and manage Solve sessions**,
> so that **I can track my problem-solving journeys**.

**Acceptance Criteria:**
1. `POST /sessions` creates new session (requires auth)
2. Session record includes: id, user_id, device_id, status, current_step
3. `GET /sessions/{id}` returns session metadata
4. `PATCH /sessions/{id}` updates status (complete, abandon)
5. Session creation increments usage counter
6. Subscription/quota check middleware applied

---

### Story 3.2: AI Service Integration

> As a **developer**,
> I want to **integrate OpenAI/Claude API with proper prompt management**,
> so that **the AI can guide users through the Solve process**.

**Acceptance Criteria:**
1. AI service abstraction layer (supports OpenAI and Claude)
2. API key configuration via environment variables
3. Prompt templates for each Solve step stored in config
4. PII stripping before sending to AI (names, emails, phone numbers)
5. Token usage tracking per request
6. Retry logic with exponential backoff
7. Timeout handling (30 second max)

---

### Story 3.3: Streaming Responses (SSE)

> As a **user**,
> I want to **see AI responses appear word by word**,
> so that **the experience feels natural and responsive**.

**Acceptance Criteria:**
1. `POST /sessions/{id}/messages` returns SSE stream
2. Each token sent as `event: token` with content
3. Final event `event: done` with metadata (next_step, emotion)
4. Client can cancel stream mid-response
5. Partial responses saved if connection drops
6. Works on both iOS and Android

---

### Story 3.4: Chat UI (Mobile)

> As a **user**,
> I want to **a familiar chat interface like ChatGPT**,
> so that **I can easily interact with Clarity**.

**Acceptance Criteria:**
1. Message list with user/AI bubbles
2. Input bar with send button
3. Streaming text display (word by word)
4. Auto-scroll to bottom on new messages
5. Keyboard handling (push input above keyboard)
6. Empty state for new session
7. Loading indicator while AI is thinking

---

### Story 3.5: Local Message Storage

> As a **user**,
> I want to **my conversations stored on my device**,
> so that **my privacy is protected**.

**Acceptance Criteria:**
1. SQLite database for local message storage
2. Messages linked to session_id
3. Messages never sent to server (only to AI via streaming)
4. `getMessages(sessionId)` returns all messages for session
5. `saveMessage(sessionId, message)` persists message
6. Data cleared on app uninstall

---

## Epic 4: Solve 5-Step Framework

**Goal**: Implement the complete Solve methodology with step progression, options, and commitment tracking.

**Timeline**: Week 6-7

### Story 4.1: Step 1 - Receive (接纳)

> As a **user**,
> I want to **share my problem and feel heard**,
> so that **I'm ready to explore solutions**.

**Acceptance Criteria:**
1. Initial prompt encourages user to share
2. AI responds with empathy and acknowledgment
3. Basic emotion detection (positive/negative/neutral)
4. Step indicator shows "Receive" as active
5. After 1-2 exchanges, AI transitions to Clarify
6. Prompt template includes emotional support guidelines

---

### Story 4.2: Step 2 - Clarify (澄清)

> As a **user**,
> I want to **answer clarifying questions**,
> so that **the root cause of my problem is identified**.

**Acceptance Criteria:**
1. AI asks 5W1H questions (What, Who, When, Where, Why, How)
2. Questions are contextual to user's problem
3. AI summarizes understanding before moving on
4. 3-5 exchanges typically needed
5. User can skip to next step manually
6. Step indicator shows "Clarify" as active

---

### Story 4.3: Step 3 - Reframe (重构)

> As a **user**,
> I want to **see my problem from new perspectives**,
> so that **I can break out of my mental patterns**.

**Acceptance Criteria:**
1. AI offers 1-2 reframing perspectives
2. Techniques used: Devil's Advocate, Zoom Out, Control Circle
3. AI explains the reframe clearly
4. User has opportunity to react/discuss
5. 1-2 exchanges before moving to Options
6. Step indicator shows "Reframe" as active

---

### Story 4.4: Step 4 - Options (方案)

> As a **user**,
> I want to **see 2-3 actionable options**,
> so that **I can choose a path forward**.

**Acceptance Criteria:**
1. AI presents 2-3 distinct options
2. Each option includes: title, actions, pros, cons
3. Options displayed as tappable cards (not just text)
4. User can ask follow-up questions about options
5. User selects preferred option to proceed
6. Step indicator shows "Options" as active

---

### Story 4.5: Option Card UI Component

> As a **user**,
> I want to **clearly see and compare my options**,
> so that **I can make an informed choice**.

**Acceptance Criteria:**
1. Card component with title, description, pros (green), cons (red)
2. Cards are horizontally scrollable or stacked
3. Tap to select, visual feedback on selection
4. "Tell me more" button for each option
5. Accessible (screen reader support)
6. Smooth animations on appear/select

---

### Story 4.6: Step 5 - Commit (承诺)

> As a **user**,
> I want to **commit to an action and get my first step**,
> so that **I leave with something concrete to do**.

**Acceptance Criteria:**
1. AI confirms selected option
2. AI breaks down into first actionable step
3. First step is specific and time-bound (e.g., "within 48 hours")
4. Optional reminder prompt (set reminder for tomorrow)
5. Session marked as completed
6. Celebratory UI feedback (subtle animation)
7. Step indicator shows "Commit" as complete

---

### Story 4.7: Step Progress Indicator

> As a **user**,
> I want to **see my progress through the Solve steps**,
> so that **I know where I am in the process**.

**Acceptance Criteria:**
1. Horizontal step indicator at top of chat
2. Shows all 5 steps: Receive → Clarify → Reframe → Options → Commit
3. Current step highlighted
4. Completed steps show checkmark
5. Tappable to see step name (tooltip)
6. Smooth transition animation between steps

---

## Epic 5: Subscription & Payment System

**Goal**: Implement Stripe integration with tiered subscriptions, usage tracking, and upgrade flows.

**Timeline**: Week 7-8

### Story 5.1: Subscription Data Model

> As a **developer**,
> I want to **a robust subscription data model**,
> so that **we can accurately track user tiers and usage**.

**Acceptance Criteria:**
1. Subscription table with tier, status, Stripe IDs, period dates
2. Usage table with session_count per billing period
3. Free tier: 10 sessions lifetime
4. Standard tier: 100 sessions per month
5. Pro tier: unlimited sessions
6. Subscription created automatically on user registration (free tier)

---

### Story 5.2: Stripe Integration (Backend)

> As a **developer**,
> I want to **integrate Stripe for payment processing**,
> so that **users can subscribe to paid plans**.

**Acceptance Criteria:**
1. Stripe SDK configured with API keys
2. Products and prices created in Stripe dashboard
3. `POST /subscriptions/checkout` creates Stripe Checkout session
4. Checkout session configured for subscription mode
5. Success/cancel URLs use deep links (clarity://...)
6. Customer portal link generation for managing subscription

---

### Story 5.3: Stripe Webhook Handler

> As the **system**,
> I want to **process Stripe webhook events**,
> so that **subscription status stays synchronized**.

**Acceptance Criteria:**
1. `POST /webhooks/stripe` endpoint with signature verification
2. Handle `checkout.session.completed` → activate subscription
3. Handle `invoice.paid` → renew subscription, reset usage
4. Handle `invoice.payment_failed` → mark as past_due
5. Handle `customer.subscription.deleted` → downgrade to free
6. Idempotency handling (don't process same event twice)
7. Logging for all webhook events

---

### Story 5.4: Usage Tracking & Quota Enforcement

> As the **system**,
> I want to **track and enforce usage quotas**,
> so that **users stay within their plan limits**.

**Acceptance Criteria:**
1. Usage incremented on session creation
2. Quota check in subscription middleware
3. Free users blocked at 10 sessions with upgrade prompt
4. Standard users warned at 90%, allowed overage at 100%
5. `GET /subscriptions/usage` returns current usage stats
6. Usage resets on subscription renewal (webhook triggered)

---

### Story 5.5: Subscription Middleware

> As the **system**,
> I want to **enforce subscription requirements on API endpoints**,
> so that **paid features are protected**.

**Acceptance Criteria:**
1. `@requires_subscription` decorator for protected routes
2. Supports `min_tier` parameter (e.g., "standard", "pro")
3. Returns 403 with upgrade prompt if tier insufficient
4. Returns 403 with quota info if sessions exceeded
5. Caches subscription data for 5 minutes (reduce DB calls)
6. Clear error codes for client to handle

---

### Story 5.6: Pricing & Upgrade UI (Mobile)

> As a **user**,
> I want to **see pricing plans and upgrade easily**,
> so that **I can unlock more features**.

**Acceptance Criteria:**
1. Pricing screen showing Free, Standard, Pro tiers
2. Feature comparison table
3. Current plan highlighted
4. "Upgrade" button opens Stripe Checkout (in-app browser)
5. Deep link handling for success/cancel redirects
6. Subscription status refreshes after successful payment
7. "Manage Subscription" opens Stripe Customer Portal

---

### Story 5.7: Quota Warning UI

> As a **user**,
> I want to **be notified when approaching my session limit**,
> so that **I'm not surprised when I run out**.

**Acceptance Criteria:**
1. Warning banner at 80% usage (8/10 for free, 80/100 for standard)
2. Hard block screen at 100% with upgrade CTA
3. Usage display in settings screen
4. Usage info returned with session creation response
5. Push notification option for quota warnings (future)

---

# V1 Phase (Week 9-12)

---

## Epic 6: Emotion Detection & UI Effects

**Goal**: Implement emotion recognition from text and dynamic UI color gradients.

**Timeline**: Week 9

### Story 6.1: Emotion Detection Service

> As the **system**,
> I want to **detect user emotions from their messages**,
> so that **the AI can respond appropriately**.

**Acceptance Criteria:**
1. Emotion detection via AI prompt analysis
2. 5 emotion categories: anxious, sad, calm, confused, neutral
3. Confidence score (0-1) for detected emotion
4. Emotion returned with each AI response
5. Client-side keyword backup detection (for immediate UI response)
6. Emotion logged for analytics (anonymized)

---

### Story 6.2: Emotion-Based UI Gradients

> As a **user**,
> I want to **the app's colors to subtly reflect my emotional state**,
> so that **I feel understood**.

**Acceptance Criteria:**
1. Background gradient component with emotion prop
2. Color mappings per architecture doc (anxious→orange-red, etc.)
3. Smooth transition animation (300ms ease)
4. Gradient only affects background, not text (accessibility)
5. Toggle in settings to disable (some users may find distracting)
6. Works in dark mode

---

### Story 6.3: Empathetic AI Response Tuning

> As a **user**,
> I want to **the AI to acknowledge my emotions**,
> so that **I feel heard before problem-solving**.

**Acceptance Criteria:**
1. Receive step prompt includes emotion-aware instructions
2. AI mirrors detected emotion in first response
3. Higher empathy for negative emotions (anxious, sad)
4. More solution-focused for neutral/calm emotions
5. A/B test: empathetic vs standard responses

---

## Epic 7: Internationalization (i18n)

**Goal**: Support English, Spanish, and Chinese with proper localization throughout the app.

**Timeline**: Week 10

### Story 7.1: i18n Infrastructure (Mobile)

> As a **developer**,
> I want to **set up i18n infrastructure**,
> so that **translations can be easily added and maintained**.

**Acceptance Criteria:**
1. react-i18next configured with Expo
2. Language detection from device locale
3. Fallback to English if translation missing
4. Translation files: en.json, es.json, zh.json
5. Language switcher in settings
6. Language preference persisted locally

---

### Story 7.2: English Translation (Complete)

> As an **English-speaking user**,
> I want to **see all app text in English**,
> so that **I can use the app in my language**.

**Acceptance Criteria:**
1. All UI strings in en.json
2. All error messages translated
3. All button labels, placeholders translated
4. Onboarding flow translated
5. Email templates in English
6. No hardcoded strings in code

---

### Story 7.3: Spanish Translation (Complete)

> As a **Spanish-speaking user**,
> I want to **see all app text in Spanish**,
> so that **I can use the app in my language**.

**Acceptance Criteria:**
1. All UI strings in es.json
2. Professional translation (not Google Translate)
3. Spain Spanish (es-ES) as base
4. Date/currency formatting for Spain
5. AI prompts include Spanish response instruction
6. Tested by native speaker

---

### Story 7.4: Chinese Translation (Complete)

> As a **Chinese-speaking user**,
> I want to **see all app text in Simplified Chinese**,
> so that **I can use the app in my language**.

**Acceptance Criteria:**
1. All UI strings in zh.json
2. Simplified Chinese (zh-CN)
3. Professional translation
4. Font supports Chinese characters
5. AI prompts include Chinese response instruction
6. Tested by native speaker

---

### Story 7.5: Backend Error Localization

> As a **user**,
> I want to **see error messages in my language**,
> so that **I understand what went wrong**.

**Acceptance Criteria:**
1. Backend returns error codes (e.g., `QUOTA_EXCEEDED`)
2. Error codes mapped to localized strings on client
3. Error params passed for interpolation (e.g., `{used}`, `{limit}`)
4. All error codes have translations in all 3 languages
5. Fallback to English if translation missing

---

## Epic 8: Anti-Abuse System

**Goal**: Complete implementation of device binding, rate limiting, concurrent session management, and anomaly detection.

**Timeline**: Week 10-11

### Story 8.1: Device Middleware (Complete)

> As the **system**,
> I want to **enforce device binding on all requests**,
> so that **account sharing is prevented**.

**Acceptance Criteria:**
1. Device fingerprint required on all authenticated requests
2. New device auto-registered if under limit
3. 403 returned if device limit exceeded
4. 403 returned if device bound to different user
5. Device last_active_at updated on each request
6. Inactive devices auto-pruned after 90 days

---

### Story 8.2: Rate Limiting (Complete)

> As the **system**,
> I want to **enforce per-user rate limits**,
> so that **API abuse is prevented**.

**Acceptance Criteria:**
1. Sliding window rate limiter (in-memory for single server)
2. Limits: Free 30/min, Standard 60/min, Pro 120/min
3. 429 response with `Retry-After` header
4. Rate limit info in response headers (`X-RateLimit-*`)
5. Separate limits for auth endpoints (stricter)
6. Logging of rate limit violations

---

### Story 8.3: Concurrent Session Enforcement

> As the **system**,
> I want to **limit concurrent active sessions**,
> so that **account sharing is detected**.

**Acceptance Criteria:**
1. Active session created on login (token hash stored)
2. Session limit: Free 1, Standard 2, Pro 3
3. New login over limit → oldest session invalidated
4. Invalidated session returns 401 on next request
5. `GET /auth/sessions` lists active sessions
6. User can manually terminate sessions

---

### Story 8.4: Anomaly Detection (Background)

> As the **system**,
> I want to **detect suspicious account activity**,
> so that **abuse can be investigated**.

**Acceptance Criteria:**
1. Background job analyzes login patterns
2. Flag: Multiple IPs + devices in < 1 hour
3. Flag: Impossible travel (e.g., NYC to Tokyo in 30 min)
4. Flag: Velocity spike (5x normal usage)
5. Flagged accounts logged for review
6. No automatic action (manual review first)

---

### Story 8.5: Device Management UI

> As a **user**,
> I want to **see and manage my registered devices**,
> so that **I can remove devices I no longer use**.

**Acceptance Criteria:**
1. Settings screen shows list of devices
2. Device info: name, platform, last active
3. Current device indicated
4. "Remove" button (except current device)
5. Remove limit: 1 device per 24 hours
6. Confirmation dialog before removal

---

## Epic 9: Testing, Optimization & Launch

**Goal**: Comprehensive testing, performance optimization, and production deployment.

**Timeline**: Week 11-12

### Story 9.1: Unit Test Coverage

> As a **developer**,
> I want to **comprehensive unit tests**,
> so that **code changes don't break functionality**.

**Acceptance Criteria:**
1. Backend: >80% coverage on services and middleware
2. Mobile: >70% coverage on business logic (stores, services)
3. Critical paths: auth, subscription, session creation at 100%
4. Tests run in CI on every PR
5. Coverage reports generated

---

### Story 9.2: Integration Tests

> As a **developer**,
> I want to **integration tests for API endpoints**,
> so that **the full request flow is validated**.

**Acceptance Criteria:**
1. Test database setup/teardown
2. Auth flow tested end-to-end
3. Session creation with subscription check tested
4. Stripe webhook handling tested (mock events)
5. Tests run in CI

---

### Story 9.3: Performance Testing

> As a **developer**,
> I want to **validate system performance under load**,
> so that **we know our capacity limits**.

**Acceptance Criteria:**
1. Load test with 100 concurrent users
2. Response time <2s for 95th percentile
3. No errors under normal load
4. Identify bottlenecks (DB, AI API, etc.)
5. Document capacity limits

---

### Story 9.4: Security Audit

> As a **developer**,
> I want to **a security review of the application**,
> so that **vulnerabilities are identified before launch**.

**Acceptance Criteria:**
1. OWASP Top 10 checklist reviewed
2. SQL injection prevention verified
3. XSS prevention verified (mobile less relevant)
4. Authentication bypass attempts tested
5. Rate limiting effectiveness verified
6. Secrets not exposed in logs or responses

---

### Story 9.5: Production Deployment

> As a **developer**,
> I want to **deploy to production environment**,
> so that **users can access the app**.

**Acceptance Criteria:**
1. Server provisioned (Ubuntu 22.04)
2. Docker Compose deployment working
3. SSL certificate configured (Let's Encrypt)
4. Domain configured (api.clarity.app)
5. Database backups scheduled
6. Monitoring alerts configured

---

### Story 9.6: App Store Submission (iOS)

> As a **product owner**,
> I want to **submit the app to Apple App Store**,
> so that **iOS users can download it**.

**Acceptance Criteria:**
1. App Store Connect account configured
2. App metadata completed (description, screenshots, keywords)
3. Privacy policy URL provided
4. App Review guidelines compliance checked
5. TestFlight beta tested
6. App submitted for review

---

### Story 9.7: Play Store Submission (Android)

> As a **product owner**,
> I want to **submit the app to Google Play Store**,
> so that **Android users can download it**.

**Acceptance Criteria:**
1. Google Play Console account configured
2. App metadata completed
3. Privacy policy URL provided
4. Content rating questionnaire completed
5. Internal testing completed
6. App submitted for review

---

## Summary

| Epic | Stories | Phase |
|------|---------|-------|
| Epic 1: Project Foundation | 5 | MVP |
| Epic 2: User Authentication | 7 | MVP |
| Epic 3: Chat Core & AI | 5 | MVP |
| Epic 4: Solve 5-Step | 7 | MVP |
| Epic 5: Subscription & Payment | 7 | MVP |
| Epic 6: Emotion Detection | 3 | V1 |
| Epic 7: i18n | 5 | V1 |
| Epic 8: Anti-Abuse | 5 | V1 |
| Epic 9: Testing & Launch | 7 | V1 |
| **Total** | **51** | |

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-12-21 | 1.0 | Initial epic breakdown | Product Team |

---

*This document is maintained by the Product Team. For questions or suggestions, contact product@clarity.app*
