# SSL 证书管理指南

**生产环境**: https://api.solacore.app
**证书类型**: Let's Encrypt 免费 DV 证书
**自动续期**: ✅ 已配置

---

## 证书信息

- **域名**: api.solacore.app
- **签发机构**: Let's Encrypt (R12)
- **证书类型**: RSA 2048-bit
- **有效期**: 90 天（自动续期）
- **当前到期日期**: 2026-03-26

---

## 证书位置

### 系统证书（Let's Encrypt 原始文件）
```bash
/etc/letsencrypt/live/api.solacore.app/
├── fullchain.pem  # 完整证书链（包含中间证书）
├── privkey.pem    # 私钥（严格保密）
├── cert.pem       # 服务器证书
└── chain.pem      # 中间证书
```

### Docker 项目证书（nginx 使用的副本）
```bash
/home/linuxuser/solacore/solacore-api/nginx/ssl/
├── fullchain.pem  # 从 Let's Encrypt 复制
└── privkey.pem    # 从 Let's Encrypt 复制
```

---

## 自动续期配置

### Certbot Timer 状态
```bash
# 查看自动续期服务状态
sudo systemctl status certbot.timer

# 查看下次执行时间
sudo systemctl list-timers certbot.timer

# 手动测试续期（dry-run，不实际更新）
sudo certbot renew --dry-run
```

**默认配置**:
- 每天运行 2 次（00:00 和 12:00）
- 证书到期前 30 天自动续期
- 续期后自动执行 deploy hook

### Renewal Hook（证书更新后自动执行）

**脚本位置**: `/etc/letsencrypt/renewal-hooks/deploy/copy-to-docker.sh`

**功能**:
1. 将新证书复制到 Docker 项目目录
2. 修改文件权限（fullchain: 644, privkey: 600）
3. 自动重启 nginx 容器
4. 记录执行日志

**测试 Hook**:
```bash
sudo bash /etc/letsencrypt/renewal-hooks/deploy/copy-to-docker.sh
```

---

## 常用检查命令

### 1. 检查证书有效期
```bash
# 方法 1：使用 certbot
sudo certbot certificates

# 方法 2：使用 openssl（远程检查）
echo | openssl s_client -connect api.solacore.app:443 -servername api.solacore.app 2>/dev/null | openssl x509 -noout -dates

# 方法 3：检查剩余天数
echo | openssl s_client -connect api.solacore.app:443 -servername api.solacore.app 2>/dev/null | openssl x509 -noout -enddate | awk -F= '{print $2}' | xargs -I {} date -d {} +%s | awk -v now=$(date +%s) '{print int(($1-now)/86400)" days remaining"}'
```

### 2. 检查证书链完整性
```bash
echo | openssl s_client -connect api.solacore.app:443 -servername api.solacore.app 2>/dev/null | openssl x509 -noout -text | grep -A 3 "Subject:"
```

### 3. 验证 HTTPS 正常工作
```bash
# 检查 HTTP/2 支持
curl -sI https://api.solacore.app/health | head -1

# 检查证书信任链
curl -v https://api.solacore.app/health 2>&1 | grep "SSL certificate verify"
```

### 4. 检查 Docker 项目中的证书
```bash
cd /home/linuxuser/solacore/solacore-api
ls -lh nginx/ssl/
openssl x509 -in nginx/ssl/fullchain.pem -noout -dates
```

---

## 手动续期证书

如果自动续期失败，可以手动续期：

### 步骤 1：停止 nginx 容器
```bash
cd /home/linuxuser/solacore/solacore-api
docker-compose -f docker-compose.prod.yml stop nginx
```

### 步骤 2：运行 certbot 续期
```bash
sudo certbot renew --force-renewal
```

### 步骤 3：复制证书到项目目录
```bash
sudo cp /etc/letsencrypt/live/api.solacore.app/fullchain.pem nginx/ssl/fullchain.pem
sudo cp /etc/letsencrypt/live/api.solacore.app/privkey.pem nginx/ssl/privkey.pem
sudo chown linuxuser:linuxuser nginx/ssl/*.pem
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem
```

### 步骤 4：重启 nginx 容器
```bash
docker-compose -f docker-compose.prod.yml start nginx
```

---

## 新增域名到证书

如果需要添加更多域名（如 www.solacore.app）：

