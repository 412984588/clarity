# Beta Support Macros

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta

---

## Purpose

Pre-written response templates for common support scenarios during Free Beta testing. These macros ensure consistent, helpful, and friendly communication with testers while saving time on repetitive responses.

**Who uses this document:**
- **Project Lead**: Primary support responder
- **Dev Team**: When responding to technical questions
- **QA**: When clarifying bug reports

**How to use:**
1. Copy the relevant template
2. Replace `[PLACEHOLDERS]` with actual values
3. Personalize with tester's name and specific details
4. Send via email or support channel

---

## Tone & Guidelines

**General Principles:**
- ✅ **Friendly & Grateful**: Always thank testers for their time
- ✅ **Clear & Concise**: No jargon, simple language
- ✅ **Responsive**: Acknowledge within 24 hours, even if "We're investigating"
- ✅ **Transparent**: Share status honestly (fixed, in progress, deferred)
- ✅ **Proactive**: Offer workarounds, suggest alternatives

**Avoid:**
- ❌ Technical jargon without explanation
- ❌ Dismissive language ("That's not a bug" → "That's expected behavior because...")
- ❌ Vague timelines ("Soon" → "Targeting fix in next build on [date]")
- ❌ Over-promising ("We'll fix everything" → "We'll prioritize based on severity")

---

## Templates

### 1. Acknowledge Bug Report

**Subject**: `Re: BUG - [Bug Title]`

**Message**:
```
Hi [TESTER_NAME],

Thank you for reporting this issue! We've received your bug report and assigned it ID: [BUG_ID].

**What we know so far:**
- Issue: [BRIEF_SUMMARY]
- Severity: [P0/P1/P2/P3]
- Affected: [DEVICES_OR_VERSIONS]

**Next steps:**
- We're investigating the root cause
- I'll update you within [24 hours / 2-3 days] with our findings
- If you discover any additional details, please reply to this email

**In the meantime:**
[WORKAROUND_IF_AVAILABLE, or "Unfortunately, no workaround at this time"]

Thanks again for your help in making Clarity better!

Best,
[YOUR_NAME]
Clarity Team
```

**Placeholders:**
- `[TESTER_NAME]`: Tester's name
- `[BUG_ID]`: Assigned bug ID (e.g., BUG-001)
- `[BRIEF_SUMMARY]`: One-sentence summary
- `[P0/P1/P2/P3]`: Priority level
- `[DEVICES_OR_VERSIONS]`: Scope of impact
- `[WORKAROUND_IF_AVAILABLE]`: Suggested workaround or "None needed"
- `[YOUR_NAME]`: Your name

---

### 2. Request More Info

**Subject**: `Re: BUG - [Bug Title] - Need More Info`

**Message**:
```
Hi [TESTER_NAME],

Thanks for reporting this! To help us investigate, could you please provide a bit more detail?

**What we need:**
1. **Steps to reproduce**: Exact steps you took before the issue occurred
   - Example: "Opened app → Tapped Solve → Selected Emotion → Tapped Step 3"
2. **Screenshots or screen recording**: Visual evidence is super helpful
3. **Device info**:
   - Device model: [e.g., Samsung Galaxy S21]
   - Android version: [e.g., Android 13]
4. **Frequency**: Does this happen every time, or only sometimes?

**What you've told us so far:**
[BRIEF_RECAP_OF_ORIGINAL_REPORT]

**Why we need this:**
[REASON - e.g., "We can't reproduce it on our test devices, so more details will help us pinpoint the cause"]

Reply when you have a chance – no rush! Appreciate your patience.

Best,
[YOUR_NAME]
Clarity Team
```

**Placeholders:**
- `[TESTER_NAME]`
- `[BRIEF_RECAP_OF_ORIGINAL_REPORT]`: Summary of what they reported
- `[REASON]`: Why additional info is needed
- `[YOUR_NAME]`

---

### 3. Provide Workaround

**Subject**: `Re: BUG - [Bug Title] - Workaround Available`

**Message**:
```
Hi [TESTER_NAME],

Good news! While we work on a permanent fix for [BUG_DESCRIPTION], here's a workaround you can use in the meantime:

**Workaround:**
[STEP_BY_STEP_WORKAROUND]

**Example:**
[CONCRETE_EXAMPLE_IF_HELPFUL]

**Limitations:**
[ANY_CAVEATS - e.g., "You'll need to do this each time you restart the app"]

**Permanent fix:**
We're targeting a fix in the next build (expected [DATE_OR_TIMEFRAME]). I'll let you know as soon as it's ready!

Does this workaround work for you? Let me know if you run into any issues.

Thanks for your patience!

Best,
[YOUR_NAME]
Clarity Team
```

