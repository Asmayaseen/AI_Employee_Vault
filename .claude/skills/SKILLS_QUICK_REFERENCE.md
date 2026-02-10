# Agent Skills - Quick Reference

All AI Employee functionality as Claude Code Agent Skills.

## 📚 Available Skills (7 Total)

### Watcher Skills

| Skill | Purpose | Trigger | File |
|-------|---------|---------|------|
| `gmail-monitor` | Check Gmail for new emails | Every 2 min / On-demand | `watchers/gmail-monitor.skill.md` |
| `whatsapp-monitor` | Watch WhatsApp messages | Every 30 sec / On-demand | `watchers/whatsapp-monitor.skill.md` |
| `linkedin-monitor` | LinkedIn messages + auto-post | Scheduled + continuous | `watchers/linkedin-monitor.skill.md` |
| `filesystem-monitor` | Watch drop folders | Real-time | `watchers/filesystem-monitor.skill.md` |
| `approval-monitor` | Execute approved actions | Every 10 sec | `watchers/approval-monitor.skill.md` |

### Processing Skills

| Skill | Purpose | Trigger | File |
|-------|---------|---------|------|
| `claude-processor` | AI reasoning & plan generation | Every 5 min / On-demand | `processing/claude-processor.skill.md` |

### Orchestration Skills

| Skill | Purpose | Trigger | File |
|-------|---------|---------|------|
| `orchestrator` | Master control & coordination | Always running | `orchestration/orchestrator.skill.md` |

## 🚀 How to Use

### Natural Language (Recommended)

Just ask Claude naturally:

```
"Check my email"                    → gmail-monitor
"Check WhatsApp for urgent messages" → whatsapp-monitor
"Post to LinkedIn"                   → linkedin-monitor
"Process all pending actions"        → claude-processor
"Show system status"                 → orchestrator
```

### Direct Command

```bash
# Invoke specific skill
claude skill gmail-monitor
claude skill whatsapp-monitor
claude skill claude-processor

# With arguments (if skill supports)
claude skill gmail-monitor --check-once
```

### Automated (via Orchestrator)

Start orchestrator and all skills run automatically:

```bash
# Foreground
python orchestrator.py

# Background (PM2 - recommended)
pm2 start orchestrator.py --name "ai-employee" --interpreter python3
pm2 save
```

## 📊 Skill Dependencies

### gmail-monitor
```bash
pip install google-auth-oauthlib google-api-python-client
# Needs: credentials.json, token.json
```

### whatsapp-monitor
```bash
pip install playwright
playwright install chromium
# Needs: .whatsapp_session/
```

### linkedin-monitor
```bash
pip install playwright
playwright install chromium
# Needs: .linkedin_session/
```

### filesystem-monitor
```bash
pip install watchdog
# No auth needed
```

### approval-monitor
```bash
# No dependencies
# Just needs folder structure
```

### claude-processor
```bash
# Requires:
# - Claude Code installed
# - Company_Handbook.md
# - Business_Goals.md
```

### orchestrator
```bash
# All of the above
pip install psutil  # For resource monitoring
```

## 🔧 Configuration

Skills read from `.env`:

```bash
# Intervals (seconds)
GMAIL_CHECK_INTERVAL=120
WHATSAPP_CHECK_INTERVAL=30
LINKEDIN_CHECK_INTERVAL=900
PROCESSOR_INTERVAL=300
APPROVAL_INTERVAL=10

# Paths
VAULT_PATH=/mnt/d/Ai-Employee/AI_Employee_Vault
GMAIL_CREDENTIALS_PATH=$VAULT_PATH/Watchers/credentials.json
WHATSAPP_SESSION_PATH=$VAULT_PATH/Watchers/.whatsapp_session
LINKEDIN_SESSION_PATH=$VAULT_PATH/Watchers/.linkedin_session

# Features
DRY_RUN=false
DEV_MODE=false
```

## 📋 Common Workflows

### Morning Startup

```bash
# 1. Start orchestrator
pm2 start orchestrator.py --name "ai-employee" --interpreter python3

# 2. Check status
pm2 status

# 3. View logs
pm2 logs ai-employee
```

### Check Email

```
User: "Check my email for urgent items"
Claude: [Invokes gmail-monitor skill]
        → Checks Gmail
        → Finds 3 unread
        → Creates action files
        → Reports to user
```

### Process Actions

```
User: "Process all pending actions"
Claude: [Invokes claude-processor skill]
        → Reads /Needs_Action (6 items)
        → Generates plans
        → Creates approvals (4 items)
        → Reports summary
```

### Approve & Execute

```
User reviews /Pending_Approval/
→ Moves approved items to /Approved/
approval-monitor detects and executes
→ Email sent / Post published / Payment made
→ Moved to /Done/
```

### Full Autonomous Cycle

```
[Continuous operation with orchestrator running]

09:30 - gmail-monitor: New email arrives
      → Creates action file

09:35 - claude-processor: Processes pending
      → Generates plan
      → Creates email draft approval

09:40 - User approves draft
      → Moves to /Approved/

09:40 - approval-monitor: Executes send
      → Email sent via Gmail API
      → Logged and archived

✅ Complete autonomous workflow!
```

## 🎯 Skill Chaining

Skills can be chained:

```
User: "Check email, process actions, and generate briefing"

Claude:
1. [Invokes gmail-monitor]
   → 3 new emails found

2. [Invokes claude-processor --process-all]
   → Plans generated

3. [Invokes claude-processor --briefing]
   → Daily briefing created

Result: Complete morning workflow executed!
```

## 🐛 Troubleshooting

### Skill not recognized
```bash
# Verify skills directory
ls -la .claude/skills/*/

# Should show 7 .skill.md files
```

### Watcher won't start
```bash
# Check dependencies
pip list | grep -E "(google|playwright|watchdog)"

# Check auth
ls -la Watchers/{credentials.json,token.json,.whatsapp_session}
```

### Orchestrator crashed
```bash
# Check logs
tail -f AI_Employee_Vault/Logs/orchestrator.log

# Restart
pm2 restart ai-employee

# Or manual
python orchestrator.py
```

## 📚 Full Documentation

Each skill includes complete documentation:
- Purpose and triggers
- Prerequisites
- Step-by-step instructions
- Error handling
- Real-world examples
- Integration points

Read full docs:
```
.claude/skills/watchers/          → Watcher skills
.claude/skills/processing/        → Processing skills
.claude/skills/orchestration/     → Orchestration skills
```

## ✅ Status Check

Verify all skills are ready:

```bash
# Count skills
ls -1 .claude/skills/*/*.skill.md | wc -l
# Should output: 7

# List all skills
ls .claude/skills/*/*.skill.md

# Expected output:
# watchers/gmail-monitor.skill.md
# watchers/whatsapp-monitor.skill.md
# watchers/linkedin-monitor.skill.md
# watchers/filesystem-monitor.skill.md
# watchers/approval-monitor.skill.md
# processing/claude-processor.skill.md
# orchestration/orchestrator.skill.md
```

---

**Created:** 2026-02-08
**Skills:** 7 Total (5 watchers, 1 processor, 1 orchestrator)
**Status:** ✅ Production Ready
