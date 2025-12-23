# Launch Communications Plan

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Purpose & Audience

本文档定义 Clarity 产品上线前后的沟通策略、渠道、时间线和消息模板。确保所有利益相关者在正确的时间收到正确的信息。

### Audiences

| Audience | Description | Priority |
|----------|-------------|----------|
| **Internal Team** | 技术团队、产品团队、管理层 | High |
| **Investors** | 投资人、董事会成员 | High |
| **Partners** | 合作伙伴、供应商（Stripe/RevenueCat/LLM Provider） | Medium |
| **Early Users** | Beta 测试用户、内测用户 | Medium |
| **Public** | 潜在用户、媒体、公众 | Low (Launch Day) |

---

## Channels

### Internal Channels（内部渠道）

| Channel | Purpose | Audience | Frequency |
|---------|---------|----------|-----------|
| **Slack #clarity-launch** | 实时状态更新、问题讨论 | 全技术团队 | 实时 |
| **Slack #clarity-announce** | 重要里程碑通知 | 全公司 | 按需 |
| **Email (Team)** | 正式通知、总结报告 | 全团队 | 每日/里程碑 |
| **Video Call** | Go/No-Go 会议、复盘会议 | 核心团队 | 按计划 |
| **Phone/SMS** | 紧急情况升级 | On-call 人员 | 仅紧急 |

### External Channels（外部渠道）

| Channel | Purpose | Audience | Owner |
|---------|---------|----------|-------|
| **App 内公告** | 服务状态、功能更新 | 现有用户 | Product |
| **Email Newsletter** | 发布公告、重大更新 | 订阅用户 | Marketing |
| **Status Page** | 服务状态实时展示 | 所有用户 | DevOps |
| **Social Media** | 发布公告、用户互动 | 公众 | Marketing |
| **Press Release** | 媒体报道 | 媒体 | Marketing |
| **Investor Update** | 进度报告 | 投资人 | CEO/Product |

---

## Timeline

### Pre-Launch（上线前）

| Time | Activity | Channel | Owner | Audience |
|------|----------|---------|-------|----------|
| **T-14d** | 发布时间线共享 | Slack + Email | Product Lead | 全团队 |
| **T-7d** | Go/No-Go 会议邀请 | Calendar | Launch Commander | 核心团队 |
| **T-7d** | 投资人预通知 | Email | CEO | 投资人 |
| **T-3d** | QA 状态通报 | Slack | QA Lead | 技术团队 |
| **T-2d** | 代码冻结通知 | Slack + Email | Backend Lead | 开发团队 |
| **T-1d** | Go/No-Go 决策公告 | Slack + Email | Launch Commander | 全团队 |
| **T-1d** | 发布公告草稿审批 | Email | Marketing | Comms Lead |
| **T-1d** | On-call 值班确认 | Slack | DevOps Lead | 技术团队 |

### Launch Day（上线当天 T-0）

| Time | Activity | Channel | Owner | Audience |
|------|----------|---------|-------|----------|
| **T-0 开始** | 团队集合确认 | Slack + Call | Launch Commander | 核心团队 |
| **部署中** | 实时状态更新 | Slack #clarity-launch | DevOps | 技术团队 |
| **冒烟测试后** | 内部确认"GO" | Slack | QA Lead | 核心团队 |
| **流量开启后** | 外部发布公告 | App/Email/Social | Marketing | 用户/公众 |
| **上线成功** | 全员庆祝通知 | Slack #clarity-announce | Launch Commander | 全公司 |
| **上线成功** | 投资人正式通知 | Email | CEO | 投资人 |

### Post-Launch（上线后）

| Time | Activity | Channel | Owner | Audience |
|------|----------|---------|-------|----------|
| **T+1d** | 24 小时状态总结 | Slack + Email | Launch Commander | 核心团队 |
| **T+3d** | 用户反馈汇总 | Slack | Support Lead | 产品团队 |
| **T+7d** | 上线复盘会议 | Video Call | Launch Commander | 核心团队 |
| **T+7d** | 复盘报告发布 | Email | Launch Commander | 全团队 |
| **T+14d** | 投资人月度更新 | Email | CEO | 投资人 |

---

## Message Templates

### Template 1: Internal Launch Notification（内部上线通知）

```
📢 [Clarity] 上线通知

各位同事，

Clarity v1.0 将于 [日期] [时间] 正式上线。

📋 关键信息：
- 部署窗口：[开始时间] - [预计结束时间]
- Launch Commander：[姓名]
- 沟通渠道：Slack #clarity-launch

🎯 今日计划：
1. [时间] - 数据库迁移
2. [时间] - 后端部署
3. [时间] - 冒烟测试
4. [时间] - 开放流量
5. [时间] - 发布公告

⚠️ 注意事项：
- 部署期间请保持在线
- 发现问题立即在 #clarity-launch 报告
- 非紧急事项请延后处理

让我们一起把 Clarity 带给用户！💪

[Launch Commander 姓名]
```

