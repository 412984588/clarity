# 账号/部署执行模板 (Execution Template)

**Date**: 2025-12-23
**Version**: 1.0
**Purpose**: 记录“需要人工账号/部署”的执行信息、负责人、凭证与验收结果

---

## 1. 决策与前置信息

| 项目 | 选择/结果 | 负责人 | 备注 |
|------|-----------|--------|------|
| 托管平台 |  |  | Vercel / Railway / Fly |
| 数据库平台 |  |  | Neon / Supabase / RDS |
| 生产域名 |  |  | 例：api.solacore.app |
| 预算范围 |  |  | 月度预算区间 |

---

## 2. 账号/付费开通清单

| 项目 | 负责人 | 状态 | 证据/链接 |
|------|--------|------|-----------|
| 域名注册商账号 + 域名购买 |  | ⬜ |  |
| Apple Developer Program |  | ⬜ |  |
| Google Play Console |  | ⬜ |  |
| Stripe Live Mode |  | ⬜ |  |
| RevenueCat 生产项目 |  | ⬜ |  |
| OpenAI / Anthropic Key |  | ⬜ |  |
| Sentry 生产项目（可选） |  | ⬜ |  |

---

## 3. 关键 URL / 凭证占位

| 项目 | 值 | 备注 |
|------|----|------|
| 生产 API Base URL |  | 例：https://api.solacore.app |
| 数据库连接串 |  | 仅记录“掩码版本” |
| Stripe Webhook |  | `/webhooks/stripe` |
| RevenueCat Webhook |  | `/webhooks/revenuecat` |
| Google OAuth Redirect URI |  |  |
| Apple Sign‑In Redirect URI |  |  |
| Sentry DSN |  | 可选 |

---

## 4. 部署与验收记录

| 步骤 | 负责人 | 状态 | 证据/结果 |
|------|--------|------|-----------|
| DNS 已配置 |  | ⬜ |  |
| 生产数据库创建完成 |  | ⬜ |  |
| 后端部署完成 |  | ⬜ |  |
| `/health` 验证 |  | ⬜ | `{"status":"healthy","version":"1.0.0","database":"connected"}` |
| Stripe Webhook 测试 |  | ⬜ | 测试事件成功 |
| RevenueCat Webhook 测试 |  | ⬜ | 测试事件成功 |
| EAS 生产构建 |  | ⬜ | Build ID / 链接 |
| iOS/Android 上架提交 |  | ⬜ |  |

---

## 5. 签字确认

| 角色 | 姓名 | 日期 | 备注 |
|------|------|------|------|
| 产品负责人 |  |  |  |
| 技术负责人 |  |  |  |
| 财务负责人 |  |  |  |

---

## 参考文档

- 快速行动清单：`docs/release/account-deploy-action-list.md`
- 预检清单：`docs/release/prod-preflight.md`
- 部署 Runbook：`docs/PROD_DEPLOY.md`
- 商店提交清单：`docs/release/store-submission-checklist.md`
