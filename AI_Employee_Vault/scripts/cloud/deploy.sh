#!/usr/bin/env bash
set -euo pipefail

# AI Employee Cloud Deployment Script (Platinum Tier)
# Deploys the full AI Employee stack to Ubuntu 22.04+ VPS
# Includes: Dashboard, Flask API, Watchers, Health Monitor

REPO_URL="${REPO_URL:-https://github.com/your-org/Ai-Employee.git}"
INSTALL_DIR="${INSTALL_DIR:-/opt/ai-employee}"
SERVICE_USER="ai-employee"
DOMAIN="${DOMAIN:-ai.example.com}"

echo "============================================"
echo "  AI Employee Cloud Deployment"
echo "============================================"

# Check Ubuntu version
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    echo "ERROR: This script requires Ubuntu 22.04+"
    exit 1
fi

echo "[1/8] Installing system packages..."
apt-get update -qq
apt-get install -y -qq \
    curl git nginx certbot python3-certbot-nginx \
    python3 python3-pip python3-venv \
    docker.io docker-compose-v2 \
    ufw fail2ban

# Install Node.js 20
if ! command -v node &>/dev/null || [[ "$(node -v)" != v20* ]]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y -qq nodejs
fi

echo "[2/8] Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -m -s /bin/bash "$SERVICE_USER"
    usermod -aG docker "$SERVICE_USER"
fi

echo "[3/8] Setting up repository..."
if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR"
    sudo -u "$SERVICE_USER" git pull --ff-only || true
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
fi

echo "[4/8] Installing dependencies..."
cd "$INSTALL_DIR/AI_Employee_Vault/web-ui"
sudo -u "$SERVICE_USER" npm install --production

cd "$INSTALL_DIR"
sudo -u "$SERVICE_USER" python3 -m venv "$INSTALL_DIR/venv"
sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -q \
    -r "$INSTALL_DIR/AI_Employee_Vault/Watchers/requirements.txt"

echo "[4b/8] Deploying Odoo Community (Docker)..."
ODOO_DIR="$INSTALL_DIR/MCP_Servers/odoo-mcp"
if [ -d "$ODOO_DIR" ]; then
    # Create Odoo data dirs with correct ownership
    mkdir -p /opt/ai-employee-odoo/{filestore,db}
    chown -R "$SERVICE_USER:$SERVICE_USER" /opt/ai-employee-odoo

    # Generate Odoo master password if not set
    ODOO_MASTER_PASS=$(openssl rand -hex 16)

    # Write Odoo env file (never synced to git)
    ODOO_ENV="/etc/ai-employee/odoo.env"
    if [ ! -f "$ODOO_ENV" ]; then
        cat > "$ODOO_ENV" <<EOF
ODOO_MASTER_PASSWORD=$ODOO_MASTER_PASS
POSTGRES_PASSWORD=$(openssl rand -hex 16)
EOF
        chmod 600 "$ODOO_ENV"
        chown "$SERVICE_USER:$SERVICE_USER" "$ODOO_ENV"
        echo "  [!] Odoo env written to $ODOO_ENV — save these credentials!"
    fi

    # Launch Odoo stack (detached, restart-always)
    cd "$ODOO_DIR"
    sudo -u "$SERVICE_USER" docker compose pull --quiet
    sudo -u "$SERVICE_USER" docker compose up -d
    echo "  Odoo starting at http://localhost:8069 (may take 30s)"
else
    echo "  [WARN] $ODOO_DIR not found — skipping Odoo deployment"
fi

echo "[5/8] Building dashboard..."
cd "$INSTALL_DIR/AI_Employee_Vault/web-ui"
sudo -u "$SERVICE_USER" npm run build

echo "[6/8] Installing systemd services..."
cp "$INSTALL_DIR/AI_Employee_Vault/scripts/cloud/systemd/"*.service \
    /etc/systemd/system/
systemctl daemon-reload

# Create environment file if it doesn't exist
ENV_FILE="/etc/ai-employee/env"
mkdir -p /etc/ai-employee
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" <<EOF
VAULT_DIR=$INSTALL_DIR/AI_Employee_Vault
VAULT_PATH=$INSTALL_DIR/AI_Employee_Vault
NODE_ENV=production
FLASK_ENV=production
PORT=9000
NEXT_PUBLIC_API_URL=https://$DOMAIN
AGENT_MODE=draft_only
AGENT_NAME=cloud
CLOUD_API_URL=https://$DOMAIN
VAULT_SYNC_REMOTE=origin
VAULT_SYNC_BRANCH=main
ALERTS_ENABLED=false
EOF
    chown "$SERVICE_USER:$SERVICE_USER" "$ENV_FILE"
    chmod 600 "$ENV_FILE"
