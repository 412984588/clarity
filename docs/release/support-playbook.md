# Support Playbook

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Purpose & Scope

本文档定义 Solacore 的用户支持流程、分级标准、响应 SLA 和常见问题处理方案。确保：

1. 用户问题得到及时响应和处理
2. 支持团队有明确的分级和升级路径
3. 常见问题有标准化回复模板
4. 复杂问题能顺利交接给工程团队

**适用范围**：
- 用户支持团队（Customer Support）
- 社区管理（Community Manager）
- 产品经理（Product Manager）
- 工程团队（Engineering - 升级后）

---

## Support Channels

### Internal Channels

| 渠道 | 用途 | 响应要求 |
|------|------|----------|
| **Slack #support** | 团队内部讨论用户问题 | 实时 |
| **JIRA Support** | 工作流追踪（Ticket 管理） | 24 小时内创建 |
| **Engineering Handoff** | 需要工程介入的问题 | 见 Handoff 流程 |
| **Weekly Support Review** | 每周复盘常见问题 | 每周五 |

### External Channels

| 渠道 | 用途 | 响应 SLA | 负责人 |
|------|------|----------|--------|
| **Email (support@solacore.app)** | 用户邮件支持 | P1: 4h, P2: 24h | Support Lead |
| **In-App Chat** | 应用内聊天支持（未来） | P1: 2h, P2: 12h | TBD |
| **App Store Reviews** | iOS/Android 商店评论 | 7 天内回复 | Community Manager |
| **Twitter/Social** | 社交媒体公开问题 | 12 小时内回复 | Community Manager |
| **GitHub Issues** | 技术用户报告 Bug | P0: 4h, P1: 24h | Engineering |
| **FAQ / Help Center** | 自助服务文档 | 每月更新 | Product Manager |

---

## Triage Levels

### 问题分级标准

| 级别 | 定义 | 示例 | 响应时间 |
|------|------|------|----------|
| **P0 Critical** | 影响所有用户的核心功能 | 无法登录、支付失败、数据丢失 | 15 分钟内 |
| **P1 High** | 影响单个用户的核心功能 | 订阅未生效、AI 无响应、闪退 | 4 小时内 |
| **P2 Normal** | 影响体验但有 workaround | UI 错位、翻译错误、性能慢 | 24 小时内 |
| **P3 Low** | 功能请求、优化建议 | 新功能建议、颜色调整 | 7 天内 |

### 分级决策树

```
用户能否使用核心功能？
├─ 否 → 影响多少用户？
│   ├─ 所有用户 → P0
│   └─ 单个用户 → P1
└─ 能用但体验不好 → P2
    └─ 功能请求 → P3
```

---

## Response SLA

### 首次响应 SLA（First Response）

| 级别 | Email | In-App | GitHub | Social |
|------|-------|--------|--------|--------|
| **P0** | 15 min | 15 min | 15 min | 1 hour |
| **P1** | 4 hours | 2 hours | 4 hours | 12 hours |
| **P2** | 24 hours | 12 hours | 24 hours | 24 hours |
| **P3** | 7 days | 7 days | 7 days | 7 days |

### 解决时间目标（Resolution Target）

| 级别 | 目标 | 最大时限 |
|------|------|----------|
| **P0** | 2 hours | 4 hours |
| **P1** | 24 hours | 72 hours |
| **P2** | 7 days | 14 days |
| **P3** | 30 days | - |

**注**：超过最大时限后，必须向用户提供明确的解决时间表或替代方案

---

## Escalation Path

### 何时升级

| 情况 | 升级到 | 时限 |
|------|--------|------|
| P0 问题持续超过 30 分钟 | Engineering Lead | 立即 |
| P1 问题超过 4 小时无进展 | Product Manager | 4 小时 |
| 用户要求退款 | Finance + Product | 立即 |
| 数据隐私问题 | Legal + Security | 立即 |
| 媒体询问 | PR + CEO | 立即 |
| 重复问题（>5 用户/天） | Product Manager | 当天 |

### 升级流程

```
1. Support 收到问题 → 分级（P0/P1/P2/P3）
2. 尝试用 Common Issues 解决（5 分钟内）
3. 无法解决 → 创建 JIRA Ticket
4. 达到升级条件 → Slack 通知 + @mention 对应负责人
5. 工程介入 → 填写 Handoff Template
6. 解决后 → 更新 FAQ + 回复用户
```

---

## Common Issues & Macros

### 1. 登录问题 - "无法登录 / 密码错误"

**诊断**：
- 检查用户是否用对了登录方式（邮箱 vs Google vs Apple）
- 检查账号状态（是否被封禁）

**解决方案**：
```
Hi [Name],

感谢联系 Solacore！

如果您忘记了密码，可以通过以下步骤重置：
1. 打开应用，点击"Forgot Password"
2. 输入您的注册邮箱
3. 查收重置链接邮件（请检查垃圾邮件文件夹）

如果您是用 Google 或 Apple 登录的，请确保使用相同的第三方账号登录。

Best,
Solacore Support
```

---

### 2. 订阅问题 - "付款成功但未解锁功能"

**诊断**：
- 检查 RevenueCat 是否同步成功
- 检查后端 `users.subscription_status`

**解决方案**：
```
Hi [Name],

感谢您订阅 Solacore Premium！

我看到您的支付已成功，但可能同步有延迟。请尝试：
1. 退出并重新登录应用
2. 点击 Settings → Restore Purchases

如果仍未解锁，请回复此邮件，我会立即为您手动激活。

Best,
Solacore Support
```

**Handoff**：如果 Restore 失败，创建 P1 Ticket 给工程

