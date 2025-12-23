# Incident Response Playbook

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Purpose & Scope

本文档定义 Clarity 生产环境故障的响应流程、严重级别定义、通信规范和复盘模板。适用于所有影响用户体验或系统可用性的生产事件。

**范围**：
- 生产环境服务中断
- 性能严重劣化
- 数据异常或丢失
- 安全事件
- 第三方服务故障（Stripe/RevenueCat/LLM）

**不在范围**：
- 开发/测试环境问题
- 非紧急的功能缺陷（走正常 Bug 流程）

---

## Severity Levels

### P0 - Critical（紧急）

| 属性 | 定义 |
|------|------|
| **影响** | 核心功能完全不可用，影响所有用户 |
| **示例** | API 全挂、数据库不可访问、支付完全失败、用户无法登录 |
| **响应时间** | 15 分钟内响应 |
| **解决目标** | 1 小时内止损或回滚 |
| **升级路径** | 立即通知所有相关负责人 + 管理层 |
| **通信频率** | 每 15 分钟更新状态 |

### P1 - High（高）

| 属性 | 定义 |
|------|------|
| **影响** | 主要功能受损，影响大量用户 |
| **示例** | Solve 流程某步骤失败、SSE 流中断、部分 API 超时、情绪检测异常 |
| **响应时间** | 30 分钟内响应 |
| **解决目标** | 4 小时内修复或提供临时方案 |
| **升级路径** | 通知相关技术负责人 |
| **通信频率** | 每 30 分钟更新状态 |

### P2 - Medium（中）

| 属性 | 定义 |
|------|------|
| **影响** | 次要功能受损，影响部分用户 |
| **示例** | i18n 显示异常、非关键 API 延迟、UI 渲染问题、日志采集中断 |
| **响应时间** | 2 小时内响应 |
| **解决目标** | 24 小时内修复 |
| **升级路径** | 通知对应模块负责人 |
| **通信频率** | 每 2 小时更新状态 |

### Severity Matrix

```
              Low Impact    Medium Impact    High Impact    Critical Impact
Widespread    P1            P0               P0             P0
Many Users    P2            P1               P0             P0
Some Users    P2            P2               P1             P1
Few Users     P2            P2               P2             P1
```

---

## Detection & Triage

### Detection Sources（信号来源）

| 来源 | 示例 | 优先级 |
|------|------|--------|
| **Monitoring Alerts** | API 错误率 > 5%、响应时间 > 2s、数据库连接池 > 90% | High |
| **Health Checks** | /health 返回非 200、/health/ready 失败 | High |
| **User Reports** | 用户投诉、App Store 差评、社交媒体 | Medium |
| **Internal Discovery** | 团队成员发现、QA 测试中发现 | Medium |
| **Third-party Alerts** | Stripe/RevenueCat/Sentry 通知 | High |
| **Scheduled Checks** | 定时巡检、每日冒烟测试 | Low |

### Triage Steps（初步判断）

1. **确认问题真实性**
   - 是否可复现？
   - 影响范围多大？
   - 是否持续发生还是偶发？

2. **初步分类**
   - 前端 / 后端 / 数据库 / 第三方服务？
   - 代码问题 / 配置问题 / 基础设施问题？

3. **确定严重级别**
   - 参照上方 Severity Matrix
   - 有疑问时，偏向选择更高级别

4. **指派 Incident Commander**
   - P0/P1：由在线的最资深工程师担任
   - P2：由对应模块负责人担任

---

## Response Workflow

### Overview

```
Detection → Triage → Contain → Recover → Postmortem
    ↓         ↓         ↓          ↓          ↓
 发现问题   判断级别   止损     恢复服务    复盘总结
```

### Phase 1: Detection（发现）

| 步骤 | 动作 | 负责人 |
|------|------|--------|
| 1.1 | 收到告警或报告 | 任何人 |
| 1.2 | 初步验证问题 | 发现者 |
| 1.3 | 创建 Incident Ticket | 发现者 |
| 1.4 | 通知 On-call 或相关负责人 | 发现者 |

### Phase 2: Triage（分类）

| 步骤 | 动作 | 负责人 |
|------|------|--------|
| 2.1 | 确认影响范围和严重级别 | Incident Commander |
| 2.2 | 组建响应团队 | Incident Commander |
| 2.3 | 建立沟通渠道（Slack/电话） | Incident Commander |
| 2.4 | 首次状态通报 | Incident Commander |

### Phase 3: Contain（止损）

| 步骤 | 动作 | 负责人 |
|------|------|--------|
| 3.1 | 快速诊断根因 | 技术团队 |
| 3.2 | 评估止损方案（回滚 / 热修复 / 降级） | 技术团队 |
| 3.3 | 执行止损方案 | Backend/DevOps Lead |
| 3.4 | 验证止损效果 | QA Lead |
| 3.5 | 更新状态通报 | Incident Commander |

### Phase 4: Recover（恢复）

| 步骤 | 动作 | 负责人 |
|------|------|--------|
| 4.1 | 彻底修复问题（如止损方案是临时的） | 技术团队 |
| 4.2 | 验证修复效果 | QA Lead |
| 4.3 | 恢复正常服务 | DevOps |
| 4.4 | 持续监控 30 分钟 | 技术团队 |
| 4.5 | 宣布事件结束 | Incident Commander |

### Phase 5: Postmortem（复盘）

