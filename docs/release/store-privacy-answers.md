# App Store Privacy + Play Data Safety (Draft)

Status: Draft. Answers locked based on current codebase; re-validate before submission.
Last Updated: 2025-12-23

---

## Data Flow Summary (for reviewers)

- Account: email + password (email auth) or OAuth provider + provider ID.
- Device security: device fingerprint + device name/platform.
- Session metadata: solve sessions, step history, analytics events (no message text stored server-side).
- User content: message text sent to the API for LLM processing; stored locally on device.
- Purchases: subscription status and identifiers (Stripe/RevenueCat).

Third-party processors:
- LLM provider (OpenAI or Anthropic): receives user content for response generation.
- Stripe: receives email and subscription identifiers for payments.
- RevenueCat: receives user ID and purchase info for mobile subscriptions.

---

## App Store Connect - App Privacy

### Tracking
- Tracking across apps/websites: **No**

### Data Collected

| Data Type (Apple category) | Linked to User | Used for Tracking | Purpose | Notes |
|---|---|---|---|---|
| Contact Info - Email Address | Yes | No | App Functionality, Account Management | Email login + support contact |
| Identifiers - User ID | Yes | No | App Functionality, Security | Used for auth + subscriptions |
| Identifiers - Device ID | Yes | No | Security, Account Management | Device fingerprint for session/device control |
| User Content - Text | Yes | No | App Functionality | Sent to LLM provider; not stored on server |
| Usage Data - App Interactions | Yes | No | Analytics, App Functionality | Session metadata + step history counts |
| Purchases - Subscription Info | Yes | No | App Functionality | Stripe/RevenueCat |

### Data Not Collected (assumed)
- Location, Contacts, Photos, Videos, Audio, Health & Fitness, Browsing History, Advertising Data.

---

## Google Play Console - Data Safety

### Data Collected

| Data Type (Play category) | Collected | Shared | Purpose | Notes |
|---|---|---|---|---|
| Personal Info - Email | Yes | Yes | Account Management | Shared with Stripe for billing |
| User IDs | Yes | Yes | App Functionality, Security | Shared with RevenueCat |
| App Activity - App Interactions | Yes | No | Analytics, App Functionality | Session metadata |
| User Content - Messages | Yes | Yes | App Functionality | Shared with LLM provider |
| Purchases | Yes | Yes | App Functionality | Stripe/RevenueCat |

### Security & Privacy
- Data encrypted in transit: **Yes (HTTPS/TLS)**
- Data deletion request: **In-app delete account**
- Data export request: **In-app export**

---

## Decisions (based on current codebase)

1) No ads SDKs, no third-party analytics beyond listed processors.
2) No location collection, no contacts, no photo/video/audio uploads.
3) No crash reporting SDK (Sentry) enabled in production.
4) No data used for advertising or tracking.
5) User message content is not stored server-side (only processed for response).
