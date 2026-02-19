# orchestrator

Master control system that manages all watchers, monitors health, and coordinates the AI Employee workflow.

## What you do

You are the central nervous system of the AI Employee. You start/stop/restart watchers, monitor their health, coordinate workflows, and ensure the entire system runs smoothly 24/7.

## When to use

- To start the entire AI Employee system
- To monitor system health and uptime
- To restart failed components
- To coordinate all watchers and processors
- When user asks to "start AI Employee" or "run orchestrator"

## Prerequisites

- All watcher scripts available
- Python dependencies installed
- Vault folder structure complete
- Environment variables configured

## Instructions

### Step 1: Pre-flight Check

Verify all components ready:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Check all watchers exist
ls -1 {gmail,whatsapp,linkedin,filesystem,approval}_watcher.py

# Check orchestrator
ls -1 orchestrator.py claude_processor.py

# Check vault structure
cd ..
ls -d {Inbox,Needs_Action,Plans,Pending_Approval,Approved,Rejected,Done,Logs}
```

### Step 2: Start Orchestrator

**Option A: Foreground (for testing)**
```bash
python orchestrator.py
```

**Option B: Background with PM2 (recommended)**
```bash
pm2 start orchestrator.py --name "ai-employee" --interpreter python3
pm2 save
pm2 startup  # Enable auto-start on reboot
```

**Option C: Background with nohup**
```bash
nohup python orchestrator.py > /dev/null 2>&1 &
echo $! > /tmp/orchestrator.pid
```

### Step 3: Orchestrator Workflow

The orchestrator manages this workflow:

```
┌─────────────────────────────────────────────────────┐
│              ORCHESTRATOR (Master)                  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Health Monitor (checks every 60s)           │  │
│  │  - Watcher process status                    │  │
│  │  - Disk space                                │  │
│  │  - Memory usage                              │  │
│  │  - API quota status                          │  │
│  └──────────────────────────────────────────────┘  │
└───────────┬─────────────────────────────────────────┘
            │
    ┌───────┼───────┬───────┬──────────┬─────────┐
    │       │       │       │          │         │
    ▼       ▼       ▼       ▼          ▼         ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌───────────┐
│ Gmail  ││WhatsApp││LinkedIn││FileSys ││ Approval  │
│Watcher ││Watcher ││Watcher ││Watcher ││ Watcher   │
│(120s)  ││ (30s)  ││ (15m)  ││(realtime)││ (10s)    │
└────┬───┘└────┬───┘└────┬───┘└────┬───┘└─────┬─────┘
     │         │         │         │          │
     └────────┬┴─────────┴─────────┴──────────┘
              │
              ▼
      ┌───────────────┐
      │ /Needs_Action │
      └───────┬───────┘
              │
              ▼
      ┌──────────────────┐
      │ Claude Processor │
      │  (every 5 min)   │
      └────────┬─────────┘
              │
     ┌────────┴────────┐
     │                 │
     ▼                 ▼
┌─────────┐    ┌──────────────┐
│ /Plans/ │    │/Pending_     │
│         │    │  Approval/   │
└─────────┘    └──────┬───────┘
                      │
                      ▼
              ┌──────────────┐
              │  /Approved/  │
              └──────┬───────┘
                     │
                     ▼
              ┌─────────────┐
              │   Execute   │
              │   Actions   │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │   /Done/    │
              └─────────────┘
```

### Step 4: Monitoring Dashboard

The orchestrator maintains real-time status:

```
═══════════════════════════════════════════════════════
        AI EMPLOYEE ORCHESTRATOR v1.0
═══════════════════════════════════════════════════════

System Status: ✅ HEALTHY
Uptime: 2 days, 14 hours, 23 minutes

Watchers Status:
  ✅ Gmail Watcher      - Running  (Last check: 30s ago)
  ✅ WhatsApp Watcher   - Running  (Last check: 5s ago)
  ✅ LinkedIn Watcher   - Running  (Last check: 2m ago)
  ✅ Filesystem Watcher - Running  (Active)
  ✅ Approval Watcher   - Running  (Last check: 3s ago)

Processing Queue:
  Needs_Action:     3 items
  Pending_Approval: 2 items
  Processing:       1 item
  Completed today:  12 items

System Health:
  CPU Usage:    12%
  Memory:       245 MB / 8 GB
  Disk Space:   45 GB free
  Network:      Online

Recent Activity:
  [12:45] Gmail: New email from client@example.com
  [12:43] Processor: Generated plan for client inquiry
  [12:40] Approval: Email draft approved and sent
  [12:35] LinkedIn: Scheduled post created

Next Scheduled Tasks:
  [13:00] Claude Processor (5 min)
  [15:00] LinkedIn Auto-Post (Friday)
  [20:00] Daily Briefing Generation

