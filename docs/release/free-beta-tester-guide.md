# Free Beta Tester Guide

**Version**: 1.0
**Last Updated**: 2025-12-24
**Phase**: Free Beta (No Payments)

---

## Purpose & Scope

Welcome to the Clarity Free Beta! This guide is designed for friends and early testers who are helping us validate the core features of Clarity before the official launch.

**What this beta includes:**
- ✅ Full 5-step problem-solving flow (Receive → Clarify → Reframe → Options → Commit)
- ✅ AI-powered conversations (OpenAI/Claude integration)
- ✅ Emotion detection with visual feedback
- ✅ Account management (email/password, Google OAuth)
- ✅ Multi-language support (English, Spanish, Chinese)

**What is NOT included in this beta:**
- ❌ Payments or subscriptions (Stripe/RevenueCat)
- ❌ App Store / Play Store distribution
- ❌ iOS version (Apple Developer Account required)
- ❌ Production-level infrastructure (using simple hosting)

**Your role:**
- Test the core features and provide honest feedback
- Report bugs and usability issues
- Share suggestions for improvements
- Help us understand what works and what doesn't

---

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| **Android** | ✅ Available | APK download required |
| **iOS** | ❌ Blocked | Requires Apple Developer Account ($99/year) - not available for beta |

---

## Getting the App

### Android Installation

**Latest Build**: 2025-12-22 (Build ID: `88df477f-4862-41ac-9c44-4134aa2b67e2`)

**Option 1: Direct APK Download (Recommended)**

1. **On your Android device**:
   - Open this link in your browser: https://expo.dev/artifacts/eas/hUhRm9YvGcYz9Jqj3AVQnY.apk
   - Tap "Download"
   - Once downloaded, tap the APK file to install
   - If prompted, enable "Install from unknown sources" (Settings → Security)

2. **Via Expo Dashboard**:
   - Visit: https://expo.dev/accounts/cllalala/projects/clarity-mobile/builds/88df477f-4862-41ac-9c44-4134aa2b67e2
   - Scan the QR code with your device

**Option 2: Install via ADB (for developers)**

```bash
# Download APK
curl -o clarity.apk https://expo.dev/artifacts/eas/hUhRm9YvGcYz9Jqj3AVQnY.apk

# Install to connected device or emulator
adb install clarity.apk
```

### iOS Installation

**Status**: ❌ **NOT AVAILABLE**

iOS builds are currently blocked due to missing Apple Developer Account. We plan to add iOS beta testing via TestFlight once the account is configured.

---

## Account & Access

### Test Accounts

**Option 1: Create Your Own Account**
- Open the app → "Sign Up"
- Enter email and password
- No verification required for beta

**Option 2: Google OAuth**
- Open the app → "Sign in with Google"
- Use your existing Google account

**Option 3: Use Test Account (TBD)**
- Test credentials will be provided if needed
- Currently not required - please create your own account

### No Payments Required

This is a **free beta** - all features are available without payment. You will not be asked to enter credit card information or subscribe to any plans.

---

## Test Scenarios

Please try the following scenarios and provide feedback:

### 1. Account Creation & Login
- [ ] Sign up with email/password
- [ ] Log in with email/password
- [ ] Sign in with Google OAuth
- [ ] Log out and log back in

### 2. Solve Flow - Basic Journey
- [ ] Start a new session from Home
- [ ] **Receive**: Describe a problem (e.g., "I'm stressed about my job interview tomorrow")
- [ ] **Clarify**: Answer AI's follow-up questions
- [ ] **Reframe**: Review the reframed problem statement
- [ ] **Options**: Browse 3-4 solution options
- [ ] **Commit**: Choose an option and set a first step action

### 3. Emotion Detection
- [ ] Type messages with anxious keywords (e.g., "I'm worried", "anxiety", "stressed")
- [ ] Observe background color change to warm tones (orange/red)
- [ ] Type calm messages (e.g., "I feel peaceful", "relaxed")
- [ ] Observe background color change to cool tones (blue/green)
- [ ] Toggle emotion background on/off in Settings

### 4. Multi-Language Support
- [ ] Change device language to Spanish
- [ ] Verify app UI switches to Spanish
- [ ] Change device language to Chinese (Simplified)
- [ ] Verify app UI switches to Chinese
- [ ] Change back to English

### 5. Session History
- [ ] Complete a solve session
- [ ] Navigate to "Sessions" tab
- [ ] Verify your session appears in the list
- [ ] Tap on a session to view details

### 6. Device Management
- [ ] Navigate to "Devices" tab
- [ ] View list of logged-in devices
- [ ] Remove a device (if you have multiple)

### 7. Account Management
- [ ] Navigate to Settings
- [ ] Export account data (downloads JSON file)
- [ ] *Optional*: Delete account (WARNING: irreversible)

### 8. Error Scenarios
- [ ] Turn on Airplane Mode
- [ ] Try to start a new session (should show network error)
- [ ] Turn off Airplane Mode
- [ ] Retry (should work)

### 9. Edge Cases
- [ ] Test with very long problem descriptions (500+ characters)
- [ ] Test with special characters in input
- [ ] Test rapid consecutive messages
- [ ] Leave app mid-session and return

