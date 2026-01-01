# 生产环境数据库紧急修复指南

**问题**: https://api.solacore.app 返回 `"database": "error"`，导致所有用户无法登录

**诊断时间**: 2026-01-01
**影响范围**: 全部用户
**严重级别**: 🔴 P0 - 生产环境故障

---

## 快速修复（5分钟）

### 第 1 步：登录服务器

```bash
ssh linuxuser@你的服务器IP
# 输入密码
```

### 第 2 步：进入项目目录

```bash
cd /home/linuxuser/solacore/solacore-api
```

### 第 3 步：执行修复脚本

```bash
bash scripts/fix-prod-db.sh
```

**如果脚本不存在**，手动执行以下命令：

```bash
# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 重启数据库
docker-compose -f docker-compose.prod.yml restart db

# 等待 10 秒
sleep 10

# 重启 API
docker-compose -f docker-compose.prod.yml restart api

# 验证修复
curl https://api.solacore.app/health
```

---

## 问题诊断

### 可能原因 1：数据库容器未运行

**检查方法**：
```bash
docker-compose -f docker-compose.prod.yml ps
```

**期望输出**：
```
NAME                STATUS
solacore-api-db-1   Up 10 minutes (healthy)
solacore-api-api-1  Up 10 minutes
```

**如果 db 容器是 `Exited` 状态**：
```bash
# 查看日志
docker-compose -f docker-compose.prod.yml logs db --tail=100

# 启动容器
docker-compose -f docker-compose.prod.yml up -d db
```

---

### 可能原因 2：数据库内存不足

**检查方法**：
```bash
docker stats --no-stream
```

**如果 db 容器 MEM USAGE 接近限制**：

编辑 `docker-compose.prod.yml`，找到 db 服务的 `mem_limit`:
```yaml
db:
  mem_limit: 1g  # 改成 2g 或更高
```

重新部署：
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

### 可能原因 3：数据库连接配置错误

**检查 .env 文件**：
```bash
cat .env | grep DATABASE_URL
```

**正确格式应该是**：
```bash
DATABASE_URL=postgresql+asyncpg://postgres:密码@db:5432/solacore
```

**注意**：
- 主机名必须是 `db`（Docker 容器网络内部名称）
- 不是 `localhost`
- 不是服务器IP

**修复方法**：
```bash
nano .env
# 修改 DATABASE_URL
# Ctrl+X 保存退出

# 重启容器
docker-compose -f docker-compose.prod.yml restart api
```

---

### 可能原因 4：磁盘空间不足

**检查方法**：
```bash
df -h
```

**如果 `/` 分区使用率 > 90%**：

清理 Docker：
```bash
# 清理未使用的镜像和容器
docker system prune -a

# 清理日志
sudo journalctl --vacuum-size=100M

# 清理旧的备份（如果有）
cd /home/linuxuser/solacore/solacore-api
du -sh backups/*
# 手动删除旧备份
```

---

## 验证修复

执行以下命令验证问题已解决：

```bash
# 1. 健康检查
curl https://api.solacore.app/health

# 期望输出：
# {"status":"healthy","checks":{"database":"connected",...}}

# 2. 测试登录（使用测试账号）
curl -X POST https://api.solacore.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "password":"Test123456",
    "device_fingerprint":"test-fp"
  }'

# 期望输出：401（账号不存在）而不是 500
```

---

## 持续监控

### 设置告警

编辑 `docker-compose.prod.yml`，确保健康检查已启用：

```yaml
api:
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live').read()"]
    interval: 30s
    timeout: 5s
    retries: 3
```

### 查看实时日志

```bash
# API 日志
docker-compose -f docker-compose.prod.yml logs -f api

# 数据库日志
docker-compose -f docker-compose.prod.yml logs -f db

# 所有日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 访问监控面板

如果 Grafana 已启用：
- URL: http://服务器IP:3000
- 默认账号：admin / admin（首次登录需修改密码）

---

## 预防措施

### 1. 启用自动重启

确保 `docker-compose.prod.yml` 中所有服务都有 `restart: always`：

```yaml
services:
  api:
    restart: always
  db:
    restart: always
  redis:
    restart: always
```

### 2. 定期备份

检查备份服务是否运行：
```bash
docker-compose -f docker-compose.prod.yml ps backup
```

手动创建备份：
```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres solacore > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 3. 资源监控

安装 `htop` 监控资源使用：
```bash
sudo apt install htop
htop
```

---

## 紧急联系方式

如果以上方法都无效，立即：

1. **回滚到上一个版本**：
   ```bash
   cd /home/linuxuser/solacore/solacore-api
   git log --oneline -5
   git reset --hard [上一个稳定的 commit]
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

2. **联系技术支持**（附上以下信息）：
   - 服务器日志：`docker-compose logs --tail=200`
   - 系统状态：`free -h && df -h`
   - 容器状态：`docker-compose ps`

---

## 修复记录

| 时间 | 操作 | 结果 |
|------|------|------|
| 2026-01-01 12:40 | 发现数据库连接失败 | - |
| | | |
| | | |

---

**最后更新**: 2026-01-01
**文档维护者**: Claude + 老板
