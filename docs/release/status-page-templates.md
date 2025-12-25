# Status Page Templates

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Purpose

本文档提供 Solacore 状态页（Status Page）的标准消息模板，用于在计划维护或故障时向用户透明沟通。确保：

1. 用户及时了解系统状态
2. 消息格式统一、清晰、易懂
3. 避免技术术语和过度承诺
4. 维护用户信任

**使用场景**：
- 计划维护（Planned Maintenance）
- 故障开始（Incident Start）
- 故障更新（Update）
- 故障解决（Resolved）

**发布渠道**：
- 官网状态页：https://status.solacore.app（未来）
- Twitter/Social Media
- In-App Banner（未来）
- Email（仅影响付费用户时）

---

## Template 1: Planned Maintenance

### 用途
提前通知用户计划内的系统维护

### 提前时间
- **小型维护**（<30 分钟）：提前 24 小时
- **大型维护**（>30 分钟）：提前 7 天

### Template

```markdown
## 🔧 Planned Maintenance - [Date] [Time]

**Scheduled**: [YYYY-MM-DD HH:mm - HH:mm UTC]
**Duration**: Approximately [X] minutes
**Impact**: [None / Read-only / Partial / Full Outage]

### What's Happening

We will be performing scheduled maintenance to [brief reason, e.g., "upgrade our database infrastructure" / "improve performance"].

### What to Expect

- ✅ **No action required** from users
- ⏸️ [Specific features affected, e.g., "New sessions cannot be started"]
- ✅ [What will still work, e.g., "Existing conversations will remain accessible"]

### Timeline

- **Start**: [YYYY-MM-DD HH:mm UTC]
- **Expected End**: [YYYY-MM-DD HH:mm UTC]
- **Status Updates**: Every 30 minutes on [Twitter / Status Page]

We appreciate your patience and understanding.

— Solacore Team
```

### 示例

```markdown
## 🔧 Planned Maintenance - Dec 25, 2025

**Scheduled**: 2025-12-25 02:00 - 03:00 UTC
**Duration**: Approximately 60 minutes
**Impact**: Partial - New sessions unavailable

### What's Happening

We will be performing scheduled maintenance to upgrade our database infrastructure for improved performance and reliability.

### What to Expect

- ✅ **No action required** from users
- ⏸️ New AI sessions cannot be started during the maintenance window
- ✅ Existing conversations will remain accessible (read-only)
- ✅ Login and account settings will work normally

### Timeline

- **Start**: 2025-12-25 02:00 UTC (9pm ET / 6pm PT)
- **Expected End**: 2025-12-25 03:00 UTC (10pm ET / 7pm PT)
- **Status Updates**: Every 30 minutes on [@solacoreapp](https://twitter.com/solacoreapp)

We appreciate your patience and understanding.

— Solacore Team
```

---

## Template 2: Incident Start

### 用途
故障发生后立即通知用户（目标：15 分钟内）

### Template

```markdown
## 🔴 Investigating Issue - [Brief Description]

**Started**: [YYYY-MM-DD HH:mm UTC]
**Status**: Investigating
**Impact**: [Specific impact, e.g., "Users may experience slow AI responses"]

### Current Status

We are currently investigating reports of [brief issue description]. Our team is working to identify the cause.

### What We Know

- ⚠️ [Symptom 1, e.g., "Some users cannot log in"]
- ⚠️ [Symptom 2, e.g., "AI responses are delayed by 30+ seconds"]
- ✅ [What is NOT affected, e.g., "Existing sessions are not impacted"]

### Next Update

We will provide an update within [30 / 60] minutes or sooner if we have more information.

We apologize for the inconvenience.

— Solacore Team
```

### 示例

```markdown
## 🔴 Investigating Issue - Login Problems

**Started**: 2025-12-23 14:30 UTC
**Status**: Investigating
**Impact**: Some users unable to log in

### Current Status

We are currently investigating reports of login failures affecting a subset of users. Our team is working to identify the cause.

### What We Know

- ⚠️ Some users see "Authentication failed" error when logging in
- ⚠️ Issue appears to affect Google Sign-In specifically
- ✅ Email/password login is working normally
- ✅ Users already logged in are not affected

### Next Update

We will provide an update within 30 minutes or sooner if we have more information.

We apologize for the inconvenience.

— Solacore Team
```

---

## Template 3: Update (Every 30–60 min)

### 用途
故障持续时定期更新进展（即使无新进展也要更新）

### Template

```markdown
## 🟡 Update - [Brief Description]

**Updated**: [YYYY-MM-DD HH:mm UTC]
**Status**: [Investigating / Identified / Monitoring / Resolved]
**Elapsed Time**: [X] minutes since start

### Progress Update

[Brief update on what has been learned or done]

### What We've Done

- ✅ [Action 1, e.g., "Identified the root cause as a database connection issue"]
- ✅ [Action 2, e.g., "Applied a temporary fix"]
- 🔄 [Action 3, e.g., "Monitoring recovery progress"]

### Current Impact

- ⚠️ [Updated impact, e.g., "95% of users can now log in normally"]
- ⚠️ [Remaining issue, e.g., "Google Sign-In still experiencing delays"]

### Next Steps

[What the team is doing next, e.g., "We are deploying a permanent fix and expect full recovery within 30 minutes"]

### Next Update

[Time, e.g., "Within 30 minutes or when resolved"]

— Solacore Team
```

