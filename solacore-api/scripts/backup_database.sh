#!/bin/sh
set -eu
umask 077

BACKUP_DIR=${BACKUP_DIR:-/backups}
BACKUP_LOG_FILE=${BACKUP_LOG_FILE:-${BACKUP_DIR}/backup.log}
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
BACKUP_PREFIX=${BACKUP_PREFIX:-backup}
BACKUP_PG_DUMP_FLAGS=${BACKUP_PG_DUMP_FLAGS:---no-owner --no-acl}
BACKUP_RUN_CLEANUP=${BACKUP_RUN_CLEANUP:-true}

BACKUP_S3_BUCKET=${BACKUP_S3_BUCKET:-}
BACKUP_S3_PREFIX=${BACKUP_S3_PREFIX:-}
BACKUP_S3_REGION=${BACKUP_S3_REGION:-}
BACKUP_S3_STORAGE_CLASS=${BACKUP_S3_STORAGE_CLASS:-STANDARD}

BACKUP_NOTIFY_WEBHOOK=${BACKUP_NOTIFY_WEBHOOK:-}
BACKUP_NOTIFY_CMD=${BACKUP_NOTIFY_CMD:-}

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)

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

notify() {
  status="$1"
  message="$2"

  if [ -n "$BACKUP_NOTIFY_WEBHOOK" ]; then
    if command -v curl >/dev/null 2>&1; then
      curl -fsS -X POST \
        -H "Content-Type: application/json" \
        -d "{\"status\":\"$status\",\"message\":\"$message\"}" \
        "$BACKUP_NOTIFY_WEBHOOK" >/dev/null 2>&1 || true
    else
      err "curl not found, cannot send webhook notification."
    fi
  fi

  if [ -n "$BACKUP_NOTIFY_CMD" ]; then
    BACKUP_STATUS="$status" BACKUP_MESSAGE="$message" BACKUP_FILE="${BACKUP_FILE:-}" \
      sh -c "$BACKUP_NOTIFY_CMD" >/dev/null 2>&1 || true
  fi
}

mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$BACKUP_LOG_FILE")"
touch "$BACKUP_LOG_FILE"

on_exit() {
  code=$?
  if [ "$code" -ne 0 ]; then
    err "Backup failed (exit $code)."
    notify "failure" "Backup failed (exit $code)."
  fi
}

trap 'on_exit' EXIT

log "Starting database backup."

if [ -n "${DATABASE_URL:-}" ]; then
  DB_DSN=$(printf '%s' "$DATABASE_URL" | sed 's/^postgresql+asyncpg:/postgresql:/')
  log "Using DATABASE_URL for connection."
  if ! pg_isready --dbname="$DB_DSN" >/dev/null 2>&1; then
    err "Database connection check failed."
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
fi

BACKUP_FILE="${BACKUP_DIR}/${BACKUP_PREFIX}_$(date +%Y%m%d_%H%M%S).sql.gz"
TMP_FILE="${BACKUP_FILE%.gz}"

if [ -n "${DATABASE_URL:-}" ]; then
  if ! pg_dump --dbname="$DB_DSN" $BACKUP_PG_DUMP_FLAGS > "$TMP_FILE"; then
    err "pg_dump failed."
    rm -f "$TMP_FILE"
    exit 1
  fi
else
  if ! pg_dump $BACKUP_PG_DUMP_FLAGS > "$TMP_FILE"; then
    err "pg_dump failed."
    rm -f "$TMP_FILE"
    exit 1
  fi
fi

if ! gzip "$TMP_FILE"; then
  err "gzip compression failed."
  rm -f "$TMP_FILE"
  exit 1
fi

if [ ! -s "$BACKUP_FILE" ]; then
  err "Backup file is missing or empty: $BACKUP_FILE"
  exit 1
fi

if ! gzip -t "$BACKUP_FILE" >/dev/null 2>&1; then
  err "Backup file integrity check failed: $BACKUP_FILE"
  exit 1
fi

log "Backup created: $BACKUP_FILE"

if [ -n "$BACKUP_S3_BUCKET" ]; then
  if ! command -v aws >/dev/null 2>&1; then
    err "aws CLI not found, cannot upload to S3."
    exit 1
  fi

  s3_key=$(basename "$BACKUP_FILE")
  if [ -n "$BACKUP_S3_PREFIX" ]; then
    cleaned_prefix=$(printf '%s' "$BACKUP_S3_PREFIX" | sed 's#^/##; s#/$##')
    if [ -n "$cleaned_prefix" ]; then
      s3_key="${cleaned_prefix}/${s3_key}"
    fi
  fi

  region_arg=""
  if [ -n "$BACKUP_S3_REGION" ]; then
    region_arg="--region $BACKUP_S3_REGION"
  fi

  storage_arg=""
  if [ -n "$BACKUP_S3_STORAGE_CLASS" ]; then
    storage_arg="--storage-class $BACKUP_S3_STORAGE_CLASS"
  fi

  if ! aws s3 cp "$BACKUP_FILE" "s3://$BACKUP_S3_BUCKET/$s3_key" \
    $region_arg $storage_arg --only-show-errors; then
    err "S3 upload failed."
    exit 1
  fi

  log "Uploaded to S3: s3://$BACKUP_S3_BUCKET/$s3_key"
fi

if [ "$BACKUP_RUN_CLEANUP" = "true" ] || [ "$BACKUP_RUN_CLEANUP" = "1" ]; then
  if [ -x "$SCRIPT_DIR/cleanup_old_backups.sh" ]; then
    BACKUP_DIR="$BACKUP_DIR" \
      BACKUP_RETENTION_DAYS="$BACKUP_RETENTION_DAYS" \
      BACKUP_LOG_FILE="$BACKUP_LOG_FILE" \
      "$SCRIPT_DIR/cleanup_old_backups.sh"
  else
    log "Cleanup script not found or not executable, skipping."
  fi
fi

notify "success" "Backup completed: $(basename "$BACKUP_FILE")"
log "Backup finished successfully."
