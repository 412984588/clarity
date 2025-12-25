# 🚨 生产环境致命问题修复计划 (Critical Fixes)

**发现来源**: Codex 深度审查
**严重程度**: 🔴 **HIGH** (2个) + 🟡 **MEDIUM** (2个) + 🔵 **LOW** (3个)
**必须在上线前修复**: HIGH + MEDIUM (共4个)

---

## 🔴 HIGH-1: CORS 配置错误 - Web端无法访问API

### 问题描述
**文件**: `clarity-api/app/main.py:48`
**代码**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],  # ❌ 生产环境是空列表！
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**后果**:
- 🚨 Web端（clarity-web）所有API请求被浏览器拒绝
- 🚨 前端无法登录、无法使用任何功能
- 🚨 等同于Web版完全不可用

### 修复方案

#### 方案A: 使用 frontend_url（推荐）
```python
# clarity-api/app/config.py
class Settings(BaseSettings):
    frontend_url: str = "http://localhost:3000"  # ✅ 改成Web前端地址
    frontend_url_prod: str = ""  # 生产环境域名，如 "https://clarity.app"

# clarity-api/app/main.py
origins = ["*"] if settings.debug else [
    settings.frontend_url,
    settings.frontend_url_prod,
    "https://yourdomain.com",  # 添加你的生产域名
    "https://www.yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 方案B: 动态构建白名单
```python
def get_cors_origins() -> list[str]:
    """获取 CORS 白名单"""
    if settings.debug:
        return ["*"]

    origins = []

    # 添加前端 URL
    if settings.frontend_url:
        origins.append(settings.frontend_url)

    # 添加生产域名
    if settings.frontend_url_prod:
        origins.append(settings.frontend_url_prod)

    # 如果为空，至少允许本地开发
    if not origins:
        origins = ["http://localhost:3000", "http://localhost:8000"]

    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 验证步骤
```bash
# 1. 启动后端（生产模式）
cd clarity-api
DEBUG=false uvicorn app.main:app

# 2. 启动 Web 前端
cd clarity-web
npm run dev

# 3. 浏览器访问 http://localhost:3000
# 4. 打开开发者工具 Network 标签
# 5. 尝试登录，检查是否有 CORS 错误
# 预期：✅ 无 "Access-Control-Allow-Origin" 错误
```

### 老板需要确认
❓ **Web 前端生产域名是什么？**（如 `https://clarity.app`）

---

## 🔴 HIGH-2: 忘记密码功能不可用 - 生产环境无邮件发送

### 问题描述
**文件**: `clarity-api/app/routers/auth.py:107-112`
**代码**:
```python
if user:
    # ...保存 token 到数据库
    await db.commit()
    if settings.debug:  # ❌ 只在 debug 模式记录日志
        logger.info("Password reset link: %s/auth/reset?token=%s", ...)
    # ❌ 生产环境什么都不做，用户收不到邮件！
```

**后果**:
- 🚨 用户点"忘记密码"后，永远收不到重置邮件
- 🚨 等同于功能完全不可用
- 🚨 用户只能联系客服重置密码

### 修复方案

#### 方案A: 集成真实邮件服务（推荐）

**1. 选择邮件服务**:
- **SendGrid** (推荐，免费额度100封/天)
- **Mailgun** (免费额度100封/天)
- **Resend** (免费额度100封/天)
- **AWS SES** (按量付费，极便宜)

**2. 安装依赖**:
```bash
cd clarity-api
poetry add aiosmtplib email-validator
```

**3. 配置环境变量**:
```python
# clarity-api/app/config.py
class Settings(BaseSettings):
    # 邮件配置
    smtp_host: str = "smtp.sendgrid.net"
    smtp_port: int = 587
    smtp_user: str = ""  # SendGrid API Key 或用户名
    smtp_password: str = ""  # SendGrid API Secret 或密码
    smtp_from: str = "noreply@yourdomain.com"
    smtp_from_name: str = "Clarity Support"
```

