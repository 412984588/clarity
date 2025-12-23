# QA / UAT Test Plan

**Version**: 1.0
**Created**: 2025-12-23
**Status**: Draft

---

## Scope & Objectives

### Scope

本测试计划覆盖 Clarity 应用的核心功能验证，包括：
- 用户认证（邮箱、Google、Apple）
- 账号数据导出与删除
- Solve 问题解决流程（5 步）
- 情绪检测与 UI 反馈
- 后端健康检查端点
- 订阅与支付功能
- 错误处理
- 国际化支持

### Objectives

1. 验证所有核心功能按预期工作
2. 确认跨平台兼容性（Android / iOS）
3. 识别并记录任何阻塞性问题
4. 为生产发布提供 Go/No-Go 决策依据

---

## Test Environments

| Environment | Platform | API URL | Purpose |
|-------------|----------|---------|---------|
| **Local Demo** | Web/Mobile | `http://localhost:8000` | 开发验证 |
| **Preview Build** | Android APK | https://expo.dev/artifacts/eas/hUhRm9YvGcYz9Jqj3AVQnY.apk (Build ID: 88df477f-4862-41ac-9c44-4134aa2b67e2) | 集成测试 |
| **Preview Build** | iOS TestFlight | BLOCKED | 需 Apple Developer |
| **Production** | All | `https://api.clarity.app` | 生产验收 |

---

## Test Data & Accounts

| Type | Details | Status |
|------|---------|--------|
| Test Email Account | `demo@test.com` (测试时创建) | TBD |
| Test Google Account | TBD | TBD |
| Test Apple ID | TBD | BLOCKED |
| Stripe Test Card | `4242 4242 4242 4242` | READY |
| RevenueCat Sandbox | TBD | TBD |

---

## Test Cases

| ID | Area | Scenario | Expected | Status |
|----|------|----------|----------|--------|
| **AUTH-01** | Auth | 邮箱注册新用户 | 注册成功，返回 access/refresh token | NOT RUN |
| **AUTH-02** | Auth | 邮箱登录已有用户 | 登录成功，跳转首页 | NOT RUN |
| **AUTH-03** | Auth | 邮箱登录密码错误 | 显示错误提示，不跳转 | NOT RUN |
| **AUTH-04** | Auth | Google OAuth 登录 | 跳转 Google，授权后返回登录成功 | NOT RUN |
| **AUTH-05** | Auth | Apple Sign-In 登录 | 跳转 Apple，授权后返回登录成功 | BLOCKED |
| **ACC-01** | Account | 导出账号数据 | 导出 JSON 可分享 | NOT RUN |
| **ACC-02** | Account | 删除账号 | 删除后返回登录，账号不可再用 | NOT RUN |
| **SOLVE-01** | Solve | Step 1: Receive 输入问题 | 问题保存，进入 Clarify | NOT RUN |
| **SOLVE-02** | Solve | Step 2: Clarify 回答追问 | AI 提问，用户回答后进入 Reframe | NOT RUN |
| **SOLVE-03** | Solve | Step 3: Reframe 重新定义 | 显示重新定义的问题 | NOT RUN |
| **SOLVE-04** | Solve | Step 4: Options 选择方案 | 显示 3-4 个方案卡片 | NOT RUN |
| **SOLVE-05** | Solve | Step 5: Commit 设定行动 | 保存行动计划，完成流程 | NOT RUN |
| **EMO-01** | Emotion | 检测焦虑情绪 | 背景色变暖色调 | NOT RUN |
| **EMO-02** | Emotion | 检测平静情绪 | 背景色变冷色调 | NOT RUN |
| **HEALTH-01** | Health | GET /health | 返回 `{"status":"healthy","version":"1.0.0","database":"connected"}` | NOT RUN |
| **HEALTH-02** | Health | GET /health/ready | 返回 `{"ready":true}` | NOT RUN |
| **HEALTH-03** | Health | GET /health/live | 返回 `{"live":true}` | NOT RUN |
| **SUB-01** | Subscription | 查看订阅计划 | 显示 Standard / Pro 选项 | BLOCKED |
| **SUB-02** | Subscription | Stripe 支付流程 | 跳转 Stripe，完成支付后更新状态 | BLOCKED |
| **SUB-03** | Subscription | RevenueCat 移动端订阅 | 触发 App Store / Play Store 购买 | BLOCKED |
| **ERR-01** | Error | 网络断开时提交 | 显示友好错误提示 | NOT RUN |
| **ERR-02** | Error | API 返回 500 | 显示"服务暂时不可用" | NOT RUN |
| **ERR-03** | Error | Token 过期 | 自动刷新或提示重新登录 | NOT RUN |
| **I18N-01** | i18n | 切换到英文 | 所有 UI 文案切换为英文 | NOT RUN |
| **I18N-02** | i18n | 切换到西班牙语 | 所有 UI 文案切换为西班牙语 | NOT RUN |
| **I18N-03** | i18n | 中文情绪检测 | 正确识别中文情绪关键词 | NOT RUN |
| **AUTH-06** | Auth | 设备数量超限 | 返回 403 + `DEVICE_LIMIT_REACHED` | NOT RUN |
| **AUTH-07** | Auth | 设备已绑定其他账号 | 返回 403 + `DEVICE_BOUND_TO_OTHER` | NOT RUN |
| **SOLVE-06** | Solve | SSE 流式响应完整 | 事件流包含 token + done，done 含 next_step + emotion_detected | NOT RUN |
| **SUB-04** | Subscription | 查看使用量 | `/subscriptions/usage` 返回 tier/limit/used | NOT RUN |
| **WEBHOOK-01** | Webhook | Stripe 端点可达 | 400/401/422 皆视为可达 | NOT RUN |
| **WEBHOOK-02** | Webhook | RevenueCat 端点可达 | 400/401/422 皆视为可达 | NOT RUN |
| **SAFETY-01** | Safety | 触发危机关键词 | 返回 crisis 响应并阻断流程 | NOT RUN |

