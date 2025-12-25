#!/usr/bin/env bash
# =============================================================================
# Clarity 一键部署脚本
# =============================================================================
# 适用系统: Ubuntu / Debian
# 功能: 安装依赖 -> 获取代码 -> 检查环境 -> Docker Compose 部署 -> 健康检查
# 使用方法: ./deploy.sh
# =============================================================================

set -euo pipefail

# --- 颜色输出（纯文本终端友好）---
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m"

CURRENT_STEP="初始化"

log_step() {
  CURRENT_STEP="$1"
  echo -e "${BLUE}▶ ${1}${NC}"
}

log_info() { echo -e "${BLUE}   ${1}${NC}"; }
log_warn() { echo -e "${YELLOW}⚠ ${1}${NC}"; }
log_ok() { echo -e "${GREEN}✅ ${1}${NC}"; }
log_fail() {
  echo -e "${RED}❌ ${1}${NC}"
  exit 1
}

on_error() {
  local line="${1:-?}"
  echo -e "${RED}❌ 部署失败（步骤：${CURRENT_STEP}，行号：${line}）${NC}"
  echo -e "${YELLOW}提示：请检查网络/权限/日志，可执行：docker compose logs -f${NC}"
  exit 1
}

trap 'on_error $LINENO' ERR

read_env_value() {
  local key="$1"
  local file="$2"
  local line
  line="$(grep -E "^${key}=" "$file" | tail -n 1 || true)"
  if [ -z "$line" ]; then
    return 1
  fi
  local value="${line#*=}"
  value="${value%\"}"
  value="${value#\"}"
  echo "$value"
}

# --- 0. 检测系统 ---
log_step "检测系统环境"
if [ ! -f /etc/os-release ]; then
  log_fail "无法识别系统（仅支持 Ubuntu/Debian）"
fi

# shellcheck source=/dev/null
. /etc/os-release
case "${ID:-}" in
  ubuntu|debian)
    log_ok "检测到系统：${PRETTY_NAME}"
    ;;
  *)
    log_fail "当前系统不支持：${PRETTY_NAME:-unknown}（仅支持 Ubuntu/Debian）"
    ;;
esac

# --- 1. 权限与 sudo ---
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    log_fail "需要 sudo 权限，但系统未安装 sudo"
  fi
fi

# --- 2. 安装依赖（Docker / Compose / Git / curl）---
log_step "安装依赖（Docker / Docker Compose / Git）"
${SUDO} apt-get update
${SUDO} apt-get install -y git curl ca-certificates gnupg lsb-release

if ! command -v docker >/dev/null 2>&1; then
  log_info "未检测到 Docker，正在安装..."
  ${SUDO} apt-get install -y docker.io
else
  log_ok "Docker 已安装"
fi

if command -v systemctl >/dev/null 2>&1; then
  ${SUDO} systemctl enable --now docker
else
  ${SUDO} service docker start || true
fi

if ! docker compose version >/dev/null 2>&1; then
  log_info "未检测到 Docker Compose，正在安装..."
  if ! ${SUDO} apt-get install -y docker-compose-plugin; then
    ${SUDO} apt-get install -y docker-compose
  fi
fi

if [ "$(id -u)" -ne 0 ]; then
  ${SUDO} usermod -aG docker "$USER" || true
  log_warn "已尝试将当前用户加入 docker 组，可能需要重新登录后生效"
fi

# --- 3. 解析 Docker / Compose 命令 ---
DOCKER_CMD=(docker)
if [ "$(id -u)" -ne 0 ]; then
  DOCKER_CMD=("${SUDO}" docker)
fi

if "${DOCKER_CMD[@]}" compose version >/dev/null 2>&1; then
  COMPOSE_CMD=("${DOCKER_CMD[@]}" compose)
elif command -v docker-compose >/dev/null 2>&1; then
  if [ "$(id -u)" -ne 0 ]; then
    COMPOSE_CMD=("${SUDO}" docker-compose)
  else
    COMPOSE_CMD=(docker-compose)
  fi
else
  log_fail "Docker Compose 未安装成功"
fi

# --- 4. 获取/更新代码 ---
log_step "获取 Clarity 代码"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -d "${SCRIPT_DIR}/.git" ] && [ -d "${SCRIPT_DIR}/clarity-api" ]; then
  REPO_DIR="${SCRIPT_DIR}"
else
  REPO_DIR="${CLARITY_REPO_DIR:-$HOME/clarity}"
fi

