# Device Fingerprint 不匹配问题修复

**修复日期**: 2026-01-01
**问题**: Google OAuth 登录后无法创建 Session（403 Forbidden）
**根本原因**: Device Fingerprint 不一致

---

## 问题现象

用户通过 Google OAuth 登录后，尝试创建 Session 时遇到错误：

```
POST https://api.solacore.app/sessions → 403 (Forbidden)
Response: {"detail": {"error": "DEVICE_NOT_FOUND"}}
```

---

## 根本原因分析

### 1. Device Fingerprint 生成逻辑不一致

**Google OAuth 登录时** (`solacore-web/lib/auth.ts` - 修复前):
```typescript
const params = new URLSearchParams({
  code: googleCode,
  device_fingerprint: `web-${Date.now()}`,  // ❌ 临时的、基于时间戳
  device_name: navigator.userAgent.substring(0, 50),
});
```

**创建 Session 时** (`solacore-web/lib/api.ts`):
```typescript
const getDeviceFingerprint = (): string => {
  const storageKey = "solacore_device_fingerprint";
  let fingerprint = localStorage.getItem(storageKey);

  if (!fingerprint) {
    fingerprint = crypto.randomUUID();  // ✅ 持久的 UUID
    localStorage.setItem(storageKey, fingerprint);
  }

  return fingerprint;
};
```

### 2. 后端验证逻辑

**后端代码** (`solacore-api/app/routers/sessions/create.py:71-80`):
```python
device_result = await db.execute(
    select(Device).where(
        Device.user_id == current_user.id,
        Device.device_fingerprint == device_fingerprint,
    )
)
device = device_result.scalars().first()
if not device:
    raise HTTPException(status_code=403, detail={"error": "DEVICE_NOT_FOUND"})
```

### 3. 问题流程

```
用户 Google OAuth 登录
  ↓
后端创建 Device 记录
  device_fingerprint = "web-1767295864123"  (临时时间戳)
  ↓
用户尝试创建 Session
  ↓
前端发送 X-Device-Fingerprint: "a1b2c3d4-e5f6-..."  (持久 UUID)
  ↓
后端查询数据库: 找不到匹配的 Device
  ↓
返回 403 DEVICE_NOT_FOUND ❌
```

---

## 修复方案

### 修改文件: `solacore-web/lib/auth.ts`

#### 1. 添加 import

```diff
import type { User } from "@/lib/types";
- import { api, refreshTokens } from "@/lib/api";
+ import { api, refreshTokens, getDeviceFingerprint } from "@/lib/api";
```

#### 2. 使用持久化 fingerprint

```diff
export const login = async (googleCode: string): Promise<void> => {
  const params = new URLSearchParams({
    code: googleCode,
-   device_fingerprint: `web-${Date.now()}`,
+   device_fingerprint: getDeviceFingerprint(), // 使用持久化的设备指纹
    device_name: navigator.userAgent.substring(0, 50),
  });

  await api.post(`/auth/oauth/google/code?${params.toString()}`);
};
```

---

## 修复验证

### 测试步骤

1. **清除 localStorage**（测试新设备场景）:
   ```javascript
   localStorage.clear();
   ```

2. **Google OAuth 登录**:
   - 访问 https://solacore.app
   - 点击 "使用 Google 登录"
   - 完成 OAuth 授权

3. **检查 Device Fingerprint**:
   ```javascript
   console.log('Device Fingerprint:', localStorage.getItem('solacore_device_fingerprint'));
   // 应该显示一个 UUID，例如: "a1b2c3d4-e5f6-..."
   ```

4. **创建 Session**:
   ```javascript
   // 在浏览器控制台
   fetch('https://api.solacore.app/sessions', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'X-CSRF-Token': '...',  // 从 cookie 获取
     },
     credentials: 'include',
     body: JSON.stringify({})
   })
   .then(r => r.json())
   .then(data => console.log('Session created:', data));
   // 应该成功返回 session_id
   ```

### 预期结果

