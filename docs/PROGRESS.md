# 项目进度记录本

**项目名称**: Clarity
**最后更新**: 2025-12-25 00:30

---

## 最新进度（倒序记录，最新的在最上面）

### [2025-12-25 00:30] - Beta 邀请消息包 + Release Notes

- [x] **新增文档 A**: `docs/release/beta-launch-message.md` (~450 lines)
  - Links Used（APK/Tester Guide/Feedback Form/Bug Template/Issue Intake/Known Issues/GitHub）
  - Message Templates（6 个模板）:
    1. Short DM (1-2 paragraphs)
    2. Email Short
    3. Email Detailed
    4. Reminder (Day 3)
    5. Reminder (Day 7)
    6. Thank You + Feedback Request
  - Do & Don't（外发注意事项）

- [x] **新增文档 B**: `docs/release/beta-release-notes-2025-12-24.md` (~350 lines)
  - Release Header（Build ID: 5d5e7b57 / APK link / Commit: f11f3f7）
  - Highlights（Free Beta Mode / GitHub Issue Templates / Beta Docs）
  - What's New（Free Beta Mode / GitHub Templates / Beta Docs Suite / Multi-language）
  - Improved（Emotion Detection / User Auth / Solve Flow）
  - Fixed（5 dev issues）
  - Known Issues（Platform-specific / Known Limitations）
  - Call for Feedback（5 high priority test areas）
  - How to Install/Update

- [x] **文档更新**: 3 份文档
  - `docs/release/beta-share-pack.md` - Important Links 新增 2 个文档
  - `docs/release/index.md` - Free Beta Testing 分区新增 2 个文档
  - `docs/release/project-status-summary.md` - Next Steps 新增 2 个文档引用

> **目的**: 提供可直接发送的 Beta 邀请消息模板 + 当前版本完整 Release Notes，方便快速邀请测试者并沟通最新进展

### [2025-12-25 00:15] - 待填信息表单（可直接填写）

- [x] **新增文档**: `docs/release/placeholders-intake-form.md` (~390 lines)
  - Purpose & How to Use（单一表单，集中填写所有占位符）
  - Critical Info Summary（15 项最关键待填项）
  - Intake Form Sections（7 个可填表格）:
    1. Company & Legal（公司信息/联系方式）
    2. Domain / Hosting / Database（域名/托管/数据库选择）
    3. Apple Developer / App Store（Apple 账号/Bundle ID/Team ID）
    4. OAuth / External Services（测试账号/API Keys）
    5. Monitoring & Support（支持时间/SLA/状态页）
    6. Beta Operations（Beta 协调员/结束日期/反馈表单）
    7. Contacts & Owners（团队角色：Ownership Matrix 8 人 + Launch Day Runbook 7 人 + Beta Checklist 5 人 + Launch Comms 4 人）
  - Where This Info Is Used（值用在哪些文档）
  - Progress Tracking（完成度追踪）
  - Next Steps（填完后如何复制到各文档）

- [x] **文档更新**: 3 份文档
  - `docs/release/placeholders-to-fill.md` - How to Use 加入新表单链接（Quick Start 提示）
  - `docs/release/index.md` - Status & Planning 分区新增 placeholders-intake-form.md
  - `docs/release/project-status-summary.md` - Next Steps 新增表单引用

> **目的**: 提供一站式数据收集表单，用户在一个文件里填完所有占位符，然后批量复制到各文档（避免跨 15+ 文件查找）

### [2025-12-25 00:00] - 占位符/TBD 待填项清单