**Placeholders:**
- `[TESTER_NAME]`
- `[BUG_DESCRIPTION]`: Brief description
- `[STEP_BY_STEP_WORKAROUND]`: Numbered steps
- `[CONCRETE_EXAMPLE_IF_HELPFUL]`: Optional example
- `[ANY_CAVEATS]`: Limitations or side effects
- `[DATE_OR_TIMEFRAME]`: Expected fix date
- `[YOUR_NAME]`

---

### 4. Fix Shipped

**Subject**: `Re: BUG - [Bug Title] - FIXED in Latest Build`

**Message**:
```
Hi [TESTER_NAME],

Great news! The issue you reported ([BUG_ID]: [BUG_DESCRIPTION]) has been fixed and is now available in the latest build.

**What was fixed:**
[TECHNICAL_SUMMARY_IN_PLAIN_LANGUAGE]

**How to get the fix:**
1. Download the latest APK: [APK_DOWNLOAD_LINK]
2. Build version: [BUILD_VERSION] (dated [BUILD_DATE])
3. Uninstall the old version first (Settings → Apps → Clarity → Uninstall)
4. Install the new APK

**Can you verify?**
Please test the fix when you have a chance and let me know if:
- ✅ Issue is resolved
- ❌ Issue still occurs (with details)

**What's new in this build:**
- Fix for [BUG_DESCRIPTION]
- [OTHER_FIXES_OR_IMPROVEMENTS]

Thanks again for reporting this – your feedback directly improved the app!

Best,
[YOUR_NAME]
Clarity Team
```

**Placeholders:**
- `[TESTER_NAME]`
- `[BUG_ID]`
- `[BUG_DESCRIPTION]`
- `[TECHNICAL_SUMMARY_IN_PLAIN_LANGUAGE]`: What was changed
- `[APK_DOWNLOAD_LINK]`: Direct download link
- `[BUILD_VERSION]`: Version number
- `[BUILD_DATE]`: Build date
- `[OTHER_FIXES_OR_IMPROVEMENTS]`: Other changes in this build
- `[YOUR_NAME]`

---

### 5. Close as Duplicate

**Subject**: `Re: BUG - [Bug Title] - Duplicate of Existing Issue`

**Message**:
```
Hi [TESTER_NAME],

Thanks for reporting this! It looks like this issue is the same as one we're already tracking: [ORIGINAL_BUG_ID] - [ORIGINAL_BUG_TITLE].

**Current status:**
- Status: [Open / Investigating / Fix in Progress]
- Priority: [P0/P1/P2/P3]
- Expected fix: [TIMEFRAME_OR_TBD]
- Workaround: [IF_AVAILABLE]

**What this means:**
We're combining reports to track this issue in one place. I'll make sure your details are added to the original report, and you'll be notified when the fix is ready.

**Check status:**
You can track progress here: [Link to Beta Known Issues doc, or direct link if available]

Appreciate you taking the time to report this!

Best,
[YOUR_NAME]
Clarity Team
```

**Placeholders:**
- `[TESTER_NAME]`
- `[ORIGINAL_BUG_ID]`
- `[ORIGINAL_BUG_TITLE]`
- `[TIMEFRAME_OR_TBD]`
- `[IF_AVAILABLE]`
- `[YOUR_NAME]`

---

### 6. Feature Request Acknowledgement

**Subject**: `Re: FEATURE REQUEST - [Feature Title]`

**Message**:
```
Hi [TESTER_NAME],

Thanks for the feature suggestion! This is exactly the kind of feedback we're looking for.

**Your suggestion:**
[BRIEF_SUMMARY_OF_REQUEST]

**Our thoughts:**
[INITIAL_REACTION - e.g., "This aligns well with our vision" OR "Interesting idea – let us think about how it fits"]

**Next steps:**
- Adding to our feature backlog (ID: [FEATURE_ID])
- We'll prioritize for [Post-Beta / Future Release / TBD]
- I'll keep you posted if we decide to implement it

**In the meantime:**
Keep the ideas coming! Your feedback is shaping the product.

Best,
[YOUR_NAME]
Clarity Team
```