### Template 2: External Launch Announcement（外部发布公告）

```
🎉 Clarity 正式上线！

我们很高兴地宣布，Clarity 现已正式上线。

Clarity 是一款 AI 驱动的心理支持助手，帮助你：
✨ 理清思绪
✨ 探索情绪
✨ 找到前进的方向

🚀 立即体验：
- iOS: [App Store 链接]
- Android: [Play Store 链接]

我们期待听到你的反馈！

—— Clarity 团队
```

### Template 3: Status Update（状态更新）

```
📋 [Clarity] 状态更新 - [时间]

当前状态：🟢 正常 / 🟡 部分受影响 / 🔴 服务中断

📊 进展：
- [已完成的步骤]
- [当前正在进行的步骤]

⏱️ 下一步：
- [即将进行的步骤]
- 预计时间：[ETA]

📞 如有问题：
- Slack: #clarity-launch
- On-call: [姓名]
```

### Template 4: Incident Notification（问题通报）

```
🚨 [P0/P1/P2] 问题通报 - [简短描述]

发现时间：[时间]
影响范围：[受影响的功能/用户]
当前状态：调查中 / 处理中 / 已解决

📋 已知信息：
- [问题描述]
- [初步原因]

🔧 处理措施：
- [正在采取的措施]
- [预计恢复时间]

📞 联系人：
- Incident Commander: [姓名]
- 沟通渠道: [Slack Thread 链接]

下次更新：[时间]
```

### Template 5: Investor Update（投资人通报）

```
主题：Clarity 上线更新

尊敬的投资人，

我们很高兴地通知您，Clarity v1.0 已于 [日期] 正式上线。

📊 上线概况：
- 部署状态：成功 ✅
- 服务可用性：99.9%
- 首日活跃用户：[数字]

🎯 关键里程碑：
- [里程碑 1]
- [里程碑 2]
- [里程碑 3]

📈 下一阶段计划：
- [计划 1]
- [计划 2]

如有任何问题，欢迎随时联系。

此致，
[CEO 姓名]
Clarity 团队
```

---

## Approvals

### Approval Matrix

| Content Type | Draft By | Review By | Approve By | Final Sign-off |
|--------------|----------|-----------|------------|----------------|
| **内部技术通知** | Any Engineer | Tech Lead | - | Tech Lead |
| **内部全员通知** | Product | Product Lead | - | Product Lead |
| **外部用户公告** | Marketing | Product Lead | CEO | CEO |
| **投资人通报** | Product | CEO | - | CEO |
| **媒体新闻稿** | Marketing | Product + Legal | CEO | CEO |
| **事故通报（外部）** | Incident Commander | Product Lead | CEO | CEO |

### Approval SLA

| Content Type | Turnaround Time |
|--------------|-----------------|
| 内部技术通知 | 即时 |
| 内部全员通知 | 2 小时 |
| 外部用户公告 | 4 小时（提前准备） |
| 投资人通报 | 24 小时 |
| 媒体新闻稿 | 48 小时 |
| 事故通报（外部） | 30 分钟（紧急流程） |

---

## Escalation Matrix

### When to Escalate（何时升级）

| Situation | Escalate To | Channel | SLA |
|-----------|-------------|---------|-----|
| 外部公告需要发布 | Marketing Lead | Slack/Email | 2 小时 |
| 外部公告内容有争议 | Product Lead + CEO | Slack/Call | 30 分钟 |
| 投资人咨询上线状态 | CEO | Email/Call | 1 小时 |
| 媒体询问 | Marketing Lead + CEO | Call | 30 分钟 |
| 重大事故需对外通报 | CEO + Legal | Call | 15 分钟 |
| 用户投诉激增 | Support Lead → Product Lead | Slack | 30 分钟 |

### Escalation Path

```
问题发现
    ↓
相关负责人（Slack）
    ↓ (30分钟无响应)
备用负责人（Slack + Phone）
    ↓ (15分钟无响应)
管理层（Phone）
```

### Emergency Contacts（紧急联系人）

| Role | Primary | Backup |
|------|---------|--------|
| Launch Commander | TBD | TBD |
| Backend Lead | TBD | TBD |
| Mobile Lead | TBD | TBD |
| DevOps Lead | TBD | TBD |
| Marketing Lead | TBD | TBD |
| CEO | TBD | TBD |

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| Release Documentation Hub | `docs/release/index.md` | 所有发布文档入口 |
| Launch Day Runbook | `docs/release/launch-day-runbook.md` | 上线当天执行流程 |
| Incident Response Playbook | `docs/release/incident-response.md` | 故障响应流程 |
| Ownership Matrix | `docs/release/ownership-matrix.md` | 负责人分工 |
| One-Page Update | `docs/release/one-page-update.md` | 投资人简报模板 |
