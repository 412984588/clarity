# Clarity Beta - Release Notes (2025-12-24)

**Version**: 1.0.0-beta
**Date**: 2025-12-24
**Build ID**: 5d5e7b57-44f7-4729-b627-e40bc93dbb76
**Commit**: f11f3f7
**APK Download**: https://expo.dev/artifacts/eas/cwHBq3tAhSrhLcQnewsmpy.apk
**Status**: Free Beta (No Payments)

---

## 🎉 Highlights

This is our **first Free Beta release**! The app is fully functional for testing core features without any payment requirements. We've hidden all payment-related UI and configured the app for friend testing with relaxed usage limits.

**Key Updates:**
- ✅ Free Beta Mode enabled (no paywall, no subscription prompts)
- ✅ GitHub Issue templates for structured bug reporting
- ✅ Comprehensive beta documentation and guides
- ✅ Android APK ready for distribution

---

## ✨ What's New

### Free Beta Mode Implementation
- **Purpose**: Enable friend testing without payment flows
- **Changes**:
  - Paywall tab completely hidden from navigation
  - Subscription status card removed from Settings
  - Beta mode notice added to Settings screen
  - Device limits relaxed to 10 devices (vs. 3 in production)
  - Session limits removed (unlimited sessions in beta)
  - All premium features accessible without payment

### GitHub Issue Templates
- **Beta Bug Report**: Structured form for reporting crashes, errors, or broken features
- **Beta Feedback**: Template for sharing experience and suggestions
- **Beta Feature Request**: Template for proposing new features or improvements
- **Access**: https://github.com/412984588/clarity/issues/new/choose

### Beta Documentation Suite
New documentation created for testers and team:
- **Free Beta Tester Guide**: Installation, testing instructions, features overview
- **Beta Issue Intake Guide**: Where & how to report issues, severity guide, response times
- **Beta Feedback Form**: Structured feedback collection template
- **Bug Report Template**: Detailed bug reporting format
- **Beta Known Issues**: Current bug status, workarounds, priority tracking
- **Beta Support Macros**: Quick response templates for common questions
- **Beta Share Pack**: What to share externally vs. keep internal

### Multi-Language Support
- **Languages**: English, Spanish (Español), Chinese (简体中文)
- **Coverage**: 110+ translation keys across all screens
- **i18n**: Complete internationalization infrastructure

---

## 🔧 Improved

### Emotion Detection
- **Accuracy**: Enhanced keyword recognition for 5 emotion categories (anxious, calm, confused, frustrated, hopeful)
- **Visual Feedback**: Gradient backgrounds adjust based on detected emotion
- **Multilingual**: Works across English, Spanish, and Chinese

### User Authentication
- **Methods**: Email/password, Google OAuth, Apple Sign-In (iOS only when available)
- **Security**: JWT tokens with refresh mechanism, device binding
- **Session Management**: Persistent sessions across app restarts

### Solve 5-Step Framework
- **Flow**: Receive → Clarify → Reframe → Options → Commit
- **AI Integration**: OpenAI GPT-4 and Claude for intelligent suggestions
- **SSE Streaming**: Real-time AI responses with streaming support
- **UI**: Option cards with expand/collapse, intuitive navigation

---

## 🐛 Fixed

This is the initial beta release, so there are no "fixes" from a previous version. However, the following issues were resolved during development:

- **[DEV-001]**: Fixed app crash on Android 12+ when accessing camera permissions
- **[DEV-002]**: Fixed emotion gradient not updating after language change
- **[DEV-003]**: Fixed session history not persisting after app restart
- **[DEV-004]**: Fixed Google OAuth redirect loop on some devices
- **[DEV-005]**: Fixed "Next" button overlapping with keyboard on small screens

---

## ⚠️ Known Issues

For the most up-to-date list, see [Beta Known Issues](beta-known-issues.md).

### Critical (P0) - App Unusable
- _(No critical issues at this time)_

### High Priority (P1) - Major Feature Broken
- _(No high priority issues reported yet - we need your help finding these!)_

### Medium Priority (P2) - Partial Feature Impact
- **Installation Friction**: APK requires "Install from unknown sources" permission on Android. **Workaround**: Enable in Settings → Security → Unknown Sources.

### Low Priority (P3) - Minor/Cosmetic
- **UI**: Some text may be cut off on very small screens (< 5 inches). **Workaround**: Use a device with larger screen or adjust system font size.

### Platform-Specific
- **iOS Not Available**: iOS build is blocked due to missing Apple Developer Account ($99/year enrollment required). Android only for beta.

### Known Limitations (By Design for Beta)
- **No Payments**: Stripe and RevenueCat integrations are disabled for beta
- **No App Store Distribution**: Manual APK installation required (not in Play Store yet)
- **Dev Infrastructure**: Backend may be slow or occasionally unavailable (using staging environment)
- **Limited Analytics**: No usage dashboard available yet

---

## 📢 Call for Feedback

We need your help testing this release! Please focus on:

### High Priority Test Areas

1. **Installation Process**
   - Were you able to download and install the APK successfully?
   - Did you encounter permission issues?
   - How long did it take from download to first launch?

2. **Account Creation**
   - Did sign-up work smoothly (email or Google OAuth)?
   - Were you able to log in after creating an account?
   - Did you experience any errors during authentication?

3. **Solve Flow (5 Steps)**
   - Try solving a real problem you're facing
   - Did the AI suggestions feel helpful and relevant?
   - Was the flow intuitive or confusing?
   - Were there any steps where you got stuck?

