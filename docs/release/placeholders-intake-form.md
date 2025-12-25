# Placeholders Intake Form

**Version**: 1.0
**Last Updated**: 2025-12-25
**Purpose**: Fillable form to collect all TBD/placeholder values needed for production launch

---

## Purpose

This form provides a **single place** to fill in all missing information identified in the [Placeholders to Fill Inventory](placeholders-to-fill.md). Once you complete this form, you can copy the values into the respective documentation files.

**How This Saves Time**:
- All critical info in one place (no hunting across 15+ files)
- Clear examples and descriptions for each field
- Copy-paste ready format for updating docs
- Progress tracking (fill what you know, mark unknowns)

---

## How to Use

1. **Fill in each table below** - start with what you know
2. **Mark unknowns** - write "TBD" or "PENDING" in the Value column
3. **Save this file** - commit changes to track progress
4. **Copy values to docs** - use "Where This Info Is Used" section to find target files
5. **Verify completeness** - cross-check with [placeholders-to-fill.md](placeholders-to-fill.md)

---

## Critical Info Summary

Before filling the detailed form, here's a quick checklist of the **15 most critical items** to complete before production:

- [ ] **Team Roles**: Ownership Matrix (8 roles), Launch Day Runbook (7 roles), Beta Checklist (5 roles)
- [ ] **Contacts**: Launch Communications (4 contacts), Beta Coordinator name + email
- [ ] **Support**: Support hours, response time SLA, status page URL
- [ ] **Beta Ops**: Beta end date, beta pricing/perks, feedback form URL
- [ ] **Testing**: Test Google Account, Test Apple ID (blocked)

---

## Intake Form Sections

Fill in the **Value** column for each field below. Leave blank or write "TBD" if unknown.

---

### 1. Company & Legal

| Field | Description | Example | Value |
|-------|-------------|---------|-------|
| **Company Name** | Official registered company name | Clarity Technologies Inc. | |
| **Company Address** | Business registration address | 123 Main St, San Francisco, CA 94102 | |
| **Support Email** | Public support contact email | support@clarity.app | |
| **Legal Contact** | Legal/compliance point of contact | legal@clarity.app | |

---

### 2. Domain / Hosting / Database

| Field | Description | Example | Value |
|-------|-------------|---------|-------|
| **Domain Name** | Primary domain for production | api.clarity.app | |
| **Hosting Provider** | Choose: Vercel / Railway / Fly.io | Railway | |
| **Database Provider** | Choose: Neon / Supabase / Railway | Neon | |
| **Database Region** | Geographic location for DB | us-east-1 | |
| **CDN Provider** | (Optional) Choose: Cloudflare / Vercel | Cloudflare | |

---

### 3. Apple Developer / App Store

| Field | Description | Example | Value |
|-------|-------------|---------|-------|
| **Apple Developer Account Type** | Individual or Organization | Individual | |
| **Apple Developer Email** | Email used for Apple Developer account | dev@clarity.app | |
| **App Bundle ID** | iOS app bundle identifier | com.clarity.app | |
| **Team ID** | Apple Developer Team ID (10 characters) | ABCD123456 | |
| **D-U-N-S Number** | (Organization only) Dun & Bradstreet number | 08-xxx-xxxx | |

---

### 4. OAuth / External Services

| Field | Description | Example | Value |
|-------|-------------|---------|-------|
| **Test Google Account** | Gmail address for testing OAuth | test-clarity@gmail.com | |
| **Test Apple ID** | Apple ID for testing Sign-In | test-clarity@icloud.com | |
| **OpenAI API Key** | Production OpenAI API key | sk-prod-xxxxxx (see .env) | See .env |
| **Anthropic API Key** | Production Claude API key | sk-ant-xxxxxx (see .env) | See .env |
| **Sentry DSN** | (Optional) Error tracking endpoint | https://xxx@sentry.io/xxx | |

---

### 5. Monitoring & Support

| Field | Description | Example | Value |
|-------|-------------|---------|-------|
| **Support Hours** | When support is available | Mon-Fri 9am-6pm PST | Best effort (no fixed hours) |
| **Response Time SLA** | Target time to first response | 1 business day | Best effort (no SLA) |
| **Status Page URL** | Public uptime status page | https://status.clarity.app | Not available |
| **On-Call Contact** | Emergency contact for incidents | oncall@clarity.app | |
| **Monitoring Tool** | Choose: Sentry / Datadog / LogRocket | Sentry | |

---

### 6. Beta Operations

| Field | Description | Example | Value |
|-------|-------------|---------|-------|
| **Beta Coordinator Name** | Person managing beta testers | Jane Doe | Owner (self) |
| **Beta Coordinator Email** | Contact email for beta questions | beta@clarity.app | Provided in invite (TBD) |
| **Beta End Date** | When beta testing will conclude | 2025-02-28 | Open-ended / TBD |
| **Beta Pricing** | Special offers for beta testers | 50% off for 6 months | None |
| **Feedback Form URL** | Web form link for beta feedback | https://forms.gle/xxxxx | TBD (web not built) |
| **Bug Report Channel** | Where testers report bugs | GitHub Issues / Email / Discord | |

---

### 7. Contacts & Owners

Fill in names and emails for each role. Use format: `Name (email@domain.com)` or GitHub handle.

#### Ownership Matrix Roles (8)

