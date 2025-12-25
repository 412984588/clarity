# Release Guide

This document outlines the release process for Solacore.

---

## Pre-Release Checklist

### Code Quality
- [ ] All tests pass (`poetry run pytest` / `npm test`)
- [ ] Linting passes (`ruff check .` / `npm run lint`)
- [ ] Type checking passes (`mypy app` / `tsc --noEmit`)
- [ ] No pending code review comments

### Database
- [ ] All migrations have been tested
- [ ] Downgrade paths have been verified
- [ ] Production backup scheduled

### Environment
- [ ] All required environment variables documented
- [ ] Secrets rotated if needed
- [ ] Third-party API keys verified

### Documentation
- [ ] CHANGELOG.md updated
- [ ] API documentation current
- [ ] README reflects latest changes

---

## Release Process

### 1. Version Bump

Update version in:
- `solacore-api/pyproject.toml`
- `solacore-mobile/app.json` (version + buildNumber/versionCode)

```bash
# Example: Bump to 1.2.0
# Edit files manually or use:
npm version minor  # in solacore-mobile
```

### 2. Update CHANGELOG

Add release notes following [Keep a Changelog](https://keepachangelog.com/) format.

### 3. Create Release Branch (Optional)

For major releases:
```bash
git checkout -b release/1.2.0
```

### 4. Backend Deployment

```bash
cd solacore-api

# Run final checks
poetry run ruff check .
poetry run mypy app --ignore-missing-imports
poetry run pytest -v

# Deploy (method depends on hosting)
# Railway: git push railway main
# Docker: docker build && docker push
```

### 5. Database Migration

```bash
# Using migration script
./scripts/migrate.sh upgrade

# Manual
cd solacore-api
poetry run alembic upgrade head
```

### 6. Mobile Build

```bash
cd solacore-mobile

# Preview build (internal testing)
eas build --profile preview --platform all

# Production build
eas build --profile production --platform all

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

### 7. Create Git Tag

```bash
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

### 8. GitHub Release

```bash
gh release create v1.2.0 \
  --title "v1.2.0" \
  --notes-file CHANGELOG.md
```

---

## Rollback Procedures

### Backend Rollback

```bash
# 1. Revert to previous version
git revert HEAD
git push

# 2. Rollback database if needed
./scripts/migrate.sh rollback

# 3. Verify health
curl https://api.solacore.app/health
```

### Mobile Rollback

For iOS:
- Use App Store Connect to revert to previous build
- Or submit expedited review for hotfix

For Android:
- Use Google Play Console staged rollout
- Halt rollout and revert percentage to 0%

---

## Emergency Contacts

| Role | Contact |
|------|---------|
| Backend Lead | [TBD] |
| Mobile Lead | [TBD] |
| DevOps | [TBD] |

---

## Post-Release

- [ ] Monitor error tracking (Sentry)
- [ ] Check application metrics
- [ ] Verify critical user flows
- [ ] Announce release internally
- [ ] Update status page if applicable