---

## Acceptance Criteria

测试通过需满足以下条件：

1. **AUTH**: 邮箱登录可用；若 OAuth 已配置，至少 1 种第三方登录可用
2. **SOLVE**: 完整 5 步流程可走通
3. **HEALTH**: 所有健康检查端点返回正常
4. **ERROR**: 所有错误场景有友好提示
5. **CRITICAL**: 无 P0/P1 级别 Bug

---

## Exit Criteria

可退出测试阶段的条件：

| Criteria | Threshold |
|----------|-----------|
| 测试用例执行率 | ≥ 90% (BLOCKED 除外) |
| 通过率 | ≥ 95% (BLOCKED 除外) |
| P0 Bug | 0 |
| P1 Bug | 0 |
| P2 Bug | ≤ 3 |

---

## Risks & Blockers

| Risk/Blocker | Impact | Mitigation |
|--------------|--------|------------|
| Apple Developer 账号未开通 | iOS 测试无法进行 | 等待账号开通，优先测试 Android |
| 域名未配置 | 无法测试生产环境 | 使用本地环境验证核心流程 |
| Stripe/RevenueCat 未激活 | 支付流程无法测试 | 标记为 BLOCKED，优先测试其他功能 |
| Preview Build 指向 staging API | 预览包可能无法连通服务 | 如无 staging，改用本地或记录为 BLOCKED |
| LLM API Key 限额 | AI 响应可能失败 | 使用 Mock 响应或低频测试 |

---

## Related Documents

- 本机演示手册: `docs/release/local-demo-runbook.md`
- 演示话术: `docs/release/demo-script.md`
- 本地部署验证: `docs/release/local-deploy-verify.md`
- Manual QA Checklist: `docs/release/manual-qa-checklist.md`
- 上线准备度: `docs/release/launch-readiness.md`
