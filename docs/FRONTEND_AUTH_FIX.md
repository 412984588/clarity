# 前端认证问题修复报告

**修复日期**: 2026-01-01
**问题**: 前端无法访问认证接口（401 Unauthorized）
**根本原因**: Cookie 缺少 `Secure` 标志

---

## 问题现象

用户在使用前端时遇到以下错误：

```
GET https://api.solacore.app/auth/me → 401 (Unauthorized)
GET https://api.solacore.app/subscriptions/current → 501 (Not Implemented)
POST https://api.solacore.app/sessions → 403 (Forbidden)
```

---

## 根本原因分析

### 1. Cookie 配置问题

**代码位置**: `solacore-api/app/routers/auth/utils.py:22`

```python
cookie_config: dict = {
    "httponly": True,
    "secure": not settings.debug,  # ⚠️ 关键：debug=True 时，secure=False
    "samesite": "lax",
}
```

**生产环境配置**（修复前）:
```bash
DEBUG=true          # ❌ 错误：生产环境开启了 debug 模式
BETA_MODE=true      # ❌ 错误：生产环境开启了 beta 模式
```

**导致的问题**:
- `DEBUG=true` → `secure=False`
- 浏览器拒绝在 HTTPS 网站上发送没有 `Secure` 标志的 cookies
- 前端请求无法携带 `access_token` 和 `refresh_token`
- API 返回 401 Unauthorized

---

## 修复步骤

### 1. 修改生产环境配置

```bash
# SSH 登录服务器
ssh linuxuser@139.180.223.98

# 修改配置
cd /home/linuxuser/solacore/solacore-api
sed -i 's/^DEBUG=true/DEBUG=false/' .env
sed -i 's/^BETA_MODE=true/BETA_MODE=false/' .env

# 验证修改
grep -E '^(DEBUG|BETA_MODE)=' .env
```

### 2. 重新创建 API 容器

```bash
# 停止并删除旧容器
docker-compose -f docker-compose.prod.yml stop api
docker-compose -f docker-compose.prod.yml rm -f api

# 创建新容器
docker-compose -f docker-compose.prod.yml up -d api

# 等待启动完成
sleep 20

# 验证健康状态
curl -sk https://api.solacore.app/health | python3 -m json.tool
```

### 3. 验证修复

```bash
# 验证 CSRF cookie
curl -sk -v https://api.solacore.app/auth/csrf 2>&1 | grep "set-cookie"
# 期望输出包含: Secure

# 验证认证 cookies
curl -sk -c cookies.txt https://api.solacore.app/auth/csrf > /dev/null
CSRF=$(grep csrf_token cookies.txt | grep -v HttpOnly | awk '{print $7}')

curl -sk -v -X POST https://api.solacore.app/auth/register \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF" \
  -d '{"email":"test@example.com","password":"Test123!","device_fingerprint":"test"}' \
  2>&1 | grep "set-cookie: access_token"
# 期望输出包含: Secure
```

---

## 修复后的 Cookie 配置

### CSRF Token Cookies

```http
set-cookie: csrf_token=...; Domain=.solacore.app; Max-Age=2592000; Path=/; SameSite=lax; Secure
set-cookie: csrf_token_http=...; Domain=.solacore.app; HttpOnly; Max-Age=2592000; Path=/; SameSite=lax; Secure
```

### 认证 Cookies（注册/登录后）

```http
set-cookie: access_token=...; Domain=.solacore.app; HttpOnly; Max-Age=3600; Path=/; SameSite=lax; Secure
set-cookie: refresh_token=...; Domain=.solacore.app; HttpOnly; Max-Age=2592000; Path=/; SameSite=lax; Secure
```

---

## 验证清单

- [x] **DEBUG=false** - 生产环境已关闭调试模式
- [x] **BETA_MODE=false** - 生产环境已关闭 Beta 模式
- [x] **Secure 标志** - 所有 cookies 包含 Secure 标志
- [x] **HttpOnly 标志** - access_token 和 refresh_token 有 HttpOnly
- [x] **SameSite=lax** - 所有 cookies 有 CSRF 保护
- [x] **Domain=.solacore.app** - 允许子域名共享 cookies
- [x] **API 健康检查** - https://api.solacore.app/health 返回正常

---

## 后续测试建议

### 前端开发者测试步骤

1. **清除浏览器缓存和 Cookies**
   - Chrome: DevTools → Application → Storage → Clear site data

2. **测试注册流程**
   ```javascript
   // 在浏览器控制台运行
   const resp = await fetch('https://api.solacore.app/auth/csrf', {credentials: 'include'});
   const {csrf_token} = await resp.json();

   const registerResp = await fetch('https://api.solacore.app/auth/register', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'X-CSRF-Token': csrf_token
     },
     credentials: 'include',
     body: JSON.stringify({
       email: 'test@example.com',
       password: 'TestPassword123!',
       device_fingerprint: 'browser-123'
     })
   });
   const data = await registerResp.json();
   console.log(data);
   ```

3. **测试认证接口**
   ```javascript
   // 注册/登录后，测试 /auth/me
   const meResp = await fetch('https://api.solacore.app/auth/me', {
     credentials: 'include'
   });
   const userData = await meResp.json();
   console.log(userData);  // 应该返回用户信息，不是 401
   ```

4. **检查浏览器 Cookies**
   - Chrome DevTools → Application → Cookies → https://api.solacore.app
   - 确认看到：access_token, refresh_token, csrf_token
   - 确认所有 cookies 有 🔒 (Secure) 标志

---

## 注意事项

### 1. DEBUG 模式的影响

| 配置 | Secure 标志 | 适用环境 |
|------|------------|----------|
| DEBUG=true | ❌ 无 | 本地开发（HTTP） |
| DEBUG=false | ✅ 有 | 生产环境（HTTPS） |

### 2. 生产环境配置验证

生产环境启动时会自动验证配置，如果配置不当会拒绝启动：

```python
# solacore-api/app/config.py:207
if settings.debug:
    raise RuntimeError("DEBUG must be disabled in production")
if settings.beta_mode:
    raise RuntimeError("BETA_MODE must be disabled in production")
```

### 3. Cookie 跨域共享

**为什么使用 `.solacore.app` 作为 Domain？**

- 前端：`solacore.app` 或 `www.solacore.app`
- API：`api.solacore.app`

设置 `Domain=.solacore.app`（前面有点）允许所有子域名共享 cookies。

---

## 相关文档

- **SSL 证书**: `docs/SSL_CERTIFICATE_GUIDE.md`
- **学习功能测试**: `docs/LEARN_FEATURE_TEST_GUIDE.md`
- **数据库监控**: `docs/DATABASE_MONITORING_GUIDE.md`

---

**最后更新**: 2026-01-01
**维护者**: Claude
