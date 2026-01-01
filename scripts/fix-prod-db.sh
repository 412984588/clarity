#!/bin/bash
# 生产环境数据库紧急修复脚本
# 使用方法：在服务器上执行 bash fix-prod-db.sh

set -e

echo "🔧 Solacore 生产环境数据库紧急修复"
echo "======================================"
echo ""

# 检查当前目录
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ 错误：请在 /home/linuxuser/solacore/solacore-api 目录下执行此脚本"
    exit 1
fi

echo "📊 步骤 1/5: 检查容器状态..."
docker-compose -f docker-compose.prod.yml ps
echo ""

echo "📊 步骤 2/5: 检查数据库容器日志..."
docker-compose -f docker-compose.prod.yml logs db --tail=50
echo ""

echo "🔄 步骤 3/5: 重启数据库容器..."
docker-compose -f docker-compose.prod.yml restart db
sleep 5
echo ""

echo "✅ 步骤 4/5: 等待数据库启动..."
for i in {1..30}; do
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ 数据库已就绪"
        break
    fi
    echo "等待中... ($i/30)"
    sleep 2
done
echo ""

echo "🔄 步骤 5/5: 重启 API 容器..."
docker-compose -f docker-compose.prod.yml restart api
sleep 3
echo ""

echo "🧪 验证修复..."
echo "1. 检查健康端点："
curl -s https://api.solacore.app/health | python3 -m json.tool || echo "⚠️  API 尚未就绪"
echo ""

echo "2. 检查容器状态："
docker-compose -f docker-compose.prod.yml ps
echo ""

echo "✅ 修复完成！"
echo ""
echo "📝 后续步骤："
echo "1. 如果问题仍未解决，请查看完整日志："
echo "   docker-compose -f docker-compose.prod.yml logs api --tail=100"
echo "   docker-compose -f docker-compose.prod.yml logs db --tail=100"
echo ""
echo "2. 检查 .env 文件中的 DATABASE_URL 配置"
echo "3. 检查服务器内存和磁盘空间："
echo "   free -h"
echo "   df -h"
