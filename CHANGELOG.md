# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Sentry Monitoring** (Phase 4.2)
  - Backend: sentry-sdk integration with FastAPI
  - Mobile: @sentry/react-native integration
  - Error tracking and performance monitoring ready
- **Test Coverage Boost** (Phase 4.3)
  - Coverage: 79% → 88%
  - New tests: AI Service, Stripe Service, OAuth Service
  - Total tests: 113 → 133

### Security
- **Security Hardening** (Phase 1)
  - Prompt injection guard with Unicode normalization
  - Device limit race condition fix with row-level locking
  - Production config validation on startup
- **Security Audit** (Phase 4.4)
  - No hardcoded API keys
  - No SQL injection vulnerabilities
  - No XSS risks
  - No environment variable leakage

### Changed
- Frontend local storage upgraded from AsyncStorage to SQLite (Phase 2)
- Password reset URL now uses configurable FRONTEND_URL (Phase 3)

### Documentation
- Production deployment guide (DEPLOY_MANUAL.md)
- One-click deployment script (deploy.sh)
- CI/CD workflows (GitHub Actions)
- Privacy compliance checklist updates
- Incident response documentation
- EAS Secrets configuration guide

## [0.5.0] - 2025-12-22

### Added
- **Solve 5-Step Flow**: Complete implementation of the 5-step problem-solving flow
  - Backend: PATCH /sessions/{id} endpoint with state machine validation
  - Backend: Usage counting and step history tracking
  - Mobile: Step progress indicator component
  - Mobile: Option cards and action cards
  - Mobile: i18n support with expo-localization
  - Mobile: Local SQLite storage for offline support
- Prompt injection guard tests
- Session analytics events

### Fixed
- Alembic multi-head migration issue
- mypy type checking errors in SQLAlchemy Column assignments

## [0.4.0] - 2025-12-XX

### Added
- RevenueCat webhook integration for mobile subscriptions
- Stripe webhook integration for web subscriptions
- Subscription management endpoints

## [0.3.0] - 2025-12-XX

### Added
- Google OAuth authentication
- Apple Sign In authentication
- JWT-based session management

## [0.2.0] - 2025-12-XX

### Added
- FastAPI backend foundation
- PostgreSQL database with SQLAlchemy
- Alembic migrations
- Basic health check endpoint

## [0.1.0] - 2025-12-XX

### Added
- Initial project setup
- React Native Expo mobile app
- Basic navigation structure

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 0.5.0 | 2025-12-22 | Solve 5-Step Flow |
| 0.4.0 | TBD | Subscription Integration |
| 0.3.0 | TBD | Authentication |
| 0.2.0 | TBD | Backend Foundation |
| 0.1.0 | TBD | Initial Setup |
