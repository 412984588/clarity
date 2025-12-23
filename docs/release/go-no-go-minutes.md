# Go/No-Go Meeting Minutes

**Template Version**: 1.0

---

## Meeting Info

| Item | Value |
|------|-------|
| **Date** | YYYY-MM-DD |
| **Time** | HH:MM - HH:MM |
| **Duration** | XX minutes |
| **Attendees** | [Name1 (Role), Name2 (Role), ...] |
| **Facilitator** | [Name] |
| **Note Taker** | [Name] |

---

## Agenda

1. 上线准备度评审 (Launch Readiness Review)
2. 阻塞项与风险评审 (Blockers & Risks Review)
3. QA 测试结果评审 (QA Results Review)
4. 发布决策 (Go/No-Go Decision)
5. 行动项与时间线 (Action Items & Timeline)

---

## Readiness Review

**Reference**: `docs/release/launch-readiness.md`

### Summary

| Category | Status | Notes |
|----------|--------|-------|
| Code Quality | [GREEN/YELLOW/RED] | |
| Documentation | [GREEN/YELLOW/RED] | |
| Local Verification | [GREEN/YELLOW/RED] | |
| Android Build | [GREEN/YELLOW/RED] | |
| iOS Build | [GREEN/YELLOW/RED] | |
| Production Deploy | [GREEN/YELLOW/RED] | |

### Key Findings

- [ ] [Finding 1]
- [ ] [Finding 2]
- [ ] [Finding 3]

---

## Blockers Review

**Reference**: `docs/release/risk-register.md`

### Critical Blockers (Must Resolve Before Launch)

| ID | Risk | Status | Resolution Plan |
|----|------|--------|-----------------|
| R01 | 域名未配置 | BLOCKED | [Plan] |
| R02 | Apple Developer 账号未开通 | BLOCKED | [Plan] |

### High Priority Risks

| ID | Risk | Status | Mitigation |
|----|------|--------|------------|
| R04 | Stripe Live Mode 未激活 | OPEN | [Mitigation] |
| R05 | RevenueCat 生产配置缺失 | OPEN | [Mitigation] |

### Discussion Notes

- [Discussion point 1]
- [Discussion point 2]

---

## QA Results Review

**Reference**: `docs/release/qa-execution-log.md`

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| 测试用例执行率 | XX% | ≥ 90% | [PASS/FAIL] |
| 通过率 | XX% | ≥ 95% | [PASS/FAIL] |
| P0 Bug | X | 0 | [PASS/FAIL] |
| P1 Bug | X | 0 | [PASS/FAIL] |
| P2 Bug | X | ≤ 3 | [PASS/FAIL] |

---

## Decision

### Final Decision

| Decision | Rationale |
|----------|-----------|
| **GO** / **NO-GO** / **GO WITH CONDITIONS** | [Brief rationale for the decision] |

### Decision Criteria Met

- [ ] 所有 Critical Blockers 已解决
- [ ] QA 测试通过率达标
- [ ] 无 P0/P1 Bug
- [ ] 回滚方案已准备
- [ ] 监控告警已配置

---

## Conditions & Owners

*仅当决策为 "GO WITH CONDITIONS" 时填写*

| Condition | Owner | Due Date | Status |
|-----------|-------|----------|--------|
| [Condition 1] | [Owner] | YYYY-MM-DD | PENDING |
| [Condition 2] | [Owner] | YYYY-MM-DD | PENDING |
| [Condition 3] | [Owner] | YYYY-MM-DD | PENDING |

---

## Action Items

| ID | Action | Owner | Due Date | Priority |
|----|--------|-------|----------|----------|
| A1 | [Action description] | [Owner] | YYYY-MM-DD | High |
| A2 | [Action description] | [Owner] | YYYY-MM-DD | Medium |
| A3 | [Action description] | [Owner] | YYYY-MM-DD | Low |

---

## Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Tech Lead | | | |
| QA Lead | | | |
| DevOps | | | |

---

## Next Meeting

| Item | Value |
|------|-------|
| **Date** | YYYY-MM-DD |
| **Purpose** | [Follow-up / Final Go-Live Confirmation] |

---

## Related Documents

- 上线准备度评估: `docs/release/launch-readiness.md`
- 风险登记表: `docs/release/risk-register.md`
- QA 执行记录: `docs/release/qa-execution-log.md`
- 生产部署 Runbook: `docs/PROD_DEPLOY.md`
