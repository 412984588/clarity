# Release Documentation Inventory

**Version**: 1.1
**Last Updated**: 2025-12-24
**Purpose**: Complete inventory of all release documentation with categorization

---

## Purpose

This document provides a comprehensive inventory of all release-related documentation in the `docs/release/` directory. It categorizes each document by purpose, audience, stage, status, and shareability to help:

- New team members quickly understand the documentation landscape
- Identify which documents are intended for external sharing vs internal use
- Ensure proper documentation coverage across all release phases
- Facilitate document maintenance and updates

---

## Inventory Table

| Document | Purpose | Audience | Stage | Status | Shareable |
|----------|---------|----------|-------|--------|-----------|
| **1. Status & Planning** | | | | | |
| [index.md](index.md) | Release documentation hub - single entry point | Internal | Both | Guide | No |
| [project-status-summary.md](project-status-summary.md) | Project global status summary | Internal | Both | Report | No |
| [remaining-work.md](remaining-work.md) | Incomplete work statistics and next actions | Internal | Both | Report | No |
| [launch-readiness.md](launch-readiness.md) | Launch readiness scorecard (Go/No-Go) | Internal | Both | Checklist | No |
| [launch-dependencies.md](launch-dependencies.md) | Launch dependency tracker | Internal | Both | Checklist | No |
| [risk-register.md](risk-register.md) | Launch risk register | Internal | Both | Checklist | No |
| [go-no-go-minutes.md](go-no-go-minutes.md) | Release decision meeting minutes template | Internal | Both | Template | No |
| [ownership-matrix.md](ownership-matrix.md) | Launch RACI / ownership matrix | Internal | Both | Checklist | No |
| [launch-communications.md](launch-communications.md) | Launch communication plan | Internal | Both | Process | No |
| [release-approval-checklist.md](release-approval-checklist.md) | Release approval checklist | Internal | Both | Checklist | No |
| [one-page-update.md](one-page-update.md) | Investor/partner one-page update | External | Both | Report | Yes |
| **2. Free Beta Testing** | | | | | |
| [free-beta-start-here.md](free-beta-start-here.md) | Quick start guide (1 hour onboarding + 7 day plan) | Internal | Free Beta | Guide | No |
| [free-beta-launch-checklist.md](free-beta-launch-checklist.md) | Free beta launch checklist (Pre-Launch/Launch Day/Week 1) | Internal | Free Beta | Checklist | No |
| [free-beta-tester-guide.md](free-beta-tester-guide.md) | Tester complete guide (install/test/feedback) | External | Free Beta | Guide | Yes |
| [free-beta-invite-templates.md](free-beta-invite-templates.md) | Invite and communication templates (Invite/Welcome/Reminder/Follow-up) | External | Free Beta | Template | Yes |
| [beta-share-pack.md](beta-share-pack.md) | External share pack (shareable content + email templates + FAQs) | External | Free Beta | Guide | Yes |
| [beta-tester-tracker.md](beta-tester-tracker.md) | Tester status tracker (Tester ID/Status/Feedback) | Internal | Free Beta | Template | No |
| [free-beta-ops-playbook.md](free-beta-ops-playbook.md) | Operations handbook (Daily/Weekly Checklist/Quality Gates) | Internal | Free Beta | Process | No |
| [beta-release-notes-template.md](beta-release-notes-template.md) | Release notes template (Version/Highlights/Fixed) | External | Free Beta | Template | Yes |
| [feedback-triage.md](feedback-triage.md) | Feedback triage workflow (Severity/SLA/Owner) | Internal | Free Beta | Process | No |
| [beta-feedback-form.md](beta-feedback-form.md) | Beta feedback form template | External | Free Beta | Template | Yes |
| [bug-report-template.md](bug-report-template.md) | Bug report template | External | Free Beta | Template | Yes |
| [beta-known-issues.md](beta-known-issues.md) | Known issues tracker (Status/Workaround/Priority) | Internal | Free Beta | Report | No |
| [beta-support-macros.md](beta-support-macros.md) | Support reply templates (Bug confirm/Fix notification/FAQ reply) | Internal | Free Beta | Template | No |
| [beta-exit-criteria.md](beta-exit-criteria.md) | Beta exit criteria (Go/No-Go) | Internal | Free Beta | Checklist | No |
| [beta-to-production-plan.md](beta-to-production-plan.md) | Beta → Production transition plan (Phases/Workstreams/Timeline) | Internal | Free Beta | Process | No |
| [beta-weekly-status-template.md](beta-weekly-status-template.md) | Weekly report template (KPIs/Progress/Decisions) | Internal | Free Beta | Template | No |
| [beta-feedback-summary-template.md](beta-feedback-summary-template.md) | Feedback summary report template (weekly aggregation) | External | Free Beta | Template | Yes |
| [beta-retrospective-template.md](beta-retrospective-template.md) | Beta retrospective template (Goals vs Outcomes/Learnings/Production Gap) | Internal | Free Beta | Template | No |
| [beta-issue-intake.md](beta-issue-intake.md) | Beta issue intake guide (reporting channels/severity/SLA/privacy) | External | Free Beta | Guide | Yes |
| **3. Demo & Presentation** | | | | | |
| [demo-script.md](demo-script.md) | 3-minute external demo script + checklist | External | Both | Guide | Yes |
| [local-demo-runbook.md](local-demo-runbook.md) | Local demo runbook | Internal | Both | Process | No |
| **4. Testing & Verification** | | | | | |
| [qa-test-plan.md](qa-test-plan.md) | QA/UAT test plan (25 test cases) | Internal | Both | Checklist | No |
| [qa-execution-log.md](qa-execution-log.md) | QA/UAT execution log template | Internal | Both | Template | No |
| [manual-qa-checklist.md](manual-qa-checklist.md) | Manual QA execution checklist | Internal | Both | Checklist | No |
| [local-deploy-verify.md](local-deploy-verify.md) | Local deployment verification results | Internal | Both | Report | No |
| [eas-preview-verify.md](eas-preview-verify.md) | EAS Preview build verification | Internal | Free Beta | Report | No |
| [eas-preview.md](eas-preview.md) | EAS Preview configuration guide | Internal | Free Beta | Guide | No |
| **5. Production Deployment** | | | | | |
| [domain-hosting-setup-guide.md](domain-hosting-setup-guide.md) | Domain/hosting/database setup guide (unblock production deployment) | Internal | Production | Guide | No |
| [apple-developer-setup-guide.md](apple-developer-setup-guide.md) | Apple Developer account setup guide (unblock iOS deployment) | Internal | Production | Guide | No |
| [account-deploy-action-list.md](account-deploy-action-list.md) | Account/deployment shortest action list | Internal | Production | Checklist | No |
| [account-deploy-execution-template.md](account-deploy-execution-template.md) | Account/deployment execution template | Internal | Production | Template | No |
| [prod-preflight.md](prod-preflight.md) | Production deployment preflight checklist | Internal | Production | Checklist | No |
| [launch-day-runbook.md](launch-day-runbook.md) | Launch day runbook | Internal | Production | Process | No |
| [release-checklist.md](release-checklist.md) | Production release checklist | Internal | Production | Checklist | No |
| **6. Operations & Support** | | | | | |
| [ops-handover.md](ops-handover.md) | Operations handover document | Internal | Production | Guide | No |
| [support-playbook.md](support-playbook.md) | Production support playbook | Internal | Production | Process | No |
| [support.md](support.md) | Support documentation | External | Both | Guide | Yes |
| [incident-response.md](incident-response.md) | Incident response plan | Internal | Production | Process | No |
| [status-page-templates.md](status-page-templates.md) | Status page templates | Internal | Production | Template | No |
| **7. Privacy & Compliance** | | | | | |
| [privacy.md](privacy.md) | Privacy policy | External | Both | Guide | Yes |
| [privacy-compliance-checklist.md](privacy-compliance-checklist.md) | Privacy compliance checklist | Internal | Production | Checklist | No |
| [store-privacy-answers.md](store-privacy-answers.md) | App Store privacy questionnaire answers | Internal | Production | Template | No |
| [store-submission-checklist.md](store-submission-checklist.md) | App Store submission checklist | Internal | Production | Checklist | No |
| **8. Metrics & Monitoring** | | | | | |
| [release-metrics.md](release-metrics.md) | Release metrics and KPIs | Internal | Both | Guide | No |

