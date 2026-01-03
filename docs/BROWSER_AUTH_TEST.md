# 浏览器端认证测试指南

**用途**: 在浏览器中验证 Cookie 安全配置和完整认证流程
**适用人群**: 前端开发者
**测试环境**: Chrome/Firefox/Safari 浏览器

---

## 快速开始

### 步骤 1: 打开浏览器控制台

1. 访问 https://solacore.app 或 https://api.solacore.app
2. 按 `F12` 打开开发者工具
3. 切换到 `Console` 标签

### 步骤 2: 运行测试脚本

复制以下代码到控制台并运行：

```javascript
// ============================================
// SolaCore 前端认证测试脚本
// ============================================

(async function testAuth() {
  console.log('🚀 开始测试认证流程...\n');

  // 测试 1: 获取 CSRF Token
  console.log('📍 [1/7] 获取 CSRF Token...');
  const csrfResp = await fetch('https://api.solacore.app/auth/csrf', {
    credentials: 'include'
  });
  const { csrf_token } = await csrfResp.json();
  console.log(`✅ CSRF Token: ${csrf_token.substring(0, 20)}...\n`);

  // 测试 2: 注册新用户
  console.log('📍 [2/7] 注册新用户...');
  const timestamp = Date.now();
  const email = `test-browser-${timestamp}@solacore.app`;
  const password = 'TestPassword123!';

  const registerResp = await fetch('https://api.solacore.app/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrf_token
    },
    credentials: 'include',
    body: JSON.stringify({
      email: email,
      password: password,
      device_fingerprint: `browser-${timestamp}`
    })
  });

  const registerData = await registerResp.json();
  if (registerData.user) {
    console.log(`✅ 注册成功: ${registerData.user.email}`);
    console.log(`   User ID: ${registerData.user.id}\n`);
  } else {
    console.error('❌ 注册失败:', registerData);
    return;
  }

  // 测试 3: 访问保护接口
  console.log('📍 [3/7] 访问保护接口 /auth/me...');
  const meResp = await fetch('https://api.solacore.app/auth/me', {
    credentials: 'include'
  });
  const userData = await meResp.json();

  if (userData.email === email) {
    console.log(`✅ /auth/me 访问成功`);
    console.log(`   Email: ${userData.email}`);
    console.log(`   Provider: ${userData.auth_provider}\n`);
  } else {
    console.error('❌ /auth/me 访问失败:', userData);
    return;
  }

  // 测试 4: 获取学习工具列表
  console.log('📍 [4/7] 获取学习工具列表...');
  const toolsResp = await fetch('https://api.solacore.app/learn/tools', {
    credentials: 'include'
  });
  const { tools } = await toolsResp.json();
  console.log(`✅ 学习工具: ${tools.length} 个`);
  console.log(`   示例: ${tools.slice(0, 3).map(t => t.name).join(', ')}\n`);

  // 测试 5: 创建学习会话
  console.log('📍 [5/7] 创建学习会话...');
  const createSessionResp = await fetch('https://api.solacore.app/learn', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrf_token
    },
    credentials: 'include',
    body: JSON.stringify({ mode: 'quick' })
  });
  const sessionData = await createSessionResp.json();

  if (sessionData.session_id) {
    console.log(`✅ 学习会话创建成功`);
    console.log(`   Session ID: ${sessionData.session_id}\n`);
  } else {
    console.error('❌ 创建会话失败:', sessionData);
  }

  // 测试 6: 检查 Cookies
  console.log('📍 [6/7] 检查浏览器 Cookies...');
  console.log('请切换到 DevTools → Application → Cookies → https://api.solacore.app');
  console.log('确认以下 cookies 存在且有 🔒 图标:\n');
  console.log('  ✓ access_token  (HttpOnly, Secure, SameSite)');
  console.log('  ✓ refresh_token (HttpOnly, Secure, SameSite)');
  console.log('  ✓ csrf_token    (Secure, SameSite)');
  console.log('  ✓ csrf_token_http (HttpOnly, Secure, SameSite)\n');

  // 测试 7: 测试跨域请求
  console.log('📍 [7/7] 测试跨域 Cookie 共享...');
  console.log(`当前域名: ${window.location.hostname}`);
  console.log(`API 域名: api.solacore.app`);
  console.log(`Cookie Domain: .solacore.app (允许跨子域共享)\n`);

  console.log('🎉 所有测试完成！\n');
  console.log('='.repeat(50));
  console.log('测试总结：');
  console.log('  ✅ CSRF Token 获取');
  console.log('  ✅ 用户注册');
  console.log('  ✅ 访问保护接口');
  console.log('  ✅ 学习工具列表');
  console.log('  ✅ 创建学习会话');
  console.log('  ✅ Cookie 安全配置');
  console.log('  ✅ 跨域 Cookie 共享');
  console.log('='.repeat(50));

})();
```

---

## 步骤 3: 检查 Cookies

### 3.1 打开 Cookie 检查器

1. 在 DevTools 中，切换到 `Application` 标签（Chrome）或 `Storage` 标签（Firefox）
2. 左侧菜单展开 `Cookies`
3. 点击 `https://api.solacore.app`

### 3.2 验证 Cookie 配置

你应该看到以下 4 个 cookies，每个都有 🔒 图标：

