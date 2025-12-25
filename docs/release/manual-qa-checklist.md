# Manual QA Checklist

**Version**: 1.0
**Created**: 2025-12-23
**Status**: Draft
**Scope**: Mobile app (Expo/EAS build) + API integration

---

## How to Use

- Execute on a real device or simulator.
- Record results in `docs/release/qa-execution-log.md`.
- For each item mark: PASS / FAIL / BLOCKED / N/A.
- If FAIL/BLOCKED, add reason + screenshot.

---

## Test Environment

| Environment | API URL | Notes |
|-------------|---------|-------|
| Local | `http://localhost:8000` | Use `docs/release/local-demo-runbook.md` |
| Preview | `https://staging-api.solacore.app` | Only if staging exists |
| Production | `https://api.solacore.app` | BLOCKED until domain + deploy |

---

## Preconditions

- [ ] Backend reachable (health endpoints return 200)
- [ ] Test account ready (email/password)
- [ ] Device has stable network
- [ ] `EXPO_PUBLIC_API_URL` matches environment

---

## Checklist

### A. Auth & Account

- [ ] **A1 Register**: Email + password + confirm. Expect success and home screen.
- [ ] **A2 Register mismatch**: Password mismatch shows error.
- [ ] **A3 Login success**: Existing account login succeeds.
- [ ] **A4 Login failure**: Wrong password shows error, no navigation.
- [ ] **A5 Logout**: Settings -> Logout returns to login screen.
- [ ] **A6 Forgot password**: Submit email; shows success state. If email service not configured, mark BLOCKED.
- [ ] **A7 Reset password**: Use token to reset and login. If no token flow, mark BLOCKED.
- [ ] **A8 Google OAuth**: Login via Google succeeds. If client IDs not configured, mark BLOCKED.
- [ ] **A9 Apple Sign-In (iOS)**: Login via Apple succeeds. If no Apple Dev account, mark BLOCKED.
- [ ] **A10 Export data**: Settings -> Data & Privacy -> Export My Data shows share sheet with JSON.
- [ ] **A11 Delete account**: Settings -> Data & Privacy -> Delete Account confirms and returns to login.

### B. Solve 5-Step Flow

- [ ] **B1 Start session**: Home -> Start Session opens new session.
- [ ] **B2 Receive**: Enter issue, streaming response shows tokens.
- [ ] **B3 Clarify**: Answer follow-up, proceeds to Reframe.
- [ ] **B4 Reframe**: Assistant reframes, proceeds to Options.
- [ ] **B5 Options**: Options cards appear; select one.
- [ ] **B6 Commit**: Enter first-step action; optional reminder; complete session.
- [ ] **B7 Completion**: Success message; Done returns to Home.

### C. Emotion Detection & UI Feedback

- [ ] **C1 Emotion detected**: Use example phrases from `solacore-api/tests/test_emotion_detector.py` and confirm background changes.
- [ ] **C2 Toggle off**: Settings -> Emotion Background off; background stops changing.
- [ ] **C3 Toggle on**: Enable again; background responds to emotion.

### D. Devices & Sessions

- [ ] **D1 Devices list**: Settings -> Manage Devices loads list or empty state.
- [ ] **D2 Device removal**: Remove non-current device. If only one device, mark N/A.
- [ ] **D3 Sessions list**: Settings -> Active Sessions loads list or empty state.
- [ ] **D4 Session terminate**: Terminate one session; list updates.

### E. Subscription & Paywall

- [ ] **E1 Paywall load**: Packages load and display price/title.
- [ ] **E2 Purchase**: Purchase flow succeeds (sandbox). If RevenueCat not configured, mark BLOCKED.
- [ ] **E3 Restore**: Restore purchases shows success state.
- [ ] **E4 Manage subscription**: Settings opens store subscription page.
- [ ] **E5 Customer center**: Settings opens RevenueCat customer center. If RevenueCat not configured, mark BLOCKED.

### F. Error Handling

- [ ] **F1 Network offline**: Disable network and submit message; show friendly error.
- [ ] **F2 API 500**: Force a server error (if no test route, mark BLOCKED).
- [ ] **F3 Token expired**: Expire token and ensure re-auth or error shown.

### G. i18n

- [ ] **G1 English**: Set device language to English; UI strings are English.
- [ ] **G2 Spanish**: Set device language to Spanish; UI strings are Spanish.
- [ ] **G3 Chinese**: Set device language to Chinese; UI strings are Chinese.

---

## Notes

- For crisis flow QA, use test phrases from `solacore-api/tests/test_crisis_detector.py` and confirm the crisis overlay appears.
- If the app shows blank screens or crashes, capture device logs and attach to the QA log.

---

## Related Documents

- QA Test Plan: `docs/release/qa-test-plan.md`
- QA Execution Log: `docs/release/qa-execution-log.md`
- Local Demo Runbook: `docs/release/local-demo-runbook.md`
- Release Hub: `docs/release/index.md`