---

## Summary Counts

### By Audience

| Audience | Count |
|----------|-------|
| Internal | 42 |
| External | 13 |
| **Total** | **55** |

### By Stage

| Stage | Count |
|-------|-------|
| Free Beta | 21 |
| Production | 15 |
| Both | 19 |
| **Total** | **55** |

### By Status

| Status | Count |
|--------|-------|
| Checklist | 14 |
| Template | 12 |
| Process | 8 |
| Guide | 13 |
| Report | 8 |
| **Total** | **55** |

### By Shareability

| Shareable | Count |
|-----------|-------|
| Yes | 13 |
| No | 42 |
| **Total** | **55** |

---

## Notes

### Audience Classification

- **Internal**: Documents for team members, developers, QA, project managers (flow charts, execution logs, internal checklists)
- **External**: Documents intended for testers, investors, partners, or public distribution (tester guides, privacy policy, demo scripts)

### Stage Classification

- **Free Beta**: Documents specifically for the free beta testing phase (no payments, friend testing)
- **Production**: Documents for production launch and operations (App Store submission, production deployment)
- **Both**: Documents applicable to both phases (QA plans, demo scripts, privacy policy)

### Shareability

- **Yes**: Documents that can be shared with external parties (testers, investors, partners)
- **No**: Internal process documents that should remain confidential

### Maintenance

- This inventory should be updated whenever:
  - New documents are added to `docs/release/`
  - Documents are renamed or removed
  - Document purposes or classifications change

---

## Related Documents

- [Release Documentation Hub](index.md) - Single entry point for all release docs
- [Project Status Summary](project-status-summary.md) - Current project status
- [Free Beta - Start Here](free-beta-start-here.md) - Quick start for beta launch
