# Feedback Triage Workflow

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta

---

## Purpose

This document defines the **triage workflow** for handling feedback, bug reports, and feature requests during the **Free Beta** phase of Clarity. It ensures consistent prioritization, clear ownership, and timely resolution of issues.

**Scope:**
- Bug reports from beta testers
- General feedback and usability issues
- Feature requests and enhancement ideas
- Questions and support requests

**Not Covered:**
- Production incidents (see [Incident Response](incident-response.md))
- Customer support for paying users (N/A during free beta)

---

## Intake Channels

All feedback enters the system through one of these channels:

| Channel | Purpose | Owner | Response SLA |
|---------|---------|-------|--------------|
| **Bug Report Email** | Critical bugs, crashes, data loss | Dev Lead | 24 hours |
| **Feedback Form** | General feedback, usability issues | PM | 48 hours |
| **Beta Feedback Form** | Structured beta tester feedback | PM | 48 hours |
| **Slack/WhatsApp** | Quick questions, minor issues | Support | 4 hours |
| **GitHub Issues** | Technical bugs from dev team | Dev Lead | 24 hours |

**Consolidation:**
All feedback is logged in [QA Execution Log](qa-execution-log.md) regardless of intake channel.

---

## Severity Levels

Every issue is assigned one of these severity levels:

### P0 - Critical

**Definition:** App is completely unusable, data loss, or security vulnerability

**Examples:**
- App crashes on launch for all users
- Data corruption or loss
- Security breach or vulnerability
- Payment processing failure (N/A during free beta)

**SLA:**
- Initial Response: 1 hour
- Resolution: 24 hours
- Owner: Dev Lead

**Escalation:** Immediate escalation to Project Lead

---

### P1 - High

**Definition:** Major feature broken, significant impact on user experience

**Examples:**
- Solve flow fails at a specific step
- Unable to log in with Google OAuth
- Emotion detection not working
- Session history not displaying

**SLA:**
- Initial Response: 4 hours
- Resolution: 3 days
- Owner: Dev Lead

**Escalation:** If not resolved in 3 days, escalate to Project Lead

---

### P2 - Medium

**Definition:** Feature partially broken, workaround available

**Examples:**
- UI element misaligned on certain devices
- Translation missing for Spanish
- Slow API response time (>5 seconds)
- Minor visual glitches

**SLA:**
- Initial Response: 24 hours
- Resolution: 1 week
- Owner: PM (prioritization), Dev (implementation)

**Escalation:** If not resolved in 1 week, review in weekly standup

---

### P3 - Low

**Definition:** Cosmetic issue, typo, minor inconvenience

**Examples:**
- Typo in UI text
- Button color inconsistency
- Unused feature suggestion
- Non-urgent feature request

**SLA:**
- Initial Response: 48 hours
- Resolution: Next release
- Owner: PM

**Escalation:** No escalation needed

---

## Triage Workflow

```
┌──────────────┐
│ Feedback In  │
│ (Email/Form/ │
│ Slack/GitHub)│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 1. Log Issue │◄── Use QA Execution Log
│    (24h)     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 2. Assign    │◄── Assign Severity (P0-P3)
│  Severity    │◄── Assign Owner
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 3. Duplicate │◄── Check if already reported
│    Check     │
└──────┬───────┘
       │
       ├─ Duplicate? ──► Link to original, close
       │
       ▼
┌──────────────┐
│ 4. Prioritize│◄── Add to sprint/backlog
│              │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 5. Implement │◄── Dev fixes issue
│    Fix       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 6. Verify    │◄── QA verifies fix
│              │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 7. Close &   │◄── Notify reporter
│    Notify    │
└──────────────┘
```

---

## Step-by-Step Process

### 1. Log Issue (Within 24 Hours)

**Who:** First responder (Support Lead or PM)

**Actions:**
- [ ] Record issue in [QA Execution Log](qa-execution-log.md)
- [ ] Assign unique Issue ID (format: `FB-YYYYMMDD-###`, e.g., `FB-20251224-001`)
- [ ] Capture all details:
  - Reporter name/email
  - Device/OS version
  - Steps to reproduce
  - Screenshots/logs if available