- [x] **全量扫描占位符**: 扫描 docs/ 目录所有文档
  - 搜索关键词：TBD / TBA / TODO / FIXME / PLACEHOLDER / REPLACE / xxx / ??? / <...>
  - 扫描范围：docs/release/**、docs/**、根目录 .md 文件
  - 发现占位符：39 个可执行项 + 10 个技术配置项 + 5 个示例数据

- [x] **新增文档**: `docs/release/placeholders-to-fill.md`
  - Purpose & How to Use
  - Placeholder Inventory（39 项，按 Critical/High/Medium/Low 分级）
    * Critical (15): 团队角色、联系方式、关键时间线
    * High (5): Beta Launch 必需项
    * Medium (12): Production Launch 必需项
    * Low (4): 可选增强项
  - Technical Placeholders（10 项，仅供参考，实际值填入 .env）
  - Example Data Placeholders（5 项，保持示例数据不变）
  - By Priority & By Category 统计表
  - Filling Guidelines & Status Values
  - Review Cadence（周度/Beta 前/Production 前）
  - Related Documents

- [x] **扫描结果摘要**:
  - Total Actionable: **39 项**
  - Top 5 Files with Most Placeholders:
    1. privacy-compliance-checklist.md - 15 项（Legal & Compliance）
    2. ownership-matrix.md - 8 项（Team Roles）
    3. launch-day-runbook.md - 7 项（Team Roles + Monitoring）
    4. free-beta-launch-checklist.md - 5 项（Beta Setup）
    5. free-beta-tester-guide.md - 5 项（Contact & Timeline）

- [x] **文档更新**: 2 份文档
  - `docs/release/index.md` - Status & Planning 分区新增 placeholders-to-fill.md
  - `docs/release/project-status-summary.md` - Next Steps 新增占位符清单引用（39 项）

> **目的**: 提供上线前必填项清单，防止遗漏关键信息（团队角色/联系方式/时间线/合规项）

### [2025-12-24 23:45] - Release Docs Inventory 刷新

- [x] **新增文档到 inventory**: 5 个文档（PR #106/#107/#108 新增）
  - `beta-feedback-summary-template.md` - 反馈汇总报告模板（External/Free Beta/Template/Yes）
  - `beta-retrospective-template.md` - Beta 复盘模板（Internal/Free Beta/Template/No）
  - `beta-issue-intake.md` - Beta Issue 接收指南（External/Free Beta/Guide/Yes）
  - `domain-hosting-setup-guide.md` - 域名/托管/数据库配置指南（Internal/Production/Guide/No）
  - `apple-developer-setup-guide.md` - Apple Developer 账号配置指南（Internal/Production/Guide/No）

- [x] **更新 Summary Counts**: 50 → 55 份文档
  - Audience: Internal 42, External 13
  - Stage: Free Beta 21, Production 15, Both 19
  - Status: Checklist 14, Template 12, Process 8, Guide 13, Report 8
  - Shareable: Yes 13, No 42

- [x] **文档更新**: 3 份文档
  - `docs/release/release-docs-inventory.md` - 补齐 5 个文档 + 更新统计（v1.0 → v1.1）
  - `docs/release/index.md` - Quick Links 更新文档数量（50 → 55）
  - `docs/release/project-status-summary.md` - Release docs inventory 描述更新（50 → 55）

> **目的**: 补齐 PR #106/#107/#108 新增的 5 份文档到 inventory，确保文档清单完整性

### [2025-12-24 23:30] - Production 阻塞项解除指南

- [x] **新增文档 A**: `docs/release/domain-hosting-setup-guide.md`
  - Purpose（域名/托管/数据库配置指南，解除生产阻塞）
  - Decisions Needed（域名选择/注册商/托管商/PostgreSQL 托管商）
  - Inputs Required（注册信息/付款方式/环境变量）
  - Step-by-Step Setup（5 阶段流程）:
    * Phase 1: Domain Registration (Namecheap/Cloudflare/GoDaddy 对比)
    * Phase 2: Hosting Provider Setup (Vercel/Railway/Fly.io 对比)
    * Phase 3: PostgreSQL Database Setup (Neon/Supabase/Railway 对比)
    * Phase 4: DNS & SSL Configuration (CNAME/Cloudflare Proxy/Let's Encrypt)
    * Phase 5: Environment Targets (Dev/Staging/Production 环境设置)
  - Completion Criteria（21 项完成检查清单）
  - Risks & Common Issues（4 个风险及解决方案）
  - Time Estimates（最快 2-3 小时，保守 1-2 天）

- [x] **新增文档 B**: `docs/release/apple-developer-setup-guide.md`
  - Purpose（Apple Developer 账号配置指南，解除 iOS 阻塞）
  - Account Types Comparison（Individual vs Organization 决策矩阵）
  - Prerequisites（Individual/Organization 不同要求，含 D-U-N-S Number）
  - Enrollment Steps（5 阶段流程）:
    * Phase 1: Prepare Apple ID (双因素认证/付款方式)
    * Phase 2: Enroll in Apple Developer Program (Individual/Organization 分流)
    * Phase 3: Access App Store Connect (Team 管理/角色分配)
    * Phase 4: Certificates & Identifiers Overview (EAS Build 自动处理)
    * Phase 5: Enable Apple Sign-In (Services ID/Private Key 配置)
  - Common Blockers & Solutions（4 个常见阻塞：D-U-N-S 延迟/付款拒绝/审核/2FA）
  - Time Estimates（Individual: 50分钟，Organization: 1h + 1-3天审核 + D-U-N-S 等待）
  - Completion Criteria（22 项完成检查清单）

- [x] **文档引用更新**: 4 份文档
  - `docs/release/launch-dependencies.md` - 4 个阻塞项（Domain/Hosting/PostgreSQL/Apple Developer）添加指南链接
  - `docs/release/index.md` - Production Deployment 分区新增 2 个指南
  - `docs/release/project-status-summary.md` - Next Steps 新增 2 个指南引用
  - `docs/release/remaining-work.md` - Critical Blockers 表格添加指南链接 + 相关文档列表新增 2 个引用

> **目的**: 为解除 2 个生产关键阻塞提供完整操作指南（域名/托管/数据库 + Apple Developer 账号）

### [2025-12-24 23:00] - Beta Issue Intake + GitHub Issue 模板

- [x] **新增 GitHub Issue 模板**: `.github/ISSUE_TEMPLATE/`
  - `beta-bug-report.yml` - Bug 报告表单（标题/步骤/期望/实际/环境/严重性/频率）
  - `beta-feedback.yml` - Beta 反馈表单（满意度/喜欢/困惑/改进/推荐/继续测试）
  - `beta-feature-request.yml` - 功能请求表单（描述/用户场景/优先级/替代方案）
  - `config.yml` - Issue 配置（contact_links 指向 Tester Guide/Feedback Form/Bug Template/Issue Intake）

- [x] **新增文档**: `docs/release/beta-issue-intake.md`
  - Purpose（Beta 测试者 Issue 接收指南）
  - Where to Report（GitHub Issue Forms / Feedback Form / Direct Message / Bug Template）
  - What to Include（Bug 必填字段/Feedback 推荐字段/Feature Request 必填字段）
  - Severity Guide（P0-P3 定义 + 示例 + SLA + 建议报告方式，引用 feedback-triage.md）
  - Response Expectations（Initial Response/Status Update/Resolution Target 表格）
  - Privacy Notes（收集内容/使用方式/可见性/禁止包含内容）
  - Related Documents（分为 For Beta Testers 和 For Team (Internal) 两组）
  - Quick Reference（快速查找不同场景的操作指南）

- [x] **文档引用更新**: 3 份文档
  - `docs/release/index.md` - Free Beta Testing 分区新增 beta-issue-intake.md
  - `docs/release/project-status-summary.md` - Next Steps 新增 beta-issue-intake.md
  - `docs/release/beta-share-pack.md` - What to Share 新增 beta-issue-intake.md + GitHub Issue Forms 链接

> **目的**: 提供统一的 Beta 反馈入口（GitHub Issue Forms）+ 完整的报告指南（Severity/SLA/Privacy）

### [2025-12-24 22:00] - Free Beta 复盘与反馈汇总模板

- [x] **新增文档 A**: `docs/release/beta-feedback-summary-template.md`
  - Purpose（反馈汇总报告，用于每周聚合）
  - Data Sources（表单/Bug/支持/指标）
  - Summary Snapshot（反馈分类统计）
  - Top 5 Issues / Top 5 Requests
  - Sentiment & Satisfaction Summary（情绪与满意度）
  - Quality Signals（崩溃率/阻塞问题/修复率）
  - Action Plan (Next 7 Days)
  - Risks & Escalations
  - Related Documents

- [x] **新增文档 B**: `docs/release/beta-retrospective-template.md`
  - Purpose & Scope（Beta 结束时的全面复盘）
  - Goals vs Outcomes（目标达成情况）
  - What Went Well / What Didn't（成功与失败）
  - Key Learnings（产品/技术/运营洞察）
  - Metrics Review（引用 release-metrics.md）
  - Product Decisions (Keep / Change / Drop)
  - Engineering Decisions（技术债/架构变更/性能优化）
  - Ops & Support Review（流程有效性/资源评估）
  - User Feedback Highlights（最赞/最批评区域）
  - Production Readiness Gap（关键阻塞/优先级项）
  - Action Items & Owners
  - Related Documents

- [x] **文档引用更新**: 3 份文档
  - `docs/release/free-beta-ops-playbook.md` - Reporting Template 新增2个模板引用
  - `docs/release/index.md` - Free Beta Testing 分区新增2个文档
  - `docs/release/project-status-summary.md` - Next Steps 新增2个文档引用

> **模板用途**: Feedback Summary（每周用） / Retrospective（Beta 结束时用）

### [2025-12-24 21:30] - Release 文档盘点 + APK 链接一致性检查

- [x] **新增文档**: `docs/release/release-docs-inventory.md`
  - Purpose（文档清单与分类总览）
  - Inventory Table（50 份文档 × 6 维度：Document/Purpose/Audience/Stage/Status/Shareable）
  - Summary Counts（按 Audience/Stage/Status/Shareable 统计）
  - Notes（分类标准说明）
  - Related Documents

- [x] **APK 链接一致性检查**: 全仓扫描 `expo.dev/artifacts/eas/` 并统一更新
  - 最新链接：`cwHBq3tAhSrhLcQnewsmpy.apk` (Build ID: `5d5e7b57`)
  - 更新 4 份文档：
    * `docs/PROGRESS.md` (第279行)
    * `docs/release/free-beta-invite-templates.md` (第180行 - 占位符)
    * `docs/release/eas-preview.md` (完整更新：日期/Build ID/URLs)
    * `docs/release/qa-test-plan.md` (第37行 - 测试环境表)

- [x] **文档引用更新**: 2 份文档
  - `docs/release/index.md` - Quick Links 新增 inventory 入口
  - `docs/release/project-status-summary.md` - Next Steps 新增 inventory 引用

> **统计结果**: 50 份文档（Internal: 39 / External: 11 | Free Beta: 18 / Production: 13 / Both: 19）

### [2025-12-24 20:05] - Android Preview Build 刷新（含 Free Beta Mode）

- [x] **EAS Build**: 新 Android Preview Build 已完成
  - Build ID: `5d5e7b57-44f7-4729-b627-e40bc93dbb76`
  - Commit: `f11f3f7`（包含 PR #97 Free Beta Mode + PR #103 Support Pack）
  - APK URL: https://expo.dev/artifacts/eas/cwHBq3tAhSrhLcQnewsmpy.apk
  - Build Time: 2025-12-24 07:57 - 08:04 (7m 8s)
  - 状态: PASS

- [x] **文档更新**: 3 份文档更新 APK 链接
  - `docs/release/eas-preview-verify.md` - 更新 Build ID / APK URL / 时间
  - `docs/release/free-beta-tester-guide.md` - 更新 APK 下载链接（3 处）
  - `docs/release/free-beta-launch-checklist.md` - 更新 Assets & Access 信息

> **重要变更**: 新 Build 包含 Free Beta 模式（设备限制放宽至 10 / 隐藏付费 UI / Beta 提示卡）

### [2025-12-24 19:30] - Free Beta 支持与对外分享包

- [x] **新增文档 A**: `docs/release/beta-known-issues.md`
  - Purpose & Scope（透明化 Bug 追踪）
  - Status Legend（6 个状态：Open/Investigating/Fix in Progress/Fixed/Deferred/Won't Fix）
  - Known Issues Tables（按优先级分类：P0/P1/P2/P3）
    - 字段：ID / Area / Description / Impact / Workaround / Status / First Seen / Last Updated / Owner / Notes
  - Priority Targets（P0: 0 issues / P1: ≤2 issues / P2: ≤10 issues / P3: backlog）
  - Platform-specific Issues / Known Limitations（非 Bug 的功能限制）
  - Statistics Tracking（周趋势统计）
  - Related Documents

- [x] **新增文档 B**: `docs/release/beta-support-macros.md`
  - Purpose & Scope（预写回复模板）
  - Tone & Guidelines（Friendly / Clear / Responsive / Transparent）
  - 8 个 Response Templates（每条含 Subject + Message + Placeholders）
    1. Acknowledge Bug Report（24h SLA）
    2. Request More Info（调试信息请求）
    3. Provide Workaround（临时解决方案）
    4. Fix Shipped（修复发布通知）
    5. Close as Duplicate（重复报告关闭）
    6. Feature Request Acknowledgement（功能请求确认）
    7. Out of Scope / Deferred（超范围/延期说明）
    8. Data/Privacy Request（数据/隐私请求处理）
  - When to Use Which Template（使用场景映射表）
  - Customization Tips（个性化建议）
  - Related Documents

- [x] **新增文档 C**: `docs/release/beta-share-pack.md`
  - Purpose & Audience（对外分享指南）
  - What to Share（6 个可对外文档：Tester Guide / Feedback Form / Bug Template / Known Issues / Privacy Policy）
  - What NOT to Share（15+ 内部文档 + 理由 + 受众范围）
  - Quick Send Checklist（7 步检查：移除内部备注 / 验证链接 / 更新日期 / 个性化 / 隐私检查 / APK 测试 / 支持联系）
  - Suggested Package（新测试者资料包：Email Subject + Body + Links）
  - Suggested Message（简短版 + 详细版）
  - Update Scenarios（3 个场景：新 Build / 安装帮助 / Bug 验证）
  - FAQs for Testers（8 条可对外 FAQ）
  - Related Documents

- [x] **更新文档**: `docs/release/free-beta-start-here.md`
  - "What to Send" 段落添加 Quick Reference 链接（指向 beta-share-pack.md）
  - Feedback Channels 添加 beta-known-issues.md 链接
  - 新增 Pro Tip 提示使用 beta-share-pack.md

- [x] **更新文档**: `docs/release/free-beta-launch-checklist.md`
  - Related Documents → During Launch 新增 3 个文档
    - Beta Share Pack
    - Beta Known Issues
    - Beta Support Macros

- [x] **更新文档**: `docs/release/index.md`
  - Free Beta Testing 分区新增 3 个文档
    - Beta Share Pack（对外分享包）
    - Beta Known Issues（已知问题追踪表）
    - Beta Support Macros（支持回复模板）

- [x] **更新文档**: `docs/release/project-status-summary.md`
  - Next Steps → Without Account/Domain (Can Do Now) 新增 3 项
    - Beta share pack - What to share externally
    - Beta known issues - Track bug status
    - Beta support macros - Response templates

> **用途**：完善 Free Beta 支持体系，提供透明的 Bug 追踪、标准化支持回复、明确对外分享边界

### [2025-12-24 18:00] - Free Beta Start Here 指南 + 文档一致性修正

- [x] **新增文档**: `docs/release/free-beta-start-here.md`
  - Purpose & Audience (快速入门指南)
  - What You Can Do Now (Free Beta)（5 条可用功能）
  - What's Blocked (Production)（3 项阻塞状态）
  - 1-Hour Setup Checklist（3 阶段：Pre-Flight / Tester Onboarding / First Session Support）
  - First 7 Days Plan（每日行动 + 每周节奏）
  - Who to Invite（推荐测试者类型 5-10 人）
  - What to Send（测试者资料包 4 项）
  - How to Track Progress（日常监控 + 周报 + 指标）
  - Related Documents（4 类共 20+ 文档链接）

- [x] **文档一致性修正**: `docs/release/index.md`
  - Free Beta Testing 分区新增 `free-beta-start-here.md`（首位，突出显示）
  - Legal & Support 分区补充 `store-privacy-answers.md`（之前遗漏）

- [x] **更新文档**: `docs/release/project-status-summary.md`
  - Next Steps 首位新增 `free-beta-start-here.md`（快速入口）

> 详见 `PROGRESS.md`

### [2025-12-24 17:30] - Beta → Production 过渡规划文档

- [x] **新增文档 A**: `docs/release/beta-exit-criteria.md`
  - Purpose & Scope (何时可从 Beta 过渡到 Production)
  - Exit Criteria (5 Categories: User Validation / QA/UAT / Risk / Dependencies / Documentation)
  - Minimum Evidence Required (每类的具体量化指标)
  - Go/No-Go Gate (强制要求与 NO-GO 触发器)
  - Transition Decision Matrix (6 scenarios mapping)
  - Related Documents

- [x] **新增文档 B**: `docs/release/beta-to-production-plan.md`
  - Overview (Current: Free Beta → Target: Production with Payments Deferred)
  - Phases (Phase 0-5: Beta → Blocker Resolution → Pre-Prod Setup → Launch → Stabilization → Payment)
  - Critical Path Dependencies (Domain → Hosting → Database → Backend → Mobile → Store)
  - Workstreams (5 parallel: Infrastructure / Mobile / Payments DEFERRED / Monitoring / Compliance)
  - Timeline Assumptions (Optimistic 4 weeks / Realistic 6-8 weeks / Conservative 10-12 weeks)
  - Decision Points & Risks & Mitigations (10 risks tracked)
  - Related Documents

- [x] **新增文档 C**: `docs/release/beta-weekly-status-template.md`
  - Header (Week / Owner / Phase / Overall Status)
  - KPI Snapshot (User Engagement / Quality & Bugs / Feedback & Satisfaction)
  - Progress Summary (Completed / In Progress / Not Started)
  - Top Issues / Blockers (Critical / High / Resolved)
  - Key Decisions Needed (with Options/Pros/Cons/Recommendation)
  - Feedback Highlights / Next Week Plan / Exit Criteria Progress
  - Risk Updates / Communications
  - Complete Example (Week 1 filled sample)

- [x] **更新文档**: `docs/release/remaining-work.md`
  - 新增 "Beta → Production Transition" 小节
  - 添加 Exit Criteria 总结（5 categories with detailed bullets）
  - 添加 Transition Timeline（Phase 0-5 breakdown）
  - 添加 Critical Path diagram
  - 链接 3 个新文档

- [x] **更新文档**: `docs/release/index.md`
  - Free Beta Testing 分区新增 3 个文档（Beta Exit Criteria / Beta to Production Plan / Beta Weekly Status Template）

- [x] **更新文档**: `docs/release/project-status-summary.md`
  - Next Steps 新增 3 个 Beta → Production 过渡文档

> 详见 `PROGRESS.md`

### [2025-12-24 16:00] - Free Beta Execution Pack 文档补齐

- [x] **新增文档 A**: `docs/release/free-beta-invite-templates.md`
  - Purpose (招募/沟通模板)
  - Audience Segments (朋友/技术同学/非技术用户)
  - Templates (Invite / Welcome / Reminder Day 3/7 / Thank You / Issue Follow-up / Wrap-up)
  - Do & Don't (沟通最佳实践)
  - Best Practices (Timing/Personalization/Response SLA)

- [x] **新增文档 B**: `docs/release/beta-tester-tracker.md`
  - Purpose (测试者状态追踪)
  - Data Fields (Tester ID / Name / Contact / Device / OS / Build / Status / Feedback / Owner)
  - Tracker Table (模板表格 + 状态图例)
  - Usage Examples (招募/开始测试/报告Bug/完成/不活跃)
  - Privacy Notes (PII 处理/GDPR 合规)
  - Summary Statistics (自动计算公式)

- [x] **新增文档 C**: `docs/release/free-beta-ops-playbook.md`
  - Purpose & Scope (日常运营手册)
  - Roles & Responsibilities (与 checklist 对齐)
  - Daily Ops Checklist (10:00 AM, ~50 min)
  - Weekly Ops Checklist (Monday 10:00 AM, ~2 hours)
  - Feedback → Triage → Fix → Verify 流程图 (与 feedback-triage 对齐)
  - Quality Gates (Green / Yellow / Red criteria)
  - Communication Cadence (Daily/Weekly 内部与测试者)
  - Reporting Template (Daily/Weekly/Tester Update)
  - Incident Response (Beta context, P0 处理流程)

- [x] **新增文档 D**: `docs/release/beta-release-notes-template.md`
  - Purpose (新 APK 发布说明模板)
  - Release Header (Version / Date / Build / APK Link)
  - Highlights (1-2 句核心亮点)
  - What's New / Improved / Fixed (分类列表)
  - Known Issues (未修复 + Workaround)
  - Call for Feedback (重点测试区域)
  - How to Update (安装步骤)
  - Example (完整填写示例)

- [x] **更新文档**: `docs/release/free-beta-launch-checklist.md`
  - Related Documents → During Launch 新增 4 个文档

- [x] **更新文档**: `docs/release/index.md`
  - Free Beta Testing 分区新增 4 个文档

- [x] **更新文档**: `docs/release/project-status-summary.md`
  - Next Steps 新增 4 个 Free Beta 执行文档

> 详见 `PROGRESS.md`

### [2025-12-24 14:00] - Free Beta Launch Pack 文档补齐

- [x] **新增文档 A**: `docs/release/free-beta-launch-checklist.md`
  - Purpose & Scope (Free Beta launch guide)
  - Prerequisites (APK, backend, testers)
  - Roles & Owners (Project Lead, Dev Lead, PM, QA, Support)
  - Assets & Access (APK link, backend URL, test accounts)
  - Launch Checklist (Pre-Launch / Launch Day / Week 1)
  - Communications (引用 launch-communications.md)
  - Feedback & Triage (引用 bug-report-template / qa-execution-log)
  - Monitoring & KPIs (引用 release-metrics.md)
  - Pause / Rollback Criteria
  - Success Criteria & Related Documents

- [x] **新增文档 B**: `docs/release/feedback-triage.md`
  - Purpose (Feedback triage workflow for Free Beta)
  - Intake Channels (Email / Form / Slack / GitHub)
  - Severity Levels (P0-P3 with SLA)
  - Triage Workflow (7-step process with decision matrix)
  - Duplicate Handling
  - Verification & Closure
  - Reporting Cadence (Daily / Weekly summaries)
  - Example Issue Entries

- [x] **更新文档**: `docs/release/remaining-work.md` v2.0.0 → v2.1.0
  - 添加说明：Free Beta Mode 已实现（PR #97 已合并）

- [x] **更新文档**: `docs/release/index.md`
  - Free Beta Testing 分区新增 2 个文档

- [x] **更新文档**: `docs/release/project-status-summary.md`
  - Next Steps 新增 Free Beta launch checklist 和 feedback triage

> 详见 `PROGRESS.md`

### [2025-12-24 08:30] - Free Beta 模式代码实现

- [x] **后端配置**:
  - `clarity-api/app/config.py`: 添加 `beta_mode` 和 `payments_enabled` 配置项
  - `clarity-api/.env.example`: 添加 `BETA_MODE` 和 `PAYMENTS_ENABLED` 环境变量
  - `docs/ENV_VARIABLES.md`: 文档化新变量，添加 Free Beta Checklist

- [x] **后端逻辑**:
  - `app/services/auth_service.py`: Beta 模式放宽设备限制（3 → 10）
  - `app/routers/sessions.py`: Beta 模式移除 session 限制（10 → 无限）
  - `app/routers/subscriptions.py`: payments_enabled=false 时返回 501
  - `app/routers/webhooks.py`: payments_enabled=false 时返回 501
  - `app/routers/revenuecat_webhooks.py`: payments_enabled=false 时返回 501

- [x] **移动端配置**:
  - `services/config.ts`: 添加 `BETA_MODE` 和 `BILLING_ENABLED` 读取
  - `.env.example`: 添加 `EXPO_PUBLIC_BETA_MODE` 和 `EXPO_PUBLIC_BILLING_ENABLED`
  - `eas.json`: preview profile 添加 `EXPO_PUBLIC_BILLING_ENABLED=false`

- [x] **移动端 UI**:
  - `app/(tabs)/_layout.tsx`: 条件隐藏 paywall tab
  - `app/(tabs)/settings.tsx`: 隐藏订阅卡片，添加 Beta 模式提示卡
  - `i18n/en.json, es.json, zh.json`: 添加 `settings.betaMode` 和 `settings.betaModeDesc`

- [x] **文档更新**:
  - `docs/release/free-beta-tester-guide.md`: 更新 Known Limitations（付费 UI 已隐藏）
  - `docs/release/project-status-summary.md`: 新增 Free Beta Mode Implementation 部分

- [ ] **下一步**: 创建 PR 并测试验证

> **启用方式**:
> - 后端: `BETA_MODE=true` + `PAYMENTS_ENABLED=false`
> - 移动端: `EXPO_PUBLIC_BILLING_ENABLED=false`

### [2025-12-24 07:00] - Free Beta 测试者文档包

- [x] **Free Beta Tester Guide**: `docs/release/free-beta-tester-guide.md`
  - Purpose & Scope（免费内测 / 不含支付）
  - Supported Platforms（Android 可用；iOS BLOCKED）
  - Getting the App（引用 APK 链接：https://expo.dev/artifacts/eas/cwHBq3tAhSrhLcQnewsmpy.apk）
  - Account & Access（测试账号/自建账号/Google OAuth）
  - Test Scenarios（10 条测试场景：账号/Solve 流程/情绪检测/多语言/历史/设备/导出/错误/边界/体验）
  - Known Limitations（无支付/无 iOS/无商店提交/简易基础设施）
  - Privacy & Data（引用 privacy.md + 数据收集说明）
  - How to Send Feedback（引用反馈表单 + Bug 模板 + 直接联系）
  - Contact / Support（测试协调员 + 技术支持 + 升级流程）
  - FAQ（8 条常见问题）

- [x] **Beta Feedback Form**: `docs/release/beta-feedback-form.md`
  - Tester Information（昵称/设备/OS/版本/测试日期/时长）
  - Session Summary（满意度 1-5 + 整体评价 + 功能测试清单）
  - Most Impressive / Most Confusing Feature
  - Bugs Encountered（3 个 Bug 报告位 + 严重性 + 复现步骤 + 预期/实际 + 截图）
  - Suggestions for Improvement（功能/UX/UI/文案）
  - Additional Feedback（5 星评价条件 + 推荐意愿 + 持续测试意愿 + 联系方式）
  - Consent（反馈使用授权 + 匿名引用授权）
  - How to Submit（邮件/Web 表单/直接消息）

- [x] **Bug Report Template**: `docs/release/bug-report-template.md`
  - Bug ID / Title / Severity（Critical/High/Medium/Low）
  - Environment（Platform/Device/OS/App Version/Build ID/Network/Date&Time）
  - Steps to Reproduce（前置条件 + 详细步骤 + 复现频率）
  - Expected vs Actual Behavior（预期行为 + 实际行为 + 影响）
  - Evidence（截图/录屏/错误消息/日志/导出数据）
  - Additional Context（尝试的 Workarounds + 相关 Bugs + 环境特殊说明）
  - Reporter Information（姓名/邮箱/联系时间/测试者类型/后续可用性）
  - Internal Use Only（分配/优先级/状态/修复版本/解决备注）
  - Examples（2 个完整示例：App Crash + Visual Glitch）

- [x] **索引更新**: `docs/release/index.md`
  - 新增 "2. Free Beta Testing" 分区（3 份文档）
  - 原有分区编号顺延：Demo & Presentation → 3, Testing & Verification → 4, Production Deployment → 5, Legal & Support → 6, Operations & Support → 7

- [x] **状态汇总更新**: `docs/release/project-status-summary.md`
  - Next Steps → Without Account/Domain (Can Do Now) 新增 3 项：
    - Free beta tester guide
    - Beta feedback form
    - Bug report template

> **用途**：为朋友内测阶段提供完整指导，包括安装、测试、反馈、Bug 报告全流程

---

### [2025-12-24 06:30] - Remaining Work 深度更新（Beta vs Production）

- [x] **Remaining Work Report**: `docs/release/remaining-work.md` v1.0.0 → v2.0.0
  - **版本升级**: 完整重写，体现 Free Beta / Production 区分
  - **Phase 标识**: 新增 "Phase: Free Beta (No Payments)" 标注
  - **Executive Summary**: 强调 Free Beta GO / Production NO-GO
  - **统计增强**: Counts 新增 DEFERRED 列（10 项）
    - READY: 17 (60.7%) - 已完成且验证
    - BLOCKED: 2 (7.1%) - 关键阻塞（域名 + Apple 账号）
    - DEFERRED: 10 (35.7%) - 免费内测不需要（支付/商店提交）
    - UNKNOWN: 8 (28.6%) - 待确认项
    - TODO: 479 (主要为 Epic 3-5 增强项 + Epic 9 生产部署)
  - **Free Beta vs Production**: 新增专节，详细对比
    - Free Beta Phase (Current): ✅ READY (Android APK + 本地部署)
    - Production Phase: 🔴 BLOCKED (2 个关键阻塞 + 10 个 DEFERRED)
  - **表格增强**: 所有统计表新增两列
    - "Free Beta Impact": ✅ No Impact / ⚠️ Nice to Have / 🔴 Blocks Beta
    - "Production Impact": ✅ No Impact / ⚠️ Required Later / 🔴 Blocks Launch
  - **Epic 分析**: 按 Epic 分组，标注每个未完成项对 Beta/Prod 的影响
  - **Blockers 重组**: 清晰区分哪些阻塞 Beta / 哪些仅阻塞 Production
  - **Next Actions 分栏**:
    - "Without Account/Domain (Can Do Now) - Free Beta Ready"
    - "Requires Account or Domain (Production)"
  - **Timeline 估算**: 分别估算 Free Beta 就绪（已就绪）和 Production 就绪（2-4 周）

> **关键结论**:
> - Free Beta: ✅ 可立即进行（0 阻塞项）
> - Production: 🔴 需解决 2 个阻塞 + 10 个 DEFERRED（2-4 周）

---

### [2025-12-24 05:05] - 免费内测阶段 / 支付延期

- [x] **阶段调整**: 项目进入**免费内测（Free Beta）**阶段
  - 支付功能（Stripe/RevenueCat）延后至正式上线
  - 移动端商店提交（App Store/Play Store）延后
  - 内测通过 Android 预览版 APK + 本地/简易部署环境
- [x] **文档更新**: 统一标记支付相关项为 DEFERRED
  - `docs/release/project-status-summary.md`（新增"当前阶段"说明 + Blockers 重组）
  - `docs/release/launch-dependencies.md`（Stripe/RevenueCat/Play Store 标记 DEFERRED）
  - `docs/release/launch-readiness.md`（更新 Summary: Production NO-GO / Beta GO）
  - `docs/release/risk-register.md`（支付风险降级为 Low Impact/DEFERRED）
  - `docs/release/qa-test-plan.md`（SUB/WEBHOOK 测试标记 DEFERRED）
  - `docs/release/release-metrics.md`（Revenue 指标标记 DEFERRED）
  - `docs/release/demo-script.md`（Q3/Q8 更新：明确免费内测阶段）
  - `docs/release/store-submission-checklist.md`（增加 Beta 说明：商店提交延后）
- [x] **Status Legend**: 新增 DEFERRED 状态说明（3 个文档）
  - launch-dependencies.md
  - risk-register.md
  - launch-readiness.md（Summary 新增 DEFERRED 统计）

> **策略调整**：当前阶段专注核心功能验证，支付和商店发布推迟到内测完成后

---

### [2025-12-24 04:00] - Remaining Work 报告

- [x] **Remaining Work Report**: `docs/release/remaining-work.md`
  - Executive Summary（项目状态总结）
  - Counts（READY 17 / BLOCKED 7 / UNKNOWN 4 / TODO 479）
  - By Epic（Epic 1-9 完成度统计）
  - Blockers & Dependencies（2 个关键阻塞 + 7 个高优先级阻塞 + 7 个待决策）
  - Open TODOs（代码中 0 个 TODO/FIXME + Ops Handover 15 项待办）
  - Gaps & Unknowns（6 个基础设施未知项 + 6 个支付服务未知项 + 4 个 QA 阻塞用例）
  - Next Actions（10 项无账号可做 + 15 项需账号或域名后做）
  - Evidence Index（所有未完成项证据文档路径）

> 完整的剩余工作统计报告，汇总所有未完成任务、阻塞项、未知项和下一步行动

---

### [2025-12-24 03:57] - QA Solve/Emotion 复测（OpenRouter）

- [x] **QA Execution Log**: `docs/release/qa-execution-log.md`
  - Solve 流程 FAIL：OpenRouter 返回 done 但无 token 内容
  - Emotion PASS：done payload 正常返回情绪
  - 新增问题: QA-LLM-01 (P1)

> 需要更换模型或兼容 reasoning 字段才能恢复 Solve 文本输出

---

### [2025-12-23 16:33] - QA Solve/Emotion 复测仍被阻塞

- [x] **QA Execution Log**: `docs/release/qa-execution-log.md`
  - OpenAI 401 仍存在（LLM_PROVIDER=openai）
  - Solve/Emotion 保持 BLOCKED

> 需要更新 OpenAI Key 或切换到 Anthropic 后再复测

---

### [2025-12-23 11:05] - QA 执行日志更新（LLM 未授权）

- [x] **QA Execution Log**: `docs/release/qa-execution-log.md`
  - Solve/Emotion 标记 BLOCKED（OpenAI/Anthropic 401）
  - Blocker 清单新增 LLM provider 未授权

> 说明：本地 API 可用，但流式响应被 LLM 认证拦截

---

### [2025-12-23 10:53] - QA 执行日志补充（自动化证据）

- [x] **QA Execution Log**: `docs/release/qa-execution-log.md`
  - PASS 14 / BLOCKED 4 / NOT RUN 16
  - 覆盖 AUTH/ACC/SUB-usage/SSE/Webhook/Safety
- [ ] **待人工执行**: Solve/Emotion/i18n/错误场景

> 说明：基于 pytest 结果补齐，人工 QA 后再更新

---

### [2025-12-23 10:40] - 发布验证日志刷新

- [x] **Release Verify Log**: `docs/release/verify-2025-12-23.log`
  - Backend: 106 tests
  - mypy: 40 files
  - Mobile: ESLint + tsc 全绿
- [x] **状态同步**: 更新汇总/评分卡/一页报告
  - `docs/release/project-status-summary.md`
  - `docs/release/launch-readiness.md`
  - `docs/release/one-page-update.md`

> 由 `./scripts/verify-release.sh` 重新生成

---

### [2025-12-23 09:50] - Support/Local Deploy 文档清理

- [x] **Support 草稿**: 增加 Legal review 标注
- [x] **Local deploy 文档**: 移除过时的 APP_VERSION 注释

> 说明：更新已完成的文档备注，避免误导

---

### [2025-12-23 09:45] - Manual QA Checklist

- [x] **Manual QA Checklist**: `docs/release/manual-qa-checklist.md`
  - Auth / Solve / Emotion / Devices / Sessions / Paywall / Error / i18n
  - BLOCKED 标注规则与失败记录提示
- [x] **Index 更新**: `docs/release/index.md`
- [x] **状态汇总更新**: `docs/release/project-status-summary.md`

> 说明：用于人工 QA 执行的逐项清单，配合 `qa-execution-log.md` 记录结果

---

### [2025-12-23 08:39] - Support/Privacy 文档草稿

- [x] **Support Page**: `docs/release/support.md`
- [x] **Privacy Policy Draft**: `docs/release/privacy.md`

> 说明：为发布准备的草稿版本，需 Legal review 后再发布

---

### [2025-12-23 08:32] - QA 执行日志（部分完成）

- [x] **QA Execution Log**: `docs/release/qa-execution-log.md`
- [x] **已完成**: HEALTH-01/02/03 (本地 smoke)
- [ ] **未完成**: Auth/Solve/Emotion/Subscription/i18n/Errors

---

### [2025-12-23 08:26] - 本地 Smoke 脚本日志

- [x] **deploy_prod_smoke.sh 本地运行**: `docs/release/deploy-prod-smoke-local-2025-12-23.log`
- [x] **结果**: /health + /ready + /live + webhooks 全部 PASS

---

### [2025-12-23 08:23] - 发布验证日志

- [x] **Release Verify Log**: `docs/release/verify-2025-12-23.log`
- [x] **结果**: 103 tests + ruff + mypy + eslint + tsc 全绿

> 由 `./scripts/verify-release.sh` 生成

---

### [2025-12-23 08:11] - 账号/部署执行清单

- [x] **最短行动清单**: `docs/release/account-deploy-action-list.md`
- [x] **执行模板**: `docs/release/account-deploy-execution-template.md`
- [x] **索引更新**: `docs/release/index.md`

> 用于记录账号开通、部署验收与签字信息

---

### [2025-12-23 23:30] - Support & Ops 文档包

- [x] **Support Playbook**: `docs/release/support-playbook.md`
  - Purpose & Scope
  - Support Channels（Internal 4 + External 6）
  - Triage Levels（P0/P1/P2/P3 定义 + 决策树）
  - Response SLA（首次响应 + 解决时间目标）
  - Escalation Path（何时升级 + 升级流程）
  - Common Issues & Macros（8 条：登录/订阅/AI/数据/闪退/退款/隐私/功能请求）
  - Handoff to Engineering（Handoff Template）
  - Related Documents

- [x] **Status Page Templates**: `docs/release/status-page-templates.md`
  - Purpose
  - Template 1: Planned Maintenance
  - Template 2: Incident Start
  - Template 3: Update (Every 30–60 min)
  - Template 4: Resolved
  - Guidelines（写作原则 + 避免内容 + 更新频率）
  - Related Documents

- [x] **Ops Handover**: `docs/release/ops-handover.md`
  - Purpose
  - Ownership & On-call（占位：负责人表 + On-call 轮值）
  - Runbooks & Key Links（引用现有 8 份核心文档）
  - Deployment & Rollback Summary（快速参考 + 关键脚本）
  - Monitoring & Alerts（关键指标 + 告警设置 + 监控工具占位）
  - Open Items / TBD（待配置 5 项 + 待优化 5 项 + 待决策 5 项）
  - Related Documents

> 完整的运维与支持流程文档，涵盖用户支持、状态沟通、运维交接三大场景

---

### [2025-12-23 23:15] - 数据隐私与合规清单

- [x] **数据隐私与合规清单**: `docs/release/privacy-compliance-checklist.md`
  - Purpose & Scope（目的与范围，适用法规）
  - Data Inventory（11 类个人数据 + 5 类敏感数据）
  - Consent & Disclosure（同意要求 + 披露要求）
  - Data Security（传输加密 + 静态加密 + 访问控制）
  - Third-party Processors（9 个第三方处理商 + AI Provider 考量）
  - User Rights（7 项用户权利 + 请求处理 SLA）
  - Compliance Checklist（17 项：Legal 4 + App Store 4 + Technical 6 + Process 3）
  - Known Gaps / TBD（High 4 + Medium 4 + Low 3）
  - Related Documents

> 确保 Clarity 在数据隐私和合规方面满足 GDPR/CCPA/PIPL 及 App Store 要求

---

### [2025-12-23 23:00] - App Store / Play Store 提交清单

- [x] **应用商店提交清单**: `docs/release/store-submission-checklist.md`
  - Purpose（目的说明）
  - iOS Submission Checklist（23 项：Account/Config/Build/Review）
  - Android Submission Checklist（23 项：Account/Config/Build/Listing/Compliance）
  - Required Assets（截图尺寸、图标、文案、URLs）
  - Versioning & Release Tracks（iOS/Android 发布轨道 + Staged Rollout）
  - Review Notes / Reviewer Instructions（审核说明占位）
  - Blockers（8 项：账号、隐私政策、支付合规等）
  - Submission Timeline
  - Related Documents

> 完整的 iOS / Android 应用商店提交流程清单

---

### [2025-12-23 22:45] - 上线指标与监控清单

- [x] **上线指标与监控清单**: `docs/release/release-metrics.md`
  - Purpose & Scope（目的与范围）
  - KPI Categories（5 类：Acquisition / Activation / Retention / Revenue / Reliability）
  - Metrics Table（30+ 指标，含 Definition / Target / Data Source / Status）
  - Monitoring Checklist（10 项监控就位检查）
  - Alert Thresholds（3 级告警：Critical / Warning / Informational）
  - Dashboard Requirements（Operations + Business）
  - Data Collection Notes（埋点事件 + 第三方数据源）
  - Related Documents

> 定义上线后需要监控的关键指标和告警阈值

---

### [2025-12-23 22:30] - 发布审批清单

- [x] **发布审批清单**: `docs/release/release-approval-checklist.md`
  - Purpose（目的说明）
  - Required Approvals（11 项审批：Core 7 + Supporting 4）
  - Readiness Gates（16 项门禁：Technical 5 + QA/UAT 4 + Operational 3 + Dependency 2 + Process 2）
  - Pre-Release Verification（10 项发布前验证）
  - Approval Conditions（有条件批准 + 豁免项）
  - Sign-off Section（最终审批签字）
  - Post-Release Verification（7 项发布后验证）
  - Related Documents

> 生产发布前的最终审批清单，确保所有准备工作完成

---

### [2025-12-23 22:15] - 上线沟通计划

- [x] **上线沟通计划**: `docs/release/launch-communications.md`
  - Purpose & Audience（5 类受众）
  - Channels（内部 5 渠道 + 外部 6 渠道）
  - Timeline（Pre-launch / Launch / Post-launch 共 20+ 活动）
  - Message Templates（5 条：内部通知、外部公告、状态更新、问题通报、投资人通报）
  - Approvals（6 类内容审批矩阵 + SLA）
  - Escalation Matrix（升级条件 + 路径 + 紧急联系人）
  - Related Documents

> 定义上线前后的沟通策略、渠道和消息模板

---

### [2025-12-23 22:00] - 故障响应手册

- [x] **故障响应手册**: `docs/release/incident-response.md`
  - Purpose & Scope（范围定义）
  - Severity Levels（P0/P1/P2 定义 + Matrix）
  - Detection & Triage（信号来源 + 初步判断）
  - Response Workflow（5 阶段：Detection → Triage → Contain → Recover → Postmortem）
  - Communication Plan（内部/外部 + Message Templates）
  - Rollback Decision Guide（何时回滚 + 回滚流程）
  - Postmortem Template（最简复盘模板）
  - Related Documents

> 定义生产环境故障的响应流程、通信规范和复盘模板

---

### [2025-12-23 21:45] - 上线当天运行手册

- [x] **运行手册**: `docs/release/launch-day-runbook.md`
  - Purpose & Scope
  - Timeline（T-7d / T-2d / T-0 / T+1d / T+7d）
  - Roles & Owners（7 角色）
  - Pre-Launch Checklist（10 条）
  - Launch Steps（10 步）
  - Post-Launch Monitoring（8 指标）
  - Rollback Triggers（7 触发条件）
  - Communication Plan

> 定义上线当天及前后的执行流程和应急措施

---

### [2025-12-23 21:30] - 上线 RACI/负责人矩阵

- [x] **负责人矩阵**: `docs/release/ownership-matrix.md`
  - Roles（8 个角色/团队）
  - RACI Matrix（16 项任务）
  - 覆盖：域名、托管、数据库、迁移、OAuth、支付、LLM、监控、QA、发布决策、上线执行、回滚
  - Notes & Assumptions

> 用于明确上线各项任务的责任分工

---

### [2025-12-23 21:15] - Go/No-Go 会议纪要模板

- [x] **会议纪要模板**: `docs/release/go-no-go-minutes.md`
  - Meeting Info（Date / Attendees / Duration）
  - Agenda（5 项）
  - Readiness Review（引用 launch-readiness.md）
  - Blockers Review（引用 risk-register.md）
  - Decision（GO / NO-GO / GO WITH CONDITIONS）
  - Conditions & Owners + Action Items
  - Sign-off

> 用于发布决策会议记录和追踪

---

### [2025-12-23 21:00] - 上线风险登记表

- [x] **风险登记表**: `docs/release/risk-register.md`
  - Overview（1 段）
  - Risk Table（12 条风险）
  - 覆盖：域名、Apple/Google 账号、Stripe/RevenueCat、LLM Key、OAuth、数据库、监控、发布窗口、回滚、QA
  - Impact / Likelihood Matrix

> 用于上线决策参考和风险跟踪

---

### [2025-12-23 20:45] - QA/UAT 执行记录模板

- [x] **执行记录模板**: `docs/release/qa-execution-log.md`
  - Title / Date / Environment / Build / Tester
  - Summary（PASS/FAIL/BLOCKED 计数）
  - Test Run Table（Case ID / Area / Result / Notes）
  - Blockers & Risks
  - Issues Found（Severity / Case ID / Description / Status）
  - Sign-off（QA Lead / Dev Lead / Product Owner）
  - History（测试轮次记录）

> 配合 qa-test-plan.md 使用，一个定义用例，一个记录执行结果

---

### [2025-12-23 20:30] - Demo Script 修正

- [x] **修正演示话术**: `docs/release/demo-script.md`
  - "收尾"段落补充完整上线依赖清单
  - Q5：移除具体模型名，改为"模型可配置"
  - Q7：移除"准确度约 80%"，改为"尚未系统评测"
  - Q8：补齐账号与生产配置清单
  - Checklist 数量修正：10 步 → 13 项

> 确保演示话术与实际依赖一致，避免误导

---

### [2025-12-23 20:15] - QA/UAT Test Plan

- [x] **QA/UAT 测试计划**: `docs/release/qa-test-plan.md`
  - Scope & Objectives
  - Test Environments（Local/Preview/Production）
  - Test Data & Accounts
  - 25 条测试用例（Auth/Solve/Emotion/Health/Subscription/Error/i18n）
  - Acceptance Criteria + Exit Criteria
  - Risks & Blockers

> 覆盖核心功能验证，支付相关标记为 BLOCKED

---

### [2025-12-23 20:00] - Release Documentation Hub

- [x] **Release 文档导航页**: `docs/release/index.md`
  - 单一入口页，索引所有 release 相关文档
  - 5 个分区：Status & Planning / Demo / Local Verify / Production / Legal
  - 14 份文档导航 + Document Flow 推荐阅读顺序

> 从此只需记住一个入口：`docs/release/index.md`

---

### [2025-12-23 19:45] - One Page Status Update

- [x] **投资人/合作方一页版简报**: `docs/release/one-page-update.md`
  - 项目概况（1 段）
  - 当前里程碑（5 条 DONE）
  - 关键阻塞（4 项）
  - 下一步（5 条）
  - 请求/需要支持（3 条）
  - 附录：关键文档链接（6 份）

> 适用于快速向投资人/合作方汇报项目状态

---

### [2025-12-23 19:30] - Launch Readiness Scorecard

- [x] **上线准备度评分卡**: `docs/release/launch-readiness.md`
  - Executive Summary（当前状态：NO-GO）
  - Readiness Scorecard（28 项检查：17 READY / 7 BLOCKED / 4 UNKNOWN）
  - Go/No-Go Criteria（5 条 Go + 5 条 No-Go）
  - Evidence Index（8 份证据文档链接）
  - Next Actions（无账号可做 vs 需账号后做）

> **结论**: 2 个关键阻塞项（域名 + Apple Developer），解除后 1-2 天可上线

---

### [2025-12-23 19:15] - Launch Dependencies Tracker

- [x] **上线依赖追踪表**: `docs/release/launch-dependencies.md`
  - 16 项依赖追踪（Domain/Apple/Google/Stripe/RevenueCat/LLM/Monitoring）
  - 状态标记：READY / BLOCKED / UNKNOWN
  - 关键路径图示
  - 依赖分组（可立即行动 / 需账号付费 / 需 Production URL）

> 追踪上线所需的所有外部账号、域名、API 密钥等

---

### [2025-12-23 19:00] - Demo Script + Checklist

- [x] **对外演示话术**: `docs/release/demo-script.md`
  - Demo 目标（1 段）
  - 3 分钟版本话术（开场/技术/功能/收尾）
  - 13 项 Demo Checklist（环境/账号/移动端/内容/网络）
  - 8 条常见问题与回答（账号/域名/iOS/支付）

> 配合 `local-demo-runbook.md` 使用，一个是技术准备，一个是话术准备

---

### [2025-12-23 18:45] - Local Demo Runbook

- [x] **本机演示运行手册**: `docs/release/local-demo-runbook.md`
  - 5 分钟快速启动流程
  - 5 条演示路径 (Health/API Docs/Register/Mobile/Solve Flow)
  - 已知限制清单 (iOS/Stripe/OAuth)
  - 清理关闭流程

> 引用了 `docs/setup.md`，避免重复

---

### [2025-12-23 18:30] - Project Status Summary

- [x] **项目状态总结文档**: `docs/release/project-status-summary.md`
  - Epic 1-8 完成概览
  - Epic 9 当前进度
  - Blockers 清单 (域名 + Apple Developer 账号)
  - 本机部署预演结果: PASS
  - 下一步清单 (可立即做 vs 需账号后做)
  - 假设与未知列表

> **文档结构**:
> 1. Completed Epics
> 2. Current Progress (Epic 9)
> 3. Blockers
> 4. Local Deployment Rehearsal
> 5. Next Steps
> 6. Assumptions & Unknowns

---

### [2025-12-23 18:05] - Fix: APP_VERSION + Smoke Script

- [x] **APP_VERSION 修复**
  - `app/config.py`: 添加 `app_version: str = "1.0.0"` 字段
  - `app/main.py`: `/health` 改用 `settings.app_version`

- [x] **Smoke 脚本 macOS 兼容**
  - `scripts/deploy_prod_smoke.sh`: `head -n -1` → `sed '$d'`

- [x] **文档更新**
  - `docs/release/local-deploy-verify.md`: 已知问题 → 已修复

> **验证**: 103 测试通过 + 冒烟测试全绿

---

### [2025-12-23 17:55] - Epic 9: Local Deploy Preflight

- [x] **iOS 文档补齐**: 虽然无 Apple Developer 账号，仍完善了步骤说明
  - `docs/release/eas-preview-verify.md`: 添加 iOS 前置条件表 + 计划步骤
  - `docs/release/eas-preview.md`: 添加 iOS 构建步骤小节
  - 状态: BLOCKED (缺 Apple Developer 账号 $99/年)

- [x] **本机部署预演**: PASS
  - 前置检查: Docker/Poetry/Node 全部可用
  - 数据库启动: PostgreSQL 容器正常
  - 迁移执行: Alembic 迁移成功
  - API 启动: Uvicorn 正常监听 8000 端口
  - 冒烟测试: /health, /health/ready, /health/live 全部 PASS

- [x] **文档产出**: `docs/release/local-deploy-verify.md`
  - 前置检查表
  - 执行命令清单
  - 结果摘要
  - 已知问题 (APP_VERSION 配置不匹配)

> **已知问题**:
> - `.env.example` 中 APP_VERSION 在 Settings 中未定义，需移除后才能启动
> - `deploy_prod_smoke.sh` 在 macOS 上 `head -n -1` 不兼容
>
> **已修复**: 见 [2025-12-23 18:05] 记录

---

### [2025-12-23 09:45] - Epic 9: Production Deployment (In Progress)

- [x] **Spec/Plan/Tasks**: 完整文档三件套
  - `docs/spec/epic-9-production-deploy.md`: 部署规格
  - `docs/plan/epic-9-production-deploy-plan.md`: 7 阶段实施计划
  - `docs/tasks/epic-9-production-deploy-tasks.md`: 30+ 任务清单

- [x] **Runbook**: `docs/PROD_DEPLOY.md`
  - 8 步部署流程
  - 验收命令和预期输出
  - 回滚程序

- [x] **Smoke 脚本**: `scripts/deploy_prod_smoke.sh`
  - 测试 /health, /health/ready, /health/live
  - 测试 webhook 端点可达性

- [x] **ENV_VARIABLES.md 增强**
  - Production Provider Examples
  - Verification Commands

> **状态**: 文档/脚本完成，待实际部署执行

---

### [2025-12-23 09:15] - Epic 8: Release & Deployment

- [x] **环境变量文档**: `docs/ENV_VARIABLES.md`
- [x] **数据库迁移指南**: `docs/DATABASE_MIGRATION.md`
- [x] **迁移脚本**: `scripts/migrate.sh`
- [x] **发布指南**: `RELEASE.md`
- [x] **变更日志**: `CHANGELOG.md`
- [x] **健康检查增强**: `/health` 返回 version

> **PR**: #32 已合并

---

### [2025-12-23 03:00] - Epic 7: Launch Readiness

- [x] **环境配置**: 三环境变量文件 (dev/staging/prod)
  - `.env.development`, `.env.staging`, `.env.production`, `.env.example`
  - `EXPO_PUBLIC_API_URL` 按环境区分

- [x] **动态配置**: `app.config.ts` 替代 `app.json`
  - 从 `process.env.EXPO_PUBLIC_API_URL` 读取 API URL
  - 添加 `extra.apiUrl` 配置

- [x] **EAS Build**: 增强构建配置
  - 三个 profile (development/preview/production) 各自注入环境变量
  - 支持不同环境自动使用对应 API

- [x] **Health 端点**: 后端健康检查增强
  - `/health/ready`: Kubernetes readiness probe
  - `/health/live`: Kubernetes liveness probe

- [x] **Error Boundary**: 移动端错误捕获
  - `components/ErrorBoundary.tsx`: Class 组件实现
  - 错误日志存储到 AsyncStorage (最近 10 条)
  - 友好的错误界面 + 重试按钮

- [x] **合规文档**: 商店上架材料占位
  - `docs/release/release-checklist.md`: 上架清单
  - `docs/release/privacy.md`: 隐私政策模板
  - `docs/release/support.md`: 支持页面模板

- [x] **验收脚本**: 一键验证
  - `scripts/verify-release.sh`: 完整验收流程
  - Backend: ruff + mypy + pytest
  - Mobile: lint + tsc

- [x] **setup.md**: 添加 iOS/Android 调试说明
  - iOS: Xcode 要求、模拟器、真机调试
  - Android: Android Studio、SDK、真机调试
  - 环境变量配置表

> **新增文件**:
> - `clarity-mobile/.env.*`, `app.config.ts`
> - `clarity-mobile/components/ErrorBoundary.tsx`
> - `docs/release/release-checklist.md`, `privacy.md`, `support.md`
> - `docs/spec/epic-7-launch.md`, `plan/epic-7-launch-plan.md`, `tasks/epic-7-launch-tasks.md`
> - `scripts/verify-release.sh`

> **测试验证**:
> - Backend: ruff ✅, mypy ✅ (39 files), pytest ✅ (103 passed)
> - Mobile: lint ✅, tsc ✅

---

### [2025-12-23 01:30] - Epic 6: Emotion Detection + UI Effects

- [x] **Backend**: 情绪检测服务
  - `app/services/emotion_detector.py`: EmotionType enum (anxious/sad/calm/confused/neutral)
  - 关键词匹配 + 权重评分，支持 en/es/zh 三语言
  - SSE done 事件返回 `emotion_detected` + `confidence` (0-1)
  - 21 个测试用例全部通过

- [x] **Mobile**: 情绪渐变背景
  - `components/AnimatedGradientBackground.tsx`: 动画渐变组件
  - `hooks/useEmotionBackground.ts`: 情绪状态 + AsyncStorage 持久化
  - 300ms 平滑过渡动画 (Animated.timing)
  - 颜色映射: anxious→橙红, sad→蓝紫, calm→绿, confused→黄橙, neutral→灰蓝

- [x] **Settings**: 情绪背景开关
  - `app/(tabs)/settings.tsx`: 添加 Preferences 卡片 + Switch 组件
  - 存储 key: `@clarity/emotion_background_enabled`
  - 默认开启

- [x] **i18n**: 新增翻译 keys
  - `settings.preferences`, `settings.emotionBackground`, `settings.emotionBackgroundDesc`
  - 支持 en/es/zh 三语言

> **新增文件**:
> - `clarity-api/app/services/emotion_detector.py`
> - `clarity-api/tests/test_emotion_detector.py`
> - `clarity-mobile/components/AnimatedGradientBackground.tsx`
> - `clarity-mobile/hooks/useEmotionBackground.ts`
> - `docs/epic6-spec.md`, `docs/epic6-plan.md`, `docs/epic6-tasks.md`

> **测试验证**:
> - Backend: ruff ✅, mypy ✅ (39 files), pytest ✅ (103 passed)
> - Mobile: lint ✅, tsc ✅

---

### [2025-12-22 23:58] - Epic 5 Wave 4: QA Verification

**验收时间**: 2025-12-22 23:58 UTC+8

#### Backend 验证

```bash
cd clarity-api
poetry install --no-root  # No dependencies to install or update
poetry run ruff check .   # All checks passed!
poetry run mypy app --ignore-missing-imports  # Success: no issues found in 38 source files
poetry run pytest -v      # 82 passed in 16.92s
```

| 命令 | 结果 |
|------|------|
| `ruff check .` | ✅ All checks passed! |
| `mypy app` | ✅ Success: no issues in 38 files |
| `pytest` | ✅ 82 passed in 16.92s |

#### Database 验证

```bash
docker compose up -d db   # Container clarity-api-db-1 Running
poetry run alembic upgrade head  # Will assume transactional DDL (already up to date)
curl http://localhost:8000/health  # {"status":"healthy","version":"1.0.0","database":"connected"}
```

| 命令 | 结果 |
|------|------|
| `docker compose up -d db` | ✅ Container Running |
| `alembic upgrade head` | ✅ Already up to date |
| `curl /health` | ✅ `{"status":"healthy","version":"1.0.0","database":"connected"}` |

#### Mobile 验证

```bash
cd clarity-mobile
npm install --legacy-peer-deps  # found 0 vulnerabilities
npm run lint                    # (no output = success)
npx tsc --noEmit               # (no output = success)
```

| 命令 | 结果 |
|------|------|
| `npm install` | ✅ 0 vulnerabilities |
| `npm run lint` | ✅ No errors |
| `npx tsc --noEmit` | ✅ No errors |

#### 结论

**🎉 PASS** - Epic 5 全部验证通过，代码质量符合标准

---

### [2025-12-22 23:00] - Epic 5 Wave 3: Mobile Solve 5-Step Flow

- [x] **核心功能**: 实现完整的 5 步问题解决流程
  - Home 页面作为入口，点击 "Start New Session" 开始
  - Session 页面：步骤进度条 (Receive→Clarify→Reframe→Options→Commit)
  - SSE 实时流式响应
  - Options 步骤卡片选择 UI
  - Commit 步骤输入 first_step_action + 可选 reminder_time
  - PATCH 回写到后端

- [x] **Safety**: 危机检测 UI
  - 后端返回 `blocked: true, reason: "CRISIS"` 时显示热线资源
  - 显示 US 988 和 Spain 717 003 717

- [x] **Step History**: 本地存储
  - 使用 AsyncStorage 持久化会话历史
  - 按步骤追踪消息和时间戳

- [x] **i18n**: 30+ 新翻译 keys
  - tabs: home, settings, paywall, devices, sessions
  - home: greeting, solveTitle, solveDescription, startSession, howItWorks...
  - solve: stepReceive, stepClarify, stepReframe, stepOptions, stepCommit...

> **新增文件**:
> - `clarity-mobile/app/(tabs)/home.tsx`
> - `clarity-mobile/app/session/[id].tsx`
> - `clarity-mobile/app/session/_layout.tsx`
> - `clarity-mobile/services/solve.ts`
> - `clarity-mobile/services/stepHistory.ts`
> - `clarity-mobile/types/solve.ts`

> **PR**: #24 已合并

---

### [2025-12-22 17:00] - Epic 5 Wave 2: Mobile i18n + Safety Docs

- [x] **Mobile i18n**: expo-localization 自动检测系统语言
  - 创建 i18n 目录：en.json, es.json, zh.json
  - 110+ 翻译 keys
  - 所有 auth/tabs 页面使用 t() 函数

- [x] **Safety 文档**: 更新 docs/setup.md
  - Crisis detection 关键词 (en/es)
  - API 响应格式 `{blocked:true, reason:"CRISIS", resources:{...}}`
  - 热线号码：US 988, Spain 717 003 717

> **PR**: #22 已合并

---

### [2025-12-22 09:00] - Epic 5 Wave 1: State Machine + Analytics

- [x] **State Machine**: 5 步状态机实现
  - SolveStep enum: receive, clarify, reframe, options, commit
  - 严格的步骤转换规则（只能前进）

- [x] **Analytics**: 分析事件追踪
  - session_started, step_completed, session_completed
  - crisis_detected 事件

- [x] **Step History**: 后端步骤历史记录
  - 每步开始/完成时间
  - 消息计数

> **PR**: #20 已合并

---

## Epic 5 总进度

| Wave | 内容 | 状态 |
|------|------|------|
| Wave 1 | State Machine + Analytics | ✅ 完成 |
| Wave 2 | Mobile i18n + Safety Docs | ✅ 完成 |
| Wave 3 | Mobile Solve 5-Step Flow | ✅ 完成 |
| Wave 4 | QA Verification | ✅ PASS |

**Epic 5 完成！** 🎉

---

## 下一步

- [ ] Epic 9: 执行生产部署（按 PROD_DEPLOY.md 操作）
- [ ] Epic 10: 用户反馈 + 迭代
