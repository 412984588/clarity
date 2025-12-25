#!/usr/bin/env bash
# =============================================================================
# Clarity SSL 证书一键配置脚本（Let's Encrypt + Nginx）
# =============================================================================
# 适用系统: Ubuntu / Debian
# 功能: 申请证书 -> 配置 Nginx -> 设置自动续期
# 使用方法: ./scripts/setup-ssl.sh
# =============================================================================

set -euo pipefail

# --- 颜色输出 ---
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
  echo -e "${RED}❌ SSL 配置失败（步骤：${CURRENT_STEP}，行号：${line}）${NC}"
  echo -e "${YELLOW}提示：请检查 DNS 解析、80/443 端口是否放通${NC}"
  exit 1
}

trap 'on_error $LINENO' ERR

enable_https_block() {
  local conf="$1"
  if grep -q "listen 443 ssl" "$conf"; then
    log_info "HTTPS 配置已启用，跳过解注释"
    return
  fi

  local tmp="${conf}.tmp"
  awk '
    BEGIN {in_ssl=0; in_block=0}
    /# HTTPS 版本/ {in_ssl=1}
    {
      if (in_ssl && $0 ~ /^  #server \{/) {in_block=1}
      if (in_block) {
        sub(/^  #/, "  ")
      }
      if (in_block && $0 ~ /^  #}/) {in_block=0; in_ssl=0}
      print
    }
  ' "$conf" > "$tmp"
  mv "$tmp" "$conf"
}

enable_https_redirect() {
  local conf="$1"
  sed -i 's/^    # return 301/    return 301/' "$conf"
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

# --- 2. 定位项目与配置文件 ---
log_step "定位配置文件"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
NGINX_CONF="${REPO_DIR}/solacore-api/nginx/nginx.conf"
SSL_DIR="${REPO_DIR}/solacore-api/nginx/ssl"
COMPOSE_FILE="${REPO_DIR}/solacore-api/docker-compose.prod.yml"
COMPOSE_DIR="${REPO_DIR}/solacore-api"

if [ ! -f "$NGINX_CONF" ]; then
  log_fail "找不到 Nginx 配置文件：${NGINX_CONF}"
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  log_fail "找不到 Docker Compose 配置：${COMPOSE_FILE}"
fi

# --- 3. 确保 Docker / Compose 可用 ---
log_step "检查 Docker 运行环境"
if ! command -v docker >/dev/null 2>&1; then
  log_fail "未检测到 Docker，请先运行 ./deploy.sh 完成基础安装"
fi

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
  log_fail "Docker Compose 未安装，请先运行 ./deploy.sh"
fi

# --- 4. 安装 certbot ---
log_step "安装 Let's Encrypt (certbot)"
if ! command -v certbot >/dev/null 2>&1; then
  ${SUDO} apt-get update
  ${SUDO} apt-get install -y certbot
else
  log_ok "certbot 已安装"
fi

# --- 5. 输入域名与邮箱 ---
log_step "收集域名信息"
read -rp "请输入域名（例如 api.example.com）: " DOMAIN
read -rp "请输入邮箱（用于证书到期提醒）: " EMAIL

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
  log_fail "域名和邮箱不能为空"
fi

log_warn "请确认域名已正确解析到本机 IP，否则申请会失败"

# --- 6. 停止 Nginx 容器（释放 80 端口）---
log_step "停止 Nginx 容器以申请证书"
${COMPOSE_CMD[@]} --project-directory "${COMPOSE_DIR}" -f "${COMPOSE_FILE}" stop nginx || true

# --- 7. 申请证书 ---
log_step "申请 SSL 证书"
${SUDO} certbot certonly \
  --standalone \
  --preferred-challenges http \
  --non-interactive \
  --agree-tos \
  --email "${EMAIL}" \
  -d "${DOMAIN}"

# --- 8. 复制证书到 Nginx 挂载目录 ---
log_step "复制证书到 Nginx 挂载目录"
${SUDO} mkdir -p "${SSL_DIR}"
${SUDO} cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" "${SSL_DIR}/fullchain.pem"
${SUDO} cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" "${SSL_DIR}/privkey.pem"
${SUDO} chmod 644 "${SSL_DIR}/fullchain.pem"
${SUDO} chmod 600 "${SSL_DIR}/privkey.pem"
${SUDO} chown -R "${USER}:${USER}" "${SSL_DIR}" || true

# --- 9. 自动启用 HTTPS 配置 ---
log_step "自动启用 Nginx HTTPS 配置"
enable_https_block "${NGINX_CONF}"
sed -i "s/server_name _;/server_name ${DOMAIN};/g" "${NGINX_CONF}"

FORCE_HTTPS="${FORCE_HTTPS:-true}"
if [ "$FORCE_HTTPS" = "true" ]; then
  enable_https_redirect "${NGINX_CONF}"
  log_ok "已启用 HTTP -> HTTPS 强制跳转"
else
  log_warn "已保留 HTTP 访问（未强制跳转）"
fi

# --- 10. 启动/重载 Nginx ---
log_step "启动 Nginx 容器"
${COMPOSE_CMD[@]} --project-directory "${COMPOSE_DIR}" -f "${COMPOSE_FILE}" up -d nginx

# --- 11. 设置自动续期 ---
log_step "设置证书自动续期"
${SUDO} systemctl enable --now certbot.timer || true

HOOK_PATH="/etc/letsencrypt/renewal-hooks/deploy/solacore-nginx.sh"
${SUDO} mkdir -p "$(dirname "${HOOK_PATH}")"
cat <<EOF | ${SUDO} tee "${HOOK_PATH}" >/dev/null
#!/usr/bin/env bash
set -euo pipefail

SSL_DIR="${SSL_DIR}"
COMPOSE_FILE="${COMPOSE_FILE}"
COMPOSE_DIR="${COMPOSE_DIR}"
RENEWED_LINEAGE="\${RENEWED_LINEAGE:-}"

if [ -z "\${RENEWED_LINEAGE}" ]; then
  exit 0
fi

cp "\${RENEWED_LINEAGE}/fullchain.pem" "\${SSL_DIR}/fullchain.pem"
cp "\${RENEWED_LINEAGE}/privkey.pem" "\${SSL_DIR}/privkey.pem"
chmod 644 "\${SSL_DIR}/fullchain.pem"
chmod 600 "\${SSL_DIR}/privkey.pem"

if docker compose version >/dev/null 2>&1; then
  docker compose --project-directory "\${COMPOSE_DIR}" -f "\${COMPOSE_FILE}" restart nginx
elif command -v docker-compose >/dev/null 2>&1; then
  docker-compose --project-directory "\${COMPOSE_DIR}" -f "\${COMPOSE_FILE}" restart nginx
fi
EOF
${SUDO} chmod +x "${HOOK_PATH}"

# --- 12. 完成提示 ---
log_step "SSL 配置完成"
log_ok "HTTPS 已启用：https://${DOMAIN}"
log_info "证书自动续期已开启（certbot.timer + renew hook）"
log_info "如需查看 Nginx 日志：docker compose -f solacore-api/docker-compose.prod.yml logs -f nginx"
