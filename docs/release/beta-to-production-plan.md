# Beta to Production Transition Plan

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta → Production

---

## Overview

This document outlines the **roadmap for transitioning Clarity from Free Beta to Production Launch**. It defines the phases, workstreams, critical dependencies, decision points, and risk mitigations required for a successful production deployment.

**Key Objectives**:
1. Complete beta testing with friends/early testers
2. Resolve critical blockers (Domain, Apple Developer Account)
3. Deploy production infrastructure
4. Submit to App Store / Play Store (iOS initially deferred pending Apple account)
5. Launch to public with monitoring and support

**Current Status**: Free Beta (No Payments)
**Target Status**: Production (Payments DEFERRED initially)

**Related Documents**:
- [Beta Exit Criteria](beta-exit-criteria.md) - Go/No-Go thresholds
- [Launch Readiness Scorecard](launch-readiness.md) - Production readiness assessment
- [Launch Dependencies](launch-dependencies.md) - Dependency tracking
- [Remaining Work](remaining-work.md) - Incomplete items and blockers

---

## Phases

### Phase 0: Free Beta Testing (Current Phase)

**Status**: ✅ IN PROGRESS
**Duration**: 2-4 weeks
**Goal**: Validate core features with 5-10 friends/early testers

**Key Activities**:
- Distribute Android preview APK to testers
- Collect feedback via [Beta Feedback Form](beta-feedback-form.md)
- Triage and fix bugs (see [Feedback Triage](feedback-triage.md))
- Run daily/weekly ops (see [Free Beta Ops Playbook](free-beta-ops-playbook.md))
- Track tester progress in [Beta Tester Tracker](beta-tester-tracker.md)

**Exit Criteria**: See [Beta Exit Criteria](beta-exit-criteria.md)
- ≥ 5 active testers
- ≥ 60% Solve completion rate
- Average satisfaction ≥ 3.5/5
- 0 P0 bugs, ≤ 2 P1 bugs

**Deliverables**:
- [x] Android preview APK distributed
- [ ] Beta testing feedback collected (≥ 5 testers)
- [ ] All P0 bugs fixed
- [ ] Beta learnings documented

---

### Phase 1: Blocker Resolution

**Status**: 🔴 BLOCKED
**Duration**: 1-2 weeks
**Goal**: Resolve critical external dependencies

