# Launch Day Runbook

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Purpose & Scope

本文档定义 Clarity 生产上线当天及前后的执行流程、时间线、责任人和应急措施。适用于首次生产发布及后续重大版本更新。不包含具体命令，仅描述步骤和时序。

---

## Timeline

| Phase | Time | Activities |
|-------|------|------------|
| **T-7d** | 上线前 7 天 | Go/No-Go 决策会议、确认所有 Blockers 已解决 |
| **T-2d** | 上线前 2 天 | 完成 QA 测试、冻结代码、准备回滚方案 |
| **T-1d** | 上线前 1 天 | 最终检查、通知相关方、准备监控面板 |
| **T-0** | 上线当天 | 执行部署、验证健康检查、发布公告 |
| **T+1d** | 上线后 1 天 | 监控观察、收集反馈、处理紧急问题 |
| **T+7d** | 上线后 7 天 | 复盘总结、更新文档、关闭临时告警 |

---

## Roles & Owners

**Reference**: `docs/release/ownership-matrix.md`

| Role | Owner | Responsibility on Launch Day |
|------|-------|------------------------------|
| **Launch Commander** | TBD | 总指挥，最终决策权 |
| **Backend Lead** | TBD | 后端部署、数据库迁移 |
| **Mobile Lead** | TBD | App Store / Play Store 发布 |
| **DevOps** | TBD | 基础设施、监控告警 |
| **QA Lead** | TBD | 冒烟测试、回归验证 |
| **Support Lead** | TBD | 用户反馈、问题上报 |
| **Comms Lead** | TBD | 发布公告、用户通知 |

---

## Pre-Launch Checklist

上线前必须完成的检查项（T-1d 或更早）：

| # | Item | Owner | Status |
|---|------|-------|--------|
| 1 | Go/No-Go 决策已通过 | Launch Commander | [ ] |
| 2 | 所有 Critical Blockers 已解决 | All Leads | [ ] |
| 3 | QA 测试通过率 ≥ 95% | QA Lead | [ ] |
| 4 | 代码已冻结（Code Freeze） | Backend/Mobile Lead | [ ] |
| 5 | 回滚方案已准备并测试 | Backend Lead | [ ] |
| 6 | 监控告警已配置 | DevOps | [ ] |
| 7 | 发布公告草稿已准备 | Comms Lead | [ ] |
| 8 | 支持团队已就位 | Support Lead | [ ] |
| 9 | 相关方已通知上线时间 | Launch Commander | [ ] |
| 10 | 生产环境变量已配置并验证 | Backend Lead | [ ] |

---

## Launch Steps

上线当天（T-0）执行步骤：

| # | Step | Owner | Duration | Checkpoint |
|---|------|-------|----------|------------|
| 1 | 团队集合、确认 Ready | Launch Commander | 10 min | All present |
| 2 | 执行数据库迁移 | Backend Lead | 15 min | Migration success |
| 3 | 部署后端服务 | DevOps | 15 min | Health check green |
| 4 | 执行冒烟测试 | QA Lead | 20 min | Core flows pass |
| 5 | 发布移动端（App Store / Play Store） | Mobile Lead | 30 min | Build submitted |
| 6 | 验证 Webhook 连通性 | Backend Lead | 10 min | Stripe/RevenueCat OK |
| 7 | 开启生产流量 | DevOps | 5 min | Traffic flowing |
| 8 | 发布公告 | Comms Lead | 10 min | Announcement sent |
| 9 | 进入监控观察期 | All | 2 hours | Metrics stable |
| 10 | 宣布上线成功 | Launch Commander | 5 min | Celebration! |

---

## Post-Launch Monitoring

上线后需持续关注的指标和观察点（T+0 至 T+7d）：

| Metric | Threshold | Alert Level | Owner |
|--------|-----------|-------------|-------|
| API 响应时间 | < 500ms p95 | Warning > 1s | Backend Lead |
| API 错误率 | < 1% | Critical > 5% | Backend Lead |
| 数据库连接数 | < 80% max | Warning > 90% | DevOps |
| 内存使用率 | < 80% | Warning > 90% | DevOps |
| 用户注册成功率 | > 95% | Warning < 90% | QA Lead |
| 支付成功率 | > 98% | Critical < 95% | Backend Lead |
| Crash-free 用户率 | > 99% | Warning < 98% | Mobile Lead |
| 用户投诉数 | < 10/day | Warning > 20 | Support Lead |

---

## Rollback Triggers

以下情况应触发回滚决策：

| Trigger | Severity | Decision Maker |
|---------|----------|----------------|
| API 错误率 > 10% 持续 5 分钟 | Critical | Launch Commander |
| 数据库连接池耗尽 | Critical | Launch Commander |
| 支付成功率 < 90% | Critical | Launch Commander |
| 用户无法登录 | Critical | Launch Commander |
| 关键功能（Solve 流程）不可用 | Critical | Launch Commander |
| Crash-free 率 < 95% | High | Mobile Lead |
| 安全漏洞被利用 | Critical | Launch Commander |

**回滚决策流程**：
1. 发现问题 → 2. 确认严重程度 → 3. 通知 Launch Commander → 4. 决策（修复 or 回滚） → 5. 执行 → 6. 验证 → 7. 通知相关方

---

## Communication Plan

| Event | Who to Notify | When | Channel | Owner |
|-------|---------------|------|---------|-------|
| 上线开始 | 团队全员 | T-0 开始时 | Slack/企业微信 | Launch Commander |
| 部署完成 | 团队全员 | 每步完成后 | Slack/企业微信 | DevOps |
| 用户公告 | 所有用户 | 冒烟测试通过后 | App 内/邮件/社交媒体 | Comms Lead |
| 上线成功 | 团队 + 管理层 | 监控观察期结束后 | Slack/邮件 | Launch Commander |
| 发现问题 | 相关负责人 | 立即 | Slack/电话 | 发现者 |
| 触发回滚 | 团队全员 + 管理层 | 决策后立即 | Slack/电话 | Launch Commander |
| 回滚完成 | 团队 + 用户 | 回滚验证后 | Slack/App 内 | Comms Lead |

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| 生产部署 Runbook | `docs/PROD_DEPLOY.md` | 具体部署命令 |
| Go/No-Go 会议纪要 | `docs/release/go-no-go-minutes.md` | 发布决策记录 |
| 负责人矩阵 | `docs/release/ownership-matrix.md` | RACI 分工 |
| 风险登记表 | `docs/release/risk-register.md` | 风险跟踪 |
| QA 执行记录 | `docs/release/qa-execution-log.md` | 测试结果 |
| 环境变量文档 | `docs/ENV_VARIABLES.md` | 配置清单 |
| 发布检查清单 | `docs/release/release-checklist.md` | 发布确认项 |
