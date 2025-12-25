# Solacore Constitution

## Core Principles

### I. Mobile-First

React Native + Expo 是首要平台，所有功能必须优先在移动端实现和测试

- iOS 和 Android 通过单一 React Native 代码库交付
- Expo 用于快速迭代和 OTA 更新
- Web 仅作为可选的 Landing Page 和 Admin Dashboard（不是核心产品）
- 任何新功能必须先考虑移动端体验，不得因"Web 更容易"而妥协

### II. Privacy-First

用户隐私是不可协商的底线，数据最小化是默认策略

- **本地存储优先**：对话内容（用户输入 + AI 响应）仅存储在用户设备本地（SQLite/SecureStore）
- **服务端最小化**：服务器只存储以下必要数据：
  - 账号信息（email, auth_provider）
  - 订阅状态（tier, Stripe IDs, period）
  - 用量统计（session_count, period）
  - 设备注册（fingerprint, platform, last_active）
  - 风控标记（abuse_flags, review_status）
- **日志禁区**：严禁将用户原文写入任何日志（应用日志、访问日志、错误追踪）
- **PII 脱敏**：发送给 AI API 前必须剥离可识别信息（姓名、邮箱、电话）

### III. Single-Server

默认架构必须支持单服务器部署，降低运维复杂度和成本

- 整个后端必须能在一台服务器上通过 Docker Compose 运行
- 不得依赖分布式组件（Redis 集群、Kafka、K8s 等）
- 内存缓存优先于外部缓存服务（TTLCache 而非 Redis）
- 数据库使用单实例 PostgreSQL
- 只有当单服务器明确无法支撑时，才允许引入水平扩展方案

### IV. Subscription-Gated

所有核心 API 必须统一经过订阅/配额/反滥用中间件链

- **强制中间件链**（按顺序）：
  1. `AuthMiddleware` - JWT 验证
  2. `DeviceMiddleware` - 设备绑定检查
  3. `SubscriptionMiddleware` - 订阅层级和配额检查
  4. `RateLimitMiddleware` - 速率限制
- 任何绕过中间件的"快捷方式"都是违规
- 中间件返回结构化错误码，客户端负责翻译
- 配额超限、设备超限、速率超限必须返回明确的升级引导

### V. i18n-Ready

所有用户可见文案必须支持国际化，硬编码字符串是违规

- **支持语言**：英语 (en)、西班牙语 (es)、简体中文 (zh)
- **前端**：所有 UI 文案使用 react-i18next，存储在 `i18n/*.json`
- **后端**：返回错误码而非错误文案，客户端负责翻译
- **AI 响应**：检测用户输入语言，AI 以相同语言回复
- **格式化**：日期、货币、数字使用 Intl API 根据 locale 格式化
- **代码审查**：任何硬编码字符串必须在 PR 中被拒绝

### VI. Safety

用户安全高于一切，危机内容必须触发安全分流

- **危机检测**：识别自伤/自杀相关关键词（多语言）
- **安全分流**：检测到危机内容时，立即展示当地心理援助热线：
  - US: 988 (Suicide & Crisis Lifeline)
  - ES: 717 003 717 (Teléfono de la Esperanza)
- **免责声明**：应用内明确声明"Solacore 不是医疗、心理或法律专业服务，不能替代专业帮助"
- **不得劝阻求助**：AI 不得试图阻止用户寻求专业帮助
- **日志脱敏**：即使是危机事件，也不得记录用户原文

### VII. Automation

AI 代理自主决策，最小化人工干预

- **默认自主**：能自行决定的实现细节（变量命名、文件结构、库选择）不得询问用户
- **仅在以下情况询问**：
  - 决策会导致大范围返工（架构级变更）
  - 涉及显著成本增加（新付费服务、大幅增加 API 调用）
  - 存在安全风险（权限、数据暴露）
  - 需求不明确到无法推断
- **里程碑纪律**：每完成一个里程碑（Epic/Story）必须：
  1. 运行相关测试
  2. 确保测试通过
  3. 提交 Git commit
- **失败处理**：测试失败时自动修复（最多 3 次），仍失败则报告并等待指示

## Technical Constraints

### Tech Stack (Locked)

| 层 | 技术 | 备注 |
|---|------|------|
| Mobile | React Native + Expo | 跨平台，OTA 更新 |
| Backend | FastAPI (Python) | 轻量，async，自动 OpenAPI |
| Database | PostgreSQL | 单实例，可选 Supabase/Neon |
| Auth | JWT + OAuth2 | Google, Apple, Email |
| Payments | Stripe | 处理 SCA，支持 US/EU |
| AI | OpenAI / Claude API | 直接调用，无中间件 |

### Security Requirements

- 所有 API 通过 HTTPS (TLS 1.3)
- 密码使用 bcrypt 哈希（cost factor 12）
- JWT access token 1 小时过期，refresh token 30 天
- 敏感配置通过环境变量，不得硬编码
- OWASP Top 10 漏洞必须在发布前修复

### Performance Standards

- API 首次响应 < 2 秒
- AI 流式响应启动 < 3 秒
- 移动端冷启动 < 3 秒
- 支持 1000 并发用户（单服务器）

## Development Workflow

### Branch Strategy

- `main` - 稳定发布分支
- `feature/N-short-name` - 功能分支（N 为递增编号）
- PR 必须通过 CI 检查才能合并

### Commit Convention

```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
Scope: auth, chat, subscription, i18n, etc.
```

### Quality Gates

- [ ] 所有测试通过
- [ ] 无 TypeScript/Python 类型错误
- [ ] 无硬编码字符串（i18n 检查）
- [ ] 无 PII 泄露到日志
- [ ] 中间件链完整（subscription-gated）

## Governance

### Amendment Process

1. 提出修改理由和影响范围
2. 评估对现有代码的影响
3. 更新 constitution.md
4. 递增版本号

### Version Policy

- **MAJOR**：核心原则变更或删除
- **MINOR**：新增原则或显著扩展
- **PATCH**：措辞澄清、格式调整

### Compliance

- 所有 PR 必须验证是否符合 Constitution
- 违反核心原则的代码不得合并
- 例外情况必须在 PR 中明确说明并获得批准

**Version**: 1.0.0 | **Ratified**: 2025-12-21 | **Last Amended**: 2025-12-21
