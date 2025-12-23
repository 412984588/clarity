# QA/UAT Execution Log

**Test Run Date**: 2025-12-23
**Environment**: Local
**Build/Version**: 1.0.0 (local)
**Tester**: Automation (Codex)

---

## Summary

| Status | Count |
|--------|-------|
| **PASS** | 3 |
| **FAIL** | 0 |
| **BLOCKED** | 4 |
| **NOT RUN** | 18 |
| **Total** | 25 |

**Overall Result**: IN PROGRESS

---

## Test Run Table

| Case ID | Area | Scenario | Result | Notes |
|---------|------|----------|--------|-------|
| AUTH-01 | Auth | 邮箱注册新用户 | NOT RUN | |
| AUTH-02 | Auth | 邮箱登录已有用户 | NOT RUN | |
| AUTH-03 | Auth | 邮箱登录密码错误 | NOT RUN | |
| AUTH-04 | Auth | Google OAuth 登录 | NOT RUN | |
| AUTH-05 | Auth | Apple Sign-In 登录 | BLOCKED | 需 Apple Developer |
| SOLVE-01 | Solve | Step 1: Receive 输入问题 | NOT RUN | |
| SOLVE-02 | Solve | Step 2: Clarify 回答追问 | NOT RUN | |
| SOLVE-03 | Solve | Step 3: Reframe 重新定义 | NOT RUN | |
| SOLVE-04 | Solve | Step 4: Options 选择方案 | NOT RUN | |
| SOLVE-05 | Solve | Step 5: Commit 设定行动 | NOT RUN | |
| EMO-01 | Emotion | 检测焦虑情绪 | NOT RUN | |
| EMO-02 | Emotion | 检测平静情绪 | NOT RUN | |
| HEALTH-01 | Health | GET /health | PASS | Local smoke 2025-12-23 |
| HEALTH-02 | Health | GET /health/ready | PASS | Local smoke 2025-12-23 |
| HEALTH-03 | Health | GET /health/live | PASS | Local smoke 2025-12-23 |
| SUB-01 | Subscription | 查看订阅计划 | BLOCKED | Stripe 未激活 |
| SUB-02 | Subscription | Stripe 支付流程 | BLOCKED | Stripe 未激活 |
| SUB-03 | Subscription | RevenueCat 移动端订阅 | BLOCKED | RevenueCat 未配置 |
| ERR-01 | Error | 网络断开时提交 | NOT RUN | |
| ERR-02 | Error | API 返回 500 | NOT RUN | |
| ERR-03 | Error | Token 过期 | NOT RUN | |
| I18N-01 | i18n | 切换到英文 | NOT RUN | |
| I18N-02 | i18n | 切换到西班牙语 | NOT RUN | |
| I18N-03 | i18n | 中文情绪检测 | NOT RUN | |

---

## Blockers & Risks

| Blocker | Impact | Mitigation |
|---------|--------|------------|
| Apple Developer 账号未开通 | AUTH-05 无法测试 | 等待账号开通 |
| Stripe/RevenueCat 未激活 | SUB-01/02/03 无法测试 | 标记 BLOCKED，优先测试其他 |
| 域名未配置 | 无法测试生产环境 | 使用本地环境验证 |

---

## Issues Found

| Issue ID | Severity | Case ID | Description | Status |
|----------|----------|---------|-------------|--------|
| - | - | - | (无问题发现) | - |

**Severity Legend**: P0 (Critical) / P1 (High) / P2 (Medium) / P3 (Low)

---

## Sign-off

| Role | Name | Date | Decision |
|------|------|------|----------|
| QA Lead | | | GO / NO-GO / CONDITIONAL |
| Dev Lead | | | APPROVED / REJECTED |
| Product Owner | | | APPROVED / REJECTED |

---

## Notes

- 测试用例定义见: `docs/release/qa-test-plan.md`
- 验收标准见: `docs/release/qa-test-plan.md#acceptance-criteria`
- 退出标准见: `docs/release/qa-test-plan.md#exit-criteria`
- 本次已验证健康检查，日志：`docs/release/deploy-prod-smoke-local-2025-12-23.log`

---

## History

| Date | Tester | Environment | Result | Notes |
|------|--------|-------------|--------|-------|
| 2025-12-23 | Automation (Codex) | Local | IN PROGRESS | Health endpoints via deploy_prod_smoke.sh |
