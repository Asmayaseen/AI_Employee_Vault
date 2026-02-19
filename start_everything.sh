#!/bin/bash
# Master Control Script - AI Employee System v3.0 (Platinum)
# Starts all watchers + dashboard + web UI + health monitor

export DISPLAY=:0

echo "================================================================"
echo "  AI Employee System v3.0 (Platinum) - Starting All Services"
echo "================================================================"
echo ""

# Change to watchers directory
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers || exit 1

# Load environment variables
if [ -f ../.env ]; then
    set -a
    source ../.env
    set +a
    echo "  Loaded .env from vault root"
elif [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "  Loaded .env from watchers directory"
fi

# Step 1: Stop any running instances
echo "  Stopping existing services..."
pkill -f "gmail_watcher" 2>/dev/null
pkill -f "linkedin_watcher" 2>/dev/null
pkill -f "whatsapp_watcher" 2>/dev/null
pkill -f "filesystem_watcher" 2>/dev/null
pkill -f "approval_watcher" 2>/dev/null
pkill -f "facebook_watcher" 2>/dev/null
pkill -f "instagram_watcher" 2>/dev/null
pkill -f "twitter_watcher" 2>/dev/null
pkill -f "orchestrator.py" 2>/dev/null
pkill -f "health_monitor.py" 2>/dev/null
pkill -f "dashboard.py" 2>/dev/null
sleep 3

# Clean up lock files
rm -f .whatsapp_session/SingletonLock 2>/dev/null
rm -f .linkedin_session/SingletonLock 2>/dev/null

echo "  Cleanup complete"
echo ""

# Step 2: Start all watchers
echo "  Starting Watchers..."
echo ""

# Gmail Watcher
echo "  Starting Gmail Watcher..."
nohup python3 -u gmail_watcher.py --interval 120 > /tmp/gmail_watcher.log 2>&1 &
GMAIL_PID=$!
sleep 2
if ps -p $GMAIL_PID > /dev/null; then
    echo "    Gmail Watcher running (PID: $GMAIL_PID)"
else
    echo "    Gmail Watcher failed"
fi

# LinkedIn Watcher
echo "  Starting LinkedIn Watcher..."
nohup python3 -u linkedin_watcher.py --interval 300 > /tmp/linkedin_watcher.log 2>&1 &
LINKEDIN_PID=$!
sleep 2
if ps -p $LINKEDIN_PID > /dev/null; then
    echo "    LinkedIn Watcher running (PID: $LINKEDIN_PID)"
else
    echo "    LinkedIn Watcher failed"
fi

# WhatsApp Watcher
echo "  Starting WhatsApp Watcher..."
nohup python3 -u whatsapp_watcher.py --interval 180 > /tmp/whatsapp_watcher.log 2>&1 &
WHATSAPP_PID=$!
sleep 2
if ps -p $WHATSAPP_PID > /dev/null; then
    echo "    WhatsApp Watcher running (PID: $WHATSAPP_PID)"
else
    echo "    WhatsApp Watcher failed"
fi

# Filesystem Watcher
echo "  Starting Filesystem Watcher..."
nohup python3 -u filesystem_watcher.py > /tmp/filesystem_watcher.log 2>&1 &
FS_PID=$!
sleep 2
if ps -p $FS_PID > /dev/null; then
    echo "    Filesystem Watcher running (PID: $FS_PID)"
else
    echo "    Filesystem Watcher failed"
fi

# Approval Watcher
echo "  Starting Approval Watcher..."
nohup python3 -u approval_watcher.py > /tmp/approval_watcher.log 2>&1 &
APPROVAL_PID=$!
sleep 2
if ps -p $APPROVAL_PID > /dev/null; then
    echo "    Approval Watcher running (PID: $APPROVAL_PID)"
else
    echo "    Approval Watcher failed"
fi

# Facebook Watcher
echo "  Starting Facebook Watcher..."
nohup python3 -u facebook_watcher.py --interval 300 > /tmp/facebook_watcher.log 2>&1 &
FACEBOOK_PID=$!
sleep 2
if ps -p $FACEBOOK_PID > /dev/null; then
    echo "    Facebook Watcher running (PID: $FACEBOOK_PID)"
else
    echo "    Facebook Watcher failed (check META_ACCESS_TOKEN in .env)"
fi

# Instagram Watcher
echo "  Starting Instagram Watcher..."
nohup python3 -u instagram_watcher.py --interval 300 > /tmp/instagram_watcher.log 2>&1 &
INSTAGRAM_PID=$!
sleep 2
if ps -p $INSTAGRAM_PID > /dev/null; then
    echo "    Instagram Watcher running (PID: $INSTAGRAM_PID)"
else
    echo "    Instagram Watcher failed (check INSTAGRAM_BUSINESS_ID in .env)"
fi

# Twitter Watcher
echo "  Starting Twitter Watcher..."
nohup python3 -u twitter_watcher.py --interval 300 > /tmp/twitter_watcher.log 2>&1 &
TWITTER_PID=$!
sleep 2
if ps -p $TWITTER_PID > /dev/null; then
    echo "    Twitter Watcher running (PID: $TWITTER_PID)"
else
    echo "    Twitter Watcher failed (check TWITTER_BEARER_TOKEN in .env)"
fi

echo ""
echo "  Waiting for watchers to stabilize..."
sleep 5

# Step 3: Start Orchestrator (monitor-only - watchers already started above)
echo ""
echo "  Starting Orchestrator (health monitor mode)..."
nohup python3 orchestrator.py --health-only > /tmp/orchestrator.log 2>&1 &
ORCH_PID=$!
sleep 3

if ps -p $ORCH_PID > /dev/null; then
    echo "    Orchestrator running (PID: $ORCH_PID)"
else
    echo "    Orchestrator failed to start"
fi

# Step 3b: Start Health Monitor (Platinum tier)
echo ""
echo "  Starting Health Monitor (Platinum)..."
nohup python3 health_monitor.py > /tmp/health_monitor.log 2>&1 &
HEALTH_PID=$!
sleep 2

if ps -p $HEALTH_PID > /dev/null; then
    echo "    Health Monitor running (PID: $HEALTH_PID)"
else
    echo "    Health Monitor failed to start (non-critical)"
fi

# Step 4: Start Dashboard
echo ""
echo "  Starting Web Dashboard..."
nohup python3 dashboard.py > /tmp/dashboard.log 2>&1 &
DASHBOARD_PID=$!
sleep 3

if ps -p $DASHBOARD_PID > /dev/null; then
    echo "    Dashboard running (PID: $DASHBOARD_PID)"
else
    echo "    Dashboard failed to start"
fi

echo ""
echo "================================================================"
echo "  System Status"
echo "================================================================"
echo ""

# Show all running processes
RUNNING=$(ps aux | grep -E "gmail_watcher|linkedin_watcher|whatsapp_watcher|filesystem_watcher|approval_watcher|facebook_watcher|instagram_watcher|twitter_watcher|orchestrator|dashboard.py|health_monitor" | grep -v grep | wc -l)
echo "  Services Running: $RUNNING/11"
echo ""

ps aux | grep -E "gmail_watcher|linkedin_watcher|whatsapp_watcher|filesystem_watcher|approval_watcher|facebook_watcher|instagram_watcher|twitter_watcher|orchestrator|dashboard.py|health_monitor" | grep -v grep | awk '{print "    " $11 " (PID: " $2 ")"}'

echo ""
echo "================================================================"
echo "  Access Points"
echo "================================================================"
echo ""
echo "    Dashboard API:     http://localhost:9000"
echo "    Web UI:            http://localhost:3000  (run: cd web-ui && npm run dev)"
echo "    Gmail Log:         tail -f /tmp/gmail_watcher.log"
echo "    LinkedIn Log:      tail -f /tmp/linkedin_watcher.log"
echo "    WhatsApp Log:      tail -f /tmp/whatsapp_watcher.log"
echo "    Filesystem Log:    tail -f /tmp/filesystem_watcher.log"
echo "    Approval Log:      tail -f /tmp/approval_watcher.log"
echo "    Facebook Log:      tail -f /tmp/facebook_watcher.log"
echo "    Instagram Log:     tail -f /tmp/instagram_watcher.log"
echo "    Twitter Log:       tail -f /tmp/twitter_watcher.log"
echo "    Orchestrator Log:  tail -f /tmp/orchestrator.log"
echo "    Health Monitor:    tail -f /tmp/health_monitor.log"
echo "    Dashboard Log:     tail -f /tmp/dashboard.log"
echo ""

echo "================================================================"
echo "  Quick Commands"
echo "================================================================"
echo ""
echo "    Stop All:     pkill -f '_watcher|dashboard.py|orchestrator|health_monitor'"
echo "    Check Status: ps aux | grep -E 'watcher|dashboard|orchestrator|health_monitor'"
echo "    Social Logs:  tail -f /tmp/{facebook,instagram,twitter}_watcher.log"
echo "    Action Files: ls -lth AI_Employee_Vault/Needs_Action/"
echo ""

echo "================================================================"
echo "  System Startup Complete!"
echo "================================================================"
echo ""
echo "  Open your browser and visit: http://localhost:9000"
echo ""
