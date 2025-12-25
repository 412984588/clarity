# Clarity 傻瓜式部署手册

> **最后更新**: 2025-12-25
> **适用人群**: 完全不懂编程的老板
> **预计时间**: 30 分钟（不含等待审批）

---

## 目录

1. [你需要准备什么](#1-你需要准备什么)
2. [买服务器（5 分钟）](#2-买服务器5-分钟)
3. [买域名（5 分钟）](#3-买域名5-分钟)
4. [一键部署（10 分钟）](#4-一键部署10-分钟)
5. [配置域名解析（5 分钟）](#5-配置域名解析5-分钟)
6. [开启 HTTPS（5 分钟）](#6-开启-https5-分钟)
7. [验证部署](#7-验证部署)
8. [日常运维](#8-日常运维)
9. [常见问题](#9-常见问题)

---

## 1. 你需要准备什么

### 必须有的东西

| 项目 | 说明 | 预计费用 |
|------|------|----------|
| **云服务器** | 推荐 2核4G 以上 | ¥50-100/月 |
| **域名** | 如 `api.clarity.app` | ¥50-100/年 |
| **信用卡/支付宝** | 用于购买上述服务 | - |

### 可选（已有可跳过）

| 项目 | 说明 |
|------|------|
| Google Cloud Console 账号 | 用于 Google 登录 |
| Apple Developer 账号 | 用于 Apple 登录（$99/年） |
| Stripe 账号 | 用于网页支付 |
| RevenueCat 账号 | 用于 App 内购 |
| OpenAI/Anthropic API Key | 用于 AI 功能 |

---

## 2. 买服务器（5 分钟）

### 推荐：阿里云 / 腾讯云 / AWS

1. 打开 [阿里云](https://www.aliyun.com/) 或 [腾讯云](https://cloud.tencent.com/)
2. 注册账号 → 实名认证
3. 购买 **云服务器 ECS**：
   - 系统：**Ubuntu 22.04 LTS**（必须）
   - 配置：2核 4G 内存 40G 硬盘（最低）
   - 地域：离用户近的（如上海、北京）
   - 带宽：按量付费 或 5Mbps 固定

4. **记下这些信息**（后面要用）：
   ```
   服务器公网 IP：xxx.xxx.xxx.xxx
   登录用户名：root（或 ubuntu）
   登录密码：你设置的密码
   ```

### 开放端口

在云服务器的**安全组**中，开放以下端口：

| 端口 | 用途 |
|------|------|
| 22 | SSH 登录 |
| 80 | HTTP 访问 |
| 443 | HTTPS 访问 |

---

## 3. 买域名（5 分钟）

### 推荐：阿里云 / Cloudflare / Namecheap

1. 搜索你想要的域名（如 `clarity.app`、`myapp.com`）
2. 付款购买
3. **先别配置 DNS**，等服务器部署好再配

---

## 4. 一键部署（10 分钟）

### 第一步：连接服务器

**Mac/Linux 用户**：
```bash
ssh root@你的服务器IP
# 输入密码
```

**Windows 用户**：
- 下载 [PuTTY](https://www.putty.org/) 或使用 Windows Terminal
- 输入服务器 IP 和密码登录

### 第二步：下载代码并运行部署脚本

复制以下命令，粘贴到终端，按回车：

```bash
# 1. 下载代码
git clone https://github.com/你的用户名/clarity.git
cd clarity

# 2. 运行一键部署脚本
chmod +x deploy.sh
./deploy.sh
```

### 第三步：填写配置

脚本会提示你 `.env` 文件不存在，并自动创建模板。

**编辑配置文件**：
```bash
nano clarity-api/.env
```

**必须修改的配置**（找到对应行，改成你的值）：

```bash
# 改成你的域名
API_BASE_URL=https://api.你的域名.com

# 改成你的 Google OAuth Client ID（没有可以先不填）
GOOGLE_CLIENT_ID=你的ID.apps.googleusercontent.com

# 改成你的 OpenAI API Key
OPENAI_API_KEY=sk-你的key

# JWT 密钥（运行这个命令生成）：openssl rand -hex 32
JWT_SECRET=生成的随机字符串

# 数据库密码（改成一个复杂的密码）
DATABASE_URL=postgresql+asyncpg://clarity_prod:你的复杂密码@db:5432/clarity
```

**保存并退出**：
- 按 `Ctrl + X`
- 按 `Y` 确认
- 按 `Enter` 保存

### 第四步：重新运行部署

```bash
./deploy.sh
```

等待几分钟，看到 `✅ 访问地址` 就成功了！

---

## 5. 配置域名解析（5 分钟）

回到你购买域名的网站，添加 DNS 记录：

| 类型 | 主机记录 | 记录值 |
|------|----------|--------|
| A | api | 你的服务器IP |

**例如**：
- 如果你的域名是 `clarity.app`
- 服务器 IP 是 `1.2.3.4`
- 添加 A 记录：`api` → `1.2.3.4`
- 最终访问地址就是 `api.clarity.app`

**等待 5-10 分钟** 让 DNS 生效。

验证是否生效：
```bash
ping api.你的域名.com
# 应该显示你的服务器 IP
```

---

## 6. 开启 HTTPS（5 分钟）

DNS 生效后，运行 SSL 配置脚本：

```bash
./scripts/setup-ssl.sh
```

按提示输入：
- 你的域名（如 `api.clarity.app`）
- 你的邮箱（用于证书到期提醒）

完成后，你的 API 就有了安全的 HTTPS 加密！

---

## 7. 验证部署

### 测试 API 是否正常

在浏览器打开：
```
https://api.你的域名.com/health
```

应该看到：
```json
{"status": "healthy", "version": "1.0.0"}
```

### 运行完整测试

```bash
./scripts/deploy_prod_smoke.sh https://api.你的域名.com
```

全部 ✅ 就表示部署成功！

---

## 8. 日常运维

### 查看服务状态

```bash
cd ~/clarity/clarity-api
docker compose -f docker-compose.prod.yml ps
```

### 查看日志

```bash
# 查看所有日志
docker compose -f docker-compose.prod.yml logs -f

# 只看 API 日志
docker compose -f docker-compose.prod.yml logs -f api
```

### 重启服务

```bash
docker compose -f docker-compose.prod.yml restart
```

### 更新代码

```bash
cd ~/clarity
git pull
./deploy.sh
```

### 停止服务

```bash
docker compose -f docker-compose.prod.yml down
```

---

## 9. 常见问题

### Q: 访问网站显示"无法连接"

**可能原因**：
1. 服务器安全组没开放 80/443 端口
2. DNS 还没生效（等 10 分钟）
3. 服务没启动成功

**解决方法**：
```bash
# 检查服务状态
docker compose -f docker-compose.prod.yml ps

# 如果显示 Exit，查看日志
docker compose -f docker-compose.prod.yml logs api
```

### Q: 日志显示数据库连接失败

**解决方法**：
```bash
# 检查数据库是否启动
docker compose -f docker-compose.prod.yml ps db

# 重启数据库
docker compose -f docker-compose.prod.yml restart db
```

### Q: SSL 证书申请失败

**可能原因**：
1. 域名还没指向服务器
2. 80 端口被占用

**解决方法**：
```bash
# 确认域名解析
ping api.你的域名.com

# 确认 80 端口开放
curl http://api.你的域名.com/health
```

### Q: 如何备份数据？

```bash
# 备份数据库
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres clarity > backup.sql

# 恢复数据库
cat backup.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U postgres clarity
```

---

## 环境变量完整说明

| 变量 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `DEBUG` | ✅ | 生产必须为 false | `false` |
| `API_BASE_URL` | ✅ | 你的 API 地址 | `https://api.clarity.app` |
| `DATABASE_URL` | ✅ | 数据库连接 | `postgresql+asyncpg://user:pass@db:5432/clarity` |
| `JWT_SECRET` | ✅ | JWT 签名密钥 | 用 `openssl rand -hex 32` 生成 |
| `GOOGLE_CLIENT_ID` | ✅ | Google 登录 | 从 Google Cloud Console 获取 |
| `APPLE_CLIENT_ID` | ⭕ | Apple 登录 | 你的 Bundle ID |
| `LLM_PROVIDER` | ✅ | AI 提供商 | `openai` 或 `anthropic` |
| `OPENAI_API_KEY` | ⭕ | OpenAI 密钥 | `sk-xxx` |
| `ANTHROPIC_API_KEY` | ⭕ | Anthropic 密钥 | `sk-ant-xxx` |
| `STRIPE_SECRET_KEY` | ⭕ | Stripe 支付 | `sk_live_xxx` |
| `REVENUECAT_WEBHOOK_SECRET` | ⭕ | RevenueCat | `whsec_xxx` |

> ✅ = 必填，⭕ = 可选（根据功能需求）

---

## 文件结构说明

```
clarity/
├── deploy.sh                    # 一键部署脚本
├── DEPLOY_MANUAL.md             # 本手册
├── clarity-api/
│   ├── .env                     # 环境变量（你需要配置）
│   ├── .env.prod.example        # 环境变量模板
│   ├── docker-compose.prod.yml  # 生产 Docker 配置
│   ├── Dockerfile               # Docker 镜像配置
│   └── nginx/
│       ├── nginx.conf           # Nginx 配置
│       └── ssl/                 # SSL 证书目录
└── scripts/
    ├── setup-ssl.sh             # SSL 配置脚本
    └── deploy_prod_smoke.sh     # 烟雾测试脚本
```

---

## 技术支持

如果遇到问题：
1. 先查看上面的"常见问题"
2. 运行 `docker compose logs` 查看错误日志
3. 在 GitHub Issues 提问

---

**恭喜你！现在你的 Clarity API 已经上线运行了！** 🎉
