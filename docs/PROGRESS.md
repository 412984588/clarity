# 项目进度记录本

**项目名称**: Clarity
**最后更新**: 2025-12-23 10:53

---

## 最新进度（倒序记录，最新的在最上面）

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
