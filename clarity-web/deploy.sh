#!/usr/bin/env bash
set -euo pipefail

REQUIRED_NODE_MAJOR=18

if ! command -v node >/dev/null 2>&1; then
  echo "未检测到 Node.js，请先安装 Node.js。" >&2
  exit 1
fi

current_version=$(node -v | sed 's/^v//')
current_major=${current_version%%.*}

if [ "$current_major" -lt "$REQUIRED_NODE_MAJOR" ]; then
  echo "需要 Node.js >= ${REQUIRED_NODE_MAJOR}，当前版本为 v${current_version}。" >&2
  exit 1
fi

echo "检测到 Node.js v${current_version}"

npm install
npm run build

if [[ "${1:-}" == "--start" ]]; then
  npm run start
else
  echo "构建完成。可运行 'npm run start' 或 './deploy.sh --start' 启动服务。"
fi