### 10. Overall Experience
- [ ] Navigate through all tabs (Home, Sessions, Devices, Settings, Paywall)
- [ ] Test app responsiveness and smoothness
- [ ] Check for any visual glitches or layout issues
- [ ] Evaluate clarity of UI text and instructions

---

## Known Limitations

Please be aware of these known limitations during the beta:

### Payment & Subscription Features
- **Stripe integration**: Disabled for beta
- **RevenueCat**: Not configured
- **Subscription plans**: Not available
- **Payment UI**: Hidden in beta builds (Paywall tab and subscription card removed)
- **Backend payment endpoints**: Return `501 Not Implemented` when disabled

### Platform Limitations
- **iOS**: Not available (requires Apple Developer Account)
- **App Store / Play Store**: Not available (direct APK only)

### Infrastructure
- **API endpoint**: Using local or simple hosting (not production-grade)
- **Domain**: No custom domain configured yet
- **Performance**: May be slower than production

### Features Not Yet Implemented
- **Push notifications**: Not configured
- **App version updates**: Manual APK download required
- **Crash reporting**: Limited (local logs only)

### LLM Provider Limitations
- **OpenAI/Claude API**: May have rate limits or authentication issues
- **Response quality**: Depends on API availability
- **Crisis detection**: Implemented but not professionally validated

---

## Privacy & Data

### What Data We Collect

Please refer to our [Privacy Policy](privacy.md) for full details. In summary:

- **Account Data**: Email, password (hashed), Google ID (if using OAuth)
- **Usage Data**: Session messages, step completions, emotion detections
- **Device Data**: Device ID, OS version (for device binding)

### Data Retention

- Your data is stored in a PostgreSQL database
- You can export your data anytime via Settings → Export Account Data
- You can delete your account and all data via Settings → Delete Account

### Third-Party Services

- **OpenAI/Claude**: AI conversation processing (messages sent to API)
- **Google OAuth**: Authentication (if you choose Google sign-in)
- **Expo**: App build and distribution platform

### Beta Testing Consent

By participating in this beta, you understand and agree that:
- This is a test version with potential bugs and incomplete features
- Your feedback may be used to improve the product
- Your data will be handled according to our Privacy Policy
- We may contact you for follow-up feedback or clarifications

---

## How to Send Feedback

We **highly value** your feedback! Please use one of the following methods:

### Option 1: Beta Feedback Form (Recommended)

Fill out our [Beta Feedback Form](beta-feedback-form.md) with:
- Your tester info (nickname, device, OS version)
- Session summary (satisfaction rating)
- Bugs encountered
- Suggestions for improvements

### Option 2: Bug Report Template

For critical bugs, use our [Bug Report Template](bug-report-template.md) to provide:
- Detailed reproduction steps
- Expected vs actual behavior
- Screenshots or screen recordings

### Option 3: Direct Contact

- **Email**: support@clarity.app (or designated beta support email)
- **Response Time**: We aim to respond within 24-48 hours

### What to Include in Feedback

**Good feedback examples**:
- ✅ "Step 3 (Reframe) took 10+ seconds to load, then showed empty screen"
- ✅ "Emotion background feature is cool, but the orange color is too bright"
- ✅ "I expected the 'Back' button to save my progress, but it didn't"

**Less helpful feedback**:
- ❌ "It doesn't work"
- ❌ "I don't like it"
- ❌ "Fix the bugs"

---

## Contact / Support

### Beta Testing Coordinator

- **Contact**: TBD (designated beta coordinator)
- **Email**: TBD
- **Availability**: Weekdays 9am-6pm

### Technical Support

- **For app crashes**: Include logs from Settings → Export Account Data
- **For login issues**: Verify network connection and retry
- **For feature questions**: Refer to this guide first

### Escalation

If you encounter a critical issue (app completely unusable, data loss, security concern):
1. Stop using the app immediately
2. Email us at: [designated urgent email]
3. Mark subject as "URGENT - Beta Critical Issue"
4. We will respond within 12 hours

---

## FAQ

**Q: Can I share the APK with others?**
A: Yes, but please only share with trusted friends who understand this is a beta test.

**Q: Will my data be transferred to the production app?**
A: TBD - we will notify you before the production launch.

**Q: Can I use this for real problem-solving?**
A: Yes, but keep in mind this is a beta version. For serious mental health concerns, please consult a professional.

**Q: What if I find a security vulnerability?**
A: Please report it immediately to [designated security email] and do NOT share it publicly.

**Q: Will I get early access to the paid version?**
A: TBD - we may offer special pricing for beta testers.

**Q: How long will the beta last?**
A: Estimated duration: 2-4 weeks, depending on feedback and issue resolution.

---

## Thank You!

Thank you for being an early tester and helping us build a better product. Your feedback is invaluable and will directly shape the final version of Clarity.

**Questions or concerns?** Don't hesitate to reach out. We're here to help!

---

## Related Documents

- [Privacy Policy](privacy.md)
- [Beta Feedback Form](beta-feedback-form.md)
- [Bug Report Template](bug-report-template.md)
- [EAS Preview Build Verification](eas-preview-verify.md)
- [QA Test Plan](qa-test-plan.md)