### 示例（进展中）

```markdown
## 🟡 Update - Login Problems

**Updated**: 2025-12-23 15:00 UTC
**Status**: Identified
**Elapsed Time**: 30 minutes since start

### Progress Update

We have identified the root cause: a third-party authentication service is experiencing degraded performance.

### What We've Done

- ✅ Identified the issue as Google OAuth service delays
- ✅ Implemented a retry mechanism to improve success rate
- 🔄 Working with Google to resolve the underlying issue

### Current Impact

- ⚠️ Google Sign-In success rate improved to ~80% (was 20%)
- ⚠️ Users may need to retry login 1-2 times
- ✅ Email/password and Apple Sign-In working normally

### Next Steps

We are continuing to monitor Google's service recovery and will provide a permanent fix if the issue persists beyond 1 hour.

### Next Update

Within 30 minutes or when fully resolved.

— Solacore Team
```

---

## Template 4: Resolved

### 用途
故障完全解决后的最终通知

### Template

```markdown
## ✅ Resolved - [Brief Description]

**Resolved**: [YYYY-MM-DD HH:mm UTC]
**Duration**: [X] minutes total
**Final Status**: Resolved

### Summary

The issue affecting [brief description] has been fully resolved. All systems are operating normally.

### What Happened

[Brief explanation of the root cause, in user-friendly language]

### Resolution

[What was done to fix it]

### Prevention

[What we're doing to prevent this in the future, optional]

### Impact Summary

- **Started**: [YYYY-MM-DD HH:mm UTC]
- **Resolved**: [YYYY-MM-DD HH:mm UTC]
- **Duration**: [X] minutes
- **Users Affected**: [Approximate number or percentage, if known]

We sincerely apologize for the disruption and appreciate your patience.

— Solacore Team
```

### 示例

```markdown
## ✅ Resolved - Login Problems

**Resolved**: 2025-12-23 15:45 UTC
**Duration**: 75 minutes total
**Final Status**: Resolved

### Summary

The issue affecting Google Sign-In has been fully resolved. All login methods are operating normally.

### What Happened

A third-party authentication provider (Google OAuth) experienced a temporary service degradation that caused login delays and failures.

### Resolution

- Google's service has fully recovered
- We implemented additional retry logic to handle future transient issues
- All affected users can now log in normally

### Prevention

We are adding monitoring alerts for third-party authentication failures to detect and respond to similar issues faster in the future.

### Impact Summary

- **Started**: 2025-12-23 14:30 UTC
- **Resolved**: 2025-12-23 15:45 UTC
- **Duration**: 75 minutes
- **Users Affected**: ~20% of login attempts during the incident window

We sincerely apologize for the disruption and appreciate your patience.

— Solacore Team
```

---

## Guidelines

### 写作原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **Be Transparent** | 诚实说明影响范围 | ✅ "20% of users affected" <br> ❌ "Some users" |
| **Be Specific** | 具体说明受影响的功能 | ✅ "Google Sign-In unavailable" <br> ❌ "Login issues" |
| **Be Timely** | 即使无新进展也要更新 | ✅ "No new updates, still investigating" <br> ❌ (沉默 2 小时) |
| **Be Human** | 使用友好、易懂的语言 | ✅ "We're working on it" <br> ❌ "Ops team initiated root cause analysis" |
| **Be Accountable** | 道歉并说明预防措施 | ✅ "We apologize and are adding monitoring" <br> ❌ (只说已修复) |

### 避免的内容

| ❌ 避免 | ✅ 推荐 |
|---------|---------|
| 技术术语（"database failover", "503 error"） | 用户友好描述（"database issue", "service unavailable"） |
| 过度承诺（"永不再发生"） | 现实承诺（"we're adding monitoring"） |
| 责怪第三方（"Google 的锅"） | 专业表述（"third-party service issue"） |
| 无时间承诺 | 明确下次更新时间 |
| 只说"我们在修" | 说明已做了什么、正在做什么 |

### 更新频率

| 故障级别 | 更新频率 |
|----------|----------|
| P0 (全面故障) | 每 30 分钟 |
| P1 (部分功能) | 每 60 分钟 |
| P2 (降级服务) | 每 2 小时 |

**即使无新进展，也必须按时更新，告知用户"仍在调查中"**

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------| | Incident Response | `docs/release/incident-response.md` | 故障响应流程 |
| Launch Communications | `docs/release/launch-communications.md` | 沟通渠道和审批 |
| Support Playbook | `docs/release/support-playbook.md` | 用户支持流程 |
| Release Documentation Hub | `docs/release/index.md` | 所有发布文档入口 |
