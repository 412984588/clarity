# 数据库监控指南

**监控目标**: PostgreSQL 数据库连接状态
**检查频率**: 每 15 分钟
**自动修复**: ✅ 已启用

---

## 监控机制

### 自动健康检查

**脚本位置**: `/home/linuxuser/check-db-health.sh`

**检查项目**:
1. PostgreSQL 容器状态（是否运行）
2. 数据库连接（pg_isready）
3. API 健康端点（/health）

**自动修复流程**:
```
发现问题 → 重启数据库容器 → 等待 10 秒 → 验证修复 → 重启 API 容器
```

### Cron 定时任务

**执行频率**: 每 15 分钟
**Cron 表达式**: `*/15 * * * *`
**执行命令**: `/home/linuxuser/check-db-health.sh`

**查看 Cron 配置**:
```bash
crontab -l | grep check-db-health
```

---

## 日志管理

### 主日志文件

**位置**: `/home/linuxuser/db-health.log`

**查看最新日志**:
```bash
tail -f /home/linuxuser/db-health.log
```

**查看最近 50 行**:
```bash
tail -n 50 /home/linuxuser/db-health.log
```

**搜索失败记录**:
```bash
grep "❌" /home/linuxuser/db-health.log
```

### Cron 执行日志

**位置**: `/home/linuxuser/db-health-cron.log`

**查看 Cron 输出**:
```bash
tail -f /home/linuxuser/db-health-cron.log
```

### 日志自动清理

- 主日志保留最新 1000 行（自动清理）
- Cron 日志需要手动清理

**手动清理 Cron 日志**:
```bash
> /home/linuxuser/db-health-cron.log
```

---

## 手动操作

### 手动执行健康检查

```bash
bash /home/linuxuser/check-db-health.sh
```

### 手动修复数据库

如果自动修复失败，按以下步骤手动修复：

```bash
cd /home/linuxuser/solacore/solacore-api

# 1. 重启数据库容器
docker-compose -f docker-compose.prod.yml restart db
sleep 10

# 2. 检查数据库是否正常
docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres

# 3. 如果连接正常，重启 API 容器
docker-compose -f docker-compose.prod.yml restart api

# 4. 验证修复
curl -s https://api.solacore.app/health | grep -o '"database":"[^"]*"'
```

### 查看容器状态

```bash
cd /home/linuxuser/solacore/solacore-api
docker-compose -f docker-compose.prod.yml ps
```

### 查看数据库日志

```bash
cd /home/linuxuser/solacore/solacore-api
docker-compose -f docker-compose.prod.yml logs --tail=100 db
```

---

## 监控指标

### 正常状态输出

```
[2026-01-01 18:19:36] === 开始数据库健康检查 ===
[2026-01-01 18:19:36] 检查 PostgreSQL 容器状态...
[2026-01-01 18:19:37] ✅ PostgreSQL 容器正常运行
[2026-01-01 18:19:37] 检查数据库连接...
[2026-01-01 18:19:38] ✅ 数据库连接正常
[2026-01-01 18:19:38] 检查 API 健康端点...
[2026-01-01 18:20:00] ✅ API 健康检查通过
[2026-01-01 18:20:00] === 健康检查完成：所有检查通过 ===
```

### 异常状态输出

```
[2026-01-01 12:00:00] === 开始数据库健康检查 ===
[2026-01-01 12:00:00] 检查 PostgreSQL 容器状态...
[2026-01-01 12:00:01] ✅ PostgreSQL 容器正常运行
[2026-01-01 12:00:01] 检查数据库连接...
[2026-01-01 12:00:02] ❌ 数据库连接失败！
[2026-01-01 12:00:02] ⚠️  尝试自动修复数据库连接...
[2026-01-01 12:00:02] 重启数据库容器...
[2026-01-01 12:00:13] ✅ 数据库已自动修复
[2026-01-01 12:00:13] 重启 API 容器...
[2026-01-01 12:00:18] 检查 API 健康端点...
[2026-01-01 12:00:20] ✅ API 健康检查通过
[2026-01-01 12:00:20] ✅ 问题已自动修复
[2026-01-01 12:00:20] === 健康检查完成：所有检查通过 ===
```

