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

### [P4] ChatInterface.tsx 组件复杂度高

**问题描述**：
- `ChatInterface.tsx` 组件混合了 UI 渲染和 API streaming 逻辑
- 组件职责过多，不利于维护和测试

**推荐解决方案**：
提取 `useChatStream` 自定义 Hook

**改动范围**（预计 2-3 小时）：
1. 创建 `hooks/useChatStream.ts`
2. 将 `sendMessage` 逻辑迁移到 hook
3. ChatInterface 组件只负责 UI 渲染

**优先级**：P2 - Medium（代码质量问题，不影响功能）

---

## 📝 归档（已完成）

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