- ✅ Google OAuth 登录成功
- ✅ Device 记录创建时使用持久 UUID
- ✅ 后续 API 请求使用相同的 UUID
- ✅ 创建 Session 成功（不再 403）

---

## 技术细节

### Device Fingerprint 生成策略

| 场景 | 策略 | 存储位置 |
|------|------|----------|
| 首次访问 | `crypto.randomUUID()` | localStorage |
| 后续访问 | 读取已存储的 UUID | localStorage |
| 服务端渲染 | 返回 "server-side-render" | N/A |

### 关键代码位置

| 文件 | 功能 | 修改状态 |
|------|------|----------|
| `solacore-web/lib/api.ts:17-32` | 生成和存储 device fingerprint | 无需修改 ✅ |
| `solacore-web/lib/api.ts:35-48` | 自动添加 X-Device-Fingerprint header | 无需修改 ✅ |
| `solacore-web/lib/auth.ts:11-21` | Google OAuth 登录 | **已修复** ✅ |
| `solacore-api/app/routers/sessions/create.py:71-80` | Device 验证逻辑 | 无需修改 ✅ |

---

## 其他登录方式验证

### 1. Email/Password 登录

**文件**: `solacore-web/app/(auth)/login/page.tsx`

```typescript
// 已使用 getDeviceFingerprint()，无需修改 ✅
const deviceFingerprint = getDeviceFingerprint();
const response = await fetch(`${API_BASE_URL}/auth/login`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRF-Token": csrfToken,
  },
  credentials: "include",
  body: JSON.stringify({
    email: email,
    password: password,
    device_fingerprint: deviceFingerprint,
  }),
});
```

### 2. Beta Login

**文件**: `solacore-web/lib/api.ts:70-91`

```typescript
// 已使用 getDeviceFingerprint()，无需修改 ✅
const betaLogin = async (): Promise<void> => {
  const fingerprint = getDeviceFingerprint();

  await api.post("/auth/beta-login", {
    device_fingerprint: fingerprint,
    device_name: "Web Browser",
  });
};
```

---

## 监控和预防

### 1. 添加前端日志

在 `solacore-web/lib/api.ts` 中：

```typescript
api.interceptors.request.use((config) => {
  const fingerprint = getDeviceFingerprint();
  config.headers["X-Device-Fingerprint"] = fingerprint;

  if (process.env.NODE_ENV === "development") {
    console.log("📤 [Request]", {
      url: config.url,
      method: config.method,
      fingerprint,  // 便于调试
    });
  }

  return config;
});
```

### 2. 后端错误增强

在返回 `DEVICE_NOT_FOUND` 错误时，可以添加更多上下文：

```python
if not device:
    raise HTTPException(
        status_code=403,
        detail={
            "error": "DEVICE_NOT_FOUND",
            "debug": {
                "user_id": str(current_user.id),
                "fingerprint_received": device_fingerprint,
                "registered_devices": [d.device_fingerprint for d in user_devices]
            } if settings.debug else None
        }
    )
```

### 3. 定期清理无效 Device

```sql
-- 清理超过 90 天未使用的设备
DELETE FROM devices
WHERE last_used_at < NOW() - INTERVAL '90 days';
```

---

## 相关文档

- **认证修复报告**: `docs/FRONTEND_AUTH_FIX.md`
- **测试完整报告**: `docs/AUTH_TEST_COMPLETE_REPORT.md`
- **浏览器测试指南**: `docs/BROWSER_AUTH_TEST.md`

---

## 总结

| 问题 | 影响 | 修复 |
|------|------|------|
| Device Fingerprint 不匹配 | Google OAuth 用户无法创建 Session | ✅ 已修复 |
| 临时 vs 持久 fingerprint | 后端验证失败 | ✅ 统一使用持久 UUID |
| 影响范围 | 仅 Google OAuth 登录 | ✅ Email 登录不受影响 |

**修复后**:
- ✅ 所有登录方式使用相同的 device fingerprint 生成逻辑
- ✅ 前端和后端 fingerprint 完全一致
- ✅ 用户可以正常创建 Session

---

**最后更新**: 2026-01-01
**修复者**: Claude + Gemini