| Role | Name | Email/GitHub | Responsibility |
|------|------|--------------|----------------|
| **Product Lead** | Owner (self) | | Product strategy, roadmap |
| **Backend Lead** | Owner (self) | | API, database, server logic |
| **Mobile Lead** | Owner (self) | | iOS/Android app development |
| **DevOps Lead** | Owner (self) | | Infrastructure, CI/CD, deployment |
| **QA Lead** | Owner (self) | | Testing, quality assurance |
| **Finance Lead** | Owner (self) | | Payments, billing, compliance |
| **Support Lead** | Owner (self) | | User support, documentation |
| **Marketing Lead** | Owner (self) | | Launch communications, growth |

#### Launch Day Runbook Roles (7)

| Role | Name | Email/GitHub | Responsibility |
|------|------|--------------|----------------|
| **Launch Commander** | Owner (self) | | Overall launch coordination |
| **Backend Lead** | Owner (self) | | Backend systems monitoring |
| **Mobile Lead** | Owner (self) | | App store submission, mobile issues |
| **DevOps Lead** | Owner (self) | | Infrastructure, deployment |
| **QA Lead** | Owner (self) | | Final testing, smoke tests |
| **Support Lead** | Owner (self) | | User onboarding, support queue |
| **Comms Lead** | Owner (self) | | Announcements, social media |

#### Beta Launch Checklist Roles (5)

| Role | Name | Email/GitHub | Responsibility |
|------|------|--------------|----------------|
| **Project Lead** | Owner (self) | | Beta program management |
| **Dev Lead** | Owner (self) | | Technical implementation |
| **PM Lead** | Owner (self) | | Coordination, timeline |
| **QA Lead** | Owner (self) | | Beta testing validation |
| **Support Lead** | Owner (self) | | Beta tester support |

#### Launch Communications Contacts (4)

| Role | Name | Email/GitHub | Responsibility |
|------|------|--------------|----------------|
| **Launch Commander** | Owner (self) | | Master contact for launch |
| **Backend Lead** | Owner (self) | | Backend escalations |
| **Mobile Lead** | Owner (self) | | Mobile app escalations |
| **DevOps Lead** | Owner (self) | | Infrastructure escalations |

---

## Where This Info Is Used

Once you fill this form, copy values into the following documents:

| Section | Target Documents | What to Update |
|---------|------------------|----------------|
| **Company & Legal** | `docs/release/privacy.md`, `docs/release/support.md` | Company name, addresses, contact emails |
| **Domain / Hosting / Database** | `docs/release/domain-hosting-setup-guide.md`, `docs/PROD_DEPLOY.md` | Provider choices, domain names |
| **Apple Developer** | `docs/release/apple-developer-setup-guide.md`, `docs/release/store-submission-checklist.md` | Account details, Team ID, Bundle ID |
| **OAuth / External** | `docs/release/qa-test-plan.md`, `docs/ENV_VARIABLES.md` | Test accounts, API keys (in .env) |
| **Monitoring & Support** | `docs/release/support.md`, `docs/release/incident-response.md` | SLA, contact info, monitoring setup |
| **Beta Operations** | `docs/release/free-beta-tester-guide.md`, `docs/release/beta-feedback-form.md`, `docs/release/free-beta-launch-checklist.md` | Coordinator info, dates, form URLs |
| **Contacts & Owners** | `docs/release/ownership-matrix.md`, `docs/release/launch-day-runbook.md`, `docs/release/launch-communications.md` | Team roles, escalation contacts |

---

## Progress Tracking

Track your completion progress here:

| Section | Status | Notes |
|---------|--------|-------|
| Company & Legal | ☐ Not Started / ☐ In Progress / ☐ Complete | |
| Domain / Hosting / Database | ☐ Not Started / ☐ In Progress / ☐ Complete | |
| Apple Developer | ☐ Not Started / ☐ In Progress / ☐ Complete | |
| OAuth / External Services | ☐ Not Started / ☐ In Progress / ☐ Complete | |
| Monitoring & Support | ☐ Not Started / ☐ In Progress / ☐ Complete | |
| Beta Operations | ☐ Not Started / ☐ In Progress / ☐ Complete | |
| Contacts & Owners | ☐ Not Started / ☐ In Progress / ☐ Complete | |

---

## Next Steps

### After Filling This Form

1. **Commit changes**: `git add docs/release/placeholders-intake-form.md && git commit -m "chore: fill placeholders intake form"`
2. **Copy to target docs**: Use "Where This Info Is Used" table to update each file
3. **Verify completeness**: Cross-check with [placeholders-to-fill.md](placeholders-to-fill.md) inventory
4. **Mark items as DONE**: Update status in placeholders-to-fill.md

### Before Beta Launch (Critical Items)

Must complete these sections:
- ✅ Beta Operations (Coordinator, End Date, Feedback Form)
- ✅ Monitoring & Support (Support Hours, Response Time)
- ✅ Contacts & Owners (At minimum: Project/Dev/PM/QA/Support Leads)

### Before Production Launch

Must complete ALL sections except:
- Apple Developer (if iOS not launching yet)
- RevenueCat (deferred for beta)

---

## Related Documents

- [Placeholders to Fill Inventory](placeholders-to-fill.md) - Complete list of all placeholders
- [Project Status Summary](project-status-summary.md) - Current project status
- [Launch Readiness](launch-readiness.md) - Go/No-Go criteria
- [Free Beta Launch Checklist](free-beta-launch-checklist.md) - Beta preparation tasks
- [Ownership Matrix](ownership-matrix.md) - Team roles and responsibilities
- [Domain & Hosting Setup Guide](domain-hosting-setup-guide.md) - Domain/hosting configuration
- [Apple Developer Setup Guide](apple-developer-setup-guide.md) - Apple account setup
- [Release Documentation Hub](index.md) - All release documentation
