# Free Beta Launch Checklist

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta (No Payments)

---

## Purpose & Scope

This checklist guides the **Free Beta launch** for Clarity, focusing on early tester validation with friends and internal users **before production release**. Payment features (Stripe/RevenueCat) are intentionally disabled during this phase.

**What This Checklist Covers:**
- ✅ Android APK distribution (preview build)
- ✅ Backend deployment (local or staging environment)
- ✅ Free beta tester onboarding
- ✅ Feedback collection and triage
- ✅ Issue tracking and resolution

**What This Checklist Does NOT Cover:**
- ❌ iOS TestFlight distribution (requires Apple Developer Account)
- ❌ App Store / Play Store submission
- ❌ Production infrastructure setup (domain, hosting)
- ❌ Payment integration (Stripe/RevenueCat)
- ❌ Custom domain configuration

**Related Documents:**
- [Free Beta Tester Guide](free-beta-tester-guide.md) - Comprehensive guide for testers
- [Launch Readiness Scorecard](launch-readiness.md) - Go/No-Go assessment
- [Project Status Summary](project-status-summary.md) - Current project status

---

## Prerequisites (Free Beta Only)

Before launching free beta, ensure these are ready:

| Item | Status | Owner | Notes |
|------|--------|-------|-------|
| **Android Preview APK** | ✅ READY | Dev | Build ID: `88df477f-4862-41ac-9c44-4134aa2b67e2` |
| **Backend Environment** | 🔴 BLOCKED | Dev | Not deployed / TBD (awaiting hosting account) |
| **Test Accounts Created** | ✅ DONE | Dev | Self-register (no pre-created accounts needed) |
| **Beta Tester List** | ⏳ IN PROGRESS | PM | Owner recruiting (see [beta-tester-tracker.md](beta-tester-tracker.md)) |
| **Feedback Channels** | ✅ DONE | PM | GitHub Issue Forms + invite email contact |
| **Bug Triage Process** | ✅ DONE | Dev | Use [feedback-triage.md](feedback-triage.md) |

---

## Roles & Owners

| Role | Responsibilities | Primary Owner |
|------|------------------|---------------|
| **Project Lead** | Overall coordination, Go/No-Go decision | Owner (self) |
| **Dev Lead** | APK distribution, backend deployment, bug fixes | Owner (self) |
| **Product Manager** | Tester recruitment, feedback collection, prioritization | Owner (self) |
| **QA Lead** | Issue verification, regression testing | Owner (self) |
| **Support Lead** | Tester onboarding, FAQ management | Owner (self) |

---

## Assets & Access

### Android APK

**Latest Preview Build:**
- **Build ID**: `5d5e7b57-44f7-4729-b627-e40bc93dbb76`
- **Date**: 2025-12-24
- **Download**: https://expo.dev/artifacts/eas/cwHBq3tAhSrhLcQnewsmpy.apk
- **Dashboard**: https://expo.dev/accounts/cllalala/projects/clarity-mobile/builds/5d5e7b57-44f7-4729-b627-e40bc93dbb76

**Distribution Method:**
- Share direct APK download link via email/Slack
- Provide QR code for quick mobile installation
- Include installation instructions (enable "Install from unknown sources")

### Backend API

**Environment:** Local or Staging

**Config Settings (Free Beta Mode):**
```bash
BETA_MODE=true
PAYMENTS_ENABLED=false
DEBUG=true
```

**Access:**
- Base URL: http://localhost:8000 (or staging URL if deployed)
- Health Check: /health
- API Docs: /docs

### Test Accounts

Create 3-5 test accounts for demos and tester reference:

| Email | Password | Purpose |
|-------|----------|---------|
| demo1@clarity.app | test123 | General demo |
| demo2@clarity.app | test123 | Error scenarios |
| tester@clarity.app | test123 | Tester reference |

---

## Launch Checklist

### Pre-Launch (1 Week Before)