---

### 3. AI 响应问题 - "AI 没有回复 / 卡住了"

**诊断**：
- 检查后端日志（是否 LLM API 超时）
- 检查用户网络（移动端连接状态）

**解决方案**：
```
Hi [Name],

抱歉您遇到了 AI 响应问题。

请尝试以下步骤：
1. 检查网络连接（建议使用 Wi-Fi）
2. 关闭并重新打开应用
3. 如果问题持续，请尝试开启一个新的 Session

如果仍然无法解决，请告诉我具体的错误信息或截图，我会立即协助处理。

Best,
Solacore Support
```

**Handoff**：如果是后端问题（LLM API 错误），创建 P1 Ticket

---

### 4. 数据问题 - "我的对话记录不见了"

**诊断**：
- 检查用户是否切换了账号
- 检查数据库是否有记录

**解决方案**：
```
Hi [Name],

我理解您的担忧。让我帮您找回对话记录。

请确认：
1. 您是否使用了相同的登录账号？
2. 是否在不同设备上登录？

Solacore 的对话记录存储在云端，只要使用相同账号登录，就能看到历史记录。

如果确认账号无误但仍看不到，请回复此邮件，我会立即调查。

Best,
Solacore Support
```

**Handoff**：如果确认数据丢失，立即创建 P0 Ticket

---

### 5. 闪退问题 - "应用一打开就闪退"

**诊断**：
- 检查设备型号和 OS 版本
- 检查是否是特定版本的 Bug

**解决方案**：
```
Hi [Name],

抱歉应用给您带来不便。

请尝试以下步骤：
1. 完全关闭应用（从后台滑掉）
2. 重启手机
3. 重新打开 Solacore

如果仍然闪退，请告诉我：
- 您的手机型号和系统版本
- 应用版本号（Settings → About）

我会立即反馈给工程团队修复。

Best,
Solacore Support
```

**Handoff**：创建 P1 Ticket，附上设备信息和崩溃日志

---

### 6. 退款请求 - "我想退款"

**诊断**：
- 检查订阅时间（App Store/Play Store 退款政策）
- 检查退款原因

**解决方案**：
```
Hi [Name],

感谢您的反馈，很抱歉 Solacore 未能满足您的期望。

关于退款：
- iOS 用户：请通过 App Store 申请退款（Settings → Apple ID → Subscriptions）
- Android 用户：请通过 Play Store 申请退款

如果您愿意告诉我们退款原因，我们会非常感谢，这将帮助我们改进产品。

Best,
Solacore Support
```

**Handoff**：创建 JIRA Ticket 记录退款原因，供 Product 分析

---

### 7. 隐私问题 - "你们如何使用我的数据？"

**解决方案**：
```
Hi [Name],

感谢您对隐私的关注。

Solacore 的数据使用政策：
- 您的对话内容仅用于提供 AI 服务
- 我们使用 OpenAI/Anthropic API，详见其隐私政策
- 我们不会出售您的数据
- 您可以随时删除账号和所有数据

详细隐私政策：https://solacore.app/privacy

如有更多问题，请随时联系我们。

Best,
Solacore Support
```

**Handoff**：如果涉及 GDPR/CCPA 请求，转发给 Legal

---

### 8. 功能请求 - "能否添加 XX 功能？"

**解决方案**：
```
Hi [Name],

感谢您的建议！

我已将您的功能请求记录下来，并转发给产品团队。虽然我无法承诺具体时间，但您的反馈对我们非常重要。

如果您想了解产品更新，可以关注我们的：
- Twitter: @solacoreapp
- Newsletter: https://solacore.app/newsletter

Best,
Solacore Support
```

**Handoff**：创建 JIRA Feature Request Ticket

---

## Handoff to Engineering

### 何时需要工程介入

| 情况 | 分级 | 工程响应时间 |
|------|------|--------------|
| 数据丢失/损坏 | P0 | 15 分钟 |
| 支付同步失败 | P1 | 4 小时 |
| 后端 API 错误 | P1 | 4 小时 |
| 移动端闪退（普遍） | P1 | 4 小时 |
| 性能问题（普遍） | P2 | 24 小时 |
| UI Bug（单个用户） | P2 | 24 小时 |

### Handoff Template

在 JIRA Ticket 中填写以下信息：

```markdown
## User Report

- **User Email**: user@example.com
- **User ID**: 12345
- **Device**: iPhone 14 Pro, iOS 17.2
- **App Version**: 1.0.0 (Build 42)
- **Subscription**: Premium / Free

## Issue Description

[用户的原始描述]

## Reproduction Steps

1. 用户打开应用
2. 点击"开始新会话"
3. AI 无响应，显示"网络错误"

## Support Actions Taken

- ✅ 已确认用户网络正常
- ✅ 已尝试 Restore Purchases（无效）
- ✅ 已检查后端日志（发现 LLM API 超时）

## Expected Behavior

AI 应在 5 秒内开始响应

## Actual Behavior

30 秒后显示"网络错误"

## Logs / Screenshots

[附上相关日志或截图]

## Urgency

P1 - 用户无法使用核心功能
```

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------| | Incident Response | `docs/release/incident-response.md` | P0 故障响应流程 |
| QA Execution Log | `docs/release/qa-execution-log.md` | 测试问题追踪 |
| Launch Communications | `docs/release/launch-communications.md` | 对外沟通模板 |
| Privacy Compliance | `docs/release/privacy-compliance-checklist.md` | 数据隐私处理 |
| Release Documentation Hub | `docs/release/index.md` | 所有发布文档入口 |
