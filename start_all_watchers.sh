#!/bin/bash
# Master Startup Script for All Watchers
# AI Employee System v2.0

export DISPLAY=:0
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

echo "════════════════════════════════════════════════"
echo "  AI Employee - Starting All Watchers"
echo "════════════════════════════════════════════════"
echo ""

# Stop any existing instances
echo "⏹️  Stopping existing watchers..."
pkill -f "gmail_watcher" 2>/dev/null
pkill -f "linkedin_watcher" 2>/dev/null
pkill -f "whatsapp_watcher" 2>/dev/null
sleep 2

# Clean up old lock files
rm -f .whatsapp_session/SingletonLock 2>/dev/null
rm -f .linkedin_session/SingletonLock 2>/dev/null

echo "✅ Cleaned up old processes"
echo ""

# Start Gmail Watcher (no display needed)
echo "📧 Starting Gmail Watcher..."
nohup python3 -u gmail_watcher.py --interval 120 > /tmp/gmail_watcher.log 2>&1 &
GMAIL_PID=$!
sleep 2
if ps -p $GMAIL_PID > /dev/null; then
    echo "   ✅ Gmail Watcher running (PID: $GMAIL_PID)"
else
    echo "   ❌ Gmail Watcher failed to start"
fi
echo ""

# Start LinkedIn Watcher (needs display)
echo "💼 Starting LinkedIn Watcher..."
nohup python3 -u linkedin_watcher.py --interval 300 > /tmp/linkedin_watcher.log 2>&1 &
LINKEDIN_PID=$!
sleep 2
if ps -p $LINKEDIN_PID > /dev/null; then
    echo "   ✅ LinkedIn Watcher running (PID: $LINKEDIN_PID)"
else
    echo "   ❌ LinkedIn Watcher failed to start"
fi
echo ""

# Start WhatsApp Watcher (needs display)
echo "💬 Starting WhatsApp Watcher..."
nohup python3 -u whatsapp_watcher.py --interval 180 > /tmp/whatsapp_watcher.log 2>&1 &
WHATSAPP_PID=$!
sleep 2
if ps -p $WHATSAPP_PID > /dev/null; then
    echo "   ✅ WhatsApp Watcher running (PID: $WHATSAPP_PID)"
else
    echo "   ❌ WhatsApp Watcher failed to start"
fi
echo ""

echo "════════════════════════════════════════════════"
echo "  Status Summary"
echo "════════════════════════════════════════════════"
echo ""
ps aux | grep -E "gmail_watcher|linkedin_watcher|whatsapp_watcher" | grep -v grep | awk '{print "  🔄 " $11 " (PID: " $2 ")"}'
echo ""

echo "📊 Check logs:"
echo "   Gmail:    tail -f /tmp/gmail_watcher.log"
echo "   LinkedIn: tail -f /tmp/linkedin_watcher.log"
echo "   WhatsApp: tail -f /tmp/whatsapp_watcher.log"
echo ""

echo "🛑 To stop all: pkill -f '_watcher'"
echo ""
echo "✅ All watchers started!"