- [ ] **Week -1, Day 1: Prepare Assets**
  - [ ] Verify Android APK download link works
  - [ ] Prepare tester onboarding email template
  - [ ] Create Google Form or email template for feedback
  - [ ] Review [Free Beta Tester Guide](free-beta-tester-guide.md)

- [ ] **Week -1, Day 3: Backend Setup**
  - [ ] Deploy backend to local or staging environment
  - [ ] Configure `BETA_MODE=true` and `PAYMENTS_ENABLED=false`
  - [ ] Verify health endpoints: /health, /health/ready, /health/live
  - [ ] Create test accounts

- [ ] **Week -1, Day 5: Recruit Testers**
  - [ ] Send invites to 5-10 friends/early adopters
  - [ ] Share Free Beta Tester Guide
  - [ ] Provide APK download link and installation instructions
  - [ ] Set expectations: 1-2 week testing period

- [ ] **Week -1, Day 7: Pre-Launch Verification**
  - [ ] Run local smoke tests (see [Local Demo Runbook](local-demo-runbook.md))
  - [ ] Complete one end-to-end Solve flow on Android APK
  - [ ] Verify feedback channels are working
  - [ ] Update [Launch Communications](launch-communications.md) templates

---

### Launch Day (Day 0)

- [ ] **Morning (09:00): Go/No-Go Decision**
  - [ ] Review [Launch Readiness Scorecard](launch-readiness.md)
  - [ ] Confirm all Pre-Launch tasks completed
  - [ ] Make Go/No-Go decision (free beta only, not production)

- [ ] **Midday (12:00): Send Invites**
  - [ ] Email tester invites with APK link
  - [ ] Share in Slack/WhatsApp group if applicable
  - [ ] Provide [Free Beta Tester Guide](free-beta-tester-guide.md)

- [ ] **Afternoon (15:00): Monitor Onboarding**
  - [ ] Check for installation issues
  - [ ] Respond to initial questions
  - [ ] Verify first tester successfully installed APK

- [ ] **Evening (18:00): Day 0 Recap**
  - [ ] Count successful installations
  - [ ] Log any critical issues
  - [ ] Update team on launch status

---

### Week 1 (Days 1-7)

#### Daily Monitoring

- [ ] **Daily 10:00 AM: Check Feedback**
  - [ ] Review new feedback submissions
  - [ ] Triage bugs (see [Feedback Triage](feedback-triage.md))
  - [ ] Respond to tester questions

- [ ] **Daily 6:00 PM: End-of-Day Summary**
  - [ ] Count active testers
  - [ ] Log new bugs/issues
  - [ ] Update [QA Execution Log](qa-execution-log.md)

#### Weekly Milestones

- [ ] **Day 3: Mid-Week Check-in**
  - [ ] Send tester survey (satisfaction, issues encountered)
  - [ ] Review feedback trends
  - [ ] Prioritize top 3 issues for fixes

- [ ] **Day 7: Week 1 Retrospective**
  - [ ] Gather all feedback
  - [ ] Analyze bug severity distribution
  - [ ] Plan fixes for Week 2
  - [ ] Send thank-you email to testers
  - [ ] Update [Remaining Work](remaining-work.md) with learnings

---

## Communications

All communication templates and channels are defined in:
- [Launch Communications](launch-communications.md) - Email templates, Slack messages, escalation paths

**Key Channels:**
- **Email**: Primary channel for tester invites and feedback
- **Slack/WhatsApp**: Quick Q&A and issue reporting
- **Google Form**: Structured feedback collection (optional)

**Message Templates:**
- Tester Invite Email (see launch-communications.md)
- Daily Update Template (see launch-communications.md)
- Issue Escalation Template (see launch-communications.md)

---

## Feedback & Triage

All feedback and bug reports follow this workflow:

**Intake → Triage → Prioritize → Fix → Verify → Close**

