# EAS Preview Builds

## Latest Build (2025-12-24)

| Field | Value |
|-------|-------|
| **Date** | 2025-12-24 07:57 - 08:04 |
| **Build ID** | `5d5e7b57-44f7-4729-b627-e40bc93dbb76` |
| **Platform** | Android |
| **Profile** | preview |
| **Distribution** | internal |
| **Status** | finished |
| **SDK Version** | 54.0.0 |
| **App Version** | 1.0.0 |
| **Version Code** | 1 |

### Links

- **Build Logs**: https://expo.dev/accounts/cllalala/projects/clarity-mobile/builds/5d5e7b57-44f7-4729-b627-e40bc93dbb76
- **APK Download**: https://expo.dev/artifacts/eas/cwHBq3tAhSrhLcQnewsmpy.apk

### Install Instructions

1. Open the build link on your Android device
2. Download and install the APK
3. Or scan the QR code from the EAS dashboard

---

## iOS Build

> **Status**: BLOCKED - Requires Apple Developer Account

### Prerequisites Checklist

| Requirement | Status | Notes |
|-------------|--------|-------|
| Apple Developer Account | ❌ BLOCKED | $99/year enrollment required |
| App Store Connect | ❌ BLOCKED | Depends on Developer Account |
| Provisioning Profile | ❌ BLOCKED | Cannot create without account |
| Distribution Certificate | ❌ BLOCKED | Cannot create without account |

### Build Steps (When Prerequisites Met)

```bash
# 1. Ensure logged into EAS
eas whoami

# 2. Configure iOS credentials (interactive)
eas credentials
# Select: iOS > Build Credentials > Set up
# Follow prompts to create/download certificates

# 3. Build iOS preview
eas build --platform ios --profile preview

# 4. Monitor build
eas build:list --platform ios --limit 1
```

### Installation (When Build Available)

1. **TestFlight** (Recommended for internal testing)
   - Upload .ipa to App Store Connect
   - Add testers via TestFlight
   - Testers download via TestFlight app

2. **Ad-hoc Distribution**
   - Register test device UDIDs in Apple Developer portal
   - Create ad-hoc provisioning profile
   - Install via Expo dashboard QR code

### Current Blockers

- [ ] Apple Developer Program enrollment ($99/year)
- [ ] Apple Developer account approval (24-48 hours after payment)

> iOS build will be added once Apple Developer Account is configured and approved.

---

## Build History

| Date | Platform | Profile | Build ID | Status |
|------|----------|---------|----------|--------|
| 2025-12-22 | Android | preview | `88df477f` | finished |
