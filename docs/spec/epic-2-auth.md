# Epic 2: User Authentication System - Specification

> **Version**: 1.0
> **Created**: 2025-12-22
> **Status**: Draft
> **Depends On**: Epic 1 (Foundation)

---

## Overview

| Attribute | Value |
|-----------|-------|
| **Goal** | 完整的用户认证系统，支持邮箱注册、OAuth 登录、设备绑定和反滥用 |
| **Timeline** | Week 3-4 |
| **Stories** | 7 |
| **Priority** | P0 (Core) |

### Constitution Compliance

| Principle | How Addressed |
|-----------|---------------|
| **Mobile-First** | 所有 OAuth 流程使用 Expo AuthSession/Apple Authentication |
| **Privacy-First** | 密码 bcrypt 哈希，Token 安全存储，无明文日志 |
| **Single-Server** | 内存速率限制（TTLCache），无 Redis 依赖 |
| **Subscription-Gated** | 中间件链：Auth → Device → Subscription → RateLimit |
| **i18n-Ready** | 返回错误码，客户端翻译 |
| **Safety** | 登录限速防暴力破解 |

---

## Story 2.1: Email Registration & Login (Backend)

### User Story

> As a **user**,
> I want to **register and log in with my email and password**,
> so that **I can create an account and access my sessions**.

### Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-2.1.1 | `POST /auth/register` 创建用户，密码使用 bcrypt (cost=12) 哈希 | 数据库验证 password_hash 非明文 |
| AC-2.1.2 | `POST /auth/login` 验证凭证，返回 JWT tokens | curl 登录返回 access_token + refresh_token |
| AC-2.1.3 | Access token 1小时过期，Refresh token 30天过期 | 解码 JWT 验证 exp claim |
| AC-2.1.4 | 密码强度要求：最少8字符、1数字、1大写字母 | 注册弱密码返回 400 WEAK_PASSWORD |
| AC-2.1.5 | 邮箱唯一性验证，重复返回 `EMAIL_ALREADY_EXISTS` | 重复注册返回 409 |
| AC-2.1.6 | 登录限速：每分钟最多5次失败尝试 | 第6次失败返回 429 RATE_LIMITED |
| AC-2.1.7 | 注册自动创建 Free tier 订阅 | 数据库验证 subscriptions 表 |
| AC-2.1.8 | 单元测试覆盖所有 auth 端点 | pytest 通过 |

### Technical Notes

- 使用 `passlib[bcrypt]` 进行密码哈希
- JWT 使用 `python-jose` 或 `PyJWT`
- 密码验证使用正则：`^(?=.*[A-Z])(?=.*\d).{8,}$`

---

## Story 2.2: JWT Token Management

### User Story

> As a **user**,
> I want to **my session to stay active without frequent re-login**,
> so that **I have a seamless experience**.

### Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-2.2.1 | `POST /auth/refresh` 用 refresh token 换取新 access token | curl 返回新 access_token |
| AC-2.2.2 | Refresh token rotation：旧 token 换取新 token 后失效 | 重复使用旧 token 返回 401 |
| AC-2.2.3 | `POST /auth/logout` 使 refresh token 失效 | logout 后 refresh 返回 401 |
| AC-2.2.4 | Token 黑名单/会话表用于吊销 | active_sessions 表存储 token_hash |
| AC-2.2.5 | Auth 中间件验证 JWT 并提取用户信息 | 无效 token 返回 401 INVALID_TOKEN |
| AC-2.2.6 | 过期 token 返回 `TOKEN_EXPIRED`，无效返回 `INVALID_TOKEN` | 不同错误码区分 |

### Technical Notes

- access_token: 短期（1h），包含 user_id, email, tier
- refresh_token: 长期（30d），仅包含 session_id
- 使用 `active_sessions` 表跟踪有效会话

---

## Story 2.3: Google OAuth Integration

### User Story

> As a **user**,
> I want to **sign in with my Google account**,
> so that **I don't need to remember another password**.

### Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-2.3.1 | `POST /auth/oauth/google` 接受 Google ID token | 端点存在且可调用 |
| AC-2.3.2 | 使用 Google 公钥验证 token | 伪造 token 返回 401 |
| AC-2.3.3 | 新用户自动创建（auth_provider='google'） | 数据库验证 |
| AC-2.3.4 | 已存在邮箱用户自动关联 | 同一邮箱不创建重复用户 |
| AC-2.3.5 | 成功返回 JWT tokens | 返回格式与邮箱登录一致 |
| AC-2.3.6 | 兼容 Expo AuthSession | 移动端能完成完整流程 |

