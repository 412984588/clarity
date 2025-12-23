# Epic 8: Release & Deployment - 任务清单

**版本**: 1.0
**创建日期**: 2025-12-22
**状态跟踪**: 使用 checkbox 标记完成状态

---

## Phase 1: 后端部署配置

### 1.1 环境变量对齐
- [ ] **Task 1.1.1**: 更新 .env.example
  - 添加所有生产必需变量
  - 标注 `# REQUIRED: change in production`
  - 添加详细注释说明每个变量用途
  - 文件: `clarity-api/.env.example`

- [ ] **Task 1.1.2**: 创建环境变量文档
  - 列出所有变量、是否必填、示例值
  - 文件: `docs/ENV_VARIABLES.md`

### 1.2 健康检查端点
- [ ] **Task 1.2.1**: 实现 /health 端点
  - 返回 JSON: `{ "status": "healthy", "version": "x.x.x", "database": "connected" }`
  - 检查数据库连接
  - 文件: `clarity-api/app/routers/health.py`

- [ ] **Task 1.2.2**: 添加健康检查测试
  - 文件: `clarity-api/tests/test_health.py`

### 1.3 部署脚本
- [ ] **Task 1.3.1**: 创建部署脚本
  - 文件: `scripts/deploy.sh`
  - 功能: 检查环境变量、运行迁移、启动服务

- [ ] **Task 1.3.2**: 更新 Dockerfile (如需要)
  - 确保包含 alembic 迁移步骤
  - 文件: `clarity-api/Dockerfile`

### 1.4 验证与提交
- [ ] **Task 1.4.1**: 运行 Backend CI
  - `poetry run ruff check .`
  - `poetry run mypy app --ignore-missing-imports`
  - `poetry run pytest -v`

- [ ] **Task 1.4.2**: 提交 Phase 1
  - `git add -A`
  - `git commit -m "feat(deploy): add health check and env config"`

---

## Phase 2: 数据库迁移策略

### 2.1 迁移验证
- [ ] **Task 2.1.1**: 检查现有迁移
  - 确保只有一个 head: `alembic heads`
  - 所有迁移都有 downgrade()

- [ ] **Task 2.1.2**: 创建迁移脚本
  - 文件: `scripts/migrate.sh`
  - 功能: backup → migrate → verify

### 2.2 CI 集成
- [ ] **Task 2.2.1**: 验证 CI 迁移步骤
  - 确保 `.github/workflows/backend.yml` 包含 `alembic upgrade head`
  - 测试失败时 CI 应失败

### 2.3 文档
- [ ] **Task 2.3.1**: 创建迁移指南
  - 文件: `docs/DATABASE_MIGRATION.md`
  - 内容: 迁移命令、回滚步骤、最佳实践

### 2.4 提交
- [ ] **Task 2.4.1**: 提交 Phase 2
  - `git add -A`
  - `git commit -m "docs(db): add migration guide and scripts"`

---

## Phase 3: EAS Build 配置

### 3.1 EAS 配置
- [ ] **Task 3.1.1**: 创建 eas.json
  - 文件: `clarity-mobile/eas.json`
  - Profiles: development, preview, production

- [ ] **Task 3.1.2**: 更新 app.config.js
  - 引用环境变量
  - 配置版本号
  - 文件: `clarity-mobile/app.config.js` 或 `app.json`

### 3.2 环境变量
- [ ] **Task 3.2.1**: 文档化 EAS Secrets
  - 列出需要在 EAS 设置的变量
  - 文件: `docs/EAS_SECRETS.md`

### 3.3 构建测试
- [ ] **Task 3.3.1**: 验证 EAS build dry-run
  - 确保 CI 中 `eas build --profile preview --platform all --non-interactive --no-wait` 成功

### 3.4 提交
- [ ] **Task 3.4.1**: 提交 Phase 3
  - `git add -A`
  - `git commit -m "build(eas): add EAS build configuration"`

---

## Phase 4: 监控集成

### 4.1 后端 Sentry (可选 - 后续实现)
- [ ] **Task 4.1.1**: 添加 Sentry 依赖
  - `poetry add sentry-sdk[fastapi]`

- [ ] **Task 4.1.2**: 配置 Sentry
  - 文件: `clarity-api/app/main.py`
  - 添加 DSN 环境变量

### 4.2 移动端 Sentry (可选 - 后续实现)
- [ ] **Task 4.2.1**: 添加 Sentry 依赖
  - `npx expo install @sentry/react-native`

### 4.3 结构化日志
- [ ] **Task 4.3.1**: 配置 structlog (可选)
  - 统一日志格式
  - JSON 输出便于搜索

### 4.4 提交
- [ ] **Task 4.4.1**: 提交 Phase 4
  - `git add -A`
  - `git commit -m "feat(monitoring): add Sentry integration"`

---

## Phase 5: Release 文档

### 5.1 发布指南
- [ ] **Task 5.1.1**: 创建 RELEASE.md
  - 文件: `RELEASE.md`
  - 内容: 发布前检查、部署步骤、回滚指南

- [ ] **Task 5.1.2**: 创建 CHANGELOG.md
  - 文件: `CHANGELOG.md`
  - 模板: Keep a Changelog 格式

### 5.2 README 更新
- [ ] **Task 5.2.1**: 更新 README.md
  - 添加部署说明
  - 添加环境变量快速参考

### 5.3 提交
- [ ] **Task 5.3.1**: 提交 Phase 5
  - `git add -A`
  - `git commit -m "docs(release): add release guide and changelog"`

---

## Phase 6: 最终验证与 PR

### 6.1 CI 验证
- [ ] **Task 6.1.1**: Backend CI 全绿
  - ruff + mypy + pytest

- [ ] **Task 6.1.2**: Mobile CI 全绿
  - lint + tsc

### 6.2 PR 创建
- [ ] **Task 6.2.1**: 推送分支
  - `git push -u origin feat/epic8-release`

- [ ] **Task 6.2.2**: 创建 PR
  - `gh pr create --base main --title "feat(release): Epic 8 - Release & Deployment"`

- [ ] **Task 6.2.3**: 设置 auto-merge
  - `gh pr merge --auto --squash --delete-branch`

### 6.3 合并后
- [ ] **Task 6.3.1**: 同步 main
  - `git switch main && git pull`

---

## 完成检查清单

- [ ] .env.example 包含所有生产必需变量
- [ ] /health 端点可用并返回正确信息
- [ ] 数据库迁移脚本和文档完整
- [ ] eas.json 配置正确
- [ ] RELEASE.md 和 CHANGELOG.md 存在
- [ ] Backend CI 全绿
- [ ] Mobile CI 全绿
- [ ] PR 已合并到 main

---

**总任务数**: ~25 个
**预计工时**: 2-3 天（按 Phase 顺序执行）