Detailed process documented in:
- [Feedback Triage](feedback-triage.md) - Triage workflow, severity levels, SLA
- [Bug Report Template](bug-report-template.md) - Standard bug report format
- [QA Execution Log](qa-execution-log.md) - Issue tracking and resolution log

**Severity Levels:**
- **Critical (P0)**: App crash, data loss, security issue - Fix within 24 hours
- **High (P1)**: Major feature broken - Fix within 3 days
- **Medium (P2)**: Minor feature issue - Fix within 1 week
- **Low (P3)**: Cosmetic issue - Fix in next release

---

## Monitoring & KPIs

Track these metrics during free beta:

**User Engagement:**
- Number of APK downloads
- Number of active users (daily/weekly)
- Number of Solve sessions created
- Average session duration

**Quality Metrics:**
- Number of bugs reported (by severity)
- Average bug resolution time
- Tester satisfaction rating (1-5 scale)

**Detailed metrics defined in:**
- [Release Metrics](release-metrics.md) - Full list of KPIs and alert thresholds

**Monitoring Tools:**
- Backend logs (manual review for free beta)
- Crash reports (local logs only, no Sentry during beta)
- Feedback forms (manual review)

---

## Pause / Rollback Criteria

**When to Pause Beta:**

If any of these conditions occur, pause beta and stop recruiting new testers:

| Condition | Action |
|-----------|--------|
| **Critical Bug Rate > 30%** | More than 30% of testers report critical bugs | Pause immediately, fix critical issues |
| **App Crash Rate > 20%** | More than 20% of testers experience crashes | Pause, investigate root cause |
| **Negative Feedback > 50%** | More than 50% of testers rate experience as "Poor" (1-2 stars) | Pause, reassess core features |
| **Data Loss Incident** | Any instance of user data loss or corruption | Pause immediately, investigate |
| **Security Vulnerability** | Any security issue reported | Pause immediately, fix before resuming |

**Rollback Process (Free Beta):**

Since this is a beta (no production deployment), "rollback" means:
1. Stop sharing APK download link
2. Email all testers to stop using the app
3. Fix issues in a new build
4. Re-invite testers with updated APK

**No formal rollback needed** - just deploy a new APK when ready.

---

## Success Criteria (Week 1)

**Minimum Success:**
- [ ] At least 5 testers installed APK
- [ ] At least 3 testers completed a full Solve flow
- [ ] No critical (P0) bugs remain open
- [ ] Average tester satisfaction ≥ 3/5

**Stretch Goals:**
- [ ] 10+ testers installed APK
- [ ] 5+ testers completed multiple Solve flows
- [ ] No high (P1) bugs remain open
- [ ] Average tester satisfaction ≥ 4/5

---

## Related Documents

**Before Launch:**
- [Project Status Summary](project-status-summary.md)
- [Launch Readiness Scorecard](launch-readiness.md)
- [Launch Dependencies](launch-dependencies.md)

**During Launch:**
- [Free Beta Tester Guide](free-beta-tester-guide.md)
- [Free Beta Invite Templates](free-beta-invite-templates.md)
- [Beta Share Pack](beta-share-pack.md)
- [Beta Tester Tracker](beta-tester-tracker.md)
- [Free Beta Ops Playbook](free-beta-ops-playbook.md)
- [Beta Release Notes Template](beta-release-notes-template.md)
- [Beta Known Issues](beta-known-issues.md)
- [Beta Support Macros](beta-support-macros.md)
- [Launch Communications](launch-communications.md)
- [Feedback Triage](feedback-triage.md)
- [Bug Report Template](bug-report-template.md)

**After Launch:**
- [QA Execution Log](qa-execution-log.md)
- [Release Metrics](release-metrics.md)
- [Remaining Work](remaining-work.md)

---

**Notes:**
- This is a **Free Beta** launch, not a production launch
- Payment features are intentionally disabled
- iOS is NOT available (requires Apple Developer Account)
- This phase focuses on feature validation and bug discovery
- Target duration: 2-4 weeks before production decision
