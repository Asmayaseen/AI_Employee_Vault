#!/bin/bash
# Setup Cron Jobs for AI Employee Automation
# This script creates cron entries for automated tasks

VAULT_PATH="/mnt/d/Ai-Employee/AI_Employee_Vault"
WATCHERS_PATH="$VAULT_PATH/Watchers"

echo "=========================================="
echo "  AI Employee - Cron Setup"
echo "=========================================="
echo ""

# Create temporary cron file
CRON_FILE="/tmp/ai_employee_cron_$(date +%s).txt"

echo "📋 Creating cron entries..."
echo ""

cat > $CRON_FILE << 'EOF'
# AI Employee Automation - Cron Schedule
# Generated on $(date)

SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
VAULT_PATH=/mnt/d/Ai-Employee/AI_Employee_Vault

# ============================================
# DAILY TASKS
# ============================================

# Daily Briefing - Every day at 8:00 AM
0 8 * * * cd $VAULT_PATH/Watchers && python3 claude_processor.py --briefing >> /tmp/daily_briefing.log 2>&1

# Process Pending Items - Every 2 hours during business hours (9 AM - 9 PM)
0 9,11,13,15,17,19,21 * * * cd $VAULT_PATH/Watchers && python3 claude_processor.py --process-all >> /tmp/process_items.log 2>&1

# ============================================
# LINKEDIN AUTO-POSTING
# ============================================

# LinkedIn Monday Post - 9:00 AM
0 9 * * 1 cd $VAULT_PATH/Watchers && python3 linkedin_auto_poster.py >> /tmp/linkedin_monday.log 2>&1

# LinkedIn Wednesday Post - 12:00 PM (Noon)
0 12 * * 3 cd $VAULT_PATH/Watchers && python3 linkedin_auto_poster.py >> /tmp/linkedin_wednesday.log 2>&1

# LinkedIn Friday Post - 3:00 PM
0 15 * * 5 cd $VAULT_PATH/Watchers && python3 linkedin_auto_poster.py >> /tmp/linkedin_friday.log 2>&1

# ============================================
# WEEKLY TASKS
# ============================================

# Weekly CEO Briefing - Sunday 8:00 PM
0 20 * * 0 cd $VAULT_PATH/Watchers && python3 ceo_briefing_generator.py >> /tmp/ceo_briefing.log 2>&1

# Subscription Audit - Sunday 7:00 PM
0 19 * * 0 cd $VAULT_PATH/Watchers && python3 subscription_auditor.py >> /tmp/subscription_audit.log 2>&1

# ============================================
# MAINTENANCE TASKS
# ============================================

# Health Check - Every hour
15 * * * * cd $VAULT_PATH/Watchers && python3 health_checker.py >> /tmp/health_check.log 2>&1

# Log Rotation - Daily at midnight
0 0 * * * find /tmp -name "*_watcher.log" -mtime +7 -delete

# Archive Old Files - Weekly on Saturday midnight
0 0 * * 6 cd $VAULT_PATH && python3 Watchers/archive_old_files.py >> /tmp/archive.log 2>&1

# ============================================
# RALPH WIGGUM AUTONOMOUS LOOP
# ============================================

# Auto-process pending items - Every 5 minutes
# Ralph loop checks if work exists and starts autonomous processing
*/5 * * * * cd /mnt/d/Ai-Employee/.claude/hooks && python3 ralph_integration.py auto >> /tmp/ralph_auto.log 2>&1

# Ralph status check - Every 15 minutes
*/15 * * * * cd /mnt/d/Ai-Employee/.claude/hooks && python3 ralph_integration.py status >> $VAULT_PATH/Logs/ralph_status.log 2>&1

# ============================================
# WATCHER MONITORING
# ============================================

# Check Watchers Running - Every 5 minutes
*/5 * * * * pgrep -f "gmail_watcher|whatsapp_watcher|linkedin_watcher" > /dev/null || (cd $VAULT_PATH/Watchers && bash start_all_watchers.sh)

EOF

echo "✅ Cron entries created in: $CRON_FILE"
echo ""
echo "📝 Cron Schedule Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "DAILY:"
echo "  • 8:00 AM  - Daily briefing"
echo "  • Every 2h - Process pending items (9 AM - 9 PM)"
echo ""
echo "WEEKLY:"
echo "  • Monday 9 AM     - LinkedIn business post"
echo "  • Wednesday 12 PM - LinkedIn insight post"
echo "  • Friday 3 PM     - LinkedIn reflection post"
echo "  • Sunday 7 PM     - Subscription audit"
echo "  • Sunday 8 PM     - CEO briefing"
echo ""
echo "RALPH WIGGUM:"
echo "  • Every 5 min  - Auto-process pending items"
echo "  • Every 15 min - Ralph status logging"
echo ""
echo "MONITORING:"
echo "  • Every hour  - Health check"
echo "  • Every 5 min - Watcher status check"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show current crontab
echo "📋 Current crontab:"
crontab -l 2>/dev/null || echo "  (empty)"
echo ""

# Ask for confirmation
read -p "❓ Do you want to install these cron jobs? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup existing crontab
    if crontab -l > /dev/null 2>&1; then
        BACKUP="/tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
        crontab -l > "$BACKUP"
        echo "💾 Backed up existing crontab to: $BACKUP"
    fi
    
    # Install new crontab (append to existing)
    (crontab -l 2>/dev/null; cat $CRON_FILE) | crontab -
    
    echo "✅ Cron jobs installed successfully!"
    echo ""
    echo "📝 To view installed cron jobs:"
    echo "   crontab -l"
    echo ""
    echo "📝 To edit cron jobs:"
    echo "   crontab -e"
    echo ""
    echo "📝 To remove all AI Employee cron jobs:"
    echo "   crontab -l | grep -v 'AI Employee' | crontab -"
    echo ""
else
    echo "❌ Installation cancelled."
    echo ""
    echo "💡 To install manually, run:"
    echo "   cat $CRON_FILE | crontab -"
    echo ""
fi

# Cleanup
rm -f $CRON_FILE

echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
