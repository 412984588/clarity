# Launch Risk Register

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Overview

本文档记录 Clarity 生产上线前识别的主要风险，包括外部账号依赖、基础设施配置、第三方服务集成等方面。每项风险标注影响程度、发生概率、缓解方向及当前状态，用于上线决策参考和风险跟踪。

---

## Risk Table

| ID | Risk | Impact | Likelihood | Mitigation | Owner | Status |
|----|------|--------|------------|------------|-------|--------|
| R01 | **域名未配置** | High | High | 购买域名，配置 DNS 指向托管服务 | Infra | BLOCKED |
| R02 | **Apple Developer 账号未开通** | High | High | 注册 Apple Developer Program ($99/年) | Product | BLOCKED |
| R03 | **Google Play Console 未开通** | Low | Low | 注册 Google Play Developer ($25 一次性) | Product | DEFERRED |
| R04 | **Stripe Live Mode 未激活** | Low | Low | 完成 Stripe 身份验证，激活 Live Mode | Finance | DEFERRED |
| R05 | **RevenueCat 生产配置缺失** | Low | Low | 配置生产环境 App，关联 App Store / Play Store | Product | DEFERRED |
| R06 | **LLM API Key 额度不足** | Medium | Medium | 申请生产级 API Key，设置用量预警 | Dev | OPEN |
| R07 | **OAuth 生产凭证未配置** | Medium | High | 在 Google Cloud / Apple Developer 创建生产凭证 | Dev | OPEN |
| R08 | **数据库备份策略未定** | Medium | Low | 确定备份频率、保留期限、恢复流程 | Infra | UNKNOWN |
| R09 | **监控告警未配置** | Medium | Medium | 配置 Sentry / UptimeRobot / PagerDuty | Dev | OPEN |
| R10 | **发布窗口未确定** | Low | Medium | 与产品/运营协调上线时间，避开高峰 | Product | UNKNOWN |
| R11 | **回滚方案未测试** | Medium | Low | 准备数据库回滚脚本，测试 EAS 历史版本发布 | Dev | OPEN |
| R12 | **QA 测试未完成** | High | Medium | 完成 qa-test-plan.md 中所有 NOT RUN 用例 | QA | OPEN |

---

## Status Legend

| Status | Meaning |
|--------|---------|
| **OPEN** | 风险已识别，缓解工作尚未开始 |
| **MITIGATED** | 已采取缓解措施，风险可控 |
| **BLOCKED** | 缺少外部依赖，无法推进 |
| **UNKNOWN** | 待进一步确认或评估 |
| **DEFERRED** | 当前免费内测阶段不需要，延后处理 |

---

## Impact / Likelihood Matrix

|  | Low Likelihood | Medium Likelihood | High Likelihood |
|--|----------------|-------------------|-----------------|
| **High Impact** | R11 | R04, R05, R12 | R01, R02 |
| **Medium Impact** | R08 | R06, R09 | R03, R07 |
| **Low Impact** | - | R10 | - |

---

## Related Documents

- 上线依赖追踪: `docs/release/launch-dependencies.md`
- 上线准备度评估: `docs/release/launch-readiness.md`
- QA 测试计划: `docs/release/qa-test-plan.md`
- 生产部署 Runbook: `docs/PROD_DEPLOY.md`