**Key Activities**:
1. **Domain Purchase & Configuration**
   - Purchase `api.clarity.app` or alternative domain
   - Configure DNS to point to hosting provider
   - Verify SSL certificate auto-provisioning (Let's Encrypt)

2. **Apple Developer Account**
   - Enroll in Apple Developer Program ($99/year)
   - Wait for approval (1-2 business days)
   - Set up App Store Connect access

3. **Hosting & Database Provider Selection**
   - Finalize hosting decision (Vercel / Railway / Fly.io)
   - Finalize database decision (Neon / Supabase / RDS)
   - Create production environments

4. **LLM API Key Confirmation**
   - Confirm OpenAI or Anthropic production API key availability
   - Test quota limits and rate limits

**Exit Criteria**:
- Domain DNS resolves correctly
- Apple Developer account active
- Hosting and database providers selected
- LLM API key tested

**Deliverables**:
- [ ] Domain purchased and DNS configured
- [ ] Apple Developer account approved
- [ ] Hosting provider environment created
- [ ] Database provider instance created
- [ ] LLM API key tested

**Risks**:
- Domain name not available → Select alternative domain
- Apple Developer approval delayed → Cannot submit iOS app for 2-3 days
- LLM API quota insufficient → Upgrade plan or switch provider

---

### Phase 2: Pre-Production Setup

**Status**: ⏳ PENDING (Depends on Phase 1)
**Duration**: 1 week
**Goal**: Set up production infrastructure

**Workstreams**:

#### Workstream A: Infrastructure 🏗️

**Owner**: DevOps Lead

| Task | Description | Duration | Dependencies |
|------|-------------|----------|--------------|
| 2.1 | Deploy backend to production | Follow [PROD_DEPLOY.md](../PROD_DEPLOY.md) | Phase 1 complete |
| 2.2 | Run database migrations | `alembic upgrade head` on production DB | Database provider ready |
| 2.3 | Configure environment variables | Set production values in [ENV_VARIABLES.md](../ENV_VARIABLES.md) | All secrets ready |
| 2.4 | Verify health endpoints | Test `/health`, `/health/ready`, `/health/live` | Backend deployed |
| 2.5 | Set up monitoring | Configure Sentry (optional), UptimeRobot, logging | Backend deployed |

**Exit Criteria**:
- Backend health check returns 200
- Database migrations successful
- Monitoring configured (optional for MVP)

---

#### Workstream B: Mobile 📱

**Owner**: Mobile Lead

| Task | Description | Duration | Dependencies |
|------|-------------|----------|--------------|
| 2.6 | Configure production API URL | Update `clarity-mobile/src/config.ts` with production URL | Backend deployed |
| 2.7 | Build iOS production binary | `eas build --platform ios --profile production` | Apple Developer account |
| 2.8 | Build Android production binary | `eas build --platform android --profile production` | None |
| 2.9 | Test iOS build with TestFlight | Internal testing with team | iOS build complete |
| 2.10 | Test Android build locally | Install APK and verify full flow | Android build complete |

**Exit Criteria**:
- iOS production build uploaded to TestFlight (if Apple account ready)
- Android production build tested locally
- Mobile app connects to production backend successfully

---

#### Workstream C: Payments (DEFERRED) 💳

**Owner**: Backend Lead / Finance

**Status**: **DEFERRED** - Payment features will launch in a later phase

| Task | Description | Status |
|------|-------------|--------|
| 2.11 | Activate Stripe Live Mode | Complete KYC, get Live API keys | **DEFERRED** |
| 2.12 | Configure Stripe Webhook | Point to `https://api.clarity.app/webhooks/stripe` | **DEFERRED** |
| 2.13 | Set up RevenueCat Production | Create production app, configure entitlements | **DEFERRED** |
| 2.14 | Configure RevenueCat Webhook | Point to `https://api.clarity.app/webhooks/revenuecat` | **DEFERRED** |
| 2.15 | Test subscription flow end-to-end | Complete purchase flow on iOS/Android | **DEFERRED** |

**Note**: Production will initially launch with `BETA_MODE=true` and `PAYMENTS_ENABLED=false`. Payment features will be enabled in a follow-up release after validating the free user experience.

---

#### Workstream D: Monitoring & Alerting 📊

**Owner**: DevOps Lead

| Task | Description | Duration | Dependencies |
|------|-------------|----------|--------------|
| 2.16 | Configure Sentry DSN (optional) | Error tracking setup | Backend deployed |
| 2.17 | Set up UptimeRobot | Monitor `/health` endpoint every 5 minutes | Backend deployed |
| 2.18 | Configure log aggregation | Centralized logging (if using Railway/Fly.io) | Backend deployed |
| 2.19 | Set up alert thresholds | Define alerts for downtime, errors, latency | Monitoring configured |

**Exit Criteria**:
- At least basic uptime monitoring configured (UptimeRobot or equivalent)
- Error tracking configured (Sentry optional)

---

#### Workstream E: Compliance & Legal ⚖️

**Owner**: Product Lead / Legal

| Task | Description | Duration | Dependencies |
|------|-------------|----------|--------------|
| 2.20 | Publish Privacy Policy | Host at `https://clarity.app/privacy` | Domain ready |
| 2.21 | Publish Terms of Service | Host at `https://clarity.app/terms` | Domain ready |
| 2.22 | Link policies in app | Add links to Settings screen | Mobile build |
| 2.23 | Configure support email | Set up `support@clarity.app` | Domain ready |
| 2.24 | Prepare GDPR/CCPA disclosures | See [Privacy Compliance Checklist](privacy-compliance-checklist.md) | - |

**Exit Criteria**:
- Privacy Policy and Terms of Service published
- Support email configured
- Compliance checklist reviewed

---

### Phase 3: Production Launch

**Status**: ⏳ PENDING (Depends on Phase 2)
**Duration**: 1-2 days (excluding store review)
**Goal**: Deploy to production and open to public

**Key Activities**:

#### 3.1 Final Pre-Launch Checks

- [ ] Run full QA regression suite (see [QA Test Plan](qa-test-plan.md))
- [ ] Verify all items in [Launch Readiness Scorecard](launch-readiness.md) are READY
- [ ] Complete [Release Approval Checklist](release-approval-checklist.md)
- [ ] Hold Go/No-Go meeting (see [Go/No-Go Minutes](go-no-go-minutes.md) template)

#### 3.2 Production Deployment

- [ ] Deploy backend to production (follow [PROD_DEPLOY.md](../PROD_DEPLOY.md))
- [ ] Run smoke tests (see [Launch Day Runbook](launch-day-runbook.md))
- [ ] Verify health endpoints and monitoring
- [ ] Test end-to-end flow on production (Solve session)

#### 3.3 Store Submission (Deferred for iOS if Apple account blocked)

**Android (Google Play Store)**:
- [ ] Upload production APK/AAB to Google Play Console
- [ ] Complete store listing (screenshots, description, keywords)
- [ ] Submit for review (1-3 days review period)
- [ ] Approve release after review

**iOS (App Store)** - **CONDITIONAL on Apple Developer Account**:
- [ ] Upload production IPA to App Store Connect
- [ ] Complete store listing (screenshots, description, keywords)
- [ ] Submit for review (1-7 days review period)
- [ ] Approve release after review

**Fallback if Apple account blocked**: Launch with Android only, defer iOS to Phase 4.

#### 3.4 Go-Live

- [ ] Execute [Launch Day Runbook](launch-day-runbook.md)
- [ ] Monitor metrics (see [Release Metrics](release-metrics.md))
- [ ] Execute [Launch Communications](launch-communications.md) plan
- [ ] Monitor support channels (`support@clarity.app`)

**Exit Criteria**:
- Backend deployed and healthy
- At least one mobile platform (Android) live in store
- Monitoring and alerts active
- Support channels operational

---

### Phase 4: Post-Launch Stabilization

**Status**: ⏳ PENDING (Depends on Phase 3)
**Duration**: 2-4 weeks
**Goal**: Monitor, stabilize, and iterate

**Key Activities**:
1. **Monitor Key Metrics**
   - Track KPIs from [Release Metrics](release-metrics.md)
   - Daily downloads, signups, active users
   - Crash rate, error rate, API latency

2. **Rapid Bug Fixes**
   - Triage production issues (see [Incident Response](incident-response.md))
   - Hot-fix critical bugs within 24 hours
   - Weekly patch releases for P1/P2 bugs

3. **User Support**
   - Respond to support@ emails (see [Support Playbook](support-playbook.md))
   - Monitor app store reviews
   - Update FAQ based on common questions

4. **Payment Integration (DEFERRED)**
   - Once free user experience validated (2-4 weeks post-launch)
   - Enable Stripe/RevenueCat in Phase 5

**Exit Criteria**:
- Crash rate < 2%
- Average app store rating ≥ 4.0/5
- Support response time < 24 hours
- No P0/P1 bugs open for more than 48 hours

---

### Phase 5: Payment Enablement (Future)

**Status**: ⏳ DEFERRED
**Goal**: Enable subscription payments

**Key Activities**:
1. Activate Stripe Live Mode
2. Configure RevenueCat Production
3. Test payment flow end-to-end
4. Enable `PAYMENTS_ENABLED=true` in production
5. Update mobile app to show paywall
6. Submit updated app to stores

**Timeline**: TBD (4-8 weeks post-launch)

---

## Critical Path Dependencies

```
Phase 0: Free Beta Testing
    ↓
Phase 1: Blocker Resolution
    ├── Domain Purchase & DNS
    ├── Apple Developer Account
    ├── Hosting/Database Selection
    └── LLM API Key Confirmation
    ↓
Phase 2: Pre-Production Setup
    ├── Infrastructure (Backend + Database)
    ├── Mobile (iOS + Android builds)
    ├── Monitoring & Alerting
    └── Compliance & Legal
    ↓
Phase 3: Production Launch
    ├── Final QA & Go/No-Go
    ├── Store Submission (Android immediate, iOS conditional)
    └── Go-Live
    ↓
Phase 4: Post-Launch Stabilization
    ↓
Phase 5: Payment Enablement (DEFERRED)
```

**Critical Path Phases**: Phase 1 → Phase 2 → Phase 3 (Phases 0 and 4-5 can overlap)

**Longest Pole**: App Store review (iOS) - 1-7 days, typically 2-3 days

---

## Timeline Assumptions

### Optimistic Scenario (4 weeks)

```
Week 1:   Phase 0 (Beta Testing) + Phase 1 (Blocker Resolution) in parallel
Week 2:   Phase 2 (Pre-Production Setup)
Week 3:   Phase 3 (Production Launch + Store Submission)
Week 4:   Store Review + Go-Live + Phase 4 (Stabilization begins)
```

**Assumptions**:
- Domain and Apple account approved within 2-3 days
- No major bugs found during beta testing
- Store review completes in 2-3 days
- Payments DEFERRED to later release

---

### Realistic Scenario (6-8 weeks)

```
Weeks 1-2:  Phase 0 (Beta Testing)
Week 3:     Phase 1 (Blocker Resolution)
Week 4:     Phase 2 (Pre-Production Setup)
Week 5:     Phase 3 (Production Launch + Store Submission)
Weeks 6-7:  Store Review (iOS may take 5-7 days)
Week 8:     Go-Live + Phase 4 (Stabilization)
```

**Assumptions**:
- Beta testing takes 2 weeks to gather sufficient feedback
- Apple Developer approval takes 2-3 days
- Store review takes 5-7 days (iOS), 1-3 days (Android)

---

### Conservative Scenario (10-12 weeks)

```
Weeks 1-4:  Phase 0 (Extended Beta Testing + iterations)
Week 5:     Phase 1 (Blocker Resolution)
Weeks 6-7:  Phase 2 (Pre-Production Setup)
Week 8:     Phase 3 (Production Launch + Store Submission)
Weeks 9-10: Store Review + iterations if rejected
Weeks 11-12: Go-Live + Phase 4 (Stabilization)
```

**Assumptions**:
- Beta testing finds significant bugs requiring iteration
- Store submission rejected once, requiring resubmission (adds 1-2 weeks)
- Additional QA rounds needed

---

## Decision Points

### Decision Point 1: End of Phase 0 (Beta Complete)

**Question**: Is beta testing complete? Can we proceed to production?

**Inputs**:
- [Beta Exit Criteria](beta-exit-criteria.md) assessment
- [Beta Tester Tracker](beta-tester-tracker.md) summary
- [QA Execution Log](qa-execution-log.md) final status

**Outcomes**:
- **GO**: Proceed to Phase 1 (Blocker Resolution)
- **EXTEND BETA**: Continue testing for 1-2 more weeks
- **PIVOT**: Significant feature gaps identified, delay production

---

### Decision Point 2: End of Phase 1 (Blockers Resolved)

**Question**: Are critical dependencies resolved? Can we set up production infrastructure?

**Inputs**:
- Domain DNS verification
- Apple Developer account status
- Hosting/database provider confirmation

**Outcomes**:
- **GO**: Proceed to Phase 2 (Pre-Production Setup)
- **BLOCKED**: Wait for external approvals (Apple, DNS propagation)
- **FALLBACK**: Launch Android-only if Apple account blocked

---

### Decision Point 3: End of Phase 2 (Pre-Production Ready)

**Question**: Is production infrastructure ready for launch?

**Inputs**:
- [Launch Readiness Scorecard](launch-readiness.md)
- Infrastructure health checks
- Final QA regression results

**Outcomes**:
- **GO**: Proceed to Phase 3 (Production Launch)
- **NO-GO**: Fix critical issues found in final QA
- **CONDITIONAL GO**: Launch with known issues if low-risk

---

### Decision Point 4: Payment Enablement (Future)

**Question**: When to enable payment features?

**Inputs**:
- Post-launch stability metrics (crash rate, error rate)
- User feedback and retention data
- Stripe/RevenueCat readiness

**Outcomes**:
- **ENABLE NOW**: Sufficient stability, proceed with payments
- **WAIT**: Extend free period to improve retention
- **DEFER INDEFINITELY**: Pivot to ad-supported model

---

## Risks & Mitigations

| ID | Risk | Impact | Likelihood | Mitigation | Owner |
|----|------|--------|------------|------------|-------|
| **R1** | Domain not available | High | Low | Select alternative domain or use subdomain | Product Lead |
| **R2** | Apple Developer approval delayed | High | Medium | Launch Android first, add iOS later | Mobile Lead |
| **R3** | Store submission rejected | Medium | Medium | Review [Store Submission Checklist](store-submission-checklist.md) carefully | Mobile Lead |
| **R4** | LLM API quota exceeded | High | Low | Set up rate limiting, quota alerts | Backend Lead |
| **R5** | Production crash rate > 5% | Critical | Low | Enable Sentry, rollback plan ready | DevOps Lead |
| **R6** | Hosting costs exceed budget | Medium | Medium | Start with smallest tier, monitor usage | Finance Lead |
| **R7** | Beta testing reveals major UX issues | High | Medium | Extend beta phase, iterate design | Product Lead |
| **R8** | Database migration fails in production | Critical | Low | Test migrations on staging, prepare rollback | Backend Lead |
| **R9** | Security vulnerability found post-launch | Critical | Low | Emergency patch process, incident response | Security Lead |
| **R10** | Support volume exceeds capacity | Medium | Medium | Prepare FAQ, auto-responder, escalation plan | Support Lead |

**Related Document**: [Risk Register](risk-register.md)

---

## Success Metrics

### Launch Success (Week 1)

| Metric | Target | Data Source |
|--------|--------|-------------|
| Daily Downloads | ≥ 50 | App Store / Play Store |
| Daily Signups | ≥ 25 | Backend analytics |
| Crash Rate | < 2% | Sentry / Firebase |
| App Store Rating | ≥ 4.0/5 | App Store reviews |
| Support Response Time | < 24 hours | support@ inbox |

### Post-Launch Stability (Week 4)

| Metric | Target | Data Source |
|--------|--------|-------------|
| Weekly Active Users (WAU) | ≥ 100 | Analytics |
| D7 Retention | ≥ 20% | Analytics |
| P0/P1 Bugs Open | 0 | Issue tracker |
| API p95 Latency | < 500ms | Monitoring |

**Detailed Metrics**: See [Release Metrics](release-metrics.md)

---

## Workstream Coordination

### Weekly Sync (During Transition)

**Attendees**: Project Lead, Backend Lead, Mobile Lead, QA Lead, Product Lead

**Agenda**:
1. Phase status review
2. Blocker discussion
3. Decision items
4. Risk updates
5. Next week plan

**Cadence**: Every Monday 10:00 AM during Phase 1-3

---

### Daily Standup (During Phase 3 - Launch Week)

**Attendees**: Core team

**Agenda**:
1. Yesterday's progress
2. Today's plan
3. Blockers

**Cadence**: Daily 9:00 AM during Phase 3

---

## Related Documents

**Planning**:
- [Beta Exit Criteria](beta-exit-criteria.md) - Go/No-Go thresholds
- [Launch Readiness Scorecard](launch-readiness.md) - Production readiness
- [Launch Dependencies](launch-dependencies.md) - Dependency tracking
- [Remaining Work](remaining-work.md) - Incomplete items

**Execution**:
- [PROD_DEPLOY.md](../PROD_DEPLOY.md) - Deployment runbook
- [Launch Day Runbook](launch-day-runbook.md) - Launch execution
- [Free Beta Ops Playbook](free-beta-ops-playbook.md) - Beta operations

**QA**:
- [QA Test Plan](qa-test-plan.md) - Test cases
- [Manual QA Checklist](manual-qa-checklist.md) - Manual testing

**Risk & Compliance**:
- [Risk Register](risk-register.md) - Risk tracking
- [Incident Response](incident-response.md) - Emergency procedures
- [Privacy Compliance Checklist](privacy-compliance-checklist.md) - GDPR/CCPA

**Communication**:
- [Launch Communications](launch-communications.md) - Stakeholder communication
- [Beta Weekly Status Template](beta-weekly-status-template.md) - Status reporting