### Technical Notes

- 使用 `google-auth` 库验证 ID token
- Google Client ID 通过环境变量配置
- 验证 token 的 aud claim 匹配 Client ID

---

## Story 2.4: Apple Sign-In Integration

### User Story

> As a **user**,
> I want to **sign in with my Apple ID**,
> so that **I can use secure authentication on iOS**.

### Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-2.4.1 | `POST /auth/oauth/apple` 接受 Apple identity token | 端点存在且可调用 |
| AC-2.4.2 | 使用 Apple 公钥验证 token | 伪造 token 返回 401 |
| AC-2.4.3 | 处理 Apple Private Relay Email | 支持 @privaterelay.appleid.com |
| AC-2.4.4 | 新用户自动创建或关联已存在用户 | 同 Google OAuth 逻辑 |
| AC-2.4.5 | 成功返回 JWT tokens | 返回格式一致 |
| AC-2.4.6 | 兼容 expo-apple-authentication | iOS 端能完成流程 |

### Technical Notes

- Apple 的 identity token 是 JWT，使用 RS256 签名
- 需要获取 Apple 公钥：https://appleid.apple.com/auth/keys
- Apple 首次登录才提供邮箱，需要持久化

---

## Story 2.5: Device Registration & Binding

### User Story

> As the **system**,
> I want to **track and limit devices per user**,
> so that **account sharing is prevented**.

### Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-2.5.1 | 所有 auth 端点要求 `X-Device-Fingerprint` header | 无 header 返回 400 |
| AC-2.5.2 | 客户端生成设备指纹（vendor ID + install ID） | 移动端实现 |
| AC-2.5.3 | 首次登录自动创建设备记录 | devices 表有记录 |
| AC-2.5.4 | 设备限制：Free=1, Standard=2, Pro=3 | 超限返回 403 DEVICE_LIMIT_REACHED |
| AC-2.5.5 | `GET /auth/devices` 列出用户设备 | 返回设备列表 |
| AC-2.5.6 | `DELETE /auth/devices/{id}` 解绑设备（每天限1次） | 解绑后可绑定新设备 |
| AC-2.5.7 | 设备超限返回明确错误信息 | 包含当前设备数和限制 |

### Technical Notes

- 设备指纹：iOS 使用 identifierForVendor，Android 使用 ANDROID_ID
- 设备表字段：id, user_id, device_fingerprint, device_name, platform, last_active_at

---

## Story 2.6: Auth UI (Mobile)

### User Story

> As a **user**,
> I want to **a clean login and signup experience in the app**,
> so that **I can easily create an account or sign in**.

### Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-2.6.1 | 登录页：邮箱/密码输入框 + 登录按钮 | UI 存在 |
| AC-2.6.2 | 注册页：邮箱/密码/确认密码 | UI 存在 |
| AC-2.6.3 | Google Sign-In 按钮（使用 Expo AuthSession） | 点击触发 OAuth 流程 |
| AC-2.6.4 | Apple Sign-In 按钮（仅 iOS，使用 expo-apple-authentication） | iOS 端可见且可用 |
| AC-2.6.5 | 表单验证 + 内联错误提示 | 输入无效时显示错误 |
| AC-2.6.6 | API 调用时显示 Loading 状态 | 按钮禁用 + spinner |
| AC-2.6.7 | Token 使用 expo-secure-store 安全存储 | 不使用 AsyncStorage |
| AC-2.6.8 | 有效 refresh token 时自动登录 | 跳过登录页 |

### Technical Notes

- 使用 Zustand 管理 auth 状态
- expo-secure-store 存储 access_token 和 refresh_token
- 表单使用 react-hook-form 或类似库

---

## Story 2.7: Password Reset Flow

### User Story

> As a **user**,
> I want to **reset my password if I forget it**,
> so that **I can regain access to my account**.

### Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-2.7.1 | `POST /auth/forgot-password` 发送重置邮件 | 邮件发送成功 |
| AC-2.7.2 | 重置 token 1小时有效 | 过期 token 返回 400 |
| AC-2.7.3 | `POST /auth/reset-password` 使用 token 设置新密码 | 新密码可登录 |
| AC-2.7.4 | 登录页显示 "Forgot Password" 链接 | UI 存在 |
| AC-2.7.5 | 支持重置链接 Deep Link | 点击邮件链接打开 App |
| AC-2.7.6 | 邮件模板专业且品牌化 | 包含 logo 和清晰指引 |

