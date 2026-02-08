#!/bin/bash
# Master Control Script - AI Employee System v2.0
# Starts all watchers + dashboard

export DISPLAY=:0

echo "════════════════════════════════════════════════════════════"
echo "  🤖 AI Employee System v2.0 - Starting All Services"
echo "════════════════════════════════════════════════════════════"
echo ""

# Change to watchers directory
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers || exit 1

# Step 1: Stop any running instances
echo "⏹️  Stopping existing services..."
pkill -f "gmail_watcher" 2>/dev/null
pkill -f "linkedin_watcher" 2>/dev/null
pkill -f "whatsapp_watcher" 2>/dev/null
pkill -f "dashboard.py" 2>/dev/null
sleep 3

# Clean up lock files
rm -f .whatsapp_session/SingletonLock 2>/dev/null
rm -f .linkedin_session/SingletonLock 2>/dev/null

echo "✅ Cleanup complete"
echo ""

# Step 2: Start all watchers
echo "🚀 Starting Watchers..."
echo ""

# Gmail Watcher
echo "📧 Starting Gmail Watcher..."
nohup python3 -u gmail_watcher.py --interval 120 > /tmp/gmail_watcher.log 2>&1 &
GMAIL_PID=$!
sleep 2
if ps -p $GMAIL_PID > /dev/null; then
    echo "   ✅ Gmail Watcher running (PID: $GMAIL_PID)"
else
    echo "   ❌ Gmail Watcher failed"
fi

# LinkedIn Watcher
echo "💼 Starting LinkedIn Watcher..."
nohup python3 -u linkedin_watcher.py --interval 300 > /tmp/linkedin_watcher.log 2>&1 &
LINKEDIN_PID=$!
sleep 2
if ps -p $LINKEDIN_PID > /dev/null; then
    echo "   ✅ LinkedIn Watcher running (PID: $LINKEDIN_PID)"
else
    echo "   ❌ LinkedIn Watcher failed"
fi

# WhatsApp Watcher
echo "💬 Starting WhatsApp Watcher..."
nohup python3 -u whatsapp_watcher.py --interval 180 > /tmp/whatsapp_watcher.log 2>&1 &
WHATSAPP_PID=$!
sleep 2
if ps -p $WHATSAPP_PID > /dev/null; then
    echo "   ✅ WhatsApp Watcher running (PID: $WHATSAPP_PID)"
else
    echo "   ❌ WhatsApp Watcher failed"
fi

echo ""
echo "⏳ Waiting for watchers to stabilize..."
sleep 5

# Step 3: Start Dashboard
echo ""
echo "🌐 Starting Web Dashboard..."
nohup python3 dashboard.py > /tmp/dashboard.log 2>&1 &
DASHBOARD_PID=$!
sleep 3

if ps -p $DASHBOARD_PID > /dev/null; then
    echo "   ✅ Dashboard running (PID: $DASHBOARD_PID)"
else
    echo "   ❌ Dashboard failed to start"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  📊 System Status"
echo "════════════════════════════════════════════════════════════"
echo ""

# Show all running processes
RUNNING=$(ps aux | grep -E "gmail_watcher|linkedin_watcher|whatsapp_watcher|dashboard.py" | grep -v grep | wc -l)
echo "✅ Services Running: $RUNNING/4"
echo ""

ps aux | grep -E "gmail_watcher|linkedin_watcher|whatsapp_watcher|dashboard.py" | grep -v grep | awk '{print "   🔄 " $11 " (PID: " $2 ")"}'

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  🌐 Access Points"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "   🌐 Dashboard:    http://localhost:9000"
echo "   📧 Gmail Log:    tail -f /tmp/gmail_watcher.log"
echo "   💼 LinkedIn Log: tail -f /tmp/linkedin_watcher.log"
echo "   💬 WhatsApp Log: tail -f /tmp/whatsapp_watcher.log"
echo "   📊 Dashboard Log: tail -f /tmp/dashboard.log"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  📝 Quick Commands"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "   🛑 Stop All:     pkill -f '_watcher|dashboard.py'"
echo "   📊 Check Status: ps aux | grep -E 'watcher|dashboard'"
echo "   📁 Action Files: ls -lth AI_Employee_Vault/Needs_Action/"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  ✅ System Startup Complete!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  🎉 Open your browser and visit: http://localhost:9000"
echo ""