---

## 告警配置（可选）

### 邮件告警

如果需要在检查失败时发送邮件告警，需要先配置 `mail` 命令：

```bash
# 安装 mailutils
sudo apt install mailutils

# 配置 SMTP（编辑 /etc/postfix/main.cf）
sudo nano /etc/postfix/main.cf

# 取消脚本中的邮件告警注释
nano /home/linuxuser/check-db-health.sh
# 找到这一行并去掉注释：
# echo "数据库健康检查失败，详情见日志" | mail -s "[ALERT] SolaCore DB Health Check Failed" $ALERT_EMAIL
```

### Webhook 告警（推荐）

使用 Webhook 推送到 Slack/Discord/钉钉：

```bash
# 编辑脚本添加 webhook 函数
nano /home/linuxuser/check-db-health.sh

# 添加以下函数
send_webhook_alert() {
    WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    MESSAGE="数据库健康检查失败！详情: $1"

    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$MESSAGE\"}" \
        > /dev/null 2>&1
}

# 在检查失败时调用
if [ $FAILED -eq 1 ]; then
    send_webhook_alert "$(tail -n 20 $LOG_FILE)"
fi
```

---

## 性能监控（扩展）

### 添加数据库性能指标

在 `/home/linuxuser/check-db-health.sh` 中添加：

```bash
# 检查数据库连接数
check_connection_count() {
    log "检查数据库连接数..."

    CONN_COUNT=$(docker-compose -f docker-compose.prod.yml exec -T db \
        psql -U postgres solacore -t -c \
        "SELECT count(*) FROM pg_stat_activity;" | xargs)

    log "当前连接数: $CONN_COUNT"

    if [ "$CONN_COUNT" -gt 80 ]; then
        log "⚠️  连接数过高！"
        return 1
    fi

    return 0
}

# 检查数据库大小
check_database_size() {
    log "检查数据库大小..."

    DB_SIZE=$(docker-compose -f docker-compose.prod.yml exec -T db \
        psql -U postgres solacore -t -c \
        "SELECT pg_size_pretty(pg_database_size('solacore'));" | xargs)

    log "数据库大小: $DB_SIZE"
    return 0
}
```

---

## 故障排查

### 问题 1: Cron 任务未执行

**检查 Cron 服务状态**:
```bash
sudo systemctl status cron
```

**查看 Cron 日志**:
```bash
grep CRON /var/log/syslog | tail -20
```

**手动测试脚本**:
```bash
bash /home/linuxuser/check-db-health.sh
```

### 问题 2: 自动修复失败

**可能原因**:
1. 数据库容器无法启动（资源不足）
2. 密码配置错误
3. 数据文件损坏

**手动诊断**:
```bash
# 查看数据库容器日志
docker-compose -f docker-compose.prod.yml logs --tail=100 db

# 检查磁盘空间
df -h

# 检查内存使用
free -h

# 检查 Docker 资源
docker stats --no-stream
```

### 问题 3: 日志文件过大

**清理日志**:
```bash
# 清空主日志
> /home/linuxuser/db-health.log

# 清空 Cron 日志
> /home/linuxuser/db-health-cron.log
```

**设置日志轮换（推荐）**:
```bash
sudo tee /etc/logrotate.d/db-health << EOF
/home/linuxuser/db-health.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}

/home/linuxuser/db-health-cron.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
EOF
```

---

## 维护建议

1. **每周检查日志**: 查看是否有异常重启记录
2. **每月验证告警**: 手动触发失败场景，验证告警是否正常
3. **每季度更新脚本**: 根据实际情况优化检查逻辑

---

## 相关文件

- **健康检查脚本**: `/home/linuxuser/check-db-health.sh`
- **主日志**: `/home/linuxuser/db-health.log`
- **Cron 日志**: `/home/linuxuser/db-health-cron.log`
- **Docker Compose**: `/home/linuxuser/solacore/solacore-api/docker-compose.prod.yml`

---

**最后更新**: 2026-01-01
**维护者**: Claude + 老板