### Technical Notes

- 重置 token 使用 secrets.token_urlsafe(32)
- 邮件使用 SendGrid/Mailgun/Resend
- Deep Link 格式：clarity://reset-password?token=xxx

---

## API Endpoints Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | 邮箱注册 | ❌ |
| POST | `/auth/login` | 邮箱登录 | ❌ |
| POST | `/auth/oauth/google` | Google OAuth | ❌ |
| POST | `/auth/oauth/apple` | Apple Sign-In | ❌ |
| POST | `/auth/refresh` | 刷新 token | ❌ (需 refresh_token) |
| POST | `/auth/logout` | 登出 | ✅ |
| POST | `/auth/forgot-password` | 请求重置密码 | ❌ |
| POST | `/auth/reset-password` | 重置密码 | ❌ (需 reset_token) |
| GET | `/auth/devices` | 列出设备 | ✅ |
| DELETE | `/auth/devices/{id}` | 解绑设备 | ✅ |
| GET | `/auth/me` | 获取当前用户 | ✅ |

---

## Data Models

### User (Extended)

```python
class User(Base):
    __tablename__ = "users"

    id: UUID
    email: str  # unique, indexed
    password_hash: Optional[str]  # NULL for OAuth users
    auth_provider: str = "email"  # email/google/apple
    auth_provider_id: Optional[str]  # OAuth user ID
    locale: str = "en"
    created_at: datetime
    updated_at: datetime
```

### Device

```python
class Device(Base):
    __tablename__ = "devices"

    id: UUID
    user_id: UUID  # FK -> users
    device_fingerprint: str  # unique per user
    device_name: str  # "iPhone 15 Pro"
    platform: str  # ios/android
    last_active_at: datetime
    is_active: bool = True
    created_at: datetime
```

### ActiveSession

```python
class ActiveSession(Base):
    __tablename__ = "active_sessions"

    id: UUID
    user_id: UUID  # FK -> users
    device_id: UUID  # FK -> devices
    token_hash: str  # hashed refresh token
    expires_at: datetime
    created_at: datetime
```

### PasswordReset

```python
class PasswordReset(Base):
    __tablename__ = "password_resets"

    id: UUID
    user_id: UUID  # FK -> users
    token_hash: str  # hashed reset token
    expires_at: datetime
    used_at: Optional[datetime]
    created_at: datetime
```

---

## Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `EMAIL_ALREADY_EXISTS` | 409 | 邮箱已注册 |
| `WEAK_PASSWORD` | 400 | 密码不符合要求 |
| `INVALID_CREDENTIALS` | 401 | 邮箱或密码错误 |
| `INVALID_TOKEN` | 401 | Token 无效 |
| `TOKEN_EXPIRED` | 401 | Token 已过期 |
| `RATE_LIMITED` | 429 | 请求过于频繁 |
| `DEVICE_FINGERPRINT_REQUIRED` | 400 | 缺少设备指纹 |
| `DEVICE_LIMIT_REACHED` | 403 | 设备数量达到上限 |
| `DEVICE_BOUND_TO_OTHER` | 403 | 设备已绑定其他账号 |
| `DEVICE_REMOVAL_LIMIT` | 429 | 每天只能解绑1个设备 |
| `OAUTH_INVALID_TOKEN` | 401 | OAuth token 验证失败 |
| `RESET_TOKEN_INVALID` | 400 | 重置 token 无效 |
| `RESET_TOKEN_EXPIRED` | 400 | 重置 token 已过期 |

---

## Security Requirements

| Requirement | Implementation |
|-------------|----------------|
| 密码哈希 | bcrypt, cost factor 12 |
| JWT 签名 | HS256 with JWT_SECRET |
| Token 存储 | expo-secure-store (mobile) |
| 传输加密 | HTTPS only |
| 登录限速 | 5次/分钟 per IP/email |
| OAuth 验证 | 验证 iss, aud, exp claims |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| 注册→登录转化率 | > 80% |
| OAuth 使用率 | > 50% |
| 登录失败率 | < 5% |
| Token 刷新成功率 | > 99% |

---

## Change Log

| Date | Version | Description |
|------|---------|-------------|
| 2025-12-22 | 1.0 | Initial specification |