| 步骤 | 动作 | 负责人 |
|------|------|--------|
| 5.1 | 收集时间线和证据 | Incident Commander |
| 5.2 | 组织复盘会议（48 小时内） | Incident Commander |
| 5.3 | 撰写 Postmortem 报告 | Incident Commander |
| 5.4 | 制定改进措施并跟踪 | 相关负责人 |

---

## Communication Plan

### Internal Communication（内部通信）

| 场景 | 渠道 | 受众 | 频率 |
|------|------|------|------|
| P0 事件启动 | Slack + 电话 | 全技术团队 + 管理层 | 立即 |
| P1 事件启动 | Slack | 相关技术团队 | 立即 |
| P2 事件启动 | Slack | 对应模块负责人 | 30 分钟内 |
| 状态更新 | Slack Thread | 响应团队 | 按 Severity 定义 |
| 事件结束 | Slack + 邮件 | 全技术团队 | 结束时 |
| 复盘完成 | 邮件 | 全团队 | 48 小时内 |

### External Communication（外部通信）

| 场景 | 渠道 | 内容 | 负责人 |
|------|------|------|--------|
| 服务中断 | App 内公告 / 状态页 | "我们正在处理服务问题，预计 X 分钟内恢复" | Comms Lead |
| 中断持续 | 同上 | 每 30 分钟更新进展 | Comms Lead |
| 服务恢复 | 同上 | "服务已恢复正常，感谢耐心等待" | Comms Lead |
| 事后说明 | 邮件 / 博客 | 仅 P0 事件需要，解释原因和改进措施 | Product + Comms |

### Message Templates

**事件启动通知**：
```
🚨 [P0/P1/P2] Incident: [简短描述]
- 影响：[受影响的功能/用户]
- 状态：调查中 / 止损中 / 已恢复
- Commander：[姓名]
- 沟通渠道：[Slack Thread / 电话]
```

**状态更新**：
```
📋 Update [时间]
- 当前状态：[进展描述]
- 下一步：[计划动作]
- ETA：[预计恢复时间]
```

**事件结束通知**：
```
✅ Incident Resolved: [简短描述]
- 持续时间：[开始时间] - [结束时间]
- 根因：[简要说明]
- 复盘：[日期/时间]
```

---

## Rollback Decision Guide

### When to Rollback（何时回滚）

**立即回滚**（无需讨论）：
- API 错误率 > 10% 持续 5 分钟
- 用户完全无法登录
- 支付成功率 < 90%
- 数据库连接池耗尽
- 严重安全漏洞被利用

**考虑回滚**（需 Incident Commander 决策）：
- API 错误率 5-10% 持续 10 分钟
- 关键功能（Solve 流程）部分失败
- 性能严重劣化（p95 > 5s）
- 热修复 30 分钟内无法完成

**不回滚**：
- 非关键功能问题
- 仅影响少量用户
- 有明确的快速修复方案

### Rollback Procedure（回滚流程）

| 组件 | 回滚方式 | 命令/操作 | 负责人 |
|------|----------|-----------|--------|
| Backend | 部署上一版本 | 参照 `PROD_DEPLOY.md` | Backend Lead |
| Database | 执行回滚脚本 | `alembic downgrade -1` | Backend Lead |
| Mobile | 禁用 OTA 更新 | EAS Update rollback | Mobile Lead |
| Config | 恢复环境变量 | 从备份恢复 | DevOps |

### Rollback Verification（回滚验证）

- [ ] Health check endpoints 全绿
- [ ] 核心 API 响应正常
- [ ] 用户可正常登录
- [ ] 支付流程可用（测试卡）
- [ ] 错误率恢复正常

---

## Postmortem Template

```markdown
# Postmortem: [事件标题]

**Date**: YYYY-MM-DD
**Severity**: P0 / P1 / P2
**Duration**: HH:MM - HH:MM (X 小时 Y 分钟)
**Author**: [姓名]
**Status**: Draft / Final

---

## Summary

[2-3 句话描述事件概要]

---

## Impact

- **用户影响**：[受影响的用户数/百分比]
- **功能影响**：[哪些功能受损]
- **持续时间**：[从发现到恢复的时间]
- **业务影响**：[收入损失、用户流失等]

---

## Timeline

| 时间 | 事件 |
|------|------|
| HH:MM | 事件开始/首次告警 |
| HH:MM | 确认问题，指派 Incident Commander |
| HH:MM | 识别根因 |
| HH:MM | 开始执行止损方案 |
| HH:MM | 止损完成，服务恢复 |
| HH:MM | 宣布事件结束 |

---

## Root Cause

[详细描述根本原因]

---

## Resolution

[描述如何解决问题]

---

## What Went Well

- [做得好的地方 1]
- [做得好的地方 2]

---

## What Went Wrong

- [可以改进的地方 1]
- [可以改进的地方 2]

---

## Action Items

| # | 改进措施 | 负责人 | 截止日期 | 状态 |
|---|----------|--------|----------|------|
| 1 | [具体改进措施] | [姓名] | YYYY-MM-DD | TODO |
| 2 | [具体改进措施] | [姓名] | YYYY-MM-DD | TODO |

---

## Lessons Learned

[从这次事件中学到的关键经验]
```

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| Launch Day Runbook | `docs/release/launch-day-runbook.md` | 上线流程与回滚触发 |
| Ownership Matrix | `docs/release/ownership-matrix.md` | 负责人分工 |
| Risk Register | `docs/release/risk-register.md` | 风险登记 |
| Prod Deploy Runbook | `docs/PROD_DEPLOY.md` | 部署与回滚命令 |
| Monitoring Setup | TBD | 监控配置（待补充） |