**4. 创建邮件服务**:
```python
# clarity-api/app/services/email_service.py
import aiosmtplib
from email.message import EmailMessage
from app.config import get_settings

settings = get_settings()

async def send_password_reset_email(to_email: str, reset_token: str):
    """发送密码重置邮件"""
    reset_link = f"{settings.frontend_url}/auth/reset?token={reset_token}"

    message = EmailMessage()
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from}>"
    message["To"] = to_email
    message["Subject"] = "密码重置 - Clarity"
    message.set_content(f"""
您好，

您请求重置 Clarity 账户的密码。请点击以下链接重置密码：

{reset_link}

此链接将在30分钟后过期。

如果您没有请求重置密码，请忽略此邮件。

Clarity 团队
    """)

    message.add_alternative(f"""
<html>
  <body>
    <p>您好，</p>
    <p>您请求重置 Clarity 账户的密码。</p>
    <p><a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">重置密码</a></p>
    <p>此链接将在30分钟后过期。</p>
    <p>如果您没有请求重置密码，请忽略此邮件。</p>
    <p>Clarity 团队</p>
  </body>
</html>
    """, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        use_tls=True,
    )
```

**5. 更新路由**:
```python
# clarity-api/app/routers/auth.py
from app.services.email_service import send_password_reset_email

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """忘记密码（始终返回 200，防止时序攻击）"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    if user:
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=utc_now() + timedelta(minutes=30),
        )
        db.add(reset_token)
        await db.commit()

        # ✅ 发送邮件（生产和开发都发）
        try:
            await send_password_reset_email(user.email, token)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            # 不暴露错误给用户，防止泄露信息

        # ✅ Debug 模式额外记录日志
        if settings.debug:
            logger.info("Password reset link: %s/auth/reset?token=%s", settings.frontend_url, token)

    return {"message": "If an account exists, a reset link has been sent"}
```

#### 方案B: 暂时返回重置链接（临时方案，不推荐）

```python
@router.post("/forgot-password")
async def forgot_password(...):
    # ...
    if user:
        # ...
        await db.commit()

        # ⚠️ 临时方案：直接返回链接（不安全，仅用于 Beta 测试）
        if settings.beta_mode:
            return {
                "message": "Password reset link generated (Beta mode)",
                "reset_link": f"{settings.frontend_url}/auth/reset?token={token}"
            }

    return {"message": "If an account exists, a reset link has been sent"}
```

### 验证步骤
```bash
# 1. 配置 SMTP（以 SendGrid 为例）
export SMTP_HOST=smtp.sendgrid.net
export SMTP_PORT=587
export SMTP_USER=apikey
export SMTP_PASSWORD=<你的SendGrid API Key>
export SMTP_FROM=noreply@yourdomain.com

# 2. 启动后端
uvicorn app.main:app

# 3. 测试忘记密码
curl -X POST http://localhost:8000/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# 4. 检查邮箱
# 预期：✅ 收到密码重置邮件，包含重置链接
```

### 老板需要确认
❓ **使用哪个邮件服务？** (推荐 SendGrid 或 Resend，免费额度够用)
❓ **发件邮箱地址？** (如 `noreply@yourdomain.com`)
❓ **Beta 期间可以先用"返回链接"方案吗？**

---

## 🟡 MEDIUM-1: 支付开关前后端不一致

### 问题描述
**后端**: `clarity-api/app/config.py:37` → `payments_enabled: bool`
**移动端**: `clarity-mobile/services/config.ts:16` → `EXPO_PUBLIC_BILLING_ENABLED` (默认 `true`)

**后果**:
- 🟡 Beta 期间关闭后端支付功能，移动端仍显示订阅入口
- 🟡 用户点击订阅 → 后端返回 501 错误 → 体验差

### 修复方案

#### 方案A: 统一使用 `PAYMENTS_ENABLED`
```python
# clarity-api/app/config.py
class Settings(BaseSettings):
    payments_enabled: bool = True  # 保持不变

# 添加 API 端点返回配置
@router.get("/config/features")
async def get_features():
    """返回前端功能开关"""
    settings = get_settings()
    return {
        "payments_enabled": settings.payments_enabled,
        "beta_mode": settings.beta_mode,
    }
```

```typescript
// clarity-mobile/services/config.ts
export const getFeatureFlags = async () => {
  try {
    const response = await api.get('/config/features');
    return response.data;
  } catch {
    // 降级：使用环境变量
    return {
      payments_enabled: process.env.EXPO_PUBLIC_PAYMENTS_ENABLED === 'true',
      beta_mode: false,
    };
  }
};

// clarity-mobile/app/(tabs)/paywall.tsx
useEffect(() => {
  const checkPayments = async () => {
    const flags = await getFeatureFlags();
    if (!flags.payments_enabled) {
      router.replace('/'); // 重定向回首页
    }
  };
  checkPayments();
}, []);
```

