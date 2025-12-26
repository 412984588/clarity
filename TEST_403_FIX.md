# 403 错误修复测试指南

## 问题诊断结果

### 根本原因
**sendMessage 函数使用原生 fetch API，绕过了 axios 拦截器，导致没有自动添加 `X-Device-Fingerprint` 请求头**

### 修复内容
1. ✅ 导出 `getDeviceFingerprint` 函数
2. ✅ 在 `sendMessage` 中手动添加设备指纹到请求头
3. ✅ 添加详细的调试日志

---

## 测试步骤

### 前置条件
```bash
cd solacore-web
npm run dev
```

### 测试流程

#### 1. 清除所有本地数据（模拟用户清除 cookies）
打开浏览器开发者工具：
1. Application → Storage → Clear site data
2. 或手动清除：
   - Cookies → 删除所有
   - Local Storage → 删除所有

#### 2. 访问应用并观察日志
```
http://localhost:3000/solve
```

#### 3. 预期日志输出
```
🔐 [Beta Login] 开始登录
  fingerprint: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  device_name: "Web Browser"
  timestamp: "2025-12-26T..."

📤 [Request]
  url: "/auth/beta-login"
  method: "post"
  fingerprint: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

✅ [Beta Login] 登录成功
  fingerprint: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

🆕 [Create Session] 开始创建会话
  fingerprint: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  timestamp: "2025-12-26T..."

📤 [Request]
  url: "/sessions"
  method: "post"
  fingerprint: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

✅ [Create Session] 会话创建成功
  sessionId: "session-uuid"
```

#### 4. 发送消息并验证
输入任意消息，点击发送，观察日志：

```
💬 [Send Message] 发送消息
  sessionId: "session-uuid"
  fingerprint: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  contentLength: 10
  timestamp: "2025-12-26T..."
```

#### 5. 验证成功标准
- ✅ 所有日志中的 `fingerprint` 必须一致
- ✅ 没有 403 错误
- ✅ 消息成功发送并收到回复

---

## 后端验证（可选）

如果前端测试通过但仍有问题，检查后端日志：

```bash
cd solacore-api
tail -f logs/app.log | grep -E "(device_fingerprint|403|DEVICE_NOT_FOUND)"
```

### 预期后端日志
```
[INFO] Beta login: user_id=xxx, device_fingerprint=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
[INFO] Device created/found: device_id=xxx
[INFO] Session created: session_id=xxx, device_id=xxx
[INFO] Message received: session_id=xxx, device_fingerprint=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 异常日志（如果仍有问题）
```
[ERROR] Device not found: device_fingerprint=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
[ERROR] 403 DEVICE_NOT_FOUND
```

---

## 常见问题排查

### Q1: 日志显示 fingerprint 不一致
**原因**：localStorage 被清除但没有重新生成
**解决**：刷新页面，确保 `getDeviceFingerprint()` 重新生成

### Q2: 仍然出现 403 错误
**检查项**：
1. 浏览器控制台 → Network → 查看请求头是否包含 `X-Device-Fingerprint`
2. 确认后端日志中的设备指纹与前端一致
3. 检查后端数据库 `devices` 表是否存在该设备记录

### Q3: Beta 登录成功但创建 session 失败
**原因**：设备创建异步延迟
**解决**：在 Beta 登录后等待 1 秒再创建 session（已在代码中处理）

---

## curl 模拟测试（高级）

### 1. Beta 登录
```bash
FINGERPRINT=$(uuidgen)
curl -v -X POST http://localhost:8000/auth/beta-login \
  -H "Content-Type: application/json" \
  -d "{\"device_fingerprint\": \"$FINGERPRINT\", \"device_name\": \"curl-test\"}" \
  -c cookies.txt
```

### 2. 创建 Session
```bash
curl -v -X POST http://localhost:8000/sessions \
  -H "X-Device-Fingerprint: $FINGERPRINT" \
  -b cookies.txt \
  -c cookies.txt
```

### 3. 发送消息
```bash
SESSION_ID="<从步骤2获取>"
curl -v -X POST http://localhost:8000/sessions/$SESSION_ID/message \
  -H "Content-Type: application/json" \
  -H "X-Device-Fingerprint: $FINGERPRINT" \
  -H "Accept: text/event-stream" \
  -d '{"content": "test message"}' \
  -b cookies.txt
```

### 预期结果
- ✅ 所有请求返回 200/201
- ✅ 没有 403 错误
- ✅ Session 创建成功
- ✅ 消息发送成功

---

## 修复文件清单

1. `/solacore-web/lib/api.ts` - 导出 `getDeviceFingerprint`，添加调试日志
2. `/solacore-web/lib/session-api.ts` - 修复 `sendMessage`，添加调试日志
3. `/solacore-web/lib/debug-helpers.ts` - 新增调试工具（未使用，备用）

---

## 回滚方案

如果修复引入新问题，执行：
```bash
cd /Users/zhimingdeng/Documents/claude/clarity
git diff HEAD~1 solacore-web/lib/api.ts solacore-web/lib/session-api.ts
git checkout HEAD~1 -- solacore-web/lib/api.ts solacore-web/lib/session-api.ts
```
