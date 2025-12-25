#!/bin/bash
# =============================================================================
# Database Migration Script
# =============================================================================
# Usage: ./scripts/migrate.sh [command]
# Commands:
#   status   - Show current migration status
#   upgrade  - Apply all pending migrations (with backup)
#   rollback - Rollback last migration
#   backup   - Create database backup only
#   heads    - Check for multiple heads
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to API directory
cd "$(dirname "$0")/../solacore-api"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

load_database_url_from_env() {
    if [ ! -f .env ]; then
        return 0
    fi

    local env_url
    env_url=$(python3 - <<'PY'
from pathlib import Path
import re

path = Path(".env")
value = ""
for line in path.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("export "):
        line = line[len("export "):].strip()
    if not line.startswith("DATABASE_URL="):
        continue
    _, raw = line.split("=", 1)
    raw = raw.strip()
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        value = raw[1:-1]
    else:
        value = re.split(r"\s+#", raw, maxsplit=1)[0].strip()
    break
print(value)
PY
)

    if [ -n "$env_url" ]; then
        export DATABASE_URL="$env_url"
    fi
}

normalize_database_url() {
    python3 - <<'PY'
import os

url = os.environ.get("DATABASE_URL", "")
if not url:
    raise SystemExit(1)
if url.startswith("postgres://"):
    url = "postgresql://" + url[len("postgres://"):]
if url.startswith("postgresql+asyncpg://"):
    url = "postgresql://" + url[len("postgresql+asyncpg://"):]
if url.startswith("postgresql+psycopg://"):
    url = "postgresql://" + url[len("postgresql+psycopg://"):]
print(url)
PY
}

check_env() {
    if [ -z "${DATABASE_URL:-}" ]; then
        load_database_url_from_env
    fi

    if [ -z "${DATABASE_URL:-}" ]; then
        log_error "DATABASE_URL not set. Please set it in .env or environment."
        exit 1
    fi
}

show_status() {
    log_info "Current migration status:"
    poetry run alembic current
    echo ""
    log_info "Available heads:"
    poetry run alembic heads
}

check_heads() {
    HEAD_COUNT=$(poetry run alembic heads 2>/dev/null | wc -l)
    if [ "$HEAD_COUNT" -gt 1 ]; then
        log_error "Multiple migration heads detected!"
        log_error "Run 'alembic merge -m \"merge heads\" <rev1> <rev2>' to fix."
        poetry run alembic heads
        exit 1
    fi
    log_info "Single head verified ✓"
}

create_backup() {
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="../backups"
    BACKUP_FILE="$BACKUP_DIR/solacore_backup_$TIMESTAMP.sql"

    mkdir -p "$BACKUP_DIR"

    log_info "Creating backup: $BACKUP_FILE"

    if command -v pg_dump &> /dev/null; then
        local pg_dump_url
        pg_dump_url=$(normalize_database_url)
        if [ -z "$pg_dump_url" ]; then
            log_warn "DATABASE_URL is invalid. Skipping backup."
            return 1
        fi

        pg_dump "$pg_dump_url" -F c -f "$BACKUP_FILE" 2>/dev/null || {
            log_warn "pg_dump failed. Skipping backup."
            return 1
        }
        log_info "Backup created: $BACKUP_FILE"
    else
        log_warn "pg_dump not found. Skipping backup."
        return 1
    fi
}

do_upgrade() {
    log_info "Starting migration upgrade..."

    # Check for multiple heads
    check_heads

    # Create backup
    create_backup || log_warn "Proceeding without backup..."

    # Run migrations
    log_info "Applying migrations..."
    poetry run alembic upgrade head

    log_info "Migration complete ✓"
    show_status
}

do_rollback() {
    log_warn "Rolling back last migration..."

    read -p "Are you sure you want to rollback? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rollback cancelled."
        exit 0
    fi

    poetry run alembic downgrade -1

    log_info "Rollback complete ✓"
    show_status
}

# Main
check_env

case "${1:-status}" in
    status)
        show_status
        ;;
    upgrade)
        do_upgrade
        ;;
    rollback)
        do_rollback
        ;;
    backup)
        create_backup
        ;;
    heads)
        check_heads
        ;;
    *)
        echo "Usage: $0 {status|upgrade|rollback|backup|heads}"
        exit 1
        ;;
esac
