# Placeholders to Fill Inventory

**Version**: 1.0
**Last Updated**: 2025-12-24
**Purpose**: Comprehensive inventory of all TBD/placeholder items requiring actual values before production launch

---

## Purpose

This document tracks all placeholders, TBD items, and missing information across the Clarity documentation. Use this as a **pre-launch checklist** to ensure no critical information is missing before going live.

**Why This Matters**:
- Prevents launching with incomplete documentation
- Identifies ownership gaps early
- Tracks progress toward production readiness
- Serves as a coordination tool across teams

---

## How to Use

**💡 Quick Start**: Use the [Placeholders Intake Form](placeholders-intake-form.md) to fill all values in one place, then copy them into the respective documents.

1. **Review** this inventory before each milestone (Beta Launch, Production Launch)
2. **Assign** owners to each placeholder item
3. **Fill in** actual values and mark as "Done"
4. **Update** target dates based on dependencies
5. **Verify** filled values are correct before marking complete

---

## Placeholder Inventory

### Critical (Must Fill Before Production)

| Document | Section | Placeholder Text | Context | Owner | Target Date | Status |
|----------|---------|------------------|---------|-------|-------------|--------|
| ownership-matrix.md | Team Roles | Owner (self) (8 roles) | Product/Backend/Mobile/DevOps/QA/Finance/Support/Marketing leads | PM | Before Go/No-Go | DONE |
| launch-day-runbook.md | Team Roles | Owner (self) (7 roles) | Launch Commander, Backend/Mobile/DevOps/QA/Support/Comms Leads | PM | Before Launch | DONE |
| free-beta-launch-checklist.md | Team Roles | Owner (self) (5 roles) | Project/Dev/PM/QA/Support Leads | PM | Before Beta | DONE |
| launch-communications.md | Contact List | Owner (self) (4 contacts) | Launch Commander, Backend/Mobile/DevOps Leads | PM | Before Launch | DONE |
| support.md | Support Hours | Best effort (no fixed hours) | Support availability hours (e.g., Mon-Fri 9am-6pm) | Support | Before Beta | DONE |
| support.md | Response Time | Best effort (no SLA) | Target response SLA (e.g., 1 business day) | Support | Before Beta | DONE |
| support.md | Status Page URL | Not available | Public status page URL | DevOps | Before Launch | DONE |
| free-beta-tester-guide.md | Beta Coordinator | Owner (self) | Manual invites only, no dedicated coordinator | PM | Before Beta | DONE |
| free-beta-tester-guide.md | Coordinator Email | Provided in invite (TBD) | Email provided when sending invite | PM | Before Beta | IN PROGRESS |
| free-beta-tester-guide.md | Beta End Date | Open-ended / TBD | No fixed end date for free beta | PM | Before Beta | IN PROGRESS |
| free-beta-tester-guide.md | Beta Pricing | None | No special pricing/perks - friend testing only | Product | Before Production | DONE |
| beta-feedback-form.md | Form URL | TBD (web not built) | Web feedback page not deployed yet | Dev | Before Beta | BLOCKED |
| qa-test-plan.md | Test Google Account | TBD | Google account for testing OAuth | QA | Before Testing | TODO |
| qa-test-plan.md | Test Apple ID | TBD | Apple ID for testing Sign-In | QA | BLOCKED (needs Apple Dev Account) | BLOCKED |
| qa-test-plan.md | RevenueCat Sandbox | TBD | RevenueCat sandbox configuration | Dev | DEFERRED (Beta doesn't need) | DEFERRED |

---

### High Priority (Beta Launch)

| Document | Section | Placeholder Text | Context | Owner | Target Date | Status |
|----------|---------|------------------|---------|-------|-------------|--------|
| free-beta-launch-checklist.md | Backend Environment | TBD | Choose hosting (Railway/Vercel/other) | DevOps | Before Beta | TODO |
| free-beta-launch-checklist.md | Test Accounts | TBD | Create 3+ test accounts for demo | Dev | Before Beta | TODO |
| free-beta-launch-checklist.md | Beta Tester List | TBD | Recruit 5-10 beta testers | PM | Before Beta | TODO |
| free-beta-launch-checklist.md | Feedback Channels | TBD | Set up email/form for feedback | PM | Before Beta | TODO |
| free-beta-launch-checklist.md | Bug Triage Process | TBD | Confirm triage workflow | Dev | Before Beta | TODO |

---

### Medium Priority (Production Launch)

| Document | Section | Placeholder Text | Context | Owner | Target Date | Status |
|----------|---------|------------------|---------|-------|-------------|--------|
| privacy-compliance-checklist.md | Analytics Consent | TBD (8 items) | Cookie banner, tracking consent, app store labels | Legal/Dev | Before Production | TODO |
| privacy-compliance-checklist.md | Database Provider DPA | TBD | Data Processing Agreement with DB provider | Legal | Before Production | TODO |
| privacy-compliance-checklist.md | Hosting Provider DPA | TBD | Data Processing Agreement with hosting provider | Legal | Before Production | TODO |
| privacy-compliance-checklist.md | User Rights Implementation | TBD (4 items) | Access/Rectification/Erasure/Portability features | Dev | Before Production | TODO |
| privacy-compliance-checklist.md | Data Request SLA | TBD (2 items) | Response time for access/deletion requests | Support | Before Production | TODO |
| incident-response.md | Monitoring Setup | TBD | Sentry/logging/alerting configuration | DevOps | Before Production | TODO |
| incident-response.md | Action Items Template | TODO (2 items) | Post-incident action tracking | DevOps | Before Production | TODO |
| beta-tester-tracker.md | Retention Policy | TBD | Data retention policy (e.g., delete 30 days post-beta) | Legal/PM | Before Production | TODO |
| beta-to-production-plan.md | Timeline | TBD | 4-8 weeks estimate needs confirmation | PM | Before Production | TODO |
| beta-release-notes-template.md | Next Release Date | TBD | Expected date for next release | PM | Per Release | TODO |
| free-beta-invite-templates.md | Future Perks | TBD (2 items) | Discounts/special offers for beta testers | Product | Before Production | TODO |

---

### Low Priority (Nice to Have)

| Document | Section | Placeholder Text | Context | Owner | Target Date | Status |
|----------|---------|------------------|---------|-------|-------------|--------|
| beta-support-macros.md | Prioritization Timeline | TBD | When feature will be prioritized | PM | Per Feature | TODO |
| privacy-compliance-checklist.md | Optional Security | TBD (4 items) | Certificate Pinning, E2E encryption, local processing | Dev | Post-Launch | DEFERRED |

---

## Technical Placeholders (Sample Data - Not Production Values)

These are **example values** that should be replaced with actual credentials during deployment. **Do NOT fill these in documentation** - they belong in `.env` files or secrets managers.

| Document | Pattern | Example | Where to Fill |
|----------|---------|---------|---------------|
| ENV_VARIABLES.md | DATABASE_URL | `ep-xxx.us-east-1.aws.neon.tech` | Production `.env` file |
| PROD_DEPLOY.md | DATABASE_URL | `ep-xxx.us-east-1.aws.neon.tech` | Production deployment |
| prod-preflight.md | GOOGLE_CLIENT_ID | `xxx.apps.googleusercontent.com` | Google Cloud Console + `.env` |
| prod-preflight.md | OPENAI_API_KEY | `sk-xxx` | OpenAI Platform + `.env` |
| prod-preflight.md | SENTRY_DSN | `https://xxx@sentry.io/xxx` | Sentry Project + `.env` |
| apple-developer-setup-guide.md | D-U-N-S Number | `08-xxx-xxxx` | Apple Developer account |
| apple-developer-setup-guide.md | APPLE_PRIVATE_KEY | `<.p8 文件内容>` | Apple Developer + `.env` |
| domain-hosting-setup-guide.md | JWT_SECRET | `<生成随机字符串>` | Generate with `openssl rand -hex 32` |
| domain-hosting-setup-guide.md | CNAME Target | `<Vercel/Railway 域名>` | Hosting provider dashboard |
| spec/epic-9-production-deploy.md | OPENAI_API_KEY | `sk-prod-xxx` | OpenAI Platform |
| spec/epic-4-payments.md | Stripe Signature | `t=xxx,v1=xxx` | Stripe webhook payload |

---

## Example Data Placeholders (Safe to Keep)

These are **illustrative examples** used in documentation and can remain as-is. They are clearly marked as examples and won't be confused with real data.

| Document | Pattern | Purpose |
|----------|---------|---------|
| beta-tester-tracker.md | `john@example.com` | Sample tester data for template |
| feedback-triage.md | `alice@example.com` | Sample reporter in examples |
| bug-report-template.md | `test@example.com` | Sample account for reproduction steps |
| domain-hosting-setup-guide.md | `admin@example.com` | Sample email for registration |
| support-playbook.md | `user@example.com` | Sample user email in scenarios |

---

## By Priority

### Summary Counts

| Priority | Count | % of Total |
|----------|-------|------------|
| **Critical** | 15 | 38% |
| **High** | 5 | 13% |
| **Medium** | 12 | 31% |
| **Low** | 4 | 10% |
| **Technical** (Not in docs) | 10 | - |
| **Example** (Keep as-is) | 5 | - |
| **Total Actionable** | **39** | **100%** |

### By Category

| Category | Count | Status |
|----------|-------|--------|
| Team Roles & Ownership | 20 | TODO |
| Contact Information | 4 | TODO |
| Timeline & Dates | 3 | TODO |
| Features & Decisions | 4 | TODO |
| Legal & Compliance | 15 | TODO |
| Technical Configuration | 10 | Handled in deployment |
| Example Data | 5 | No action needed |

---

## Notes

### Filling Guidelines

1. **Owner Names**: Use full names or GitHub handles (not "TBD")
2. **Email Addresses**: Use actual team/support emails (not example.com)
3. **Dates**: Use YYYY-MM-DD format
4. **URLs**: Ensure HTTPS and test links before marking done
5. **Sensitive Data**: Never commit API keys, passwords, or secrets to documentation
   - Use environment variables
   - Reference secrets manager (e.g., "See Vercel Environment Variables")

### Status Values

- **TODO**: Not started
- **IN PROGRESS**: Owner assigned, work in progress
- **BLOCKED**: Waiting on external dependency
- **DEFERRED**: Intentionally postponed (e.g., post-launch features)
- **DONE**: Verified and completed

### Review Cadence

- **Weekly**: Review Critical and High priority items
- **Before Beta**: All Critical items must be DONE
- **Before Production**: All Critical + High + Medium items must be DONE
- **Post-Launch**: Address Low priority items as needed

---

## Related Documents

- [Release Documentation Hub](index.md) - All release docs
- [Project Status Summary](project-status-summary.md) - Current status
- [Launch Readiness](launch-readiness.md) - Go/No-Go criteria
- [Free Beta Launch Checklist](free-beta-launch-checklist.md) - Beta preparation
- [Ownership Matrix](ownership-matrix.md) - Team responsibilities
- [Privacy Compliance Checklist](privacy-compliance-checklist.md) - GDPR/CCPA compliance