**Placeholders:**
- `[TESTER_NAME]`
- `[BRIEF_SUMMARY_OF_REQUEST]`
- `[INITIAL_REACTION]`
- `[FEATURE_ID]`: Internal tracking ID
- `[YOUR_NAME]`

---

### 7. Out of Scope / Deferred

**Subject**: `Re: [Issue or Request] - Not Planned for Beta`

**Message**:
```
Hi [TESTER_NAME],

Thank you for bringing this up! After discussing with the team, we've decided this is [out of scope for Free Beta / deferred to production].

**Why:**
[CLEAR_REASON - e.g., "This requires iOS version, which we don't have for beta" OR "This is a production-only feature"]

**What this means:**
- We're not ignoring it – just parking it for now
- Status: [Deferred to Production / Out of Scope / Won't Fix]
- If you feel strongly about this, let us know and we'll reconsider

**Alternative (if applicable):**
[SUGGEST_ALTERNATIVE_IF_AVAILABLE]

Appreciate your understanding – and keep the feedback coming!

Best,
[YOUR_NAME]
Clarity Team
```

**Placeholders:**
- `[TESTER_NAME]`
- `[CLEAR_REASON]`
- `[SUGGEST_ALTERNATIVE_IF_AVAILABLE]`
- `[YOUR_NAME]`

---

### 8. Data/Privacy Request

**Subject**: `Re: Data/Privacy Request`

**Message**:
```
Hi [TESTER_NAME],

Thanks for reaching out about your data/privacy request.

**Your request:**
[SUMMARY - e.g., "Delete my account and all data" OR "Export my data"]

**What we'll do:**
[ACTION - e.g., "We'll delete your account and all associated data within 7 days" OR "We'll send you a data export within 48 hours"]

**What data we have:**
- Account info: [Email, device ID]
- Session data: [Solve sessions, timestamps]
- No message text is stored on our servers (processed in real-time only)

**Confirmation:**
I'll email you when this is complete. If you have any questions, reply to this email.

Thanks for being part of the beta!

Best,
[YOUR_NAME]
Clarity Team
```

**Placeholders:**
- `[TESTER_NAME]`
- `[SUMMARY]`
- `[ACTION]`
- `[YOUR_NAME]`

---

## When to Use Which Template

| Scenario | Template | Response Time |
|----------|----------|---------------|
| New bug report received | **1. Acknowledge Bug Report** | Within 24 hours |
| Bug report missing details | **2. Request More Info** | Within 24 hours |
| Known issue with workaround | **3. Provide Workaround** | Within 24 hours |
| Bug fixed in new build | **4. Fix Shipped** | Same day as build release |
| Duplicate report | **5. Close as Duplicate** | Within 24 hours |
| Feature idea submitted | **6. Feature Request Acknowledgement** | Within 48 hours |
| Request not in scope | **7. Out of Scope / Deferred** | Within 48 hours |
| Data/privacy question | **8. Data/Privacy Request** | Within 24 hours (or per legal requirement) |

---

## Customization Tips

**Personalize each response:**
- Use tester's name (not "Hey there" or "Hi user")
- Reference specific details from their report
- Add a personal note if you know the tester well

**Adjust tone based on severity:**
- **P0/Critical**: More urgent, apologetic, faster response
- **P3/Low**: Casual, appreciative, no rush

**Include relevant links:**
- [Beta Known Issues](beta-known-issues.md) - Check status
- [Beta Feedback Form](beta-feedback-form.md) - General feedback
- [Free Beta Tester Guide](free-beta-tester-guide.md) - Installation help

---

## Related Documents

- [Beta Known Issues](beta-known-issues.md) - Track bug status
- [Feedback Triage Workflow](feedback-triage.md) - How to process feedback
- [Bug Report Template](bug-report-template.md) - What testers should submit
- [Free Beta Invite Templates](free-beta-invite-templates.md) - Initial outreach
- [Beta Tester Tracker](beta-tester-tracker.md) - Track tester status
- [Support Playbook](support-playbook.md) - General support guidelines

---

**Need Help?**
- Review [Feedback Triage Workflow](feedback-triage.md) for prioritization rules
- Check [Beta Known Issues](beta-known-issues.md) before responding
- If unsure, consult with the dev team before committing to a timeline
