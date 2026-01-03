# 前端认证 401 错误诊断报告

**日期**：2026-01-03
**问题**：生产环境认证 API 全部返回 401

---

## 🔴 问题现象

浏览器控制台出现以下错误：
```
GET https://api.solacore.app/auth/me 401 (Unauthorized)
POST https://api.solacore.app/auth/refresh 401 (Unauthorized)
POST https://api.solacore.app/auth/login 401 (Unauthorized)
```

---

## 🔍 诊断过程

### 1. 排查方向

- ✅ 检查后端认证中间件（app/middleware/auth.py）
- ✅ 检查 CSRF 配置（/auth/login 在豁免列表）
- ✅ 检查 Cookie 设置逻辑（app/routers/auth/utils.py）
- ✅ 检查前端 withCredentials 配置
- ✅ 检查 Nginx CORS 配置

### 2. 关键发现

**后端代码审查**：
- `/auth/login` 端点不需要认证（正常）
- Cookie 设置逻辑正确（httpOnly, Secure, SameSite=lax）
- **关键问题**：`settings.cookie_domain` 为空

**前端配置审查**：
- ✅ axios withCredentials: true 已配置
- ✅ fetch credentials: 'include' 已配置
- ✅ 所有认证 API 使用正确配置

**Nginx 配置审查**：
- ✅ CORS headers 正确配置
- ✅ Access-Control-Allow-Credentials: true
- ✅ Access-Control-Allow-Origin: https://solacore.app

### 3. 根因定位

**问题代码**（app/routers/auth/utils.py:26-29）：
```python
# 生产环境设置 domain，允许跨子域名共享 cookie
if settings.cookie_domain:
    cookie_config["domain"] = settings.cookie_domain
```

**当 `cookie_domain` 为空时**：
- Cookie 被设置到精确域名 `api.solacore.app`
- 前端域名 `solacore.app` 无法读取该 Cookie
- 导致后续请求不带 Cookie → 401 Unauthorized

---

## ✅ 修复方案

### 方案 1：后端配置（推荐）

在生产环境添加环境变量：
```bash
COOKIE_DOMAIN=.solacore.app
```

**注意**：必须以 `.` 开头，允许子域名共享

### 方案 2：配置文件

更新 `.env` 或 `docker-compose.yml`：
```yaml
environment:
  - COOKIE_DOMAIN=.solacore.app
```

---

## 🧪 验证步骤

修复后，在浏览器 DevTools 检查：

**1. 检查响应头**
```
Network → /auth/login → Response Headers
应包含：Set-Cookie: access_token=...; Domain=.solacore.app
```

**2. 验证 Cookie**
```
Application → Cookies → https://api.solacore.app
应看到 access_token、refresh_token、csrf_token
```

**3. 验证认证 API**
```
Network → /auth/me → Request Headers
应包含：Cookie: access_token=...
响应：200 OK
```

---

## 📊 其他发现

### 问题 1: DraggableContainer 错误
- **状态**：⚠️ 非项目代码
- **原因**：浏览器扩展注入
- **解决**：禁用相关扩展

### 问题 2: KaTeX quirks mode 警告
- **状态**：⚠️ 次要
- **原因**：iframe 或特殊渲染环境缺少 doctype
- **影响**：不影响功能

---

## 📝 总结

- **根本原因**：生产环境缺少 `COOKIE_DOMAIN` 配置
- **影响范围**：所有需要认证的 API
- **修复难度**：⭐ 简单（仅需添加环境变量）
- **修复时间**：5 分钟（重启服务）
- **配置模板**：已更新 `.env.prod.example`

---

**报告人**：Claude Orchestrator + Codex
**协作窗口**：Window 1 (编排) + Window 3 (分析) + Window 5 (检查)
