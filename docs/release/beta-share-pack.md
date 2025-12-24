# Beta Share Pack

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta

---

## Purpose & Audience

Quick reference for what to share externally with beta testers vs. what should remain internal. Ensures consistent, safe, and helpful communication when onboarding new testers or providing support.

**Who uses this document:**
- **Project Lead**: When sending invites or follow-ups
- **Team Members**: If helping with tester onboarding
- **QA/Support**: When responding to tester questions

**When to use:**
- Onboarding new beta testers
- Responding to "How do I...?" questions
- Sharing updates or new builds
- Providing documentation links

---

## What to Share (Safe for External Distribution)

These documents are tester-facing and can be shared publicly or with anyone testing the app:

| Document | Purpose | When to Share |
|----------|---------|---------------|
| ✅ [Free Beta Tester Guide](free-beta-tester-guide.md) | Installation, testing instructions, features overview | **Always** - Include in every invite |
| ✅ [Beta Feedback Form](beta-feedback-form.md) | Structured feedback collection | **Always** - Include in invite or follow-up |
| ✅ [Bug Report Template](bug-report-template.md) | How to report bugs | **Always** - Include in invite |
| ✅ [Beta Known Issues](beta-known-issues.md) | Current bug status, workarounds | **Proactively** - Share link when onboarding or when testers ask "Is this a known issue?" |
| ✅ [Beta Issue Intake Guide](beta-issue-intake.md) | Where to report issues, severity guide, response times | **Always** - Include in invite or when testers ask how to report bugs |
| ✅ **GitHub Issue Forms** | Structured bug reports and feedback via GitHub | **Always** - Link: [https://github.com/412984588/clarity/issues/new/choose](https://github.com/412984588/clarity/issues/new/choose) |
| ✅ [Privacy Policy](privacy.md) | Data handling, user rights | **Always** - Legal requirement, link in app + tester guide |
| ✅ [Free Beta - Start Here](free-beta-start-here.md) | Quick overview (optional for testers) | **Optional** - For testers who want to understand the bigger picture |

---

## What NOT to Share (Internal Only)

These documents contain internal processes, team workflows, or sensitive information:

| Document | Reason | Audience |
|----------|--------|----------|
| ❌ [Beta Support Macros](beta-support-macros.md) | Internal response templates | **Project Team Only** |
| ❌ [Free Beta Launch Checklist](free-beta-launch-checklist.md) | Internal launch process | **Project Team Only** |
| ❌ [Free Beta Ops Playbook](free-beta-ops-playbook.md) | Daily/weekly ops workflows | **Project Team Only** |
| ❌ [Beta Tester Tracker](beta-tester-tracker.md) | Internal tester status tracking (contains PII) | **Project Team Only** |
| ❌ [Feedback Triage Workflow](feedback-triage.md) | Internal bug prioritization process | **Project Team Only** |
| ❌ [Beta to Production Plan](beta-to-production-plan.md) | Internal roadmap and timelines | **Project Team Only** |
| ❌ [Beta Exit Criteria](beta-exit-criteria.md) | Internal quality gates | **Project Team Only** |
| ❌ [Beta Weekly Status Template](beta-weekly-status-template.md) | Internal reporting | **Project Team Only** |
| ❌ [Remaining Work Report](remaining-work.md) | Internal progress tracking | **Project Team Only** |
| ❌ [Launch Readiness](launch-readiness.md) | Internal Go/No-Go assessment | **Project Team Only** |
| ❌ Any docs in `/docs/spec/`, `/docs/plan/`, `/docs/tasks/` | Technical implementation details | **Dev Team Only** |

---

## Quick Send Checklist

**Before sending anything to a tester:**

- [ ] **1. Remove internal notes**: Check for `INTERNAL:`, `TODO:`, or team-only comments
- [ ] **2. Verify links work**: Test all links in the document (especially APK downloads)
- [ ] **3. Update dates**: Ensure `Last Updated` and version numbers are current
- [ ] **4. Personalize**: Replace placeholders like `[TESTER_NAME]`, `[APK_LINK]`
- [ ] **5. Double-check privacy**: No PII (other testers' emails, names, phone numbers)
- [ ] **6. Test APK link**: Ensure latest build link is valid before sharing
- [ ] **7. Include support contact**: Provide email or support channel for questions

---

## Suggested Package (New Tester Onboarding)

**Recommended bundle to send when inviting a new tester:**

### Email Subject
`Invitation: Help Test Clarity (Free Beta)`

### Email Body (Short Version)
```
Hi [TESTER_NAME],

I'd love your help testing Clarity, a coaching app that helps you think through decisions.
It's in Free Beta right now (no payments, just testing core features).

**What you'll need:**
- Android phone (iOS not available yet)
- 30 minutes to try it out
- Honest feedback!

**Get Started:**
1. Download the APK: [LATEST_APK_LINK]
2. Read the tester guide: [Link to Free Beta Tester Guide]
3. Try a Solve session and share your thoughts

**Important Links:**
- Installation Guide: [free-beta-tester-guide.md](free-beta-tester-guide.md)
- Feedback Form: [beta-feedback-form.md](beta-feedback-form.md)
- Bug Report: [bug-report-template.md](bug-report-template.md)
- Known Issues: [beta-known-issues.md](beta-known-issues.md)
- Privacy Policy: [privacy.md](privacy.md)

**Questions?**
Reply to this email or reach out at [SUPPORT_EMAIL].

Thanks for being part of this!

Best,
[YOUR_NAME]
```

### Attachments (Optional)
- **None needed** - All documents are linked, not attached
- If tester has limited internet: Attach `free-beta-tester-guide.md` as PDF

---

## Suggested Message (Detailed Version)

For a more comprehensive onboarding (e.g., tech-savvy testers or those who want full context):

**Use**: [Free Beta Invite Templates](free-beta-invite-templates.md) - **"Initial Invite (Detailed)"** template

**Customize with**:
- APK download link
- Support email/contact
- Testing timeframe (e.g., "Next 7 days")
- Expected time commitment (e.g., "30-60 minutes total")

---

## Update Scenarios

**Scenario 1: Sharing a new build with existing testers**

**Email Subject**: `New Clarity Build Available - [BUILD_DATE]`

**Message**:
```
Hi [TESTER_NAME],

A new build is ready with bug fixes and improvements!

**What's New:**
- Fixed: [BUG_1]
- Fixed: [BUG_2]
- Improved: [FEATURE]

**Download:**
[LATEST_APK_LINK] (Build: [BUILD_VERSION], Date: [BUILD_DATE])

**Installation:**
Uninstall old version first, then install new APK (see guide: [free-beta-tester-guide.md](free-beta-tester-guide.md))

**What to test:**
- Verify your previous issues are fixed
- Try the improved features
- Submit feedback: [beta-feedback-form.md](beta-feedback-form.md)

**Known Issues:**
Check here before reporting: [beta-known-issues.md](beta-known-issues.md)

Thanks for your continued help!

Best,
[YOUR_NAME]
```

**Share**:
- ✅ APK link
- ✅ Release notes (what's new/fixed)
- ✅ Known issues doc
- ✅ Feedback form

---

**Scenario 2: Responding to "How do I install?"**

**Short Answer**:
```
Hi [TESTER_NAME],

Installation steps are here: [free-beta-tester-guide.md](free-beta-tester-guide.md)

Quick version:
1. Enable "Unknown Sources" (Settings → Security)
2. Download APK: [LATEST_APK_LINK]
3. Tap downloaded file to install
4. Open Clarity app

Stuck? Reply with your error message and I'll help!

Best,
[YOUR_NAME]
```

**Share**:
- ✅ Tester guide link
- ✅ APK link
- ✅ Quick steps

---

**Scenario 3: Tester asks "Is this a bug or expected?"**

**Response**:
```
Hi [TESTER_NAME],

Good question! Let me check...

**Check here first:**
[beta-known-issues.md](beta-known-issues.md) - See if it's already tracked

**If it's not listed:**
Please submit a bug report: [bug-report-template.md](bug-report-template.md)

**Include:**
- What you were doing
- What you expected
- What actually happened
- Screenshots (super helpful!)

I'll investigate and get back to you within 24 hours.

Thanks!
[YOUR_NAME]
```

**Share**:
- ✅ Known issues doc
- ✅ Bug report template

---

## FAQs for Testers (Safe to Share)

**Q: Can I share the app with friends?**
A: Please ask first! We're keeping beta small right now, but if you know someone who'd be a great tester, let us know.

**Q: Is my data safe?**
A: Yes. See our Privacy Policy: [privacy.md](privacy.md). Key points: No message text is stored on servers, account data is encrypted.

**Q: What if I find a security issue?**
A: Email us immediately at [SECURITY_EMAIL]. Do NOT post publicly. We'll prioritize and respond within 24 hours.

**Q: Can I use this for real problems?**
A: Go for it! Just know it's beta quality – there may be bugs. Don't rely on it for mission-critical decisions.

**Q: How long will beta last?**
A: 2-4 weeks, depending on feedback. You'll be the first to know when we launch publicly!

**Q: Will I have to pay later?**
A: Not during beta. If we launch with paid features, beta testers will get [define benefit – e.g., free access for 3 months, discounted pricing, etc.].

---

## Related Documents

### Tester-Facing (Safe to Share)
- [Free Beta Tester Guide](free-beta-tester-guide.md)
- [Beta Feedback Form](beta-feedback-form.md)
- [Bug Report Template](bug-report-template.md)
- [Beta Known Issues](beta-known-issues.md)
- [Privacy Policy](privacy.md)
- [Free Beta - Start Here](free-beta-start-here.md)

### Internal Only (Do NOT Share)
- [Beta Support Macros](beta-support-macros.md)
- [Free Beta Launch Checklist](free-beta-launch-checklist.md)
- [Free Beta Ops Playbook](free-beta-ops-playbook.md)
- [Beta Tester Tracker](beta-tester-tracker.md)
- [Feedback Triage Workflow](feedback-triage.md)

### Onboarding Templates
- [Free Beta Invite Templates](free-beta-invite-templates.md) - Pre-written invite emails

---

**Need Help?**
- Unsure what to share? Ask the Project Lead
- Review [Free Beta Invite Templates](free-beta-invite-templates.md) for pre-approved messages
- Check [Privacy Policy](privacy.md) to understand data handling before answering privacy questions
