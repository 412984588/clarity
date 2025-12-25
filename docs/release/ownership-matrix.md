# Launch Ownership Matrix (RACI)

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Overview

本文档定义 Clarity 生产上线各项任务的责任分工，使用 RACI 模型明确每项任务的负责人（Responsible）、决策者（Accountable）、咨询对象（Consulted）和知会对象（Informed）。用于确保上线过程中职责清晰、沟通顺畅。

---

## Roles

| Role | Team/Person | Responsibility |
|------|-------------|----------------|
| **Product** | Owner (self) | 产品决策、用户体验、发布时机 |
| **Backend** | Owner (self) | API 开发、数据库、服务端部署 |
| **Mobile** | Owner (self) | iOS/Android 应用开发、App Store 提交 |
| **DevOps** | Owner (self) | 基础设施、CI/CD、监控告警 |
| **QA** | Owner (self) | 测试执行、质量把关、Bug 跟踪 |
| **Finance** | Owner (self) | 支付账号、订阅配置、财务合规 |
| **Support** | Owner (self) | 用户支持、文档维护、FAQ |
| **Marketing** | Owner (self) | 发布公告、用户沟通、推广 |

---

## RACI Matrix

| Task | Responsible | Accountable | Consulted | Informed | Status |
|------|-------------|-------------|-----------|----------|--------|
| **域名购买与配置** | DevOps | Product | Backend | All | BLOCKED |
| **托管服务选型与部署** | DevOps | Product | Backend | All | UNKNOWN |
| **数据库创建与配置** | DevOps | Backend | - | Product, QA | UNKNOWN |
| **数据库迁移执行** | Backend | Backend | DevOps | Product, QA | PENDING |
| **OAuth 生产凭证配置** | Backend | Backend | Mobile | Product | OPEN |
| **Stripe Live Mode 激活** | Finance | Product | Backend | All | OPEN |
| **RevenueCat 生产配置** | Mobile | Product | Finance | Backend | OPEN |
| **LLM API Key 配置** | Backend | Backend | Product | DevOps | OPEN |
| **监控告警配置** | DevOps | Backend | - | Product, QA | OPEN |
| **QA 测试执行** | QA | QA | Backend, Mobile | Product | IN_PROGRESS |
| **发布决策 (Go/No-Go)** | Product | Product | All Leads | All | PENDING |
| **上线执行** | DevOps | Product | Backend, Mobile | All | PENDING |
| **回滚方案准备** | Backend | Backend | DevOps | Product, QA | OPEN |
| **iOS 构建与提交** | Mobile | Product | - | All | BLOCKED |
| **Android 构建与提交** | Mobile | Product | - | All | PENDING |
| **用户支持准备** | Support | Product | Backend | Marketing | PENDING |

---

## RACI Legend

| Code | Meaning |
|------|---------|
| **R** (Responsible) | 执行任务的人，实际完成工作 |
| **A** (Accountable) | 最终决策者，对结果负责（每任务仅 1 人） |
| **C** (Consulted) | 提供意见的人，双向沟通 |
| **I** (Informed) | 需被通知的人，单向沟通 |

---

## Status Legend

| Status | Meaning |
|--------|---------|
| **BLOCKED** | 缺少外部依赖，无法推进 |
| **UNKNOWN** | 待确认负责人或状态 |
| **OPEN** | 任务已分配，尚未开始 |
| **IN_PROGRESS** | 进行中 |
| **PENDING** | 等待前置任务完成 |
| **DONE** | 已完成 |

---

## Notes & Assumptions

| Item | Note |
|------|------|
| 负责人待定 | 所有 TBD 需在 Go/No-Go 会议前确定 |
| 单人团队 | 如某角色由同一人兼任，可合并 |
| 外部依赖 | 域名、Apple Developer、Google Play 需外部采购 |
| 上线窗口 | 待 Product 与 Marketing 协调后确定 |
| 回滚权限 | DevOps 和 Backend 均有权执行回滚 |

---

## Related Documents

- 上线依赖追踪: `docs/release/launch-dependencies.md`
- 风险登记表: `docs/release/risk-register.md`
- Go/No-Go 会议纪要: `docs/release/go-no-go-minutes.md`
- 生产部署 Runbook: `docs/PROD_DEPLOY.md`