4. **Emotion Detection**
   - Does the background color change based on your mood/words?
   - Try different emotional words ("I'm anxious", "I feel calm", etc.)
   - Does it work in Spanish or Chinese (if you speak those languages)?

5. **Multilingual Support**
   - Switch language in Settings → Language
   - Does the app fully translate to your chosen language?
   - Are there any English words remaining after switching?

### How to Report Issues

**Choose the method that works best for you:**

| Method | Best For | Link |
|--------|----------|------|
| **GitHub Issue Forms** | Structured bug reports & feedback | https://github.com/412984588/clarity/issues/new/choose |
| **Beta Feedback Form** | Comprehensive weekly feedback | [beta-feedback-form.md](beta-feedback-form.md) |
| **Bug Report Template** | Detailed bug reports with screenshots | [bug-report-template.md](bug-report-template.md) |
| **Direct Message** | Quick questions or urgent issues | Reply to invite email |

**For guidance on reporting:**
- See [Beta Issue Intake Guide](beta-issue-intake.md) for severity levels and response times
- Check [Beta Known Issues](beta-known-issues.md) to see if your issue is already known

---

## 📥 How to Install/Update

### First-Time Installation

**Prerequisites:**
- Android device (version 8.0 or higher recommended)
- ~50 MB free storage
- Internet connection

**Installation Steps:**

1. **Download APK**
   - On your Android device, visit: https://expo.dev/artifacts/eas/cwHBq3tAhSrhLcQnewsmpy.apk
   - Or scan QR code: https://expo.dev/accounts/cllalala/projects/clarity-mobile/builds/5d5e7b57-44f7-4729-b627-e40bc93dbb76

2. **Enable Unknown Sources** (if prompted)
   - Settings → Security → Install from unknown sources
   - Enable for your browser app

3. **Install APK**
   - Tap the downloaded APK file
   - Tap "Install"
   - Wait for installation to complete (~30 seconds)

4. **Open & Sign Up**
   - Tap "Open" or find "Clarity" in your app drawer
   - Sign up with email/password or Google OAuth
   - No verification required for beta

**Full Installation Guide**: See [Free Beta Tester Guide](free-beta-tester-guide.md) for detailed instructions.

### Updating to a Future Build

When a new APK is released:
1. Uninstall the old version (your data will be safe if you're logged in)
2. Download the new APK from the updated link
3. Install the new APK following the same steps
4. Log back in with your account - your sessions will be restored

---

## 🙏 Thank You

Thank you for being one of our first beta testers! Your feedback will directly shape the future of Clarity.

**What Happens Next:**
1. **This week**: We'll monitor GitHub Issues and respond within 24 hours
2. **Next week**: If bugs are reported, we'll release a fix build and notify you
3. **Weekly**: We'll send status updates and request feedback summaries
4. **After beta** (~4-6 weeks): We'll transition to production with your input

**Stay in Touch:**
- **Bug reports**: https://github.com/412984588/clarity/issues/new/choose
- **Feedback**: [beta-feedback-form.md](beta-feedback-form.md)
- **Questions**: Reply to your invite email
- **Urgent issues**: Direct message via Slack/WeChat/Email (check your invite for contact info)

---

## 🔗 Useful Links

| Resource | Link |
|----------|------|
| **APK Download** | https://expo.dev/artifacts/eas/cwHBq3tAhSrhLcQnewsmpy.apk |
| **Expo Build Page** | https://expo.dev/accounts/cllalala/projects/clarity-mobile/builds/5d5e7b57-44f7-4729-b627-e40bc93dbb76 |
| **Full Tester Guide** | [free-beta-tester-guide.md](free-beta-tester-guide.md) |
| **Report Bugs (GitHub)** | https://github.com/412984588/clarity/issues/new/choose |
| **Feedback Form** | [beta-feedback-form.md](beta-feedback-form.md) |
| **Known Issues** | [beta-known-issues.md](beta-known-issues.md) |
| **Issue Intake Guide** | [beta-issue-intake.md](beta-issue-intake.md) |
| **Privacy Policy** | [privacy.md](privacy.md) |

---

## 📅 What's Next?

**Next Release**: TBD (depends on feedback and bug reports from this beta)

**Planned Improvements:**
- iOS beta testing (requires Apple Developer Account)
- Offline mode for Solve flow
- Performance optimizations (faster AI responses)
- Additional emotion categories
- Session export/backup functionality

**Your Input Shapes the Roadmap**: If you have feature requests or suggestions, please share them via the [Beta Feature Request](https://github.com/412984588/clarity/issues/new/choose) form.

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [Free Beta Tester Guide](free-beta-tester-guide.md) | Installation & testing instructions |
| [Beta Launch Message](beta-launch-message.md) | Templates for inviting new testers |
| [Beta Issue Intake Guide](beta-issue-intake.md) | Where & how to report issues |
| [Beta Feedback Form](beta-feedback-form.md) | Structured feedback template |
| [Bug Report Template](bug-report-template.md) | Detailed bug reporting format |
| [Beta Known Issues](beta-known-issues.md) | Current bug list & workarounds |
| [Beta Share Pack](beta-share-pack.md) | What to share vs. keep internal |
| [EAS Preview Verify](eas-preview-verify.md) | Build verification details |

---

**Last Updated**: 2025-12-24
**Maintained By**: Product/PM Team
**Review Cadence**: Per beta release
