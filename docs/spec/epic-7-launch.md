# Epic 7: Launch Readiness (发布准备)

## 概述

**目标**: 让项目进入可内测/可上架状态，不再加新功能，只做"发布闭环"

**前置条件** (已完成):
- Epic 1-6 全部完成
- i18n (en/es/zh) 已实现
- Safety/Crisis Detection 已实现
- Payments/RevenueCat IAP 已实现
- 5-Step Solve Flow 已实现
- Emotion Detection + UI Effects 已实现

---

## 1. 移动端运行配置

### 1.1 环境变量固化

**目标**: 为 dev/staging/prod 三个环境配置独立的 API URL

| 环境 | EXPO_PUBLIC_API_URL | 用途 |
|------|---------------------|------|
| dev | `http://localhost:8000` | 本地开发 |
| staging | `https://staging-api.clarity.app` | 测试环境 |
| prod | `https://api.clarity.app` | 生产环境 |

**实现方式**:
- 创建 `.env.development`, `.env.staging`, `.env.production`
- 在 `app.config.ts` 中读取 `process.env.EXPO_PUBLIC_API_URL`
- EAS Build 时通过 `--profile` 自动选择环境

### 1.2 本地调试说明

**iOS 调试**:
- Xcode 14+ 要求
- 模拟器: `npx expo start --ios`
- 真机: 需要 Apple Developer Account

**Android 调试**:
- Android Studio + SDK 要求
- 模拟器: `npx expo start --android`
- 真机: 开启 USB 调试

---

## 2. 构建/发布流水线

### 2.1 EAS Build Profiles

**现有配置** (`eas.json`):
```json
{
  "build": {
    "development": { "developmentClient": true, "distribution": "internal" },
    "preview": { "distribution": "internal" },
    "production": {}
  }
}
```

**增强配置**:
- `development`: 加载 `.env.development`, 开启 dev client
- `preview`: 加载 `.env.staging`, 内部分发 (TestFlight/Internal)
- `production`: 加载 `.env.production`, 商店分发

### 2.2 npm ci 稳定性

**问题**: `npm ci` 在 CI 环境可能因版本冲突失败

**解决方案**:
- 锁定 `react` 和 `react-dom` 版本 (已完成: 19.2.3)
- 保持 `package-lock.json` 同步
- CI 使用 `npm ci --legacy-peer-deps`

---

## 3. 监控与回滚

### 3.1 后端 Health/Metrics 端点

**现有**: `/health` 返回 `{"status":"healthy","version":"1.0.0","database":"connected"}`

**增强**:
- `/health/ready`: Kubernetes readiness probe
- `/health/live`: Kubernetes liveness probe
- `/metrics`: 基础指标 (可选, 最小化实现)

### 3.2 移动端 Crash Reporting

**最小化方案**:
- 使用 Expo 内置的 ErrorBoundary
- 捕获未处理异常并记录到 AsyncStorage
- 可选: 集成 Sentry (不在此 Epic 范围)

---

## 4. 合规/商店材料占位

### 4.1 Release Checklist

`docs/release/release-checklist.md`:
- [ ] App Store 截图 (6.5", 5.5", iPad)
- [ ] Play Store 截图 (phone, tablet)
- [ ] App 图标 (1024x1024)
- [ ] Privacy Policy URL
- [ ] Terms of Service URL
- [ ] Support Email
- [ ] Age Rating 信息
- [ ] App Description (各语言)

### 4.2 Privacy Policy

`docs/release/privacy.md`:
- 数据收集说明
- 第三方服务 (RevenueCat, OpenAI)
- 用户权利 (GDPR/CCPA)
- 联系方式

### 4.3 Support Page

`docs/release/support.md`:
- FAQ 常见问题
- 联系邮箱
- 反馈渠道

---

## 5. 最终验收脚本

### 5.1 一键验收命令

```bash
# 完整验收 (所有检查)
./scripts/verify-release.sh

# 或分步执行:
# Backend
cd clarity-api && poetry run ruff check . && poetry run mypy app --ignore-missing-imports && poetry run pytest -v

# Mobile
cd clarity-mobile && npm run lint && npx tsc --noEmit

# Database
cd clarity-api && poetry run alembic upgrade head

# Health Check
curl http://localhost:8000/health
```

### 5.2 验收标准

| 检查项 | 命令 | 期望结果 |
|--------|------|----------|
| Backend Lint | `ruff check .` | All checks passed! |
| Backend Types | `mypy app` | Success: no issues |
| Backend Tests | `pytest` | 100% passed |
| Mobile Lint | `npm run lint` | No errors |
| Mobile Types | `npx tsc --noEmit` | No errors |
| DB Migration | `alembic upgrade head` | Up to date |
| Health Check | `curl /health` | `{"status":"healthy"}` |

---

## 非功能性需求

### 性能
- App 启动时间 < 3s
- API 响应时间 < 500ms (P95)

### 安全
- 所有 API 使用 HTTPS
- JWT Token 过期时间合理 (15min access, 7d refresh)
- 敏感数据不记录日志

### 可用性
- Health endpoint 响应时间 < 100ms
- 数据库连接池配置合理

---

## 时间线

| 阶段 | 内容 |
|------|------|
| Phase 1 | 环境配置 + 构建流水线 |
| Phase 2 | 监控 + 合规材料 |
| Phase 3 | 验收脚本 + 最终检查 |

---

## 验收条件

1. 所有环境变量正确配置
2. EAS Build 三个 profile 可正常构建
3. `/health` 端点返回正确状态
4. 合规文档占位完成
5. 一键验收脚本通过