- [ ] Send acknowledgment to reporter ("Thank you, we've logged issue FB-20251224-001")

---

### 2. Assign Severity (Within 4 Hours)

**Who:** Dev Lead (for technical issues) or PM (for UX issues)

**Actions:**
- [ ] Review issue details
- [ ] Assign severity level (P0-P3)
- [ ] Assign owner based on severity
- [ ] Update issue status in QA Execution Log

**Decision Matrix:**

| Impact | Frequency | Severity |
|--------|-----------|----------|
| High (app unusable) | Affects all users | P0 |
| High | Affects >50% users | P1 |
| Medium (feature broken) | Affects >50% users | P1 |
| Medium | Affects <50% users | P2 |
| Low (cosmetic) | Any frequency | P3 |

---

### 3. Duplicate Check

**Who:** PM or Dev Lead

**Actions:**
- [ ] Search QA Execution Log for similar issues
- [ ] If duplicate found:
  - Link to original issue
  - Add reporter to notification list
  - Mark as duplicate in log
  - Close duplicate issue
- [ ] If unique:
  - Proceed to Step 4

---

### 4. Prioritize

**Who:** PM (in consultation with Dev Lead)

**Actions:**
- [ ] Add to current sprint (P0, P1)
- [ ] Add to backlog (P2, P3)
- [ ] Estimate effort (S/M/L)
- [ ] Consider impact vs effort:
  - High impact, low effort → Do now
  - High impact, high effort → Schedule for next sprint
  - Low impact, low effort → Backlog
  - Low impact, high effort → Defer or reject

---

### 5. Implement Fix

**Who:** Dev assigned to issue

**Actions:**
- [ ] Create branch: `fix/fb-20251224-001-issue-description`
- [ ] Implement fix
- [ ] Add/update tests
- [ ] Create PR
- [ ] Request code review
- [ ] Merge after approval

---

### 6. Verify

**Who:** QA Lead or PM

**Actions:**
- [ ] Test fix in latest build
- [ ] Verify original steps no longer reproduce issue
- [ ] Check for regressions
- [ ] Mark as "Verified" or "Reopen" in QA Execution Log

---

### 7. Close & Notify

**Who:** PM or Support Lead

**Actions:**
- [ ] Update issue status to "Closed - Fixed"
- [ ] Notify reporter:
  ```
  Hi [Reporter],

  Good news! Issue FB-20251224-001 has been fixed and is available in the latest beta build.

  Download the updated APK here: [link]

  Please test and let us know if you encounter any issues.

  Thanks for your feedback!
  ```
- [ ] Remove from active issues list

---

## SLA & Ownership

### Response SLA

| Severity | Initial Response | Resolution Target |
|----------|-----------------|-------------------|
| P0 - Critical | 1 hour | 24 hours |
| P1 - High | 4 hours | 3 days |
| P2 - Medium | 24 hours | 1 week |
| P3 - Low | 48 hours | Next release |

### Default Owners

| Issue Type | Owner |
|------------|-------|
| Crash/Error | Dev Lead |
| UI/UX Issue | PM + Designer (if available) |
| API/Backend | Dev Lead |
| Mobile App | Dev Lead |
| Content/Copy | PM |
| Feature Request | PM (triaged for future) |

---

## Duplicate Handling

**When to Mark as Duplicate:**
- Same root cause as existing issue
- Same steps to reproduce
- Same symptoms, even if slightly different manifestation

**How to Handle:**
- Link duplicate to original (reference Issue ID)
- Consolidate reporter notes into original issue
- Notify duplicate reporter with original Issue ID
- Close duplicate with status "Closed - Duplicate of FB-XXXXXX-XXX"

**When NOT to Mark as Duplicate:**
- Different root cause (even if similar symptoms)
- Affects different platform (Android vs iOS)
- Different severity level

---

## Verification & Closure

### Verification Checklist

- [ ] Original issue no longer reproduces
- [ ] No new regressions introduced
- [ ] Fix works on all supported devices/OS versions
- [ ] Documentation updated (if needed)
- [ ] Reporter notified

### Closure Reasons

