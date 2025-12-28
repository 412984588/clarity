#!/bin/sh
set -eu

BACKUP_DIR=${BACKUP_DIR:-/backups}
BACKUP_LOG_FILE=${BACKUP_LOG_FILE:-${BACKUP_DIR}/backup.log}
RESTORE_PSQL_FLAGS=${RESTORE_PSQL_FLAGS:-"-v ON_ERROR_STOP=1"}

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

log() {
  msg="$(timestamp) [INFO] $*"
  echo "$msg"
  echo "$msg" >> "$BACKUP_LOG_FILE"
}

err() {
  msg="$(timestamp) [ERROR] $*"
  echo "$msg" >&2
  echo "$msg" >> "$BACKUP_LOG_FILE"
}

mkdir -p "$(dirname "$BACKUP_LOG_FILE")"
touch "$BACKUP_LOG_FILE"

BACKUP_FILE=${1:-${BACKUP_FILE:-}}

if [ -z "$BACKUP_FILE" ]; then
  err "Usage: $0 /path/to/backup_YYYYMMDD_HHmmss.sql.gz"
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  err "Backup file not found: $BACKUP_FILE"
  exit 1
fi

if ! gzip -t "$BACKUP_FILE" >/dev/null 2>&1; then
  err "Backup file integrity check failed: $BACKUP_FILE"
  exit 1
fi

log "Starting restore from $BACKUP_FILE."

if [ -n "${DATABASE_URL:-}" ]; then
  DB_DSN=$(printf '%s' "$DATABASE_URL" | sed 's/^postgresql+asyncpg:/postgresql:/')
  if ! pg_isready --dbname="$DB_DSN" >/dev/null 2>&1; then
    err "Database connection check failed."
    exit 1
  fi
  if ! gunzip -c "$BACKUP_FILE" | psql --dbname="$DB_DSN" $RESTORE_PSQL_FLAGS; then
    err "Restore failed."
    exit 1
  fi
else
  export PGHOST=${POSTGRES_HOST:-db}
  export PGPORT=${POSTGRES_PORT:-5432}
  export PGUSER=${POSTGRES_USER:-postgres}
  export PGPASSWORD=${POSTGRES_PASSWORD:-}
  export PGDATABASE=${POSTGRES_DB:-postgres}
  if ! pg_isready >/dev/null 2>&1; then
    err "Database connection check failed."
    exit 1
  fi
  if ! gunzip -c "$BACKUP_FILE" | psql $RESTORE_PSQL_FLAGS; then
    err "Restore failed."
    exit 1
  fi
fi

log "Restore completed successfully."
