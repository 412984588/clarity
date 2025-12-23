# Release Metrics & KPIs

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Purpose & Scope

本文档定义 Clarity 上线后需要监控的关键指标（KPIs）和告警阈值。用于：

1. **上线验证**：确认发布成功，核心功能正常
2. **健康监控**：持续跟踪系统健康状态
3. **业务洞察**：了解用户行为和产品表现
4. **问题预警**：及时发现异常并触发响应

**范围**：
- 覆盖 AARRR 漏斗（Acquisition / Activation / Retention / Revenue / Referral）
- 覆盖系统可靠性指标（Reliability）
- 不包含具体监控工具配置（仅定义指标和阈值）

---

## KPI Categories

### Overview

| Category | Focus | Key Question |
|----------|-------|--------------|
| **Acquisition** | 用户获取 | 有多少人下载/注册？ |
| **Activation** | 用户激活 | 注册用户是否使用核心功能？ |
| **Retention** | 用户留存 | 用户是否持续回来？ |
| **Revenue** | 收入变现 | 付费转化和收入情况？ |
| **Reliability** | 系统可靠性 | 系统是否稳定可用？ |

---

## Metrics Table

### 1. Acquisition（用户获取）

| Metric | Definition | Target | Data Source | Status |
|--------|------------|--------|-------------|--------|
| **Daily Downloads** | 每日 App 下载量 | ≥ 100/day (MVP) | App Store / Play Store | [ ] Tracking |
| **Daily Signups** | 每日新注册用户数 | ≥ 50/day (MVP) | Backend Database | [ ] Tracking |
| **Signup Conversion** | 下载 → 注册转化率 | ≥ 50% | Analytics | [ ] Tracking |
| **Traffic Sources** | 流量来源分布 | N/A (观察) | Analytics | [ ] Tracking |

### 2. Activation（用户激活）

| Metric | Definition | Target | Data Source | Status |
|--------|------------|--------|-------------|--------|
| **First Solve Completion** | 新用户完成首次 Solve 流程比例 | ≥ 40% | Backend Events | [ ] Tracking |
| **Time to First Solve** | 注册到首次完成 Solve 的时间 | < 10 min | Backend Events | [ ] Tracking |
| **Onboarding Completion** | 完成引导流程的比例 | ≥ 60% | Backend Events | [ ] Tracking |
| **Session Count (Day 1)** | 首日平均会话数 | ≥ 2 | Analytics | [ ] Tracking |

### 3. Retention（用户留存）

| Metric | Definition | Target | Data Source | Status |
|--------|------------|--------|-------------|--------|
| **D1 Retention** | 次日留存率 | ≥ 30% | Analytics | [ ] Tracking |
| **D7 Retention** | 7 日留存率 | ≥ 15% | Analytics | [ ] Tracking |
| **D30 Retention** | 30 日留存率 | ≥ 8% | Analytics | [ ] Tracking |
| **Weekly Active Users (WAU)** | 周活跃用户数 | ≥ 200 (MVP) | Analytics | [ ] Tracking |
| **Monthly Active Users (MAU)** | 月活跃用户数 | ≥ 500 (MVP) | Analytics | [ ] Tracking |
| **Stickiness (DAU/MAU)** | 用户粘性 | ≥ 15% | Analytics | [ ] Tracking |

### 4. Revenue（收入变现）

| Metric | Definition | Target | Data Source | Status |
|--------|------------|--------|-------------|--------|
| **Free Trial Starts** | 开始免费试用的用户数 | 观察 | RevenueCat | [ ] Tracking |
| **Trial to Paid Conversion** | 试用 → 付费转化率 | ≥ 5% | RevenueCat | [ ] Tracking |
| **Monthly Recurring Revenue (MRR)** | 月度经常性收入 | 观察 | Stripe / RevenueCat | [ ] Tracking |
| **Average Revenue Per User (ARPU)** | 每用户平均收入 | 观察 | Stripe / RevenueCat | [ ] Tracking |
| **Churn Rate** | 月度订阅流失率 | < 10% | RevenueCat | [ ] Tracking |
| **Refund Rate** | 退款率 | < 5% | Stripe | [ ] Tracking |

### 5. Reliability（系统可靠性）

| Metric | Definition | Target | Data Source | Status |
|--------|------------|--------|-------------|--------|
| **Uptime** | 服务可用性 | ≥ 99.5% | Monitoring | [ ] Tracking |
| **API Latency (p50)** | API 响应时间中位数 | < 200ms | APM | [ ] Tracking |
| **API Latency (p95)** | API 响应时间 95 分位 | < 500ms | APM | [ ] Tracking |
| **API Latency (p99)** | API 响应时间 99 分位 | < 1000ms | APM | [ ] Tracking |
| **Error Rate** | API 错误率 (4xx + 5xx) | < 1% | Monitoring | [ ] Tracking |
| **5xx Error Rate** | 服务端错误率 | < 0.1% | Monitoring | [ ] Tracking |
| **Crash-free Users** | 无崩溃用户比例 | ≥ 99% | Mobile Analytics | [ ] Tracking |
| **Database Connection Pool** | 数据库连接池使用率 | < 80% | Monitoring | [ ] Tracking |
| **Memory Usage** | 服务内存使用率 | < 80% | Monitoring | [ ] Tracking |
| **CPU Usage** | 服务 CPU 使用率 | < 70% | Monitoring | [ ] Tracking |

