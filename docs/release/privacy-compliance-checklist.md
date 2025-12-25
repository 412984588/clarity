# Data Privacy & Compliance Checklist

**Version**: 1.0
**Last Updated**: 2025-12-23

---

## Purpose & Scope

本文档定义 Clarity 在数据隐私和合规方面的要求、检查项和当前状态。确保：

1. 用户数据的收集、处理、存储符合隐私法规
2. 第三方数据处理商已正确评估和披露
3. 用户权利（访问、删除、导出）得到保障
4. 上线前所有合规要求已满足或有明确计划

**适用法规**（按市场覆盖）：
- **GDPR** - 欧盟通用数据保护条例
- **CCPA/CPRA** - 加州消费者隐私法
- **PIPL** - 中国个人信息保护法
- **Apple App Store Guidelines** - 隐私相关要求
- **Google Play Policy** - 数据安全相关要求

---

## Data Inventory

### Personal Data Collected

| Data Type | Purpose | Retention | Required/Optional | Legal Basis |
|-----------|---------|-----------|-------------------|-------------|
| **Email** | 账号注册、通知 | 账号存续期 | Required | Contract |
| **Password (Hashed)** | 认证 | 账号存续期 | Required | Contract |
| **Display Name** | 个性化显示 | 账号存续期 | Optional | Consent |
| **Device ID** | 设备绑定、安全 | 账号存续期 | Required | Legitimate Interest |
| **Chat Messages** | 核心功能（Solve 流程） | 账号存续期 | Required | Contract |
| **Emotion Tags** | 情绪检测功能 | 账号存续期 | Required | Contract |
| **Session Metadata** | 会话管理 | 30 天 | Required | Contract |
| **Usage Metrics** | 产品改进 | 匿名化后永久 | Optional | Legitimate Interest |
| **Payment Info** | 订阅管理 | 由 Stripe 管理 | Required (付费用户) | Contract |
| **IP Address** | 安全、欺诈防护 | 90 天 | Required | Legitimate Interest |
| **Crash Logs** | 错误排查 | 90 天 | Required | Legitimate Interest |

### Sensitive Data

| Data Type | Collected | Justification | Special Handling |
|-----------|-----------|---------------|------------------|
| Health Data | 间接（情绪相关） | 核心功能需要 | 加密存储，不共享原始内容 |
| Biometric | No | - | - |
| Location | No | - | - |
| Financial | 间接（通过 Stripe） | 支付处理 | 不存储卡号，由 Stripe 托管 |
| Children's Data | No | 不面向 13 岁以下 | 年龄门槛检查 |

---

## Consent & Disclosure

### Consent Requirements

| Consent Type | When Obtained | Method | Status |
|--------------|---------------|--------|--------|
| **Terms of Service** | 注册时 | Checkbox + Link | [ ] Implemented |
| **Privacy Policy** | 注册时 | Checkbox + Link | [ ] Implemented |
| **Marketing Emails** | 可选 | Opt-in Checkbox | [ ] Implemented |
| **Analytics/Tracking** | 首次启动 | Consent Banner | [ ] Deferred (Beta: mobile app only, no web tracking) |
| **Push Notifications** | 使用时 | System Prompt | [ ] Implemented |

### Disclosure Requirements

| Disclosure | Location | Status |
|------------|----------|--------|
| 数据收集类型和目的 | Privacy Policy | [ ] Complete |
| 第三方数据共享 | Privacy Policy | [ ] Complete |
| 数据保留期限 | Privacy Policy | [ ] Complete |
| 用户权利说明 | Privacy Policy | [ ] Complete |
| Cookie/Tracking 说明 | Privacy Policy | [ ] N/A (Beta: mobile app only, no cookies) |
| App Store 隐私标签 | App Store Connect | [ ] Pending Apple Developer Account |
| Play Store 数据安全 | Play Console | [ ] Ready to submit with APK |

---

## Data Security

### Data in Transit

| Measure | Status | Notes |
|---------|--------|-------|
| HTTPS/TLS 1.2+ 强制 | [ ] Implemented | 所有 API 通信 |
| Certificate Pinning | [ ] Deferred (Post-Launch security enhancement) | 移动端可选增强 |
| Secure WebSocket (WSS) | [ ] Implemented | SSE 流使用 HTTPS |