```bash
# 停止 nginx
docker-compose -f docker-compose.prod.yml stop nginx

# 扩展证书
sudo certbot certonly --standalone --expand --non-interactive \
  --agree-tos --email admin@solacore.app \
  -d api.solacore.app \
  -d solacore.app \
  -d www.solacore.app

# 复制证书并重启
sudo bash /etc/letsencrypt/renewal-hooks/deploy/copy-to-docker.sh
```

---

## 证书撤销（紧急情况）

如果私钥泄露，需要立即撤销证书：

```bash
# 撤销证书
sudo certbot revoke --cert-path /etc/letsencrypt/live/api.solacore.app/cert.pem

# 删除旧证书
sudo certbot delete --cert-name api.solacore.app

# 重新申请新证书
sudo certbot certonly --standalone --non-interactive \
  --agree-tos --email admin@solacore.app \
  -d api.solacore.app
```

---

## 监控和告警

### 设置证书到期告警（推荐）

使用 cron 每周检查证书有效期：

```bash
# 编辑 crontab
sudo crontab -e

# 添加以下行（每周一上午 9 点检查）
0 9 * * 1 /usr/bin/certbot renew --quiet --deploy-hook "/etc/letsencrypt/renewal-hooks/deploy/copy-to-docker.sh"
```

### 手动检查脚本

创建检查脚本 `/home/linuxuser/check-ssl-expiry.sh`：

```bash
#!/bin/bash
# 检查 SSL 证书到期时间

DOMAIN="api.solacore.app"
DAYS_THRESHOLD=30

# 获取到期日期（时间戳）
EXPIRY_TIMESTAMP=$(echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2 | xargs -I {} date -d "{}" +%s)

# 当前时间（时间戳）
NOW_TIMESTAMP=$(date +%s)

# 计算剩余天数
DAYS_REMAINING=$(( ($EXPIRY_TIMESTAMP - $NOW_TIMESTAMP) / 86400 ))

echo "证书剩余天数: $DAYS_REMAINING 天"

if [ $DAYS_REMAINING -lt $DAYS_THRESHOLD ]; then
    echo "⚠️  警告：证书即将到期！"
    exit 1
else
    echo "✅ 证书状态正常"
    exit 0
fi
```

---

## 故障排查

### 问题 1: 证书更新后 nginx 仍使用旧证书

**原因**: Docker 容器挂载的是旧文件
**解决**:
```bash
# 重新复制证书
sudo bash /etc/letsencrypt/renewal-hooks/deploy/copy-to-docker.sh

# 强制重启 nginx（不只是 reload）
docker-compose -f docker-compose.prod.yml restart nginx
```

### 问题 2: Certbot 续期失败（端口 80 被占用）

**原因**: nginx 容器占用了 80 端口
**解决**:
```bash
# 停止 nginx 容器
docker-compose -f docker-compose.prod.yml stop nginx

# 手动续期
sudo certbot renew --force-renewal

# 复制证书并重启
sudo bash /etc/letsencrypt/renewal-hooks/deploy/copy-to-docker.sh
```

### 问题 3: 证书文件权限错误

**原因**: 复制后权限不正确
**解决**:
```bash
cd /home/linuxuser/solacore/solacore-api/nginx/ssl
sudo chown linuxuser:linuxuser *.pem
sudo chmod 644 fullchain.pem
sudo chmod 600 privkey.pem
```

### 问题 4: Let's Encrypt 速率限制

**原因**: 同一域名每周最多申请 5 次
**解决**: 等待 7 天，或使用 staging 环境测试

---

## 最佳实践

1. **定期检查证书状态**（每月至少一次）
2. **保持 certbot 更新** (`sudo apt update && sudo apt upgrade certbot`)
3. **备份私钥** (加密存储在安全位置)
4. **监控续期日志** (`/var/log/letsencrypt/letsencrypt.log`)
5. **测试 renewal hook** (每季度测试一次)

---

## 相关文件

- **Renewal Hook**: `/etc/letsencrypt/renewal-hooks/deploy/copy-to-docker.sh`
- **Renewal 配置**: `/etc/letsencrypt/renewal/api.solacore.app.conf`
- **Certbot 日志**: `/var/log/letsencrypt/letsencrypt.log`
- **Nginx 配置**: `/home/linuxuser/solacore/solacore-api/nginx/nginx.conf`
- **Docker Compose**: `/home/linuxuser/solacore/solacore-api/docker-compose.prod.yml`

---

**最后更新**: 2026-01-01
**维护者**: Claude + 老板