---

## Monitoring Checklist

上线后必须确保以下监控项就位：

| # | Item | Category | Priority | Status |
|---|------|----------|----------|--------|
| 1 | **Health Check Monitoring** | Reliability | P0 | [ ] Done |
| 2 | **API Error Rate Alerting** | Reliability | P0 | [ ] Done |
| 3 | **API Latency Tracking** | Reliability | P0 | [ ] Done |
| 4 | **Database Connection Monitoring** | Reliability | P0 | [ ] Done |
| 5 | **User Signup Event Tracking** | Acquisition | P1 | [ ] Done |
| 6 | **Solve Flow Completion Tracking** | Activation | P1 | [ ] Done |
| 7 | **Payment Success/Failure Tracking** | Revenue | P1 | [ ] Done |
| 8 | **Mobile Crash Reporting** | Reliability | P1 | [ ] Done |
| 9 | **Third-party API Monitoring** | Reliability | P1 | [ ] Done |
| 10 | **User Retention Cohort Setup** | Retention | P2 | [ ] Done |

---

## Alert Thresholds

### Critical Alerts（P0 - 立即响应）

| Metric | Condition | Action |
|--------|-----------|--------|
| Health Check | 连续 2 次失败 | Page On-call |
| API Error Rate | > 5% 持续 5 分钟 | Page On-call |
| 5xx Error Rate | > 1% 持续 3 分钟 | Page On-call |
| Database Connections | > 90% 持续 5 分钟 | Page On-call |
| Payment Failure Rate | > 20% 持续 10 分钟 | Page On-call + Finance |

### Warning Alerts（P1 - 15 分钟内响应）

| Metric | Condition | Action |
|--------|-----------|--------|
| API Latency p95 | > 1000ms 持续 10 分钟 | Slack Alert |
| Memory Usage | > 85% 持续 15 分钟 | Slack Alert |
| CPU Usage | > 80% 持续 15 分钟 | Slack Alert |
| Error Rate | > 2% 持续 10 分钟 | Slack Alert |
| Crash-free Users | < 98% 持续 1 小时 | Slack Alert |

### Informational Alerts（P2 - 工作时间处理）

| Metric | Condition | Action |
|--------|-----------|--------|
| Daily Signups | < 10/day | Daily Report |
| D1 Retention | < 20% 连续 3 天 | Weekly Review |
| Trial Conversion | < 2% 连续 7 天 | Weekly Review |
| API Latency p95 | > 500ms 持续 1 小时 | Daily Report |

---

## Dashboard Requirements

### Operations Dashboard

| Panel | Metrics | Refresh |
|-------|---------|---------|
| Health Status | Health check results | 30s |
| Error Rate | 4xx + 5xx rates over time | 1m |
| Latency | p50/p95/p99 over time | 1m |
| Throughput | Requests per second | 1m |
| Resource Usage | CPU / Memory / Connections | 1m |

### Business Dashboard

| Panel | Metrics | Refresh |
|-------|---------|---------|
| User Funnel | Downloads → Signups → Activated | Daily |
| Retention Curves | D1/D7/D30 cohort analysis | Daily |
| Revenue | MRR, ARPU, Conversion rate | Daily |
| User Activity | DAU, WAU, MAU | Daily |

---

## Data Collection Notes

### Backend Events（需要埋点）

| Event | Trigger | Properties |
|-------|---------|------------|
| `user_signup` | 用户注册成功 | user_id, method (email/google/apple) |
| `solve_started` | 开始 Solve 流程 | user_id, session_id |
| `solve_completed` | 完成 Solve 流程 | user_id, session_id, duration |
| `subscription_started` | 开始订阅 | user_id, plan, source |
| `subscription_cancelled` | 取消订阅 | user_id, reason |
| `payment_success` | 支付成功 | user_id, amount, plan |
| `payment_failed` | 支付失败 | user_id, error_code |

### Third-party Data Sources

| Source | Provides | Integration |
|--------|----------|-------------|
| App Store Connect | iOS downloads, ratings | API / Dashboard |
| Google Play Console | Android downloads, ratings | API / Dashboard |
| Stripe | Payment data, MRR | Webhook + API |
| RevenueCat | Subscription lifecycle | Webhook + API |
| Sentry | Error tracking, crashes | SDK |

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| Release Documentation Hub | `docs/release/index.md` | 所有发布文档入口 |
| Incident Response Playbook | `docs/release/incident-response.md` | 告警触发后的响应流程 |
| Launch Day Runbook | `docs/release/launch-day-runbook.md` | 上线当天监控观察 |
| Post-Launch Monitoring | `docs/release/launch-day-runbook.md#post-launch-monitoring` | 上线后监控指标 |