### Data at Rest

| Measure | Status | Notes |
|---------|--------|-------|
| 数据库加密 | [ ] Depends on Provider | PostgreSQL 提供商配置 |
| 密码 Bcrypt 哈希 | [ ] Implemented | 不可逆 |
| 敏感字段加密 | [ ] Deferred (Chat content encrypted in transit, at-rest encryption via DB provider) | Chat 内容可选 |
| 备份加密 | [ ] Depends on Provider | 数据库提供商配置 |

### Access Control

| Measure | Status | Notes |
|---------|--------|-------|
| JWT Token 认证 | [ ] Implemented | 有效期控制 |
| Role-based Access | [ ] N/A | 单一用户角色 |
| Admin Access Logging | [ ] Planned (Production: via hosting provider logs) | 生产环境需要 |
| API Rate Limiting | [ ] Implemented | 防滥用 |
| Device Binding | [ ] Implemented | 防账号共享 |

---

## Third-party Processors

### Data Sub-processors

| Provider | Data Shared | Purpose | DPA Status | Privacy Policy |
|----------|-------------|---------|------------|----------------|
| **OpenAI** | Chat Messages | AI 对话生成 | [ ] Review | [Link](https://openai.com/privacy) |
| **Anthropic** | Chat Messages | AI 对话生成（可选） | [ ] Review | [Link](https://anthropic.com/privacy) |
| **Stripe** | Email, Payment Info | 支付处理 | [ ] Standard | [Link](https://stripe.com/privacy) |
| **RevenueCat** | User ID, Purchase Data | 订阅管理 | [ ] Review | [Link](https://revenuecat.com/privacy) |
| **Sentry** | Error Logs, Device Info | 错误监控 | [ ] Review | [Link](https://sentry.io/privacy) |
| **Database Provider** | All User Data | 数据存储 | [ ] Pending (Neon/Supabase selection) | [Neon](https://neon.tech/privacy) / [Supabase](https://supabase.com/privacy) |
| **Hosting Provider** | All Traffic | 服务托管 | [ ] Pending (Railway/Vercel selection) | [Railway](https://railway.app/legal/privacy) / [Vercel](https://vercel.com/legal/privacy-policy) |
| **Apple** | App Analytics | 应用分发 | N/A (Platform) | [Link](https://apple.com/privacy) |
| **Google** | App Analytics | 应用分发 | N/A (Platform) | [Link](https://policies.google.com/privacy) |

### AI Provider Considerations

| Consideration | OpenAI | Anthropic | Status |
|---------------|--------|-----------|--------|
| 数据用于模型训练？ | Opt-out 可用 | 默认不用 | [ ] Verify |
| 数据保留期限 | 30 天（API） | 30 天（API） | [ ] Verify |
| 数据处理地区 | US | US | [ ] Disclose |
| SOC 2 认证 | Yes | Yes | [ ] Document |

---

## User Rights

### Supported Rights

| Right | Description | Implementation | Status |
|-------|-------------|----------------|--------|
| **Access** | 用户可查看其数据 | 账户设置页面 | [ ] Planned (POST /users/me/export) |
| **Rectification** | 用户可更正其数据 | 账户设置页面 | [ ] Partial (Display name editable) |
| **Erasure** | 用户可删除账号和数据 | 删除账号功能 | [ ] Planned (DELETE /users/me) |
| **Data Portability** | 用户可导出其数据 | 数据导出功能 | [ ] Planned (JSON export via settings) |
| **Withdraw Consent** | 用户可撤回同意 | 设置中关闭 | [ ] Planned (Settings toggle) |
| **Opt-out of Sale** | CCPA 要求 | N/A（不出售数据） | N/A |
| **Lodge Complaint** | 向监管机构投诉 | 隐私政策中说明 | [ ] Document |

### Request Handling

| Request Type | Response Time | Method | Status |
|--------------|---------------|--------|--------|
| 数据访问请求 | 30 天内 | Email / In-app | [ ] Best effort (no fixed SLA during Beta) |
| 数据删除请求 | 30 天内 | Email / In-app | [ ] Best effort (no fixed SLA during Beta) |
| 数据导出请求 | 30 天内 | In-app | [x] `/account/export` |

---

## Compliance Checklist

### Legal Documents

| # | Item | Status | Owner | Notes |
|---|------|--------|-------|-------|
| 1 | Privacy Policy 已发布且可访问 | [ ] | Legal | 需有效 URL |
| 2 | Terms of Service 已发布 | [ ] | Legal | 需有效 URL |
| 3 | Cookie Policy（如适用） | [ ] | Legal | Web 端需要 |
| 4 | DPA 与关键供应商已签署 | [ ] | Legal | OpenAI, Stripe, DB |

### App Store Compliance

| # | Item | Status | Owner | Notes |
|---|------|--------|-------|-------|
| 5 | App Privacy Questionnaire 已完成 (iOS) | [ ] | Mobile Lead | See `docs/release/store-privacy-answers.md` |
| 6 | Data Safety Form 已完成 (Android) | [ ] | Mobile Lead | See `docs/release/store-privacy-answers.md` |
| 7 | 删除账号功能已实现 | [x] | Backend Lead | 设置页内提供 |
| 8 | Sign in with Apple 已实现（如用第三方登录） | [ ] | Mobile Lead | Apple 要求 |

### Technical Compliance

| # | Item | Status | Owner | Notes |
|---|------|--------|-------|-------|
| 9 | 所有 API 使用 HTTPS | [ ] | Backend Lead | |
| 10 | 密码使用安全哈希存储 | [ ] | Backend Lead | Bcrypt |
| 11 | JWT Token 有合理有效期 | [ ] | Backend Lead | |
| 12 | 敏感日志已脱敏 | [ ] | Backend Lead | 不记录密码/Token |
| 13 | 错误消息不泄露敏感信息 | [ ] | Backend Lead | |
| 14 | Rate Limiting 已配置 | [ ] | Backend Lead | |

### Process Compliance

| # | Item | Status | Owner | Notes |
|---|------|--------|-------|-------|
| 15 | 数据处理记录已建立 | [ ] | Legal | GDPR Art.30 |
| 16 | 数据泄露响应流程已定义 | [ ] | Security | 72 小时通知 |
| 17 | 用户权利请求流程已定义 | [ ] | Support | 30 天响应 |

---

## Known Gaps / TBD

### High Priority (Before Launch)

| Gap | Impact | Plan | Owner | Deadline |
|-----|--------|------|-------|----------|
| App Store 隐私标签 | 提交必须 | 填写问卷 | Mobile Lead | Pending Apple Developer Account |
| Play Store 数据安全 | 提交必须 | 填写表单 | Mobile Lead | With first Play Store submission |

### Medium Priority (Post-Launch)

| Gap | Impact | Plan | Owner | Deadline |
|-----|--------|------|-------|----------|
| Cookie Consent Banner | Web 端合规 | 实现 Banner | Frontend | N/A (mobile-only for now) |
| 数据访问请求自助 | 用户体验 | In-app 实现 | Full Stack | Post-Beta (4-8 weeks) |
| 数据保留自动清理 | 合规 + 成本 | Cron Job | Backend | Post-Beta (4-8 weeks) |
| 审计日志 | 安全审计 | 实现日志系统 | Backend | Post-Beta (4-8 weeks) |

### Low Priority / Nice-to-Have

| Gap | Impact | Plan | Owner | Deadline |
|-----|--------|------|-------|----------|
| Certificate Pinning | 安全增强 | 评估必要性 | Mobile | Post-Production |
| Chat 内容端到端加密 | 隐私增强 | 评估可行性 | Backend | Post-Production |
| 本地数据处理选项 | 隐私增强 | 评估可行性 | Backend | Post-Production |

---

## Related Documents

| Document | Path | Purpose |
|----------|------|---------|
| Privacy Policy | `docs/release/privacy.md` | 用户隐私政策 |
| Support | `docs/release/support.md` | 用户支持联系方式 |
| Launch Readiness | `docs/release/launch-readiness.md` | 上线准备度评估 |
| Risk Register | `docs/release/risk-register.md` | 风险登记表 |
| Release Documentation Hub | `docs/release/index.md` | 所有发布文档入口 |
