# Domain & Hosting Setup Guide

**Version**: 1.0
**Last Updated**: 2025-12-24
**Purpose**: 解除生产阻塞项 - 域名与托管配置

---

## Purpose & Scope

本指南帮助完成 Solacore 生产环境的 **域名注册** 和 **托管服务配置**，是生产部署的关键前置步骤。

**解除的阻塞项**:
- ✅ Domain 配置（api.solacore.app）
- ✅ Hosting Provider 选择与配置
- ✅ PostgreSQL 托管数据库配置
- ✅ SSL/TLS 证书自动化
- ✅ DNS 记录配置

**不包含**:
- ❌ 代码部署命令（见 PROD_DEPLOY.md）
- ❌ 数据库迁移脚本（见 DATABASE_MIGRATION.md）
- ❌ CI/CD 流水线配置（见 .github/workflows/）

---

## Decisions Needed

在开始前，需要做出以下决策：

### 1. Domain Decision

| 选项 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| **solacore.app** | 简短、品牌一致 | 可能已被注册或价格高 | ⭐ 优先 |
| **solacore.io** | 技术感强 | 稍长 | ✅ 备选 |
| **solacore.co** | 简洁、专业 | 可能价格高 | ✅ 备选 |
| **usesolacore.com** | .com 域名、易记 | 稍长 | ✅ 备选 |

**Decision**: [ ] 选择域名：`__________`

---

### 2. Domain Registrar Decision

| 服务商 | 年费（约） | 优点 | 缺点 | 推荐 |
|--------|-----------|------|------|------|
| **Namecheap** | $10-15 | 便宜、界面简洁、支持支付宝 | DNS 速度一般 | ⭐ 推荐 |
| **Cloudflare Registrar** | $8-12 | 成本价、无隐藏费用、CDN 集成 | 需先有 Cloudflare 账号 | ⭐ 推荐 |
| **GoDaddy** | $15-20 | 知名度高、客服好 | 价格略贵、续费涨价 | ✅ 可选 |
| **Google Domains** | $12-18 | 与 Google Cloud 集成 | 已被 Squarespace 收购 | ⚠️ 谨慎 |

**Decision**: [ ] 选择注册商：`__________`

---

### 3. Hosting Provider Decision

| 服务商 | 免费额度 | 月费（约） | 优点 | 缺点 | 推荐 |
|--------|---------|-----------|------|------|------|
| **Vercel** | 有 | $0-20 | 零配置、自动 SSL、性能极佳 | 不适合长运行任务 | ⭐ 推荐（前端+API） |
| **Railway** | $5 免费额度 | $5-20 | 一键部署、PostgreSQL 内置、简单 | 新平台、生态少 | ⭐ 推荐（全栈） |
| **Fly.io** | $5 免费额度 | $0-15 | 全球部署、Docker 支持、灵活 | 配置稍复杂 | ✅ 可选（高级用户） |
| **Render** | 有 | $0-25 | 类似 Heroku、易用 | 冷启动慢 | ✅ 可选 |

**Decision**: [ ] 选择托管商：`__________`

---

### 4. PostgreSQL Hosting Decision

| 服务商 | 免费额度 | 月费（约） | 优点 | 缺点 | 推荐 |
|--------|---------|-----------|------|------|------|
| **Neon** | 0.5GB 免费 | $0-19 | Serverless、自动扩缩容、备份 | 新平台 | ⭐ 推荐 |
| **Supabase** | 500MB 免费 | $0-25 | 开源、RESTful API、实时订阅 | 功能复杂（如不需要额外功能） | ⭐ 推荐 |
| **Railway PostgreSQL** | 包含在 Railway 计划 | $5-20 | 与 Railway 应用一体化 | 与 Railway 绑定 | ✅ 推荐（如选 Railway） |
| **AWS RDS** | 无 | $15-50+ | 企业级、高可用 | 配置复杂、价格高 | ⚠️ 仅大规模 |

**Decision**: [ ] 选择数据库托管商：`__________`

---

## Inputs Required

完成以下信息准备，确保注册流程顺畅：

### For Domain Registration

| 信息项 | 说明 | 示例 |
|--------|------|------|
| **注册人姓名** | 个人或公司法人姓名 | John Doe / Solacore Inc. |
| **注册邮箱** | 用于接收域名通知 | admin@example.com |
| **联系地址** | 完整邮寄地址 | 123 Main St, San Francisco, CA 94103, USA |
| **联系电话** | 带国际区号 | +1-555-123-4567 |
| **付款方式** | 信用卡或支付宝 | Visa / Mastercard / Alipay |

**Privacy Protection**: ☑️ 建议启用 WHOIS Privacy（隐藏个人信息）

---

### For Hosting Provider

