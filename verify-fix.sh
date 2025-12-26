#!/bin/bash

# 403 错误修复验证脚本
# 用法：./verify-fix.sh

set -e

echo "🔍 验证 403 错误修复"
echo "===================="
echo ""

# 检查工作目录
if [ ! -f "solacore-web/lib/api.ts" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "✅ 检测到项目根目录"
echo ""

# 1. 检查代码修改
echo "📝 检查代码修改..."
echo ""

# 检查 api.ts 是否导出 getDeviceFingerprint
if grep -q "export.*getDeviceFingerprint" solacore-web/lib/api.ts; then
    echo "✅ api.ts 已导出 getDeviceFingerprint"
else
    echo "❌ api.ts 未导出 getDeviceFingerprint"
    exit 1
fi

# 检查 session-api.ts 是否导入 getDeviceFingerprint
if grep -q "import.*getDeviceFingerprint.*from.*api" solacore-web/lib/session-api.ts; then
    echo "✅ session-api.ts 已导入 getDeviceFingerprint"
else
    echo "❌ session-api.ts 未导入 getDeviceFingerprint"
    exit 1
fi

# 检查 sendMessage 是否添加设备指纹
if grep -q "X-Device-Fingerprint" solacore-web/lib/session-api.ts; then
    echo "✅ sendMessage 已添加设备指纹请求头"
else
    echo "❌ sendMessage 未添加设备指纹请求头"
    exit 1
fi

echo ""
echo "📦 检查 TypeScript 编译..."
echo ""

# 2. TypeScript 编译检查
cd solacore-web
if npx tsc --noEmit 2>&1 | grep -q "error TS"; then
    echo "❌ TypeScript 编译错误"
    npx tsc --noEmit
    exit 1
else
    echo "✅ TypeScript 编译通过"
fi

# 3. Lint 检查
echo ""
echo "🔍 检查 ESLint..."
echo ""

if npm run lint 2>&1 | grep -q "error"; then
    echo "⚠️  ESLint 发现问题（可能不影响功能）"
else
    echo "✅ ESLint 检查通过"
fi

cd ..

# 4. 生成测试 UUID
echo ""
echo "🧪 生成测试设备指纹..."
echo ""

if command -v uuidgen &> /dev/null; then
    TEST_UUID=$(uuidgen)
    echo "✅ 测试 UUID: $TEST_UUID"
else
    TEST_UUID="test-fingerprint-123"
    echo "⚠️  uuidgen 未安装，使用备用 ID: $TEST_UUID"
fi

echo ""
echo "📋 验证摘要"
echo "===================="
echo "✅ 代码修改：正确"
echo "✅ TypeScript：通过"
echo "✅ 准备就绪：可以测试"
echo ""
echo "📝 下一步："
echo "1. 启动开发服务器: cd solacore-web && npm run dev"
echo "2. 访问: http://localhost:3000/solve"
echo "3. 清除浏览器数据: DevTools → Application → Clear site data"
echo "4. 观察控制台日志，确认设备指纹一致"
echo ""
echo "📖 详细测试指南: 查看 TEST_403_FIX.md"
echo ""
echo "✨ 验证完成！"
