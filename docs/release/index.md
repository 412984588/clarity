# Release Documentation Hub

**Last Updated**: 2025-12-23
**Single Entry Point for All Release Documentation**

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [One-Page Update](one-page-update.md) | 投资人/合作方快速简报 |
| [Launch Readiness](launch-readiness.md) | Go/No-Go 评估 |
| [Local Demo Runbook](local-demo-runbook.md) | 5 分钟本机演示 |

---

## 1. Status & Planning

项目状态与规划相关文档。

| Document | Purpose | Status |
|----------|---------|--------|
| [Project Status Summary](project-status-summary.md) | 项目全局状态总结 | READY |
| [Launch Readiness](launch-readiness.md) | 上线准备度评分卡 (Go/No-Go) | READY |
| [Launch Dependencies](launch-dependencies.md) | 上线依赖追踪表 | READY |
| [One-Page Update](one-page-update.md) | 投资人/合作方一页版简报 | READY |

---

## 2. Demo & Presentation

演示与展示相关文档。

| Document | Purpose | Status |
|----------|---------|--------|
| [Demo Script](demo-script.md) | 3 分钟对外演示话术 + Checklist | READY |
| [Local Demo Runbook](local-demo-runbook.md) | 本机演示运行手册 | READY |

---

## 3. Testing & Verification

测试与验证相关文档。

| Document | Purpose | Status |
|----------|---------|--------|
| [QA Test Plan](qa-test-plan.md) | QA/UAT 测试计划 (25 条用例) | READY |
| [QA Execution Log](qa-execution-log.md) | QA/UAT 执行记录模板 | READY |
| [Local Deploy Verify](local-deploy-verify.md) | 本地部署验证结果 | READY |
| [EAS Preview Verify](eas-preview-verify.md) | EAS Preview 构建验证 | READY |
| [EAS Preview](eas-preview.md) | EAS Preview 配置指南 | READY |

---

## 4. Production Deployment

生产部署相关文档。

| Document | Purpose | Status |
|----------|---------|--------|
| [Prod Preflight](prod-preflight.md) | 生产部署预检清单 | READY |
| [PROD_DEPLOY](../PROD_DEPLOY.md) | 生产部署 Runbook | READY |
| [Release Checklist](release-checklist.md) | 发布检查清单 | READY |
| [RELEASE](../../RELEASE.md) | 版本发布说明 | READY |

---

## 5. Legal & Support

法律与支持相关文档。

| Document | Purpose | Status |
|----------|---------|--------|
| [Privacy Policy](privacy.md) | 隐私政策 | READY |
| [Support](support.md) | 用户支持信息 | READY |

---

## Document Flow

从准备到上线的推荐阅读顺序：

```
1. project-status-summary.md    ← 了解项目全貌
         ↓
2. launch-dependencies.md       ← 查看依赖项
         ↓
3. launch-readiness.md          ← Go/No-Go 评估
         ↓
4. local-demo-runbook.md        ← 本机演示
         ↓
5. prod-preflight.md            ← 预检清单
         ↓
6. PROD_DEPLOY.md               ← 执行部署
         ↓
7. release-checklist.md         ← 发布确认
```

---

## Status Legend

| Status | Meaning |
|--------|---------|
| **READY** | 文档完整，可直接使用 |
| **BLOCKED** | 需外部依赖解决后才能使用 |
| **UNKNOWN** | 待确认状态 |

---

## Related

- 项目主 README: [README.md](../../README.md)
- 进度记录: [docs/PROGRESS.md](../PROGRESS.md)
- 环境变量文档: [docs/ENV_VARIABLES.md](../ENV_VARIABLES.md)