| 信息项 | 说明 | 示例 |
|--------|------|------|
| **支付方式** | 信用卡（大多数平台必需） | Visa / Mastercard |
| **GitHub 账号** | 用于 OAuth 登录和仓库授权 | github.com/your-username |
| **项目仓库** | Solacore 代码仓库 URL | github.com/your-org/solacore |
| **环境变量** | 见 ENV_VARIABLES.md | DATABASE_URL, JWT_SECRET, etc. |

---

### For PostgreSQL Hosting

| 信息项 | 说明 | 示例 |
|--------|------|------|
| **数据库名称** | 生产数据库名 | solacore_production |
| **区域选择** | 就近用户位置 | US West (Oregon) / Asia Pacific (Singapore) |
| **备份策略** | 自动备份频率 | 每日备份，保留 7 天 |

---

## Step-by-Step Setup

### Phase 1: Domain Registration

**预计时间**: 15-30 分钟

#### Step 1.1: 选择并购买域名

1. 访问所选注册商网站（Namecheap / Cloudflare / GoDaddy）
2. 搜索域名可用性（如 `solacore.app`）
3. 如域名不可用，尝试备选方案（solacore.io / usesolacore.com）
4. 添加到购物车，选择注册年限（推荐 1 年起）
5. 启用 **WHOIS Privacy Protection**（隐私保护）
6. 完成支付

**⏱️ 生效时间**: 即时（DNS 传播需 5-30 分钟）

---

#### Step 1.2: 配置 Nameservers

**如果使用 Cloudflare 作为 DNS 提供商**（推荐）:
1. 注册 Cloudflare 账号（cloudflare.com）
2. 添加站点（Add a Site），输入域名
3. Cloudflare 会显示 2 个 Nameserver 地址（如 `lisa.ns.cloudflare.com`）
4. 回到域名注册商，修改 Nameservers 为 Cloudflare 提供的地址
5. 等待 DNS 传播（5 分钟 - 48 小时，通常 30 分钟内完成）

**如果直接使用注册商 DNS**:
1. 保持默认 Nameservers 不变
2. 后续在注册商控制面板配置 DNS 记录

---

### Phase 2: Hosting Provider Setup

**预计时间**: 20-40 分钟

#### Step 2.1: 创建 Hosting 账号

1. 访问所选托管商网站（Vercel / Railway / Fly.io）
2. 使用 GitHub 账号 OAuth 登录
3. 连接 GitHub 仓库（`solacore` 后端仓库）
4. 授权读取代码和 Webhooks 权限

---

#### Step 2.2: 创建生产项目

**For Vercel**:
1. 点击 "New Project"
2. 选择 `solacore-backend` 仓库
3. Framework Preset: **Other** (FastAPI 不在预设中)
4. Build Command: 留空（Docker 部署）或 `pip install -r requirements.txt`
5. Output Directory: 留空
6. 点击 "Deploy"

**For Railway**:
1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择 `solacore-backend` 仓库
4. Railway 会自动检测 Python 项目
5. 添加 PostgreSQL Database（点击 "+ New" → "Database" → "PostgreSQL"）
6. 点击 "Deploy"

**For Fly.io**:
1. 创建新应用：访问 fly.io/apps
2. 选择 "Launch a new app"
3. 连接 GitHub 仓库或上传 `fly.toml` 配置
4. 选择区域（推荐就近用户位置）
5. 点击 "Deploy"

---

#### Step 2.3: 配置环境变量

**⚠️ 关键步骤**：在托管平台配置以下环境变量（详见 `docs/ENV_VARIABLES.md`）:

**必需变量** (生产环境):
```
DATABASE_URL=postgresql://...         # PostgreSQL 连接串
JWT_SECRET=<生成随机字符串>           # 至少 32 字符
CORS_ORIGINS=https://solacore.app      # 允许的前端域名
APP_ENV=production                    # 环境标识
OPENAI_API_KEY=sk-...                 # OpenAI API 密钥（生产用）
```

**可选变量** (生产环境):
```
SENTRY_DSN=https://...                # 错误监控（推荐）
BETA_MODE=false                       # 生产环境关闭 Beta 模式
PAYMENTS_ENABLED=true                 # 生产环境启用支付（延后也可）
```

**如何生成 JWT_SECRET**:
```bash
# 使用 Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 使用 OpenSSL
openssl rand -base64 32
```

---

### Phase 3: PostgreSQL Database Setup

**预计时间**: 15-30 分钟

#### Step 3.1: 创建生产数据库

**For Neon**:
1. 访问 neon.tech，注册账号
2. 点击 "Create Project"
3. 项目名称: `solacore-production`
4. 区域: 选择就近用户（US West / EU / Asia Pacific）
5. PostgreSQL 版本: 默认（最新稳定版）
6. 点击 "Create"
7. 复制 **Connection String**（格式：`postgresql://user:password@host/dbname`）

