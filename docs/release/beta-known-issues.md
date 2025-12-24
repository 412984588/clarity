# Beta Known Issues

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta

---

## Purpose

This document tracks known issues, bugs, and limitations discovered during the Free Beta testing phase. It serves as a transparent communication tool for testers and a prioritization guide for the development team.

**Who uses this document:**
- **Testers**: Check if your issue is already known before reporting
- **Project Team**: Track bug status and plan fixes
- **Support**: Provide workarounds to testers

**Update Cadence**: Updated daily during active beta testing.

---

## Status Legend

| Status | Meaning | Next Action |
|--------|---------|-------------|
| **Open** | Newly reported, not yet triaged | Investigate and prioritize |
| **Investigating** | Under investigation by dev team | Reproduce and diagnose root cause |
| **Fix in Progress** | Actively being worked on | Implement and test fix |
| **Fixed** | Fix merged and available in latest build | Verify with reporter, close after confirmation |
| **Deferred** | Acknowledged but not planned for current beta | Revisit for production or future release |
| **Won't Fix** | Not a bug or out of scope | Document rationale, close |

---

## Known Issues Table

### Critical (P0) - App Unusable

| ID | Area | Description | Impact | Workaround | Status | First Seen | Last Updated | Owner | Notes |
|----|------|-------------|--------|------------|--------|------------|--------------|-------|-------|
| _(No critical issues at this time)_ | - | - | - | - | - | - | - | - | - |

**Target**: 0 P0 issues open. Any P0 issue should be fixed within 24 hours.

---

### High Priority (P1) - Major Feature Broken

| ID | Area | Description | Impact | Workaround | Status | First Seen | Last Updated | Owner | Notes |
|----|------|-------------|--------|------------|--------|------------|--------------|-------|-------|
| _(Example)_ | Solve Flow | Step 4 (Options) freezes on some devices | Cannot complete Solve | Restart app and retry | Investigating | 2025-12-24 | 2025-12-24 | Dev Team | Affects Android 12 only |

**Target**: ≤ 2 P1 issues open. Fix within 3 days.

---

### Medium Priority (P2) - Partial Feature Impact

| ID | Area | Description | Impact | Workaround | Status | First Seen | Last Updated | Owner | Notes |
|----|------|-------------|--------|------------|--------|------------|--------------|-------|-------|
| _(Example)_ | Emotion Detection | Sometimes shows wrong emotion color | Visual confusion, no functional impact | Ignore color, focus on text | Fix in Progress | 2025-12-23 | 2025-12-24 | Dev Team | Fixed in next build |

**Target**: Fix before production launch.

---

### Low Priority (P3) - Minor/Cosmetic

| ID | Area | Description | Impact | Workaround | Status | First Seen | Last Updated | Owner | Notes |
|----|------|-------------|--------|------------|--------|------------|--------------|-------|-------|
| _(Example)_ | UI | Button text cut off on small screens | Visual only | None needed | Deferred | 2025-12-22 | 2025-12-24 | Design | Will fix in UI refresh |

**Target**: Nice-to-have, can defer to production.

---

### Platform-Specific Issues

**Android Only**

| ID | Area | Description | Impact | Workaround | Status | First Seen | Last Updated | Owner | Notes |
|----|------|-------------|--------|------------|--------|------------|--------------|-------|-------|
| _(Example)_ | Install | APK requires "Unknown Sources" permission | Installation friction | Enable in Settings → Security | Open | 2025-12-20 | 2025-12-24 | Infra | Expected for APK distribution |

**iOS Issues** (Not applicable for Free Beta - no iOS build available)

---

### Known Limitations (Not Bugs)

These are intentional constraints during Free Beta:

| ID | Limitation | Reason | Planned Fix | Status |
|----|------------|--------|-------------|--------|
| L-001 | iOS version not available | No Apple Developer Account | After account purchase | Blocked |
| L-002 | No payment/subscription features | Free Beta phase | Deferred until production | Deferred |
| L-003 | No App Store / Play Store distribution | Manual APK only for beta | After store submission approval | Blocked |
| L-004 | Backend may be slow or unavailable | Using dev/staging infrastructure | Production deployment | Blocked |
| L-005 | Limited to 10 devices per user | Beta mode relaxed limit | Production will enforce stricter limits | By Design |
| L-006 | No usage analytics dashboard | Not implemented yet | Future feature | Deferred |

---

## How to Report New Issues

**Before reporting:**
1. Check this document to see if your issue is already known
2. Try the suggested workaround (if available)
3. Restart the app and see if the issue persists

**If your issue is not listed:**
1. Use the [Bug Report Template](bug-report-template.md)
2. Fill in all required fields (especially: steps to reproduce, device info, screenshots)
3. Email to: [designated bug report email]
4. Subject: "BUG - [Brief Description]"

**What happens next:**
1. We'll acknowledge within 24 hours
2. Assign an ID and triage priority (P0/P1/P2/P3)
3. Add to this document with status "Investigating"
4. Update you on progress every 2-3 days
5. Notify you when fixed (with new build link if applicable)

---

## Update Cadence

**During Active Beta** (first 2-4 weeks):
- **Daily**: Update statuses, add new issues
- **Weekly**: Review priorities, close fixed issues, update workarounds

**Post-Beta** (stabilization phase):
- **Weekly**: Update only if new issues reported

**Who updates this document:**
- **Project Lead**: Reviews and approves all entries
- **Dev Team**: Updates technical details and status
- **Support**: Adds workarounds and tester feedback

---

## Statistics (Auto-Calculate Weekly)

**Current Snapshot** (2025-12-24):

| Metric | Count | Target | Status |
|--------|-------|--------|--------|
| **P0 Open** | 0 | 0 | 🟢 |
| **P1 Open** | 1 | ≤ 2 | 🟢 |
| **P2 Open** | 1 | < 10 | 🟢 |
| **P3 Open** | 1 | < 20 | 🟢 |
| **Total Open** | 3 | < 30 | 🟢 |
| **Avg Time to Fix (P0)** | N/A | < 24h | - |
| **Avg Time to Fix (P1)** | N/A | < 3 days | - |

**Historical Trends** (track weekly):

| Week | P0 | P1 | P2 | P3 | Fixed | Notes |
|------|----|----|----|----|-------|-------|
| Week 1 (Dec 22-28) | 0 | 1 | 1 | 1 | 0 | Initial beta launch |

---

## Related Documents

- [Bug Report Template](bug-report-template.md) - How to report new bugs
- [Feedback Triage Workflow](feedback-triage.md) - How bugs are processed
- [Free Beta Tester Guide](free-beta-tester-guide.md) - General testing guide
- [Beta Support Macros](beta-support-macros.md) - Response templates for testers
- [Beta Weekly Status Template](beta-weekly-status-template.md) - Includes bug metrics
- [Beta Exit Criteria](beta-exit-criteria.md) - Bug thresholds for production readiness

---

**Need Help?**
- Check [Free Beta Tester Guide](free-beta-tester-guide.md) for installation and usage help
- Email support: [designated support email]
- Response time: Within 24 hours
