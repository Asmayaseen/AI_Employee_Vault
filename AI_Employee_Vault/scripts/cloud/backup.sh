#!/usr/bin/env bash
set -euo pipefail

# AI Employee Backup Script
# Creates compressed backups with 7-day rotation

INSTALL_DIR="${INSTALL_DIR:-/opt/ai-employee}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/ai-employee}"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="ai-employee-backup-${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "[Backup] Starting backup: ${BACKUP_NAME}"

mkdir -p "$BACKUP_PATH"

# Backup vault directory (excluding node_modules and .git)
echo "[Backup] Backing up vault..."
tar czf "$BACKUP_PATH/vault.tar.gz" \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='__pycache__' \
    -C "$INSTALL_DIR" AI_Employee_Vault 2>/dev/null || true

# Backup nginx configuration
echo "[Backup] Backing up nginx config..."
tar czf "$BACKUP_PATH/nginx.tar.gz" \
    -C /etc nginx/sites-available nginx/sites-enabled 2>/dev/null || true

# Backup environment file
echo "[Backup] Backing up environment..."
cp /etc/ai-employee/env "$BACKUP_PATH/env.backup" 2>/dev/null || true

# Backup Odoo database (if any odoo postgres container is running)
ODOO_DB_CONTAINER=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -E "odoo.db|odoo_db" | head -1 || true)
if [ -n "$ODOO_DB_CONTAINER" ]; then
    echo "[Backup] Backing up Odoo database from container: $ODOO_DB_CONTAINER..."
    docker exec "$ODOO_DB_CONTAINER" pg_dumpall -U odoo \
        | gzip > "$BACKUP_PATH/odoo-db.sql.gz" 2>/dev/null || true
else
    echo "[Backup] No Odoo DB container running — skipping database backup"
fi

# Backup Odoo filestore if volume exists
ODOO_FILESTORE=$(docker volume ls -q 2>/dev/null | grep -E "odoo.data|odoo_data" | head -1 || true)
if [ -n "$ODOO_FILESTORE" ]; then
    echo "[Backup] Backing up Odoo filestore volume: $ODOO_FILESTORE..."
    docker run --rm -v "$ODOO_FILESTORE:/odoo_data:ro" \
        -v "$BACKUP_PATH:/backup" alpine \
        tar czf "/backup/odoo-filestore.tar.gz" /odoo_data 2>/dev/null || true
fi

# Create final compressed archive
echo "[Backup] Compressing..."
tar czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
rm -rf "$BACKUP_PATH"

# Rotate old backups
echo "[Backup] Rotating old backups (keeping last ${RETENTION_DAYS} days)..."
find "$BACKUP_DIR" -name "ai-employee-backup-*.tar.gz" -mtime "+${RETENTION_DAYS}" -delete

# Report
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
echo "[Backup] Complete: ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE})"
echo "[Backup] Location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