**For Supabase**:
1. 访问 supabase.com，注册账号
2. 点击 "New Project"
3. 项目名称: `solacore-production`
4. Database Password: 生成强密码并保存
5. 区域: 选择就近用户
6. 点击 "Create new project"
7. 复制 **Connection String**（Settings → Database → Connection string）

**For Railway PostgreSQL** (如果 Hosting 也选 Railway):
1. 在 Railway 项目中点击 "+ New"
2. 选择 "Database" → "PostgreSQL"
3. Railway 自动创建数据库
4. 复制 **DATABASE_URL** 环境变量（自动生成）

---

#### Step 3.2: 更新环境变量

1. 将数据库 Connection String 添加到托管平台的环境变量
2. 变量名: `DATABASE_URL`
3. 格式验证: 确保格式为 `postgresql://user:password@host:port/dbname`
4. 重启应用（如需要）

---

#### Step 3.3: 运行数据库迁移

**⚠️ 注意**: 此步骤需要在后端部署成功后执行（见 `docs/DATABASE_MIGRATION.md`）

---

### Phase 4: DNS & SSL Configuration

**预计时间**: 15-30 分钟（DNS 传播可能需要 24 小时）

#### Step 4.1: 配置 DNS 记录

**如果使用 Cloudflare**:
1. 登录 Cloudflare Dashboard
2. 选择域名（solacore.app）
3. 进入 "DNS" 标签
4. 添加以下记录：

**Backend API (api.solacore.app)**:
| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| **CNAME** | `api` | `<Vercel/Railway/Fly.io 提供的域名>` | ☑️ Proxied | Auto |

**Frontend (solacore.app)**:
| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| **CNAME** | `@` 或 留空 | `<Vercel 提供的域名>` | ☑️ Proxied | Auto |

**示例**:
```
CNAME  api    solacore-backend.vercel.app    Proxied  Auto
CNAME  @      solacore-frontend.vercel.app   Proxied  Auto
```

---

**如果使用域名注册商 DNS**:
1. 登录域名注册商控制面板
2. 进入 DNS Management / DNS Records
3. 添加相同的 CNAME 记录
4. Proxy 选项不可用（仅 Cloudflare 有）

---

#### Step 4.2: SSL/TLS 证书配置

**如果使用 Cloudflare**:
- ✅ **自动**: Cloudflare 自动提供免费 SSL 证书
- 设置 SSL/TLS 模式为 **Full (strict)**（推荐）
- 路径: Cloudflare → SSL/TLS → Overview → Full (strict)

**如果使用 Vercel/Railway**:
- ✅ **自动**: 平台自动配置 Let's Encrypt 证书
- 添加自定义域名后，等待证书自动生成（2-5 分钟）

**如果使用 Fly.io**:
- ✅ **自动**: Fly.io 自动配置证书
- 使用命令查看证书状态: `fly certs show <域名>`

---

#### Step 4.3: 验证 DNS 生效

**检查 DNS 是否生效**:
```bash
# macOS / Linux
dig api.solacore.app

# Windows
nslookup api.solacore.app

# 或使用在线工具
https://dnschecker.org
```

**预期结果**:
- CNAME 记录指向托管商提供的域名
- 无错误信息（NXDOMAIN = 域名不存在，需等待传播）

---

### Phase 5: Environment Targets

Solacore 项目支持以下环境：

| 环境 | 域名 | 用途 | 数据库 |
|------|------|------|--------|
| **Development** | `localhost:8000` | 本地开发 | SQLite / Local PostgreSQL |
| **Staging** (可选) | `api-staging.solacore.app` | 预生产测试 | Staging PostgreSQL |
| **Production** | `api.solacore.app` | 生产环境 | Production PostgreSQL |

**Staging 环境配置** (可选):
- 重复上述步骤，但使用 `api-staging` 子域名
- 使用独立的数据库实例
- 环境变量设置 `APP_ENV=staging`

---

## Completion Criteria

完成以下所有检查项后，域名与托管配置即为完成：

### Domain Checklist

- [ ] **1. 域名已购买**（solacore.app 或备选）
- [ ] **2. WHOIS Privacy 已启用**
- [ ] **3. Nameservers 已配置**（Cloudflare 或注册商 DNS）
- [ ] **4. DNS 记录已添加**（api.solacore.app → 托管商域名）
- [ ] **5. DNS 传播已验证**（dig/nslookup 检查通过）

---

### Hosting Checklist

