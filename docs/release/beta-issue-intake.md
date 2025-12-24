# Beta Issue Intake Guide

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta

---

## Purpose

This guide helps **Beta testers** understand **where and how to report issues**, what information to include, and what to expect in terms of response times. It serves as the entry point for all Beta feedback channels.

**Use This Guide When:**
- You encounter a bug or crash
- You want to share feedback about the app
- You have a feature request or suggestion
- You need help or have questions

---

## Where to Report

We offer multiple ways to report issues and provide feedback. Choose the method that works best for you:

### 1. GitHub Issue Forms (Recommended)

**Best For:** Structured bug reports, feedback, and feature requests

**How to Access:**
- Visit the [Clarity GitHub Issues](https://github.com/412984588/clarity/issues/new/choose) page
- Select the appropriate issue template:
  - 🐛 **Beta Bug Report** - Report crashes, errors, or broken features
  - 💬 **Beta Feedback** - Share your experience and suggestions
  - ✨ **Beta Feature Request** - Suggest new features or improvements

**Advantages:**
- Pre-formatted templates ensure you provide all necessary details
- Automatic tracking and status updates
- Transparent - you can see responses and resolution progress

**Privacy:** Issue submissions are visible to the Clarity team and public GitHub users. Do not include sensitive personal information.

---

### 2. Beta Feedback Form

**Best For:** Detailed, structured feedback for weekly reports

**How to Access:**
- Use the [Beta Feedback Form Template](beta-feedback-form.md)
- Fill out and send via email or preferred communication channel

**Advantages:**
- Comprehensive - covers all aspects of your experience
- Can be filled out offline
- More detailed than GitHub forms

---

### 3. Direct Message (Slack / WeChat / Email)

**Best For:** Quick questions, urgent issues, or private concerns

**Contact Methods:**
- Slack: [Your Beta Testing Slack Channel] (if applicable)
- WeChat: [Beta Tester WeChat Group] (if applicable)
- Email: [Beta Testing Email Address] (if applicable)

**Advantages:**
- Fast response for urgent issues
- Private communication
- Good for clarifying questions

**Note:** For tracking purposes, critical bugs reported via direct message will be logged as GitHub Issues by the team.

---

### 4. Bug Report Template (Email)

**Best For:** Detailed bug reports with attachments (screenshots, videos)

**How to Access:**
- Use the [Bug Report Template](bug-report-template.md)
- Fill out and send via email with attachments

**Advantages:**
- Detailed step-by-step format
- Easy to attach large files (videos, logs)
- Can be sent via email or messaging apps

---

## What to Include

To help us understand and fix issues quickly, please provide the following information:

### For Bug Reports

| Field | Required | Why It Matters |
|-------|----------|----------------|
| **Bug Title** | ✅ Yes | Helps us quickly identify the issue |
| **Steps to Reproduce** | ✅ Yes | We need to reproduce the bug to fix it |
| **Expected vs Actual Behavior** | ✅ Yes | Clarifies what should happen vs what does happen |
| **Device & OS Version** | ✅ Yes | Many bugs are device/OS-specific |
| **App Version / Build ID** | ⚠️ Recommended | Ensures we're testing the same version |
| **Screenshots / Video** | ⚠️ Recommended | Visual evidence speeds up diagnosis |
| **Severity** | ✅ Yes | Helps us prioritize (see Severity Guide below) |
| **Frequency** | ✅ Yes | Is it always happening or intermittent? |

### For General Feedback

| Field | Required | Why It Matters |
|-------|----------|----------------|
| **What You Liked** | ⚠️ Recommended | Helps us know what's working well |
| **What Was Confusing** | ⚠️ Recommended | Identifies usability issues |
| **Suggestions** | ⚠️ Recommended | Guides future improvements |
| **Satisfaction Rating** | ✅ Yes | Tracks overall sentiment |

### For Feature Requests

| Field | Required | Why It Matters |
|-------|----------|----------------|
| **Feature Description** | ✅ Yes | What you want to see |
| **User Scenario** | ✅ Yes | Why you need it, when you'd use it |
| **Priority** | ⚠️ Recommended | How important is it to you? |
| **Alternatives** | Optional | Current workarounds you're using |

---

## Severity Guide

When reporting a bug, please assign a severity level to help us prioritize. Use this guide:

### P0 - Blocker (Critical)

**What It Means:** App is completely unusable, data loss, or security issue

**Examples:**
- App crashes immediately on launch
- All user data is lost or corrupted
- Security vulnerability (e.g., anyone can access your sessions)

**What Happens:**
- ⏱️ **Response Time:** 1 hour
- 🔧 **Resolution Target:** 24 hours
- 🚨 **Escalation:** Immediate escalation to Dev Lead

**What You Should Do:** Report immediately via **direct message** AND GitHub Issue

---

### P1 - Critical (High)

**What It Means:** Major feature broken, significant impact on usability

**Examples:**
- Solve flow fails at a specific step
- Cannot log in with Google/Apple
- Emotion detection shows wrong colors
- Session history is empty or doesn't load

**What Happens:**
- ⏱️ **Response Time:** 4 hours
- 🔧 **Resolution Target:** 3 days
- 🚨 **Escalation:** If not resolved in 3 days, escalate to Project Lead

**What You Should Do:** Report via **GitHub Issue** (Bug Report form)

---

### P2 - High (Medium)

**What It Means:** Feature partially broken, workaround available

**Examples:**
- UI elements misaligned on certain devices
- Some translations missing (Chinese/Spanish)
- Slow API response time (>5 seconds)
- Minor visual glitches (colors, spacing)

**What Happens:**
- ⏱️ **Response Time:** 24 hours
- 🔧 **Resolution Target:** 1 week
- 🚨 **Escalation:** Review in weekly standup if not resolved

**What You Should Do:** Report via **GitHub Issue** or **Feedback Form**

---

### P3 - Low (Minor)

**What It Means:** Cosmetic issue, very minor annoyance, no workaround needed

**Examples:**
- Typo in button label
- Icon slightly off-center
- Inconsistent font sizes
- Suggested feature improvement (not a bug)

**What Happens:**
- ⏱️ **Response Time:** 48 hours
- 🔧 **Resolution Target:** 2 weeks or deferred to production
- 🚨 **Escalation:** Reviewed in backlog grooming

**What You Should Do:** Report via **GitHub Issue** or **Feedback Form**

---

**Not Sure Which Severity?** When in doubt, choose a **higher severity** (P1 or P2). We'd rather over-prioritize than miss a critical issue.

**Reference:** Full triage workflow details in [Feedback Triage Workflow](feedback-triage.md).

---

## Response Expectations

Here's what you can expect after submitting an issue:

| Severity | Initial Response | Status Update | Resolution Target |
|----------|------------------|---------------|-------------------|
| **P0 - Blocker** | 1 hour | Every 4 hours | 24 hours |
| **P1 - Critical** | 4 hours | Every 24 hours | 3 days |
| **P2 - High** | 24 hours | Every 48 hours | 1 week |
| **P3 - Low** | 48 hours | Weekly | 2 weeks or backlog |

**Initial Response:** Acknowledgment that we received your report and initial assessment.

**Status Update:** Regular updates on progress (e.g., "under investigation", "fix in progress", "deployed in new build").

**Resolution Target:** Our goal for when the issue should be fixed. Actual resolution may vary based on complexity.

---

## Privacy Notes

### What We Collect

When you submit an issue via GitHub, Beta Feedback Form, or direct message, we collect:
- Your contact information (email, WeChat ID, etc.) - **optional**
- Device and app version information
- Bug descriptions, screenshots, or videos you provide
- Your feedback and suggestions

### How We Use It

- To investigate and fix bugs
- To improve the app based on your feedback
- To contact you for follow-up questions or testing
- To measure satisfaction and success metrics

### Who Can See It

- **GitHub Issues:** Visible to the Clarity team and public GitHub users
- **Direct Messages / Feedback Forms:** Visible only to the Clarity team
- **Aggregated Data:** Used in weekly reports (anonymized, no personal info)

### What You Should NOT Include

❌ **Do not include:**
- Passwords or API keys
- Credit card information (not applicable during free beta)
- Highly sensitive personal information (SSN, ID numbers, etc.)

✅ **Safe to include:**
- Screenshots of the app (no sensitive data visible)
- Your email or WeChat ID for follow-up
- Device model and OS version
- General feedback and suggestions

**Reference:** [Privacy Compliance Checklist](privacy-compliance-checklist.md)

---

## Related Documents

### For Beta Testers

- [Free Beta Tester Guide](free-beta-tester-guide.md) - Complete guide for beta testers
- [Beta Feedback Form](beta-feedback-form.md) - Structured feedback template
- [Bug Report Template](bug-report-template.md) - Detailed bug report format
- [Beta Known Issues](beta-known-issues.md) - List of known bugs and workarounds

### For Team (Internal)

- [Feedback Triage Workflow](feedback-triage.md) - Full triage process and SLA definitions
- [QA Execution Log](qa-execution-log.md) - Issue tracking and status
- [Beta Support Macros](beta-support-macros.md) - Response templates for common issues
- [Free Beta Ops Playbook](free-beta-ops-playbook.md) - Daily/weekly ops checklist

---

## Quick Reference

**Need Help Right Away?**
1. Check [Beta Known Issues](beta-known-issues.md) - your issue might already be documented
2. Use direct message (Slack/WeChat/Email) for urgent issues
3. File a GitHub Issue for tracking

**Want to Provide Detailed Feedback?**
1. Use [Beta Feedback Form](beta-feedback-form.md) for structured responses
2. Or file a GitHub Issue using the "Beta Feedback" template

**Found a Bug?**
1. Check [Beta Known Issues](beta-known-issues.md) first
2. File a GitHub Issue using the "Beta Bug Report" template
3. Include screenshots/video if possible

**Have a Feature Idea?**
1. File a GitHub Issue using the "Beta Feature Request" template
2. Describe the use case and why it matters to you

---

**Thank you for helping us improve Clarity!** 🙏

Your feedback is invaluable in making Clarity the best decision-making tool possible.
