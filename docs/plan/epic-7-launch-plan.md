# Epic 7: Launch Readiness - Implementation Plan

## 概述

基于 `docs/spec/epic-7-launch.md` 规格，本计划将 Epic 7 拆分为 4 个 Phase，确保项目进入可发布状态

---

## Phase 1: 移动端运行配置

### 1.1 环境变量文件

**文件**: `solacore-mobile/.env.development`, `.env.staging`, `.env.production`

```bash
# .env.development
EXPO_PUBLIC_API_URL=http://localhost:8000

# .env.staging
EXPO_PUBLIC_API_URL=https://staging-api.solacore.app

# .env.production
EXPO_PUBLIC_API_URL=https://api.solacore.app
```

### 1.2 动态配置

**文件**: `solacore-mobile/app.config.ts`

- 替换静态 `app.json` 为动态 `app.config.ts`
- 根据 `process.env.EXPO_PUBLIC_API_URL` 设置 extra 配置
- 保留原有配置 (icon, splash, plugins)

### 1.3 更新 docs/setup.md

添加 iOS/Android 本地调试完整说明：
- Xcode 要求和设置
- Android Studio 和 SDK 配置
- 真机调试步骤

---

## Phase 2: 构建/发布流水线

### 2.1 增强 eas.json

**当前配置**:
```json
{
  "build": {
    "development": { "developmentClient": true, "distribution": "internal" },
    "preview": { "distribution": "internal" },
    "production": {}
  }
}
```

**目标配置**:
```json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "env": { "EXPO_PUBLIC_API_URL": "http://localhost:8000" }
    },
    "preview": {
      "distribution": "internal",
      "env": { "EXPO_PUBLIC_API_URL": "https://staging-api.solacore.app" }
    },
    "production": {
      "env": { "EXPO_PUBLIC_API_URL": "https://api.solacore.app" }
    }
  },
  "submit": {
    "production": {}
  }
}
```

### 2.2 npm ci 稳定性

- 确认 `package-lock.json` 已提交
- 版本已锁定: react@19.2.3, react-dom@19.2.3
- CI 命令使用 `npm ci --legacy-peer-deps`

---

## Phase 3: 监控与回滚

### 3.1 后端 Health 端点增强

**文件**: `solacore-api/app/main.py`

新增端点:
- `GET /health/ready`: Readiness probe (数据库连接正常)
- `GET /health/live`: Liveness probe (进程存活)

```python
@app.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe"""
    await db.execute(text("SELECT 1"))
    return {"ready": True}

@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"live": True}
```

### 3.2 移动端 Error Boundary

**文件**: `solacore-mobile/components/ErrorBoundary.tsx`

最小化实现:
- 捕获未处理的 React 渲染错误
- 显示友好的错误界面
- 记录错误到 AsyncStorage (可选导出)

---

## Phase 4: 合规/商店材料 + 验收脚本

### 4.1 Release 文档占位

**目录**: `docs/release/`

| 文件 | 内容 |
|------|------|
| `release-checklist.md` | App Store/Play Store 上架清单 |
| `privacy.md` | 隐私政策模板 |
| `support.md` | 支持页面模板 |

### 4.2 验收脚本

**文件**: `scripts/verify-release.sh`

```bash
#!/bin/bash
set -e

echo "=== Backend Verification ==="
cd solacore-api
poetry run ruff check .
poetry run mypy app --ignore-missing-imports
poetry run pytest -v

echo "=== Mobile Verification ==="
cd ../solacore-mobile
npm run lint
npx tsc --noEmit

echo "=== Database Migration ==="
cd ../solacore-api
poetry run alembic upgrade head

echo "=== Health Check ==="
curl -f http://localhost:8000/health || echo "Health check failed (server not running)"

echo "=== ALL CHECKS PASSED ==="
```

---

## 文件变更清单

### 新增文件

| 文件 | 用途 |
|------|------|
| `solacore-mobile/.env.development` | 开发环境变量 |
| `solacore-mobile/.env.staging` | 测试环境变量 |
| `solacore-mobile/.env.production` | 生产环境变量 |
| `solacore-mobile/app.config.ts` | 动态 Expo 配置 |
| `solacore-mobile/components/ErrorBoundary.tsx` | 错误边界组件 |
| `docs/release/release-checklist.md` | 上架清单 |
| `docs/release/privacy.md` | 隐私政策 |
| `docs/release/support.md` | 支持页面 |
| `scripts/verify-release.sh` | 验收脚本 |

### 修改文件

| 文件 | 变更 |
|------|------|
| `solacore-mobile/eas.json` | 添加环境变量配置 |
| `solacore-mobile/.gitignore` | 添加 `.env.*` (保留 .env.example) |
| `solacore-api/app/main.py` | 添加 /health/ready, /health/live |
| `docs/setup.md` | 添加 iOS/Android 调试说明 |
| `docs/PROGRESS.md` | 更新进度 |

---

## 验证步骤

每个 Phase 完成后执行:

```bash
# Backend
cd solacore-api && poetry run ruff check . && poetry run mypy app --ignore-missing-imports && poetry run pytest -v

# Mobile
cd solacore-mobile && npm run lint && npx tsc --noEmit
```

全部完成后执行:
```bash
./scripts/verify-release.sh
```

---

## 依赖关系

```
Phase 1 (环境配置)
    ↓
Phase 2 (构建流水线) ← 依赖 Phase 1 的环境变量
    ↓
Phase 3 (监控) ← 独立，可并行
    ↓
Phase 4 (验收) ← 依赖所有 Phase 完成
```
