# Launch Dependencies Tracker

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Overview

本文档追踪 Solacore 上线所需的所有外部账号、域名、API 密钥等依赖项。

**状态说明**：
- **READY**: 已准备就绪，可直接使用
- **BLOCKED**: 缺少必要资源，无法继续
- **UNKNOWN**: 待确认状态
- **DEFERRED**: 当前阶段不需要，延后处理（免费内测阶段）

---

## Dependencies Tracker

| Category | Dependency | 账号/资源 | Status | 负责人 | 预计时间 | 备注 |
|----------|------------|-----------|--------|--------|----------|------|
| **Infrastructure** | Domain | `api.solacore.app` | BLOCKED | | | 需购买域名并配置 DNS → [Domain & Hosting Setup Guide](domain-hosting-setup-guide.md) |
| **Infrastructure** | Hosting Provider | Vercel / Railway / Fly.io | UNKNOWN | | | 需决定托管服务商 → [Domain & Hosting Setup Guide](domain-hosting-setup-guide.md) |
| **Infrastructure** | PostgreSQL | Neon / Supabase / RDS | UNKNOWN | | | 需决定数据库托管商 → [Domain & Hosting Setup Guide](domain-hosting-setup-guide.md) |
| **Mobile - iOS** | Apple Developer Account | Apple Developer Program | BLOCKED | | | 需 $99/年订阅 → [Apple Developer Setup Guide](apple-developer-setup-guide.md) |
| **Mobile - iOS** | App Store Connect | App Store 提交 | BLOCKED | | | 依赖 Apple Developer Account |
| **Mobile - iOS** | Apple Sign-In Credentials | Services ID + Key | BLOCKED | | | 依赖 Apple Developer Account |
| **Mobile - Android** | Google Play Console | Play Console 账号 | DEFERRED | | | 商店提交在免费内测阶段延后 |
| **Mobile - Android** | Google OAuth Client ID | Production Client ID | UNKNOWN | | | 需在 Google Cloud Console 配置 |
| **Payments** | Stripe Live Mode | Live API Keys | DEFERRED | | | 免费内测阶段无需支付功能 |
| **Payments** | Stripe Webhook Secret | Production Webhook | DEFERRED | | | 免费内测阶段无需支付功能 |
| **Payments** | RevenueCat Production | RC Project + API Keys | DEFERRED | | | 免费内测阶段无需支付功能 |
| **Payments** | RevenueCat Webhook | Production Webhook | DEFERRED | | | 免费内测阶段无需支付功能 |
| **AI/LLM** | OpenAI API Key | Production Key | UNKNOWN | | | 需确认是否有生产用 API Key |
| **AI/LLM** | Anthropic API Key | Production Key | UNKNOWN | | | 备用 LLM 引擎 |
| **Monitoring** | Sentry DSN | Production Project | UNKNOWN | | | 可选，推荐用于错误追踪 |
| **Monitoring** | Analytics | Google Analytics / Mixpanel | UNKNOWN | | | 可选，推荐用于用户行为分析 |

---

## Critical Path

以下依赖项构成上线关键路径（缺一不可）：

```
Domain → Hosting → Database → Backend Deploy → Webhooks
                                    ↓
Apple Developer → iOS Build → App Store
                                    ↓
                            Production Launch
```

---

## Dependency Groups

### Group A: 可立即行动（无外部依赖）

| Dependency | Action |
|------------|--------|
| Hosting Provider | 决定选择 Vercel / Railway / Fly.io |
| PostgreSQL Provider | 决定选择 Neon / Supabase / RDS |
| OpenAI API Key | 确认是否已有可用 Key |
| Anthropic API Key | 确认是否已有可用 Key |

### Group B: 需账号/付费

| Dependency | Cost | Action |
|------------|------|--------|
| Domain | ~$12/年 | 购买 solacore.app 或替代域名 |
| Apple Developer | $99/年 | 注册 Apple Developer Program |
| Google Play Console | $25 一次性 | 注册 Google Play 开发者账号 |

### Group C: 需 Production URL 后配置

| Dependency | Prerequisite |
|------------|--------------|
| Stripe Webhook | 需 `https://api.solacore.app/webhooks/stripe` |
| RevenueCat Webhook | 需 `https://api.solacore.app/webhooks/revenuecat` |
| Apple Sign-In | 需 Apple Developer + Return URL |
| Google OAuth | 需 Production Redirect URI |

---

## Status Legend

| Status | Meaning | Next Action |
|--------|---------|-------------|
| READY | 已就绪 | 无需操作 |
| BLOCKED | 被阻塞 | 见"备注"列了解缺失项 |
| UNKNOWN | 待确认 | 需负责人确认当前状态 |
| DEFERRED | 延后处理 | 当前免费内测阶段不需要 |

---

## Related Documents

- 项目状态总结: `docs/release/project-status-summary.md`
- 生产部署指南: `docs/PROD_DEPLOY.md`
- 环境变量文档: `docs/ENV_VARIABLES.md`
