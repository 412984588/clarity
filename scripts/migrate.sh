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

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to API directory
cd "$(dirname "$0")/../clarity-api"

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

check_env() {
    if [ -z "$DATABASE_URL" ]; then
        if [ -f .env ]; then
            export $(grep -v '^#' .env | xargs)
        fi
    fi

    if [ -z "$DATABASE_URL" ]; then
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
    BACKUP_FILE="$BACKUP_DIR/clarity_backup_$TIMESTAMP.sql"

    mkdir -p "$BACKUP_DIR"

    log_info "Creating backup: $BACKUP_FILE"

    # Extract connection info from DATABASE_URL
    # Format: postgresql+asyncpg://user:pass@host:port/dbname
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')

    if command -v pg_dump &> /dev/null; then
        PGPASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p') \
            pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -F c -f "$BACKUP_FILE" 2>/dev/null || {
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
