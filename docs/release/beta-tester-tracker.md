# Beta Tester Tracker

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta (No Payments)

---

## Purpose

This document serves as a **live tracker** for managing Free Beta testers. Use it to:
- Track tester recruitment and onboarding status
- Monitor testing progress and engagement
- Record key feedback and issues per tester
- Assign ownership for follow-ups
- Maintain tester contact information

**Who should use this:**
- Product Manager: Track overall beta progress
- Dev Lead: Identify testers reporting bugs
- Support Lead: Follow up on specific tester questions

**Update frequency**: Daily during beta (or after each significant tester interaction)

---

## Data Fields (Table Headers)

| Field | Description | Example Values |
|-------|-------------|----------------|
| **Tester ID** | Unique identifier for the tester | T001, T002, T003 |
| **Name** | Tester's name or nickname | John D., Sarah K., Tester #5 |
| **Contact** | Email or phone for follow-ups | john@example.com, +1-555-1234 |
| **Device** | Device model | Samsung S21, Pixel 7, OnePlus 9 |
| **OS** | Android version | Android 13, Android 14 |
| **Build** | APK build ID they're testing | `88df477f` (short form) |
| **Invited** | Date invitation sent | 2025-12-24 |
| **Started** | Date they first opened the app | 2025-12-25 (or "Not yet") |
| **Status** | Current testing status | Active, Inactive, Dropped, Completed |
| **Last Seen** | Last activity/login date | 2025-12-26 |
| **Key Feedback** | Summary of their main feedback | "Loves emotion feature, confused by Step 3" |
| **Open Issues** | Count of bugs they reported | 2 bugs (1 P1, 1 P2) |
| **Owner** | Who's responsible for follow-up | PM, Dev, Support |
| **Notes** | Any additional context | "Friend of founder, willing to test long-term" |

---

## Tracker Table (Template)

| Tester ID | Name | Contact | Device | OS | Build | Invited | Started | Status | Last Seen | Key Feedback | Open Issues | Owner | Notes |
|-----------|------|---------|--------|----|----|---------|---------|--------|-----------|--------------|-------------|-------|-------|
| T001 | John D. | john@example.com | Samsung S21 | Android 13 | `88df477f` | 2025-12-20 | 2025-12-21 | Active | 2025-12-23 | "Emotion feature is cool" | 0 | PM | Friend of founder |
| T002 | Sarah K. | sarah.k@example.com | Pixel 7 | Android 14 | `88df477f` | 2025-12-20 | Not yet | Inactive | N/A | N/A | 0 | Support | Sent reminder on Day 3 |
| T003 | Alex T. | alex.tech@example.com | OnePlus 9 | Android 13 | `88df477f` | 2025-12-20 | 2025-12-20 | Completed | 2025-12-22 | "Great flow, minor UI bugs" | 2 (P2) | Dev | Submitted full feedback |
| T004 | Maria L. | maria@example.com | Xiaomi 12 | Android 12 | `88df477f` | 2025-12-21 | 2025-12-21 | Active | 2025-12-24 | "Confused by Reframe step" | 1 (P1) | PM | Non-tech user |
| T005 | David W. | david@example.com | Samsung A52 | Android 13 | `88df477f` | 2025-12-21 | Not yet | Inactive | N/A | N/A | 0 | Support | No response after Day 7 |
| T006 | Emily C. | emily.chen@example.com | Pixel 6 | Android 14 | `88df477f` | 2025-12-22 | 2025-12-22 | Active | 2025-12-24 | "Works well overall" | 0 | PM | Tech background |
| T007 | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

**Instructions**:
- Copy this table to a spreadsheet (Google Sheets, Excel, Notion) for live editing
- Add new rows as you recruit more testers
- Update "Status" and "Last Seen" daily
- Link "Open Issues" to [QA Execution Log](qa-execution-log.md) or bug tracker

---

## Status Legend

| Status | Definition | When to Use | Next Action |
|--------|------------|-------------|-------------|
| **Active** | Tester is actively testing | Logged in within last 3 days | Monitor feedback, thank them |
| **Inactive** | Tester hasn't started or stopped testing | No activity for 3+ days | Send reminder (Day 3/7) |
| **Dropped** | Tester explicitly quit or unresponsive | No response after Day 7 reminder | Remove from active list |
| **Completed** | Tester finished testing + submitted feedback | Filled out feedback form | Send thank-you email |
| **Blocked** | Tester wants to test but has technical issues | Can't install APK, login issues | Provide technical support |

**Color Coding (Optional for Spreadsheets)**:
- 🟢 **Active** - Green
- 🟡 **Inactive** - Yellow
- 🔴 **Dropped** - Red
- ✅ **Completed** - Blue/Green
- ⚠️ **Blocked** - Orange

---

## Usage Examples

### Example 1: Recruiting New Tester

1. Add new row with:
   - Tester ID: T008
   - Name: New Tester
   - Contact: newtester@example.com
   - Status: **Invited**
   - Owner: PM