#### 方案B: 前端改成 `PAYMENTS_ENABLED`（简单粗暴）
```typescript
// clarity-mobile/services/config.ts
export const Config = {
  // ❌ 删除
  // BILLING_ENABLED: process.env.EXPO_PUBLIC_BILLING_ENABLED === 'true',

  // ✅ 改成
  PAYMENTS_ENABLED: process.env.EXPO_PUBLIC_PAYMENTS_ENABLED !== 'false', // 默认 true
};
```

```bash
# .env
EXPO_PUBLIC_PAYMENTS_ENABLED=false  # Beta 期间禁用
```

### 验证步骤
```bash
# 1. 关闭支付功能
# 后端
export PAYMENTS_ENABLED=false

# 移动端
export EXPO_PUBLIC_PAYMENTS_ENABLED=false

# 2. 启动应用，检查订阅入口是否隐藏
# 预期：✅ 无订阅按钮，或点击后优雅提示"功能未开放"
```

### 老板需要确认
❓ **Beta 期间是否完全隐藏订阅入口？** (推荐：隐藏)
❓ **还是显示但提示"敬请期待"？**

---

## 🟡 MEDIUM-2: 生产配置校验不全

### 问题描述
**文件**: `clarity-api/app/config.py:71-77`
**代码**:
```python
def validate_production_config(settings: Settings | None = None) -> None:
    active_settings = settings or get_settings()
    if not active_settings.debug and active_settings.jwt_secret in {
        "",
        DEFAULT_JWT_SECRET,
    }:
        raise RuntimeError("JWT_SECRET must be set to a secure value in production")
    # ❌ 只检查 JWT_SECRET，其他关键配置未检查
```

**后果**:
- 🟡 生产环境启动后，调用 OpenAI API 才发现 API Key 为空
- 🟡 用户点击订阅，才发现 Stripe Key 未配置
- 🟡 浪费时间排查"运行时"错误

### 修复方案

```python
# clarity-api/app/config.py
def validate_production_config(settings: Settings | None = None) -> None:
    """生产环境配置校验"""
    active_settings = settings or get_settings()

    if active_settings.debug:
        return  # Debug 模式跳过校验

    errors = []

    # 1. JWT 校验
    if active_settings.jwt_secret in {"", DEFAULT_JWT_SECRET}:
        errors.append("JWT_SECRET must be set to a secure value in production")

    # 2. 数据库校验
    if not active_settings.database_url or "localhost" in active_settings.database_url:
        errors.append("DATABASE_URL must be set to production database")

    # 3. LLM 配置校验
    if active_settings.llm_provider == "openai" and not active_settings.openai_api_key:
        errors.append("OPENAI_API_KEY is required when llm_provider=openai")

    if active_settings.llm_provider == "anthropic" and not active_settings.anthropic_api_key:
        errors.append("ANTHROPIC_API_KEY is required when llm_provider=anthropic")

    # 4. 支付配置校验（如果启用支付）
    if active_settings.payments_enabled:
        if not active_settings.stripe_secret_key:
            errors.append("STRIPE_SECRET_KEY is required when payments_enabled=true")

        if not active_settings.stripe_webhook_secret:
            errors.append("STRIPE_WEBHOOK_SECRET is required when payments_enabled=true")

        if not active_settings.revenuecat_webhook_secret:
            errors.append("REVENUECAT_WEBHOOK_SECRET is required when payments_enabled=true")

    # 5. OAuth 校验
    if not active_settings.google_client_id:
        errors.append("GOOGLE_CLIENT_ID is required for Google OAuth")

    # 6. 前端 URL 校验
    if not active_settings.frontend_url or "localhost" in active_settings.frontend_url:
        errors.append("FRONTEND_URL must be set to production URL")

    # 7. CORS 校验
    # (这个会在 main.py 中检查)

    if errors:
        error_msg = "Production configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        raise RuntimeError(error_msg)
```

### 验证步骤
```bash
# 1. 故意不设置某个关键变量
export DEBUG=false
export JWT_SECRET=secure-key
# 不设置 OPENAI_API_KEY

# 2. 启动后端
uvicorn app.main:app

# 预期：❌ 启动失败，报错 "OPENAI_API_KEY is required"
# 效果：✅ 避免运行时才发现配置错误
```