Press Ctrl+C to stop gracefully...
═══════════════════════════════════════════════════════
```

### Step 5: Auto-Recovery

The orchestrator automatically handles failures:

**Watcher Crash:**
1. Detect process exit
2. Log error
3. Wait 10 seconds
4. Restart watcher
5. If crashes 3 times in 5 minutes, alert user and pause

**API Rate Limit:**
1. Detect rate limit error
2. Pause affected watcher
3. Wait for reset (typically 1 hour)
4. Resume automatically

**Disk Space Low:**
1. Detect < 5GB free space
2. Archive old logs
3. Compress old /Done files
4. Alert user if still < 2GB

**Memory High:**
1. Detect > 80% memory usage
2. Restart watchers one by one
3. Clear cache
4. Alert if issue persists

## Output format

```
Starting AI Employee Orchestrator...

[12:30:00] Initializing system...
[12:30:01] ✅ Vault structure verified
[12:30:02] ✅ Environment variables loaded
[12:30:03] ✅ Company Handbook loaded
[12:30:04] ✅ Business Goals loaded

[12:30:05] Starting watchers...
[12:30:06] ✅ Gmail Watcher started (PID: 12345)
[12:30:07] ✅ WhatsApp Watcher started (PID: 12346)
[12:30:08] ✅ LinkedIn Watcher started (PID: 12347)
[12:30:09] ✅ Filesystem Watcher started (PID: 12348)
[12:30:10] ✅ Approval Watcher started (PID: 12349)

[12:30:11] ✅ All watchers operational
[12:30:12] ✅ Orchestrator ready

System running - monitoring every 60 seconds
Logs: /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/orchestrator.log
```

## Control commands

### Status Check
```bash
# Using PM2
pm2 status ai-employee

# Using PID file
ps -p $(cat /tmp/orchestrator.pid)
```

### Stop Orchestrator
```bash
# Graceful shutdown (PM2)
pm2 stop ai-employee

# Kill process
kill $(cat /tmp/orchestrator.pid)
```

### Restart Orchestrator
```bash
pm2 restart ai-employee
```

### View Logs
```bash
# Real-time
tail -f AI_Employee_Vault/Logs/orchestrator.log

# PM2 logs
pm2 logs ai-employee
```

## Configuration

Edit `orchestrator.py` to configure:

```python
# Watcher intervals (seconds)
GMAIL_INTERVAL = 120      # Check every 2 minutes
WHATSAPP_INTERVAL = 30    # Check every 30 seconds
LINKEDIN_INTERVAL = 900   # Check every 15 minutes
APPROVAL_INTERVAL = 10    # Check every 10 seconds

# Processing intervals
PROCESSOR_INTERVAL = 300  # Run every 5 minutes
BRIEFING_TIME = "08:00"   # Daily briefing at 8 AM

# Health check
HEALTH_CHECK_INTERVAL = 60  # Check every minute
MAX_RESTART_ATTEMPTS = 3
RESTART_WINDOW = 300        # 5 minutes

# Resource limits
MAX_MEMORY_MB = 500
MIN_DISK_GB = 2
```

## Integration points

- **All Watchers**: Managed and monitored
- **Claude Processor**: Triggered on schedule
- **Dashboard**: Status updates
- **Logs**: Comprehensive logging
- **Cron**: Scheduled tasks

## Error handling

**Orchestrator crashes:**
- Use PM2 for auto-restart
- Or set up systemd service
- Logs preserved for debugging

**All watchers fail:**
- Check internet connection
- Verify API credentials
- Check system resources
- Review logs

**Performance degradation:**
- Reduce watcher intervals
- Increase processing intervals
- Check disk I/O
- Monitor memory leaks

## Examples

**Example 1: Morning startup**
```bash
pm2 start orchestrator.py --name "ai-employee" --interpreter python3
→ All watchers start
→ System begins monitoring
→ 8 AM: Daily briefing generated
→ Watchers detect new emails, messages
→ Processor creates plans
→ User approves actions
→ Actions executed
→ All day: Continuous autonomous operation
```

**Example 2: Watcher recovery**
```
[14:30] WhatsApp Watcher crashed (network timeout)
[14:30] Orchestrator detected failure
[14:30] Waiting 10 seconds...
[14:40] Restarting WhatsApp Watcher
[14:41] ✅ WhatsApp Watcher resumed
[14:41] No data loss - continues from last checkpoint
```

## Success criteria

✅ All watchers running continuously
✅ Health checks passing
✅ Auto-recovery working
✅ Processing queue flowing
✅ Actions executing
✅ Logs being written
✅ System uptime > 99%

## Performance targets

- Watcher restart: < 30 seconds
- Health check: < 5 seconds
- Memory footprint: < 500 MB total
- CPU usage: < 20% average
- Uptime: > 99.5%

---

**Skill Type:** Orchestration (Master Control)
**Tier:** Silver (Essential for autonomous operation)
**Automation:** Always running in background
**Criticality:** High (Single point of coordination)