if [ -d "${REPO_DIR}/.git" ]; then
  if [ -n "$(git -C "${REPO_DIR}" status --porcelain)" ]; then
    log_warn "检测到本地改动，已跳过 git pull（请自行处理冲突）"
  else
    git -C "${REPO_DIR}" pull --ff-only
    log_ok "代码已更新"
  fi
else
  if [ -d "${REPO_DIR}" ] && [ "$(ls -A "${REPO_DIR}" 2>/dev/null)" ]; then
    log_fail "目标目录已存在且不是 Git 仓库：${REPO_DIR}"
  fi
  REPO_URL="${CLARITY_REPO_URL:-}"
  if [ -z "$REPO_URL" ] && [ -d "${SCRIPT_DIR}/.git" ]; then
    REPO_URL="$(git -C "${SCRIPT_DIR}" config --get remote.origin.url || true)"
  fi
  if [ -z "$REPO_URL" ]; then
    read -rp "请输入 Clarity 仓库地址 (git URL): " REPO_URL
  fi
  git clone "$REPO_URL" "$REPO_DIR"
  log_ok "代码已拉取到：${REPO_DIR}"
fi

# --- 5. 环境变量检查 ---
log_step "检查环境变量"
ENV_FILE="${REPO_DIR}/clarity-api/.env"
ENV_TEMPLATE="${REPO_DIR}/clarity-api/.env.prod.example"

if [ ! -f "$ENV_TEMPLATE" ]; then
  ENV_TEMPLATE="${REPO_DIR}/clarity-api/.env.example"
fi

if [ ! -f "$ENV_FILE" ]; then
  cp "$ENV_TEMPLATE" "$ENV_FILE"
  log_warn "已生成 ${ENV_FILE}"
  log_warn "请先填写 .env 中的必填项后再重新运行脚本"
  log_info "快速编辑命令：nano ${ENV_FILE}"
  exit 1
fi

# --- 6. 构建并启动 ---
log_step "构建并启动服务（Docker Compose）"
COMPOSE_FILE="${REPO_DIR}/clarity-api/docker-compose.prod.yml"
COMPOSE_DIR="${REPO_DIR}/clarity-api"

if [ ! -f "$COMPOSE_FILE" ]; then
  log_fail "找不到部署配置文件：${COMPOSE_FILE}"
fi

if "${COMPOSE_CMD[@]}" --project-directory "${COMPOSE_DIR}" -f "${COMPOSE_FILE}" up -d --build; then
  log_ok "容器已启动"
fi

# --- 7. 等待健康并运行烟雾测试 ---
log_step "等待服务健康"
API_CONTAINER="$("${COMPOSE_CMD[@]}" --project-directory "${COMPOSE_DIR}" -f "${COMPOSE_FILE}" ps -q api)"

if [ -n "$API_CONTAINER" ]; then
  for i in $(seq 1 30); do
    STATUS="$("${DOCKER_CMD[@]}" inspect --format='{{.State.Health.Status}}' "$API_CONTAINER" 2>/dev/null || echo "unknown")"
    if [ "$STATUS" = "healthy" ]; then
      log_ok "API 容器健康检查通过"
      break
    fi
    if [ "$STATUS" = "unhealthy" ]; then
      log_fail "API 容器健康检查失败，请检查日志"
    fi
    sleep 2
  done
else
  log_warn "未找到 API 容器，跳过容器健康检查"
fi

log_step "运行烟雾测试"
BASE_URL="$(read_env_value "API_BASE_URL" "$ENV_FILE" || true)"
if [ -z "$BASE_URL" ]; then
  BASE_URL="http://localhost"
fi
BASE_URL="${BASE_URL%/}"

if [ -x "${REPO_DIR}/scripts/deploy_prod_smoke.sh" ]; then
  "${REPO_DIR}/scripts/deploy_prod_smoke.sh" "$BASE_URL"
else
  bash "${REPO_DIR}/scripts/deploy_prod_smoke.sh" "$BASE_URL"
fi

# --- 8. 输出状态与访问地址 ---
log_step "部署完成，当前状态如下"
"${COMPOSE_CMD[@]}" --project-directory "${COMPOSE_DIR}" -f "${COMPOSE_FILE}" ps
echo ""
log_ok "访问地址：${BASE_URL}"
echo ""
echo "下一步建议："
echo "1) 配置域名与 SSL：./scripts/setup-ssl.sh"
echo "2) 查看日志：docker compose -f clarity-api/docker-compose.prod.yml logs -f"
echo "3) 如需重启：docker compose -f clarity-api/docker-compose.prod.yml restart"
