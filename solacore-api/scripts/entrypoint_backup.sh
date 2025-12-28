#!/bin/sh
set -e

echo "=== Backup Container Entrypoint ==="
echo "Starting initialization..."

# 设置权限
chmod +x /scripts/*.sh

# 生成 crontab (每晚 2 点运行)
echo "Setting up cron schedule..."
echo "PATH=/usr/local/bin:/usr/bin:/bin" > /etc/crontabs/root
echo "0 2 * * * /scripts/backup_database.sh >> /var/log/cron.log 2>&1" >> /etc/crontabs/root

# 创建日志文件
touch /var/log/cron.log

# 显示 cron 配置
echo "Crontab configuration:"
cat /etc/crontabs/root

# 启动 crond
echo "Starting cron daemon..."
echo "Backup service is ready. Logs will be written to /var/log/cron.log"
exec crond -f -l 2
