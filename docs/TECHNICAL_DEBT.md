# 技术债务清单 (Technical Debt)

> **说明**：记录需要改进但暂时不紧迫的技术问题

---

## 🔴 P0 - Critical（需要尽快处理）

### [P1] localStorage 存储 JWT Token → XSS 安全风险

**问题描述**：
- 前端使用 `localStorage` 存储 JWT access_token 和 refresh_token
- localStorage 可被任何客户端 JavaScript 读取
- 如果存在 XSS 漏洞，恶意脚本可窃取用户 session

**当前风险评估**：
- ⚠️ **Medium-High**：需要先存在 XSS 注入点才能利用
- ✅ 当前使用 react-markdown（默认转义 HTML），没有明显的 XSS 漏洞
- ✅ TypeScript 严格模式，减少代码注入风险

**推荐解决方案**：
改用 **httpOnly cookies** 存储认证 token

**改动范围**（预计 2-3 天）：
1. **后端改造**（6 个端点）：
   - `/auth/register`, `/auth/login`, `/auth/beta-login`
   - `/auth/refresh`, `/auth/oauth/google`, `/auth/oauth/apple`
   - 改为设置 `Set-Cookie` 响应头（httpOnly, Secure, SameSite）
   - 新增 `/auth/me` 端点（前端验证登录状态）

2. **前端改造**：
   - `lib/api.ts`: 移除 `readTokens()`, `writeTokens()`, `clearTokens()` 中的 localStorage 逻辑
   - 移除 API 拦截器中手动添加 Authorization 头（浏览器会自动发送 cookie）
   - `lib/auth.ts`: 修改 `isAuthenticated()` 改为调用 `/auth/me` API

3. **全面测试**：
   - Beta 自动登录流程
   - Email 注册/登录流程
   - Google OAuth 流程
   - Token 刷新流程
   - 登出流程
   - 跨域 CORS 配置（确保 credentials: 'include'）

**实施建议**：
- 使用 `git worktree` 创建隔离分支：`feature/httponly-cookies`
- 后端先改，前端再改
- 每个端点改完后立即测试
- 全部改完后进行回归测试
- 测试通过后再合并主分支

**参考资料**：
- [OWASP - XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [MDN - HttpOnly Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#restrict_access_to_cookies)

**创建时间**：2025-12-25
**发现来源**：三 AI 协作安全审核（Gemini）
**优先级**：P0 - Critical（但可等待合适时机处理）

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

### ✅ [P2] 部分路由缺少 Rate Limiting 保护
- **状态**：已修复 ✅（2025-12-25）
- **提交**：fe13a70

### ✅ [P3] 日志可能包含敏感信息
- **状态**：已修复 ✅（2025-12-25）
- **提交**：fe13a70