- [ ] **6. 托管账号已创建**（Vercel / Railway / Fly.io）
- [ ] **7. 项目已部署**（后端应用）
- [ ] **8. 环境变量已配置**（DATABASE_URL, JWT_SECRET, etc.）
- [ ] **9. Health endpoint 可访问**（`https://api.solacore.app/health` 返回 200）

---

### Database Checklist

- [ ] **10. PostgreSQL 实例已创建**（Neon / Supabase / Railway）
- [ ] **11. Connection String 已获取**
- [ ] **12. DATABASE_URL 已配置**到托管平台
- [ ] **13. 数据库迁移已运行**（见 DATABASE_MIGRATION.md）
- [ ] **14. 备份策略已启用**（每日备份，保留 7 天）

---

### SSL/TLS Checklist

- [ ] **15. SSL 证书已生成**（Cloudflare / Vercel / Railway 自动）
- [ ] **16. HTTPS 可访问**（`https://api.solacore.app/health`）
- [ ] **17. HTTP → HTTPS 重定向已启用**
- [ ] **18. SSL Labs 测试通过**（https://www.ssllabs.com/ssltest/ 评级 A）

---

### Final Validation

- [ ] **19. Backend API 可通过自定义域名访问**
  - 测试: `curl https://api.solacore.app/health`
  - 预期: `{"status":"healthy","version":"1.0.0","database":"connected"}`

- [ ] **20. CORS 配置正确**
  - 前端可调用后端 API
  - 无 CORS 错误

- [ ] **21. 所有环境变量已验证**
  - 检查: `https://api.solacore.app/health` 返回正确版本号
  - 检查: 数据库连接正常（"database": "connected"）

---

## Risks & Common Issues

### Risk 1: DNS 传播延迟

**问题**: DNS 记录添加后，域名仍无法访问

**原因**: DNS 传播需要时间（5 分钟 - 48 小时）

**解决**:
- 等待至少 30 分钟
- 使用 `https://dnschecker.org` 检查全球传播状态
- 清除本地 DNS 缓存: `sudo dscacheutil -flushcache` (macOS)

---

### Risk 2: SSL 证书生成失败

**问题**: HTTPS 无法访问，显示证书错误

**原因**: DNS 未生效或托管商无法验证域名所有权

**解决**:
- 确认 DNS 记录已正确配置
- 等待 DNS 完全传播
- 在托管平台手动触发证书重新生成

---

### Risk 3: 数据库连接失败

**问题**: Backend 报错 "Unable to connect to database"

**原因**: DATABASE_URL 格式错误或网络限制

**解决**:
- 验证 CONNECTION_STRING 格式: `postgresql://user:password@host:port/dbname`
- 检查数据库托管商是否允许外部连接（部分需要白名单 IP）
- 确认数据库实例状态为 "Running"

---

### Risk 4: 环境变量未生效

**问题**: 应用行为异常，环境变量读取失败

**原因**: 托管平台需要重启应用以加载新变量

**解决**:
- 在托管平台手动触发 "Redeploy" 或 "Restart"
- 检查环境变量拼写（严格区分大小写）

---

## Time Estimates

| 阶段 | 预计时间 | 依赖 |
|------|---------|------|
| **Domain Registration** | 15-30 分钟 | 无 |
| **Nameservers 配置** | 5 分钟（生效需 30 分钟 - 48 小时） | Domain |
| **Hosting Setup** | 20-40 分钟 | GitHub 账号 |
| **PostgreSQL Setup** | 15-30 分钟 | 无 |
| **DNS Records** | 15 分钟（生效需 30 分钟 - 24 小时） | Domain + Hosting |
| **SSL 证书生成** | 2-5 分钟（自动） | DNS 生效 |
| **最终验证** | 10-15 分钟 | 所有上述步骤 |
| **总计（最快）** | **2-3 小时**（如 DNS 快速生效） | |
| **总计（保守）** | **1-2 天**（考虑 DNS 传播） | |

---

## Related Documents

### Prerequisites

- [ENV_VARIABLES.md](../ENV_VARIABLES.md) - 完整环境变量清单
- [Launch Dependencies](launch-dependencies.md) - 所有生产依赖项追踪

### Next Steps (After Domain/Hosting Setup)

- [DATABASE_MIGRATION.md](../DATABASE_MIGRATION.md) - 数据库迁移指南
- [PROD_DEPLOY.md](../PROD_DEPLOY.md) - 生产部署 Runbook
- [Prod Preflight](prod-preflight.md) - 部署前预检清单

### Related Guides

- [Apple Developer Setup Guide](apple-developer-setup-guide.md) - iOS 构建与 App Store 阻塞项解除
- [Store Submission Checklist](store-submission-checklist.md) - App Store / Play Store 提交清单

---

**完成此指南后，您将解除 "Domain" 和 "Hosting" 两个生产阻塞项，并可继续进行后端部署。**
