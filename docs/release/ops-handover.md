# Operations Handover

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Purpose

本文档作为 Solacore 项目的运维交接文档，汇总所有运维相关的关键信息、负责人、Runbook 链接和待办事项。确保：

1. 新接手的运维人员能快速上手
2. 关键运维流程有明确文档可查
3. On-call 责任清晰
4. 待办事项不丢失

**适用人员**：
- 运维工程师（DevOps / SRE）
- On-call 工程师
- 新加入的技术负责人

---

## Ownership & On-call

### 当前负责人（占位）

| 角色 | 姓名 | 联系方式 | 职责范围 |
|------|------|----------|----------|
| **Tech Lead** | TBD | TBD | 架构决策、技术方向 |
| **DevOps Lead** | TBD | TBD | 基础设施、CI/CD、监控 |
| **On-call Primary** | TBD | TBD | 7×24 故障响应 |
| **On-call Secondary** | TBD | TBD | 备份 On-call |
| **Database Owner** | TBD | TBD | 数据库维护、迁移 |
| **Security Owner** | TBD | TBD | 安全事件响应 |

### On-call 轮值（占位）

| 周期 | Primary | Secondary |
|------|---------|-----------|
| Week 1 | TBD | TBD |
| Week 2 | TBD | TBD |
| Week 3 | TBD | TBD |
| Week 4 | TBD | TBD |

**On-call 工具**：
- 告警渠道：TBD（Sentry / PagerDuty / 其他）
- Escalation：Slack #oncall
- 记录：`docs/incidents/YYYY-MM-DD-incident-name.md`

---

## Runbooks & Key Links

### 核心 Runbook

| 文档 | 路径 | 用途 |
|------|------|------|
| **生产部署 Runbook** | `docs/PROD_DEPLOY.md` | 生产环境部署流程（8 步） |
| **Launch Day Runbook** | `docs/release/launch-day-runbook.md` | 上线当天执行清单 |
| **Incident Response** | `docs/release/incident-response.md` | P0/P1/P2 故障响应流程 |
| **Support Playbook** | `docs/release/support-playbook.md` | 用户支持流程和常见问题 |
| **Status Page Templates** | `docs/release/status-page-templates.md` | 对外沟通消息模板 |

### 配置文档

| 文档 | 路径 | 用途 |
|------|------|------|
| **环境变量** | `docs/ENV_VARIABLES.md` | 所有环境变量说明 |
| **数据库迁移** | `docs/DATABASE_MIGRATION.md` | Alembic 迁移指南 |
| **EAS Build** | `docs/release/eas-preview.md` | 移动端构建配置 |

### 决策文档

| 文档 | 路径 | 用途 |
|------|------|------|
| **Epic 9 Spec** | `docs/spec/epic-9-production-deploy.md` | 生产部署架构设计 |
| **Epic 9 Plan** | `docs/plan/epic-9-production-deploy-plan.md` | 生产部署实施计划 |
| **Risk Register** | `docs/release/risk-register.md` | 上线风险登记表 |
| **Launch Dependencies** | `docs/release/launch-dependencies.md` | 上线依赖追踪 |

---

## Deployment & Rollback Summary

**详细流程见**：`docs/PROD_DEPLOY.md`

### 快速参考

| 操作 | 命令 / 步骤 |
|------|-------------|
| **部署后端** | 见 `PROD_DEPLOY.md` Phase 2-3 |
| **数据库迁移** | `alembic upgrade head` |
| **回滚后端** | `git revert <commit> && git push` + 重新部署 |
| **回滚数据库** | `alembic downgrade -1`（谨慎使用） |
| **部署移动端** | `eas build --platform all --profile production` |
| **回滚移动端** | 无法回滚，只能发布新版本 |

### 关键脚本

| 脚本 | 路径 | 用途 |
|------|------|------|
| **冒烟测试** | `scripts/deploy_prod_smoke.sh` | 部署后健康检查 |
| **数据库迁移** | `scripts/migrate.sh` | 自动化迁移脚本 |
| **发布验证** | `scripts/verify-release.sh` | 完整验收流程 |