fi

# Copy zones.json if not present
ZONES_FILE="$INSTALL_DIR/AI_Employee_Vault/zones.json"
if [ ! -f "$ZONES_FILE" ]; then
    sudo -u "$SERVICE_USER" cat > "$ZONES_FILE" <<'ZONES'
{
  "active_zone": "cloud",
  "auto_failover": true,
  "failover_threshold": 3,
  "zones": {
    "local": { "api_url": "http://localhost:9000", "name": "Local", "enabled": true },
    "cloud": { "api_url": "https://DOMAIN_PLACEHOLDER", "name": "Cloud", "enabled": true }
  },
  "routing_rules": {
    "email_processing": "active",
    "social_media": "active",
    "approvals": "local",
    "vault_operations": "local",
    "whatsapp": "local",
    "payments": "local",
    "accounting": "active",
    "system_monitoring": "both"
  }
}
ZONES
    sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" "$ZONES_FILE"
fi

echo "[7/8] Configuring nginx..."
cp "$INSTALL_DIR/AI_Employee_Vault/scripts/cloud/nginx.conf" \
    /etc/nginx/sites-available/ai-employee
sed -i "s/ai.example.com/$DOMAIN/g" /etc/nginx/sites-available/ai-employee
ln -sf /etc/nginx/sites-available/ai-employee /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo "[8/8] Starting services..."
systemctl enable --now ai-employee-api
systemctl enable --now ai-employee-dashboard
systemctl enable --now ai-employee-watchers
systemctl enable --now ai-employee-health-monitor

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Install backup cron job
BACKUP_SCRIPT="$INSTALL_DIR/AI_Employee_Vault/scripts/cloud/backup.sh"
if [ -f "$BACKUP_SCRIPT" ]; then
    chmod +x "$BACKUP_SCRIPT"
    CRON_LINE="0 2 * * * $SERVICE_USER $BACKUP_SCRIPT >> /var/log/ai-employee-backup.log 2>&1"
    CRON_FILE="/etc/cron.d/ai-employee-backup"
    if [ ! -f "$CRON_FILE" ]; then
        echo "$CRON_LINE" > "$CRON_FILE"
        chmod 644 "$CRON_FILE"
        echo "  Backup cron installed: daily at 02:00"
    fi
fi

# Provision HTTPS via certbot (only if DNS already points here)
echo ""
echo "[+] Attempting SSL provisioning via certbot..."
if host "$DOMAIN" 2>/dev/null | grep -q "has address"; then
    CURRENT_IP=$(curl -s ifconfig.me 2>/dev/null || echo "")
    DOMAIN_IP=$(host "$DOMAIN" 2>/dev/null | awk '/has address/{print $4}' | head -1)
    if [ "$CURRENT_IP" = "$DOMAIN_IP" ] && [ -n "$CURRENT_IP" ]; then
        certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos \
            --email "admin@$DOMAIN" --redirect
        echo "  SSL provisioned for $DOMAIN"
        systemctl reload nginx
    else
        echo "  [SKIP] DNS not pointing to this server yet (domain=$DOMAIN_IP, server=$CURRENT_IP)"
        echo "  Run manually after DNS update: certbot --nginx -d $DOMAIN"
    fi
else
    echo "  [SKIP] DNS lookup failed — run manually: certbot --nginx -d $DOMAIN"
fi

echo ""
echo "============================================"
echo "  Deployment Complete!"
echo "============================================"
echo "  Dashboard: https://$DOMAIN"
echo "  API:       https://$DOMAIN/api/health"
echo "  Odoo:      http://localhost:8069 (internal)"
echo ""
echo "  What was deployed:"
echo "  - Flask API (port 9000) via systemd"
echo "  - Next.js Dashboard (port 3000) via systemd"
echo "  - Watchers + Orchestrator via systemd"
echo "  - Health Monitor via systemd"
echo "  - Odoo Community (port 8069) via Docker"
echo "  - Nginx reverse proxy"
echo "  - Backup cron (daily 02:00)"
echo ""
echo "  If SSL not provisioned:"
echo "  1. Point DNS $DOMAIN -> $(curl -s ifconfig.me 2>/dev/null)"
echo "  2. Run: certbot --nginx -d $DOMAIN"
echo ""
echo "  Edit cloud config: nano /etc/ai-employee/env"
echo "  Odoo credentials:  cat /etc/ai-employee/odoo.env"
echo "============================================"
