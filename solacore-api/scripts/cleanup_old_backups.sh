#!/bin/sh
set -eu

BACKUP_DIR=${BACKUP_DIR:-/backups}
BACKUP_LOG_FILE=${BACKUP_LOG_FILE:-${BACKUP_DIR}/backup.log}
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

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

if [ ! -d "$BACKUP_DIR" ]; then
  log "Backup directory not found, skipping cleanup: $BACKUP_DIR"
  exit 0
fi

log "Cleaning backups older than ${BACKUP_RETENTION_DAYS} days in $BACKUP_DIR."

# Count old backups
old_count=$(find "$BACKUP_DIR" -type f -name "backup_*.sql.gz" -mtime +"$BACKUP_RETENTION_DAYS" -print 2>/dev/null | wc -l | tr -d ' ')

# Remove old backups if any exist
if [ "$old_count" -gt 0 ]; then
  find "$BACKUP_DIR" -type f -name "backup_*.sql.gz" -mtime +"$BACKUP_RETENTION_DAYS" -exec rm -f {} \;
  if [ $? -eq 0 ]; then
    log "Removed $old_count old backup(s)."
  else
    err "Failed to remove old backups."
    exit 1
  fi
else
  log "No old backups to remove."
fi