---

## Monitoring & Alerts

**详细指标定义见**：`docs/release/release-metrics.md`

### 关键指标

| 分类 | 关键指标 | 目标 | 告警阈值 |
|------|----------|------|----------|
| **Availability** | API Uptime | 99.5% | < 99% |
| **Performance** | API Response Time (P95) | < 500ms | > 1000ms |
| **Errors** | Error Rate | < 1% | > 5% |
| **Business** | Daily Active Users | TBD | TBD |
| **Revenue** | MRR | TBD | TBD |

### 告警设置

| 告警级别 | 响应要求 | 示例 |
|----------|----------|------|
| **P0 Critical** | 15 分钟内响应 | API 完全不可用 |
| **P1 Warning** | 1 小时内响应 | Error Rate > 5% |
| **P2 Info** | 工作时间内处理 | Disk Usage > 80% |

### 监控工具（占位）

| 工具 | 用途 | 状态 |
|------|------|------|
| **Sentry** | 错误监控 | TBD |
| **Hosting Provider Metrics** | API/Database 性能 | TBD |
| **Google Analytics** | 用户行为 | TBD |
| **App Store Connect** | iOS 下载/崩溃 | TBD |
| **Play Console** | Android 下载/崩溃 | TBD |

**详细告警阈值见**：`docs/release/release-metrics.md` 中的 "Alert Thresholds" 章节

---

## Open Items / TBD

### 待配置（上线前必须完成）

| # | 项目 | 负责人 | 状态 | 截止日期 |
|---|------|--------|------|----------|
| 1 | 确定 On-call 轮值表 | DevOps Lead | TBD | TBD |
| 2 | 配置 Sentry 告警 | DevOps Lead | TBD | TBD |
| 3 | 配置生产监控 Dashboard | DevOps Lead | TBD | TBD |
| 4 | 设置数据库备份策略 | Database Owner | TBD | TBD |
| 5 | 编写首次故障演练脚本 | Tech Lead | TBD | TBD |

### 待优化（上线后 30 天内）

| # | 项目 | 负责人 | 优先级 | 备注 |
|---|------|--------|--------|------|
| 1 | 自动化回滚流程 | DevOps Lead | High | 当前为手动 |
| 2 | 实现金丝雀发布 | DevOps Lead | Medium | 降低发布风险 |
| 3 | 完善监控覆盖率 | DevOps Lead | High | 补充业务指标 |
| 4 | 建立 Postmortem 流程 | Tech Lead | Medium | 故障复盘模板 |
| 5 | 编写更多 Runbook | DevOps Lead | Low | 常见操作文档化 |

### 待决策（需要讨论）

| # | 问题 | 涉及人员 | 状态 |
|---|------|----------|------|
| 1 | 数据库备份保留多久？ | Database Owner + Finance | TBD |
| 2 | On-call 补偿政策？ | HR + Tech Lead | TBD |
| 3 | 是否需要 24/7 On-call？ | Tech Lead + CEO | TBD |
| 4 | 监控工具选型（Sentry vs 其他）？ | DevOps Lead | TBD |
| 5 | 是否需要灾备环境？ | Tech Lead + Finance | TBD |

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------| | Release Documentation Hub | `docs/release/index.md` | 所有发布文档入口 |
| Launch Day Runbook | `docs/release/launch-day-runbook.md` | 上线当天执行清单 |
| Risk Register | `docs/release/risk-register.md` | 上线风险登记表 |
| Incident Response | `docs/release/incident-response.md` | 故障响应流程 |
| Release Metrics | `docs/release/release-metrics.md` | 监控指标定义 |
| Support Playbook | `docs/release/support-playbook.md` | 用户支持流程 |
| PROD_DEPLOY | `docs/PROD_DEPLOY.md` | 生产部署 Runbook |
