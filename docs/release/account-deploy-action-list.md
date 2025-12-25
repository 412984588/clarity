# 账号/部署最短行动清单 (Fast Path)

**Date**: 2025-12-23
**Version**: 1.0
**Scope**: 只列必须人工账号/部署动作，不含本地可自动化步骤

---

## 一次性决策（先拍板）

- [ ] 选择托管平台：Vercel / Railway / Fly
- [ ] 选择数据库平台：Neon / Supabase / RDS
- [ ] 选定生产域名：`api.solacore.app`（或替代）

---

## 必要账号与付费（需人工操作）

- [ ] 域名注册商账号 + 购买域名（~$12/年）
- [ ] Apple Developer Program（$99/年，iOS 构建/上架必需）
- [ ] Google Play Console（$25 一次性，Android 上架必需）
- [ ] Stripe Live Mode 开通 + 生产密钥
- [ ] RevenueCat 生产项目 + 生产密钥
- [ ] OpenAI / Anthropic 生产 API Key（至少一个）
- [ ] （可选）Sentry 生产项目 + DSN

---

## 最短执行顺序（建议按此完成）

1. 购买域名并配置 DNS → 指向托管平台
2. 创建生产 PostgreSQL 实例
3. 部署后端到生产（获得 `https://api.solacore.app`）
4. 配置 Stripe Webhook：`https://api.solacore.app/webhooks/stripe`
5. 配置 RevenueCat Webhook：`https://api.solacore.app/webhooks/revenuecat`
6. 配置 OAuth 生产凭证（Google / Apple）
7. 生成 EAS 生产包（iOS 需 Apple Developer）
8. 提交 App Store / Play Store

---

## 完成后的产出物（可验收）

- [ ] 生产域名可访问（HTTPS 正常）
- [ ] `/health` 返回 `{"status":"healthy","version":"1.0.0","database":"connected"}`
- [ ] Stripe / RevenueCat Webhook 连通（测试事件成功）
- [ ] LLM API Key 可用（有额度）
- [ ] iOS/Android 生产构建包可下载

---

## 参考文档

- 依赖追踪表：`docs/release/launch-dependencies.md`
- 生产预检清单：`docs/release/prod-preflight.md`
- 上线准备度：`docs/release/launch-readiness.md`
- 生产部署 Runbook：`docs/PROD_DEPLOY.md`
- 商店提交清单：`docs/release/store-submission-checklist.md`
