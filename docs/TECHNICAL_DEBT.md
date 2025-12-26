# 技术债务清单 (Technical Debt)

> **说明**：记录需要改进但暂时不紧迫的技术问题

---

## 🔴 P0 - Critical（需要尽快处理）

_暂无_

---

## 🟡 P1 - High（建议近期处理）

_暂无_

---

## 🟢 P2 - Medium（可延后处理）

_暂无_

---

## 📝 归档（已完成）

### ✅ [P4] ChatInterface.tsx 组件复杂度高
- **状态**：已修复 ✅（2025-12-25）
- **提交**：1a94ec0
- **解决方案**：提取 useChatStream 自定义 Hook
- **改动范围**：
  - 新增 hooks/useChatStream.ts
  - 重构 ChatInterface.tsx (188行 → 133行)
- **优化效果**: 职责分离、可测试性提升、可复用性增强

### ✅ [P1] localStorage 存储 JWT Token → XSS 安全风险
- **状态**：已修复 ✅（2025-12-25）
- **提交**：aed3595
- **解决方案**：改用 httpOnly cookies 存储认证 token
- **改动范围**：
  - 后端: 7 个端点 + auth 中间件
  - 前端: lib/api.ts, lib/auth.ts, AuthProvider.tsx, login/page.tsx
- **安全提升**: XSS 防护、CSRF 防护、传输安全

### ✅ [P2] 部分路由缺少 Rate Limiting 保护
- **状态**：已修复 ✅（2025-12-25）
- **提交**：fe13a70

### ✅ [P3] 日志可能包含敏感信息
- **状态**：已修复 ✅（2025-12-25）
- **提交**：fe13a70
