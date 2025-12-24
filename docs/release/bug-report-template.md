# Bug Report Template

**Version**: 1.0
**Last Updated**: 2025-12-24

---

## Instructions

Use this template to report critical bugs or issues that prevent you from using the app. For general feedback, please use the [Beta Feedback Form](beta-feedback-form.md) instead.

**When to use this template:**
- App crashes or freezes
- Critical features don't work
- Data loss or corruption
- Security or privacy concerns
- Severe performance issues

**How to submit:**
1. Copy this template
2. Fill in all required fields
3. Attach screenshots, logs, or screen recordings
4. Email to: [designated bug report email]
5. Subject: "BUG - [Bug Title]"

---

## Bug Report

### Bug ID

**ID**: _(Leave blank - will be assigned)_

### Title

**Bug Title**: _(Clear, concise description in one sentence)_

Example: "App crashes when selecting Option 3 in Solve flow"

### Severity

Select one:

- [ ] **Critical** - App is completely unusable, data loss, security issue
- [ ] **High** - Major feature broken, significant impact on user experience
- [ ] **Medium** - Feature partially broken, workaround available
- [ ] **Low** - Minor issue, cosmetic problem, typo

### Environment

| Field | Value |
|-------|-------|
| **Platform** | _(Android / iOS)_ |
| **Device Model** | _(e.g., Samsung Galaxy S21, Google Pixel 7)_ |
| **OS Version** | _(e.g., Android 13, Android 14)_ |
| **App Version** | _(found in Settings, or use: 1.0.0)_ |
| **Build ID** | _(if known, e.g., 88df477f-4862-41ac-9c44-4134aa2b67e2)_ |
| **Network Type** | _(WiFi / Mobile Data / Offline)_ |
| **Date & Time** | _(when bug occurred, e.g., 2025-12-24 14:30)_ |

---

## Steps to Reproduce

Provide **detailed, step-by-step** instructions to reproduce the bug. Be as specific as possible.

### Preconditions

What setup is required before the bug can be reproduced?

```
Example:
- Must be logged in with a Google account
- Must have at least one active session
- Must be connected to WiFi
```

**Your preconditions:**
```
[List preconditions here]
```

### Reproduction Steps

Number each step clearly. Include specific values, buttons clicked, text entered, etc.

1. _[First action]_
   - Example: "Open the app and log in with email: test@example.com"
2. _[Second action]_
   - Example: "Navigate to Home tab and tap 'Start New Session'"
3. _[Third action]_
   - Example: "Type 'I am stressed' and tap Send"
4. _[Fourth action]_
   - Example: "Wait for AI response, then tap 'Option 3' card"
5. _[Continue...]_

**Your steps:**
```
1. [Your first step]
2. [Your second step]
3. [Your third step]
4. [Continue as needed...]
```

### Frequency

How often does this bug occur when you follow the above steps?

- [ ] Always (100%)
- [ ] Frequently (> 50%)
- [ ] Sometimes (< 50%)
- [ ] Rarely (< 10%)
- [ ] Once (only happened once)

---

## Expected vs Actual Behavior

### Expected Behavior

What did you expect to happen?

```
[Describe the expected behavior]

Example:
"I expected Option 3 card to expand and show details when tapped."
```

### Actual Behavior

What actually happened?

```
[Describe the actual behavior]

Example:
"The app froze for 2 seconds, then crashed to the home screen.
When I reopened the app, my session was lost."
```

### Impact

How does this bug affect your use of the app?

```
[Describe the impact]

Example:
"I cannot complete the Solve flow, so I cannot test the core feature.
This is a critical blocker for my testing."
```

---

## Evidence

Please attach as much evidence as possible to help us diagnose the issue.

### Screenshots

**Did you take screenshots?**
- [ ] Yes (attach below or via email)
- [ ] No