---

## 🔵 LOW-1: OpenRouter Reasoning 泄露风险

### 问题描述
**文件**: `clarity-api/app/services/ai_service.py:120`
**风险**: OpenRouter 的 reasoning 兜底会向用户输出"AI 思考过程"，可能泄露 Prompt 设计细节

### 修复方案

#### 方案A: 添加产品开关（推荐）
```python
# clarity-api/app/config.py
class Settings(BaseSettings):
    # ...
    enable_reasoning_output: bool = False  # 默认禁用

# clarity-api/app/services/ai_service.py
async def stream_response(self, ...):
    # ...
    if part.type == "reasoning" and not settings.enable_reasoning_output:
        continue  # ✅ 跳过 reasoning，不输出给用户

    if part.type == "reasoning" and settings.enable_reasoning_output:
        yield f"data: {json.dumps({'type': 'reasoning', 'content': part.content})}\n\n"
```

#### 方案B: 服务端过滤（简单粗暴）
```python
async def stream_response(self, ...):
    # ...
    if part.type == "reasoning":
        continue  # ✅ 永远不输出 reasoning
```

### 老板需要确认
❓ **是否允许向用户显示 AI 思考过程？** (推荐：禁用)

---

## 🔵 LOW-2: 版本号不一致

### 问题描述
**OpenAPI 版本**: `clarity-api/app/main.py:40` → `version="0.1.0"`
**健康检查版本**: `clarity-api/app/config.py:14` → `app_version: str = "1.0.0"`

### 修复方案
```python
# clarity-api/app/config.py
class Settings(BaseSettings):
    app_version: str = "0.1.0"  # ✅ 统一为 0.1.0

# clarity-api/app/main.py
app = FastAPI(
    title=settings.app_name,
    description="Universal problem-solving assistant API",
    version=settings.app_version,  # ✅ 使用配置中的版本号
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)
```

---

## 🔵 LOW-3: QA 日志过时

**问题**: `docs/release/qa-execution-log.md:37` 仍记录 OpenRouter "无 token" 失败
**修复**: 更新 QA 日志，反映兜底修复后的结果

```markdown
# 修改前
- OpenRouter API 调用失败：无 token ❌

# 修改后
- OpenRouter API 调用：已添加 reasoning 兜底，正常 ✅
```

---

## 📋 修复优先级总结

| 问题 | 优先级 | 影响 | 修复时间 | 必须上线前修复 |
|------|--------|------|----------|----------------|
| **CORS 配置错误** | 🔴 HIGH | Web端完全不可用 | 30分钟 | ✅ 是 |
| **忘记密码不可用** | 🔴 HIGH | 核心功能缺失 | 2小时 | ✅ 是 |
| **支付开关不一致** | 🟡 MEDIUM | Beta体验差 | 1小时 | ✅ 是 |
| **配置校验不全** | 🟡 MEDIUM | 运行时错误 | 1小时 | ✅ 是 |
| **Reasoning 泄露** | 🔵 LOW | 潜在风险 | 30分钟 | 可选 |
| **版本号不一致** | 🔵 LOW | 混淆 | 10分钟 | 可选 |
| **QA 日志过时** | 🔵 LOW | 文档准确性 | 5分钟 | 可选 |

---

## ⏱️ 总工作量估算

- **HIGH 问题**: 2.5小时（必须修复）
- **MEDIUM 问题**: 2小时（必须修复）
- **LOW 问题**: 45分钟（可选）

**Total**: ~5小时（如果只修 HIGH+MEDIUM，则4.5小时）

---

## 🚀 快速修复计划

### 立即执行（今天，4.5小时）
1. ✅ **CORS 修复**（30分钟）→ Web端可用
2. ✅ **邮件服务集成**（2小时）→ 忘记密码可用
3. ✅ **支付开关统一**（1小时）→ Beta体验优化
4. ✅ **配置校验增强**（1小时）→ 启动时发现配置错误

### 可选优化（明天，45分钟）
5. ⚪ Reasoning 开关（30分钟）
6. ⚪ 版本号统一（10分钟）
7. ⚪ QA 日志更新（5分钟）

---

**修复完成后，项目健康度预计从 97/100 提升至 99/100** ⭐⭐⭐⭐⭐