2. Send invitation using [Invite Template](free-beta-invite-templates.md#template-1-invite-first-ask)

3. Update "Invited" date when sent

### Example 2: Tester Starts Testing

1. Tester emails "I installed the app!"
2. Update:
   - Started: 2025-12-24
   - Status: **Active**
   - Device: (ask them or check logs)
   - OS: (ask them or check logs)

3. Send [Welcome Email](free-beta-invite-templates.md#template-2-acceptance--welcome)

### Example 3: Tester Reports Bug

1. Tester submits bug report
2. Update:
   - Open Issues: 1 (P1)
   - Key Feedback: "App crashes on Option 3"
   - Owner: Dev

3. Dev investigates, logs in [QA Execution Log](qa-execution-log.md)

4. After fix, send [Issue Follow-up](free-beta-invite-templates.md#template-6-issue-follow-up)

### Example 4: Tester Completes Testing

1. Tester submits [Feedback Form](beta-feedback-form.md)
2. Update:
   - Status: **Completed**
   - Key Feedback: (summarize their main points)

3. Send [Thank You Email](free-beta-invite-templates.md#template-5-thank-you--feedback-request)

### Example 5: Inactive Tester

1. Check "Last Seen" - no activity for 4 days
2. Update Status: **Inactive**
3. Send [Day 3 Reminder](free-beta-invite-templates.md#template-3-reminder-day-3)

4. If no response after 7 days:
   - Update Status: **Dropped**
   - Remove from active follow-up list

---

## Summary Statistics (Auto-Calculate in Spreadsheet)

Add these formulas at the bottom of your tracker:

| Metric | Formula (Google Sheets) | Target |
|--------|-------------------------|--------|
| **Total Invited** | `=COUNTA(A:A)-1` | 10+ |
| **Active Testers** | `=COUNTIF(I:I,"Active")` | 5+ |
| **Completed** | `=COUNTIF(I:I,"Completed")` | 3+ |
| **Dropped** | `=COUNTIF(I:I,"Dropped")` | < 30% |
| **Response Rate** | `=(Active + Completed) / Total Invited` | > 50% |
| **Open Issues Total** | `=SUM(L:L)` | Decreasing over time |

**Dashboard View (Optional)**:
- Create a separate sheet with charts showing:
  - Status distribution (pie chart)
  - Tester activity over time (line chart)
  - Issues reported per tester (bar chart)

---

## Privacy Notes

**⚠️ IMPORTANT - Handle with Care**

This tracker contains **Personally Identifiable Information (PII)**:
- Names
- Email addresses
- Phone numbers

**Best Practices**:
- ✅ Store in a secure, access-controlled location (Google Drive with restricted permissions)
- ✅ Only share with team members who need it
- ✅ Do NOT commit this file to Git if it contains real data
- ✅ Use ".gitignore" to exclude tracker files
- ✅ Delete or anonymize data after beta ends (or per privacy policy)

**GDPR/CCPA Compliance**:
- Testers have the right to access their data
- Testers can request deletion of their data
- Document retention policy: Retain indefinitely during beta; delete on user request or 90 days after beta ends

**Template vs Live Data**:
- This file (`beta-tester-tracker.md`) is a **template** for documentation
- Create a **separate spreadsheet** for live tester data (e.g., `beta-tester-tracker-2025.xlsx`)
- Keep live data out of version control

---

## Maintenance Schedule

| Task | Frequency | Owner | Notes |
|------|-----------|-------|-------|
| **Update "Last Seen"** | Daily | Support | Check backend logs or ask testers |
| **Update "Status"** | Daily | PM | Based on tester activity |
| **Review "Open Issues"** | Daily | Dev | Sync with [QA Log](qa-execution-log.md) |
| **Send reminders** | Day 3, Day 7 | PM/Support | Use [Reminder Templates](free-beta-invite-templates.md) |
| **Weekly summary** | Every Monday | PM | Report to team: Active/Completed/Issues |
| **End-of-beta cleanup** | After beta ends | PM | Archive data, anonymize if needed |

---

## Integration with Other Documents

| Document | How to Use Together |
|----------|---------------------|
| [Free Beta Tester Guide](free-beta-tester-guide.md) | Send to all testers in "Started" status |
| [Invite Templates](free-beta-invite-templates.md) | Use when updating "Invited" or "Status" |
| [Feedback Form](beta-feedback-form.md) | Link to testers in "Active" status |
| [Bug Report Template](bug-report-template.md) | Link to testers reporting issues |
| [QA Execution Log](qa-execution-log.md) | Cross-reference "Open Issues" with QA log |
| [Feedback Triage](feedback-triage.md) | Triage bugs reported by testers |
| [Free Beta Launch Checklist](free-beta-launch-checklist.md) | Use tracker to verify recruitment milestones |

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| Free Beta Tester Guide | `free-beta-tester-guide.md` | What testers need to know |
| Free Beta Invite Templates | `free-beta-invite-templates.md` | Communication templates |
| Beta Feedback Form | `beta-feedback-form.md` | Structured feedback collection |
| Bug Report Template | `bug-report-template.md` | Bug reporting format |
| Feedback Triage Workflow | `feedback-triage.md` | How to process feedback |
| QA Execution Log | `qa-execution-log.md` | Issue tracking |
| Free Beta Launch Checklist | `free-beta-launch-checklist.md` | Launch execution |
| Release Documentation Hub | `index.md` | All release docs |

---

## Export & Backup

**Recommended Setup**:
1. Create a Google Sheet based on this template
2. Share with team (Editor access for PM/Dev/Support)
3. Enable version history (Google Sheets auto-saves)
4. Export weekly snapshot to CSV for backup

**Backup Schedule**:
- Weekly: Export to CSV and save to project folder (excluded from Git)
- End of beta: Final export + anonymization

**Anonymization Steps (Post-Beta)**:
1. Replace names with Tester IDs only
2. Remove email/phone columns
3. Keep Device/OS/Feedback for analysis
4. Archive anonymized version for future reference

---

**Last Updated**: 2025-12-24
**Maintained By**: Product/PM Team
**Review Cadence**: Daily during beta