**Screenshot filenames**: _(list files you're attaching)_
```
[e.g., crash_screen_1.png, error_message_2.png]
```

### Screen Recording

**Did you record a video of the bug?**
- [ ] Yes (attach below or via email)
- [ ] No

**Video filename**: _(e.g., bug_reproduction.mp4)_
```
[filename]
```

### Error Messages

**Did you see any error messages?** If yes, copy the exact text below.

```
[Paste error message here]

Example:
"Error: Failed to load options
Status Code: 500
Message: Internal Server Error"
```

### Console Logs / Stack Trace

**For developers**: If you have access to console logs or stack traces, paste them here.

```
[Paste logs here]
```

### Exported Account Data

**If the bug involves data loss or corruption**, export your account data from Settings and attach the JSON file.

- [ ] Account data exported and attached

---

## Additional Context

### Did You Try Any Workarounds?

What did you try to fix or work around the issue?

```
[Your attempts]

Example:
- Tried restarting the app: didn't help
- Tried clearing app cache: didn't help
- Tried different problem text: worked once, then failed again
```

### Related Bugs

Are there any other bugs or issues that seem related?

```
[Related issues]

Example:
"This seems similar to the 'slow loading' issue I reported earlier.
Both involve the Options step."
```

### Environment-Specific Notes

Any other details about your device, network, or environment that might be relevant?

```
[Additional context]

Example:
- Using VPN
- Device storage almost full (< 1GB free)
- Running other heavy apps in background
```

---

## Reporter Information

| Field | Value |
|-------|-------|
| **Your Name / Nickname** | _[e.g., John D., Tester #5]_ |
| **Email** | _[for follow-up questions]_ |
| **Best Contact Time** | _[e.g., Weekdays 9am-5pm]_ |
| **Reporter Type** | _(Beta Tester / Developer / Internal QA)_ |

### Availability for Follow-up

Are you available for follow-up questions or testing fixes?

- [ ] Yes, happy to help
- [ ] Yes, but limited availability
- [ ] No, prefer to submit report only

---

## Internal Use Only

_(Leave blank - for internal tracking)_

| Field | Value |
|-------|-------|
| **Assigned To** | _[Developer name]_ |
| **Priority** | _[P0 / P1 / P2 / P3]_ |
| **Status** | _[Open / In Progress / Fixed / Closed]_ |
| **Fix Version** | _[e.g., 1.0.1]_ |
| **Resolution Notes** | _[How the bug was fixed]_ |

---

## Examples

Here are two examples of well-written bug reports:

### Example 1: App Crash

**Title**: App crashes when selecting Option 3 in Solve flow

**Severity**: Critical

**Environment**: Android 13, Samsung Galaxy S21, App 1.0.0

**Steps to Reproduce**:
1. Log in with email test@example.com
2. Navigate to Home and tap "Start New Session"
3. Type "I am stressed about work" and tap Send
4. Answer clarifying questions (any answers)
5. Tap "Option 3" card in Options step

**Expected**: Card expands to show details

**Actual**: App freezes for 2 seconds, then crashes. Session is lost.

**Frequency**: Always (100%)

**Evidence**:
- Screenshot: crash_screen.png
- Video: crash_reproduction.mp4
- Error log attached

---

### Example 2: Visual Glitch

**Title**: Emotion background color doesn't change for Spanish keywords

**Severity**: Medium

**Environment**: Android 14, Google Pixel 7, App 1.0.0

**Steps to Reproduce**:
1. Change device language to Spanish
2. Log in and start a new session
3. Type "Estoy ansioso" (I am anxious)
4. Send message and wait for response

**Expected**: Background changes to warm orange/red tones

**Actual**: Background remains default blue

**Frequency**: Always (100%)

**Evidence**: Screenshot showing Spanish text but blue background

**Note**: Works correctly in English ("I am anxious" → orange background)

---

## Related Documents

- [Free Beta Tester Guide](free-beta-tester-guide.md)
- [Beta Feedback Form](beta-feedback-form.md)
- [Privacy Policy](privacy.md)
- [QA Test Plan](qa-test-plan.md)