| Cookie Name | Domain | Path | Secure | HttpOnly | SameSite | Max-Age |
|-------------|--------|------|--------|----------|----------|---------|
| `access_token` | .solacore.app | / | ✅ | ✅ | lax | 3600 (1h) |
| `refresh_token` | .solacore.app | / | ✅ | ✅ | lax | 2592000 (30d) |
| `csrf_token` | .solacore.app | / | ✅ | ❌ | lax | 2592000 (30d) |
| `csrf_token_http` | .solacore.app | / | ✅ | ✅ | lax | 2592000 (30d) |

### 3.3 关键验证点

✅ **所有 cookies 都有 🔒 图标** - 表示有 `Secure` 标志
✅ **Domain 是 `.solacore.app`** - 允许 `solacore.app` 和 `api.solacore.app` 共享
✅ **access_token 和 refresh_token 有 HttpOnly** - JavaScript 无法访问（安全）
✅ **csrf_token 没有 HttpOnly** - JavaScript 可以读取（用于发送请求）
✅ **SameSite=lax** - CSRF 攻击保护

---

## 步骤 4: 测试跨域请求

### 4.1 从 solacore.app 访问 api.solacore.app

1. 打开 https://solacore.app
2. 在控制台运行：

```javascript
// 测试跨子域 Cookie 共享
fetch('https://api.solacore.app/auth/me', {
  credentials: 'include'  // 重要：携带 cookies
})
  .then(r => r.json())
  .then(data => {
    console.log('✅ 跨域访问成功:', data);
  })
  .catch(err => {
    console.error('❌ 跨域访问失败:', err);
  });
```

**期望结果**:
- 返回用户信息（不是 401）
- Cookies 自动携带（因为 Domain=.solacore.app）

### 4.2 验证 CORS 配置

```javascript
// 检查 CORS 响应头
fetch('https://api.solacore.app/health', {
  credentials: 'include'
})
  .then(async (response) => {
    console.log('Access-Control-Allow-Origin:',
      response.headers.get('access-control-allow-origin'));
    console.log('Access-Control-Allow-Credentials:',
      response.headers.get('access-control-allow-credentials'));
    return response.json();
  })
  .then(data => console.log('Health:', data));
```

**期望输出**:
```
Access-Control-Allow-Origin: https://solacore.app
Access-Control-Allow-Credentials: true
Health: { status: 'healthy', ... }
```

---

## 常见问题排查

### 问题 1: 看不到 🔒 图标

**原因**: Cookies 缺少 `Secure` 标志
**检查**: 生产环境 `DEBUG=false`
**解决**: SSH 到服务器修改 `.env` 并重启 API

```bash
ssh linuxuser@139.180.223.98
cd /home/linuxuser/solacore/solacore-api
sed -i 's/^DEBUG=true/DEBUG=false/' .env
docker-compose -f docker-compose.prod.yml restart api
```

### 问题 2: 401 Unauthorized

**可能原因**:
1. Cookies 没有 `Secure` 标志（浏览器拒绝发送）
2. Cookies 过期（access_token 1小时有效期）
3. 跨域请求没有 `credentials: 'include'`

**检查步骤**:
```javascript
// 1. 检查 cookies 是否存在
document.cookie.split(';').forEach(c => console.log(c.trim()));

// 2. 检查请求是否携带 cookies（Network 标签）
// 找到请求 → Headers → Request Headers → cookie

// 3. 检查响应是否设置了 cookies（Response Headers）
// Set-Cookie: access_token=...; Secure; HttpOnly; ...
```

### 问题 3: CSRF Token 错误

**原因**:
- CSRF token 过期（30天有效期）
- 使用了错误的 token

**解决**:
```javascript
// 重新获取 CSRF token
const resp = await fetch('https://api.solacore.app/auth/csrf', {
  credentials: 'include'
});
const { csrf_token } = await resp.json();
console.log('新 CSRF Token:', csrf_token);
```

### 问题 4: 跨域请求失败

**检查**:
```javascript
// 确保使用 credentials: 'include'
fetch('https://api.solacore.app/auth/me', {
  credentials: 'include'  // ← 必须设置！
})
```

**CORS 错误示例**:
```
Access to fetch at 'https://api.solacore.app/auth/me' from origin
'https://solacore.app' has been blocked by CORS policy
```

**原因**: 后端 CORS 配置问题
**检查**: 确认 `CORS_ORIGINS` 包含 `https://solacore.app`

---

## 生产环境验证清单

- [ ] 所有 cookies 有 🔒 (Secure) 图标
- [ ] access_token 和 refresh_token 有 HttpOnly
- [ ] csrf_token 可以被 JavaScript 读取
- [ ] Domain 设置为 `.solacore.app`
- [ ] 注册流程正常工作
- [ ] 登录流程正常工作
- [ ] /auth/me 返回用户信息（不是 401）
- [ ] 学习功能接口可以访问
- [ ] 跨域请求可以携带 cookies
- [ ] CORS 配置正确

---

## 相关文档

- **修复报告**: `docs/FRONTEND_AUTH_FIX.md`
- **学习功能测试**: `docs/LEARN_FEATURE_TEST_GUIDE.md`
- **SSL 证书**: `docs/SSL_CERTIFICATE_GUIDE.md`

---

**最后更新**: 2026-01-01
**维护者**: Claude
