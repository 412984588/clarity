# Beta Release Notes Template

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta (No Payments)

---

## Purpose

This template provides a standard format for creating **beta release notes** when distributing new APK builds to testers. Use it to communicate what's changed, what's fixed, and what's still in progress.

**When to Use**:
- Deploying a new beta APK build
- Sending update notifications to testers
- Documenting iteration progress
- Providing transparency about bug fixes

**Audience**:
- Free Beta testers
- Internal team members

**Distribution Channels**:
- Email to testers
- Slack #clarity-beta
- Include in [Tester Tracker](beta-tester-tracker.md) notes
- Attach to APK download link

---

## Template Structure

Copy the template below and fill in the bracketed placeholders `[...]`.

---

# Clarity Beta - Release Notes

**Version**: [e.g., 1.0.1-beta]
**Date**: [e.g., 2025-12-24]
**Build ID**: [e.g., 88df477f-4862-41ac-9c44-4134aa2b67e2 (first 8 chars: 88df477f)]
**APK Download**: [e.g., https://expo.dev/artifacts/eas/hUhRm9YvGcYz9Jqj3AVQnY.apk]

---

## 🎉 Highlights

[1-2 sentence summary of what's most important in this release]

**Example**:
> This release fixes the critical app crash issue in the Options step and improves the emotion detection accuracy. We also added dark mode support based on your feedback!

---

## ✨ What's New

[List new features added in this release]

- **[Feature Name]**: [Brief description]
  - Example: **Dark Mode**: Toggle dark mode on/off in Settings → Appearance

- **[Feature Name]**: [Brief description]
  - Example: **Session Export**: Export your session history as JSON from Settings

---

## 🔧 Improved

[List improvements to existing features]

- **[Feature/Area]**: [What was improved and why]
  - Example: **Emotion Detection**: Improved keyword recognition for Spanish and Chinese

- **[Feature/Area]**: [What was improved and why]
  - Example: **Solve Flow**: Reduced loading time between steps by 50%

- **[Feature/Area]**: [What was improved and why]
  - Example: **UI**: Increased font size in Settings for better readability

---

## 🐛 Fixed

[List bugs fixed in this release - reference bug IDs if available]

- **[Bug ID/Title]**: [What was fixed]
  - Example: **QA-001**: Fixed app crash when tapping Option 3 card

- **[Bug ID/Title]**: [What was fixed]
  - Example: **QA-005**: Fixed emotion background not changing for Spanish keywords

- **[Bug ID/Title]**: [What was fixed]
  - Example: **QA-012**: Fixed session history not showing after logout/login

---

## ⚠️ Known Issues

[List issues that are NOT fixed yet - set expectations]

- **[Issue Title]**: [Description and workaround if available]
  - Example: **Long Problem Text**: Very long problem descriptions (> 500 chars) may cause slow loading. **Workaround**: Keep problem statements concise.

- **[Issue Title]**: [Description and workaround if available]
  - Example: **Google OAuth on Android 12**: Google sign-in may fail on some Android 12 devices. **Workaround**: Use email/password sign-up instead.

---

## 📢 Call for Feedback

We need your help testing this release! Please focus on:

- **[Test Area 1]**: [What to test]
  - Example: **Dark Mode**: Try switching between light/dark mode and report any visual glitches

- **[Test Area 2]**: [What to test]
  - Example: **Session Export**: Export your data and verify it contains all your sessions

**How to Report Issues**:
- Use [Bug Report Template](bug-report-template.md) for critical bugs
- Use [Feedback Form](beta-feedback-form.md) for general feedback
- Email: [support@clarity.app] or reply to this email

---

## 📥 How to Update

### Option 1: Download New APK (Recommended)

1. Uninstall the old version (your data will be safe if you're logged in)
2. Download new APK: [APK Download Link]
3. Install the new APK
4. Log back in with your account

### Option 2: Keep Old Version

- You can continue using the old version
- But you won't get bug fixes or new features
- We recommend updating for the best experience

---

## 🙏 Thank You

Thank you for testing Clarity and providing valuable feedback! Your reports directly shaped this release.

**Special Thanks To**:
- [Tester Name] for reporting [Bug X]
- [Tester Name] for suggesting [Feature Y]

Questions? Reach out anytime: [support email]

---

**Next Release**: [Expected date or "TBD"]

---

# Example: Filled Template

Below is a **complete example** of how the template looks when filled out:

---

# Clarity Beta - Release Notes

**Version**: 1.0.1-beta
**Date**: 2025-12-26
**Build ID**: a1b2c3d4-5678-90ef-ghij-klmnopqrstuv (short: a1b2c3d4)
**APK Download**: https://expo.dev/artifacts/eas/example-apk-link.apk

---

## 🎉 Highlights

This release fixes the critical app crash in the Options step and adds dark mode support. We also improved Spanish emotion detection based on your feedback!

---

## ✨ What's New

- **Dark Mode**: Toggle dark mode on/off in Settings → Appearance. The app now respects your system theme preference.

- **Session Export**: Export all your session data as JSON from Settings → Export Account Data. Useful for backup or sharing with support.

---

## 🔧 Improved

- **Emotion Detection**: Improved keyword recognition for Spanish ("ansioso", "preocupado") and Chinese ("焦虑", "担心").

- **Solve Flow**: Reduced loading time between steps by ~50%. Step transitions should feel much smoother now.

- **UI**: Increased font size in Settings from 14px to 16px for better readability on smaller devices.

---

## 🐛 Fixed

- **QA-001**: Fixed app crash when tapping Option 3 card in the Solve flow (affected 30% of testers). Root cause: null pointer exception in option expansion.

- **QA-005**: Fixed emotion background not changing for Spanish anxious keywords like "estoy ansioso". The gradient now correctly shifts to warm tones.

- **QA-012**: Fixed session history not showing after logout and login. Sessions now persist correctly across authentication cycles.

- **QA-018**: Fixed "Next" button being cut off on smaller screens (< 5.5 inches). Button now has proper padding.

---

## ⚠️ Known Issues

- **Long Problem Text**: Very long problem descriptions (> 500 characters) may cause slow loading in the Clarify step. **Workaround**: Keep problem statements concise (< 300 chars recommended).

- **Google OAuth on Android 12**: Google sign-in may fail intermittently on some Android 12 devices. **Workaround**: Use email/password sign-up instead. We're investigating the root cause.

- **Offline Mode**: App does not gracefully handle offline scenarios yet. If you lose connection mid-session, the app may hang. **Workaround**: Ensure stable WiFi/data before starting a session.

---

## 📢 Call for Feedback

We need your help testing this release! Please focus on:

- **Dark Mode**: Try switching between light/dark mode in Settings. Report any UI elements that don't render correctly (e.g., text hard to read, buttons invisible).

- **Spanish Emotion Detection**: If you speak Spanish, try the app in Spanish and see if emotion backgrounds change correctly for anxious phrases like "estoy ansioso" or calm phrases like "estoy tranquilo".

- **Session Export**: Go to Settings → Export Account Data and download the JSON file. Verify it contains all your sessions with timestamps.

**How to Report Issues**:
- **Critical bugs** (app crash, data loss): Use [Bug Report Template](bug-report-template.md)
- **General feedback**: Use [Feedback Form](beta-feedback-form.md)
- **Quick questions**: Reply to this email or contact [support@clarity.app]

---

## 📥 How to Update

### Option 1: Download New APK (Recommended)

1. Uninstall the old version from your device
   - Your data is safe if you're logged in with email/Google
2. Download the new APK: https://expo.dev/artifacts/eas/example-apk-link.apk
3. Install the new APK (you may need to enable "Install from unknown sources")
4. Open the app and log back in
5. Your sessions and account data will be restored

### Option 2: Keep Old Version

- You can continue using v1.0.0-beta
- But you won't get the crash fix or new features
- We strongly recommend updating to avoid the Options step crash

---

## 🙏 Thank You

Thank you for testing Clarity and providing valuable feedback! Your reports directly shaped this release.

**Special Thanks To**:
- **John D.** for reporting the Option 3 crash (QA-001) with detailed reproduction steps
- **Maria L.** for suggesting dark mode and providing mockups
- **Alex T.** for identifying the Spanish emotion detection bug (QA-005)

Your contributions are making Clarity better for everyone. 🙏

Questions? Reach out anytime: support@clarity.app

---

**Next Release**: Tentatively 2025-12-30 (will include iOS offline mode fix and performance improvements)

---

## Usage Guidelines

### When to Send Release Notes

| Scenario | Send Release Notes? | Audience |
|----------|---------------------|----------|
| **Major bug fix** (P0/P1) | ✅ Yes | All active testers |
| **New feature added** | ✅ Yes | All active testers |
| **Minor bug fixes only** (P2/P3) | ⏳ Optional | Can batch into weekly update |
| **Internal testing build** | ❌ No | Internal team only |
| **No user-facing changes** | ❌ No | N/A |

### Timing

- Send release notes **same day** as APK is available
- Morning (9-10am) is best for tester engagement
- Avoid Friday afternoons or weekends (testers may miss it)

### Length

- Keep it concise: **1-2 pages max**
- Use bullet points, not paragraphs
- Prioritize most important changes at the top

### Tone

- **Friendly and transparent**: Acknowledge issues, celebrate fixes
- **Appreciative**: Thank testers for their contributions
- **Actionable**: Tell them what to test and how to report

---

## Checklist Before Sending

Before sending release notes to testers:

- [ ] All placeholders `[...]` filled in
- [ ] APK download link tested and working
- [ ] Build ID matches the APK you're distributing
- [ ] "Fixed" section references actual QA log entries
- [ ] "Known Issues" lists real unresolved bugs
- [ ] "Call for Feedback" has specific test areas
- [ ] Spell-check and grammar-check done
- [ ] Reviewed by at least 1 team member
- [ ] [Beta Tester Tracker](beta-tester-tracker.md) updated with new build ID

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| Free Beta Tester Guide | `free-beta-tester-guide.md` | What testers need to know |
| Beta Feedback Form | `beta-feedback-form.md` | Feedback collection template |
| Bug Report Template | `bug-report-template.md` | Bug reporting format |
| QA Execution Log | `qa-execution-log.md` | Issue tracking log |
| Free Beta Ops Playbook | `free-beta-ops-playbook.md` | Daily/weekly ops tasks |
| Free Beta Invite Templates | `free-beta-invite-templates.md` | Communication templates |
| Beta Tester Tracker | `beta-tester-tracker.md` | Tester status tracking |
| Release Documentation Hub | `index.md` | All release docs |

---

**Last Updated**: 2025-12-24
**Maintained By**: Product/PM Team
**Review Cadence**: Per release
