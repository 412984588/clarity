# Free Beta Ops Playbook

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta (No Payments)

---

## Purpose & Scope

This playbook defines the **day-to-day operations** for managing the Clarity Free Beta. It serves as a quick reference for the team to:
- Execute daily and weekly operational tasks
- Triage and route feedback efficiently
- Monitor quality gates and health metrics
- Communicate status updates
- Make Go/Pause/Stop decisions

**Scope**:
- ✅ Free Beta phase operations (recruitment → testing → wrap-up)
- ✅ Feedback collection and triage workflow
- ✅ Issue tracking and resolution
- ✅ Tester communication and support

**Out of Scope**:
- ❌ Production launch operations (see [Launch Day Runbook](launch-day-runbook.md))
- ❌ Infrastructure setup (see [PROD_DEPLOY.md](../PROD_DEPLOY.md))
- ❌ Payment integration (deferred for Free Beta)

---

## Roles & Responsibilities

Aligned with [Free Beta Launch Checklist](free-beta-launch-checklist.md#roles--owners):

| Role | Daily Responsibilities | Weekly Responsibilities |
|------|------------------------|-------------------------|
| **Project Lead** | Monitor overall progress, make critical decisions | Run weekly check-in, decide Go/Pause/Continue |
| **Dev Lead** | Fix critical bugs, deploy patches | Review bug trends, prioritize backlog |
| **Product Manager** | Triage feedback, respond to testers | Analyze feedback themes, update roadmap |
| **QA Lead** | Verify bug fixes, update [QA Log](qa-execution-log.md) | Run regression tests, sign off on fixes |
| **Support Lead** | Answer tester questions, onboard new testers | Compile FAQ, update [Tester Guide](free-beta-tester-guide.md) |

**On-Call Rotation** (Optional for Free Beta):
- Primary: Dev Lead
- Backup: Project Lead
- Hours: Weekdays 9am-6pm (no 24/7 for beta)

---

## Daily Ops Checklist

Run this checklist every morning at **10:00 AM** during beta:

### 1. Check Tester Activity (5 min)

- [ ] Open [Beta Tester Tracker](beta-tester-tracker.md)
- [ ] Review "Last Seen" column - any testers inactive for 3+ days?
- [ ] Update "Status" column (Active/Inactive/Dropped)
- [ ] **Action**: Send [Day 3 Reminder](free-beta-invite-templates.md#template-3-reminder-day-3) to inactive testers

### 2. Review New Feedback (10 min)

- [ ] Check feedback inbox (email/form responses)
- [ ] Count new submissions since yesterday
- [ ] Quick scan for critical issues (P0/P1)
- [ ] **Action**: Acknowledge receipt within 24 hours

### 3. Triage New Issues (15 min)

- [ ] For each new feedback/bug:
  - [ ] Assign severity (P0/P1/P2/P3) - see [Severity Levels](#severity-levels)
  - [ ] Log in [QA Execution Log](qa-execution-log.md)
  - [ ] Assign owner (Dev/PM/Support)
  - [ ] Set SLA deadline
- [ ] **Action**: Escalate P0 issues immediately to Dev Lead

### 4. Check Open Issues (5 min)

- [ ] Review [QA Execution Log](qa-execution-log.md)
- [ ] Count open issues by severity
- [ ] Identify any SLA breaches (P0 > 24h, P1 > 3 days)
- [ ] **Action**: Chase owners for status updates

### 5. Answer Tester Questions (10 min)

- [ ] Check Slack/email for tester questions
- [ ] Respond within 24 hours or assign to Support Lead
- [ ] Update FAQ if question is common

### 6. Update Tracker (5 min)

- [ ] Update [Beta Tester Tracker](beta-tester-tracker.md) with today's changes
- [ ] Move completed testers to "Completed" status
- [ ] Add notes for any special cases

**Total Time**: ~50 minutes/day

---

## Weekly Ops Checklist

Run this checklist every **Monday at 10:00 AM**:

### 1. Weekly Metrics Review (15 min)

- [ ] Calculate weekly stats:
  - [ ] Active testers (target: 5+)
  - [ ] Completed testers (target: 3+)
  - [ ] New bugs reported (trend: decreasing)
  - [ ] Open bugs by severity (P0: 0, P1: < 3)
  - [ ] Average tester satisfaction (target: 3+/5)

- [ ] Compare to last week - improving or declining?

### 2. Feedback Theme Analysis (20 min)

- [ ] Review all feedback from past 7 days
- [ ] Identify top 3 themes:
  - Most requested features
  - Most confusing parts
  - Most praised features
- [ ] Document in [Remaining Work](remaining-work.md) if actionable

### 3. Bug Trend Analysis (15 min)

- [ ] Group bugs by category (UI, Backend, Solve Flow, etc.)
- [ ] Identify any patterns (e.g., "all P1 bugs are on Android 12")
- [ ] Prioritize fixes for next sprint

### 4. Quality Gates Check (10 min)

- [ ] Evaluate [Quality Gates](#quality-gates-gono-go-criteria)
- [ ] Decision: **Continue / Pause / Stop** beta?
- [ ] Document decision and reasoning

### 5. Tester Communication (15 min)

- [ ] Send weekly update to active testers:
  - Thank them for participation
  - Share what's been fixed
  - Remind about feedback if pending
- [ ] Use template: [Weekly Update](#reporting-template-weekly-update)

### 6. Team Sync (30 min)

- [ ] Weekly standup with Project Lead, Dev Lead, PM, QA
- [ ] Review metrics, issues, decisions
- [ ] Plan next week's priorities
- [ ] Update [Free Beta Launch Checklist](free-beta-launch-checklist.md) milestones

**Total Time**: ~2 hours/week

---

## Feedback → Triage → Fix → Verify Workflow

Aligned with [Feedback Triage](feedback-triage.md):

```
┌─────────────────────┐
│ Feedback Submitted  │
│ (Email/Form/Slack)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 1. LOG ISSUE (24h)  │
│ - Assign ID         │
│ - Record in QA Log  │
│ - Acknowledge tester│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. ASSIGN SEVERITY  │
│ (4h)                │
│ P0/P1/P2/P3         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. DUPLICATE CHECK  │
│ - Search QA Log     │
│ - Link if duplicate │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. PRIORITIZE       │
│ - Assign owner      │
│ - Set SLA deadline  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. IMPLEMENT FIX    │
│ - Dev fixes code    │
│ - Test locally      │
│ - Deploy new APK    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 6. VERIFY FIX       │
│ - QA regression test│
│ - Tester re-tests   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 7. CLOSE & NOTIFY   │
│ - Mark resolved     │
│ - Notify tester     │
│ - Update tracker    │
└─────────────────────┘
```

### Severity Levels

| Severity | Response SLA | Resolution SLA | Example |
|----------|-------------|----------------|---------|
| **P0 Critical** | 1 hour | 24 hours | App crash, data loss, security |
| **P1 High** | 4 hours | 3 days | Major feature broken |
| **P2 Medium** | 24 hours | 1 week | Minor feature issue |
| **P3 Low** | 48 hours | Next release | Cosmetic, typo |

### Escalation Path

```
Tester → Support Lead → PM/Dev Lead → Project Lead
```

- **Support Lead** handles: Questions, onboarding, P3 bugs
- **PM** handles: Feature feedback, prioritization, P2 bugs
- **Dev Lead** handles: Technical bugs, P0/P1 fixes
- **Project Lead** handles: Go/No-Go decisions, resource conflicts

---

## Quality Gates (Go/No-Go Criteria)

Evaluate these gates **weekly** to decide whether to continue beta:

### Green (Continue Beta ✅)

| Metric | Threshold | Current |
|--------|-----------|---------|
| Active testers | ≥ 5 | _[Track weekly]_ |
| P0 bugs open | 0 | _[Track weekly]_ |
| P1 bugs open | ≤ 3 | _[Track weekly]_ |
| Tester satisfaction | ≥ 3/5 average | _[Track weekly]_ |
| Negative feedback rate | < 30% | _[Track weekly]_ |

**Action**: Continue beta, keep recruiting

---

### Yellow (Pause Recruitment ⚠️)

| Metric | Threshold | Current |
|--------|-----------|---------|
| P0 bugs open | 1-2 | _[Track weekly]_ |
| P1 bugs open | 4-5 | _[Track weekly]_ |
| Tester satisfaction | 2-3/5 average | _[Track weekly]_ |
| Negative feedback rate | 30-50% | _[Track weekly]_ |

**Action**:
- Stop recruiting new testers
- Focus on fixing open issues
- Send status update to active testers
- Re-evaluate weekly

---

### Red (Stop Beta 🛑)

| Metric | Threshold | Current |
|--------|-----------|---------|
| P0 bugs open | ≥ 3 | _[Track weekly]_ |
| Critical bug rate | > 30% of testers affected | _[Track weekly]_ |
| Tester satisfaction | < 2/5 average | _[Track weekly]_ |
| Negative feedback rate | > 50% | _[Track weekly]_ |
| Data loss incident | Any occurrence | _[Track immediately]_ |

**Action**:
- **Immediately stop beta**
- Email all testers to stop using app
- Fix critical issues
- Decide: Resume later or pivot approach?

---

## Communication Cadence

Based on [Launch Communications](launch-communications.md):

| Touchpoint | Frequency | Channel | Owner | Template |
|------------|-----------|---------|-------|----------|
| **Daily Update (Internal)** | Daily 6pm | Slack #clarity-beta | PM | [Daily](#reporting-template-daily-update) |
| **Tester Reminder** | Day 3, Day 7 | Email | Support | [Reminder](free-beta-invite-templates.md#template-3-reminder-day-3) |
| **Weekly Update (Internal)** | Every Monday | Slack + Email | PM | [Weekly](#reporting-template-weekly-update) |
| **Weekly Update (Testers)** | Every Friday (optional) | Email | PM | [Tester Update](#reporting-template-tester-weekly-update) |
| **Issue Follow-up** | As needed | Email | Dev/Support | [Follow-up](free-beta-invite-templates.md#template-6-issue-follow-up) |
| **Critical Bug Alert** | Immediate | Slack + Phone | Dev Lead | Ad-hoc |

---

## Reporting Template

### Daily Update (Internal)

Post to Slack #clarity-beta every day at **6:00 PM**:

```
📊 Clarity Beta - Daily Update [Date]

**Today's Activity**:
- Active testers: [X] (↑/↓ from yesterday)
- New feedback: [Y] submissions
- New bugs: [Z] (P0: 0, P1: 1, P2: 2, P3: 1)

**Issues Resolved**:
- [Issue ID]: [Brief description]
- [Issue ID]: [Brief description]

**Blockers**:
- [Any blockers or urgent issues]

**Tomorrow's Plan**:
- [What you'll focus on tomorrow]

🟢/🟡/🔴 Overall Status: [Green/Yellow/Red]
```

---

### Weekly Update (Internal)

Send email to team every **Monday at 11:00 AM**:

```
Subject: Clarity Beta - Week [N] Summary

Hi team,

Here's the weekly summary for Clarity Free Beta:

**Metrics (Week [N])**:
- Total testers invited: [X]
- Active testers: [Y]
- Completed testers: [Z]
- Response rate: [Y+Z]/[X] = [%]

**Feedback Summary**:
- Total feedback: [N] submissions
- Average satisfaction: [X.X]/5
- Top request: [Feature X]
- Top complaint: [Issue Y]

**Bugs**:
- New this week: [X] (P0: 0, P1: 2, P2: 5, P3: 3)
- Fixed this week: [Y]
- Still open: [Z] (P0: 0, P1: 1, P2: 3, P3: 2)

**Quality Gate Status**: 🟢 Green / 🟡 Yellow / 🔴 Red
- [Brief reasoning]

**Next Week's Priorities**:
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

**Blockers/Risks**:
- [Any blockers or risks]

**Action Items**:
- [Owner]: [Action]
- [Owner]: [Action]

Questions? Let's discuss in today's standup.

Cheers,
[PM Name]
```

---

### Tester Weekly Update (Optional)

Send to active testers every **Friday at 5:00 PM**:

```
Subject: Clarity Beta - This Week's Updates 🎉

Hi [Name],

Thanks for testing Clarity this week! Here's what we've been up to:

**What We Fixed**:
- ✅ [Bug X]: [Description]
- ✅ [Bug Y]: [Description]

**What We're Working On**:
- 🔧 [Issue Z]: Expected fix next week

**Your Feedback**:
- We heard you about [specific feedback]
- This is really helpful and we're prioritizing it

**Next Steps**:
- If you haven't already, please try the latest APK: [Link]
- Fill out the feedback form: [Link]

**Questions?**
- Email us: [support email]
- We respond within 24 hours

Thanks again for your help! 🙏

[PM Name]
```

---

## Incident Response (Beta Context)

If a **critical issue (P0)** occurs during beta:

### 1. Detect (Tester reports or team discovers)

- **Who**: Any team member
- **Action**: Immediately post in Slack #clarity-beta with "P0 ALERT"

### 2. Assess (Within 1 hour)

- **Who**: Dev Lead + Project Lead
- **Action**:
  - Confirm severity (is it really P0?)
  - Estimate impact (how many testers affected?)
  - Decide: Fix now or pause beta?

### 3. Communicate (Within 2 hours)

- **Who**: PM
- **Action**:
  - Email affected testers: "We found a critical bug, working on it"
  - Post update in Slack #clarity-beta every 2 hours

### 4. Fix (Within 24 hours)

- **Who**: Dev Lead
- **Action**:
  - Fix code
  - Test locally
  - Deploy new APK
  - Update [QA Log](qa-execution-log.md)

### 5. Verify (Within 48 hours)

- **Who**: QA Lead + affected testers
- **Action**:
  - Regression test
  - Ask affected testers to re-test
  - Confirm resolution

### 6. Close (Within 72 hours)

- **Who**: PM
- **Action**:
  - Email all testers: "Bug fixed, please update to new APK"
  - Mark resolved in tracker
  - Document lessons learned

---

## Tools & Resources

### Required Tools

| Tool | Purpose | Access |
|------|---------|--------|
| **Google Sheets** | [Beta Tester Tracker](beta-tester-tracker.md) | Team editors |
| **Slack #clarity-beta** | Daily updates, team communication | Team members |
| **Email** | Tester communication | PM/Support |
| **GitHub Issues** (or equivalent) | [QA Execution Log](qa-execution-log.md) | Team contributors |
| **APK Download Link** | Distribute builds | Public (but unlisted) |

### Optional Tools

| Tool | Purpose | Status |
|------|---------|--------|
| **Google Forms** | Feedback collection | Optional (vs email) |
| **Notion** | Documentation hub | Optional (vs Markdown) |
| **Sentry** | Crash reporting | Deferred for beta |
| **Mixpanel** | Usage analytics | Deferred for beta |

---

## Handoff & Wrap-up

### End-of-Beta Checklist

When beta ends (after 2-4 weeks):

- [ ] Send [Wrap-up Email](free-beta-invite-templates.md#template-7-wrap-up--exit-survey) to all testers
- [ ] Compile final metrics and feedback summary
- [ ] Archive [Beta Tester Tracker](beta-tester-tracker.md) (anonymize if needed)
- [ ] Export [QA Execution Log](qa-execution-log.md) for future reference
- [ ] Update [Remaining Work](remaining-work.md) with beta learnings
- [ ] Run retrospective meeting with team
- [ ] Decide: Proceed to production or iterate?

### Retrospective Questions

- What went well?
- What didn't go well?
- What surprised us?
- What should we do differently for production launch?
- Top 3 learnings from beta?

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| Free Beta Launch Checklist | `free-beta-launch-checklist.md` | Pre-launch and launch day tasks |
| Free Beta Tester Guide | `free-beta-tester-guide.md` | What testers need to know |
| Free Beta Invite Templates | `free-beta-invite-templates.md` | Communication templates |
| Beta Tester Tracker | `beta-tester-tracker.md` | Tester status tracking |
| Feedback Triage Workflow | `feedback-triage.md` | Triage process and severity |
| Bug Report Template | `bug-report-template.md` | Bug reporting format |
| QA Execution Log | `qa-execution-log.md` | Issue tracking log |
| Launch Communications | `launch-communications.md` | Broader comms strategy |
| Remaining Work | `remaining-work.md` | Backlog and roadmap |
| Release Documentation Hub | `index.md` | All release docs |

---

**Last Updated**: 2025-12-24
**Maintained By**: Product/PM Team
**Review Cadence**: After each beta cycle