| Status | When to Use |
|--------|-------------|
| **Closed - Fixed** | Issue resolved and verified |
| **Closed - Cannot Reproduce** | Unable to reproduce issue, need more info |
| **Closed - Duplicate** | Same as existing issue |
| **Closed - Won't Fix** | Out of scope, low priority, or intentional behavior |
| **Closed - Not a Bug** | Working as designed |

---

## Reporting Cadence

### Daily (During Active Beta)

**Who:** Support Lead
**When:** End of day (6:00 PM)
**Format:** Slack message

```
📊 Daily Beta Feedback Summary (YYYY-MM-DD)

New Issues Today: X
- P0: X (list if any)
- P1: X
- P2: X
- P3: X

Resolved Today: X
Open Issues: X (P0: X, P1: X, P2: X, P3: X)

Top Issue: [Brief description + Issue ID]
```

---

### Weekly (During Active Beta)

**Who:** PM
**When:** Friday end of day
**Format:** Email + [QA Execution Log](qa-execution-log.md) update

```
📈 Weekly Beta Feedback Report (Week of YYYY-MM-DD)

## Summary
- Total Issues Reported: X
- Total Issues Resolved: X
- Open Issues: X

## By Severity
- P0: X reported, X resolved
- P1: X reported, X resolved
- P2: X reported, X resolved
- P3: X reported, X resolved

## Top 3 Issues
1. [Issue ID] - [Description] - [Status]
2. [Issue ID] - [Description] - [Status]
3. [Issue ID] - [Description] - [Status]

## Trend Analysis
- [Insight 1]
- [Insight 2]

## Action Items for Next Week
- [Action 1]
- [Action 2]
```

---

## Related Documents

**Feedback Collection:**
- [Free Beta Tester Guide](free-beta-tester-guide.md) - Tester instructions
- [Beta Feedback Form](beta-feedback-form.md) - Structured feedback template
- [Bug Report Template](bug-report-template.md) - Bug report format

**Tracking & Resolution:**
- [QA Execution Log](qa-execution-log.md) - Issue tracking log
- [QA Test Plan](qa-test-plan.md) - Test cases
- [Manual QA Checklist](manual-qa-checklist.md) - QA verification steps

**Escalation & Metrics:**
- [Incident Response](incident-response.md) - Production incident handling
- [Release Metrics](release-metrics.md) - KPIs and monitoring
- [Launch Communications](launch-communications.md) - Communication templates

---

## Appendix: Example Issue Entries

### Example 1: P0 Critical Bug

```
Issue ID: FB-20251224-001
Reporter: alice@example.com
Date Reported: 2025-12-24 10:30
Severity: P0 - Critical
Owner: Dev Lead
Status: Fixed

Description: App crashes on launch after update
Steps to Reproduce:
1. Install latest APK
2. Open app
3. App crashes immediately

Environment:
- Device: Samsung Galaxy S21
- OS: Android 13
- App Version: Preview build 20251224

Resolution:
- Root Cause: Missing null check in emotion service initialization
- Fix: Added null check in EmotionService.ts:45
- Verified: 2025-12-24 14:00
- Notified Reporter: 2025-12-24 14:15
```

---

### Example 2: P2 Medium Issue

```
Issue ID: FB-20251224-012
Reporter: bob@example.com
Date Reported: 2025-12-24 15:20
Severity: P2 - Medium
Owner: PM
Status: In Progress

Description: Spanish translation missing for "Options" step
Steps to Reproduce:
1. Change device language to Spanish
2. Start Solve flow
3. Reach "Options" step
4. Title still shows "Options" instead of "Opciones"

Environment:
- Device: Google Pixel 6
- OS: Android 14
- App Version: Preview build 20251224

Resolution:
- Assigned to: Dev Lead
- ETA: 2025-12-26
- PR: #99 (pending review)
```

---

**Notes:**
- This workflow applies to **Free Beta phase only**
- For production incident handling, see [Incident Response](incident-response.md)
- All issues must be logged in [QA Execution Log](qa-execution-log.md)
- Feedback trends inform [Remaining Work](remaining-work.md) prioritization
