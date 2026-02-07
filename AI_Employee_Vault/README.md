# AI Employee Vault

Personal AI Employee system using Claude Code + Obsidian.

**Current Tier: Silver ✅ Complete**

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/              # Raw incoming items (drop files here)
├── Needs_Action/       # Items requiring AI processing
├── Pending_Approval/   # Items awaiting human approval
├── Approved/           # Human-approved actions
├── Rejected/           # Rejected actions
├── Done/               # Completed items
├── Logs/               # Audit logs (JSON)
├── Plans/              # AI-generated action plans
├── Briefings/          # CEO briefings and reports
├── Accounting/         # Financial tracking
├── Archive/            # Old completed items
├── Watchers/           # Python watcher scripts
├── MCP_Servers/        # MCP server configurations
├── Dashboard.md        # Real-time status overview
├── Company_Handbook.md # Rules of engagement
└── Business_Goals.md   # Targets and metrics
```

## Quick Start

### 1. Install Dependencies
```bash
cd Watchers
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API credentials
```

### 3. Start the System
```bash
# Option A: Start all watchers via orchestrator
python Watchers/orchestrator.py

# Option B: Start individual watchers
python Watchers/filesystem_watcher.py
python Watchers/gmail_watcher.py      # Needs credentials.json
python Watchers/whatsapp_watcher.py   # Needs QR scan
python Watchers/linkedin_watcher.py   # Needs login
```

### 4. Process Items
```bash
python Watchers/claude_processor.py --process-all  # Generate plans
python Watchers/claude_processor.py --briefing     # Daily briefing
```

### 5. Setup Scheduling
```bash
python Watchers/scheduler.py --run            # Built-in scheduler
python Watchers/scheduler.py --generate-cron  # Generate crontab
```

## Components

### Watchers (4 Total)
| File | Purpose |
|------|---------|
| `filesystem_watcher.py` | Monitor /Inbox for new files |
| `gmail_watcher.py` | Monitor Gmail for important emails |
| `whatsapp_watcher.py` | Monitor WhatsApp Web messages |
| `linkedin_watcher.py` | Monitor LinkedIn messages/notifications |

### Core Components
| File | Purpose |
|------|---------|
| `orchestrator.py` | Manages all watchers, health checks |
| `approval_watcher.py` | Human-in-the-loop workflow |
| `claude_processor.py` | AI reasoning, Plan.md generation |
| `scheduler.py` | Task scheduling (cron/Windows) |
| `MCP_Servers/email_mcp.py` | Email sending via Gmail API |

## Workflow

1. **Watchers** detect new items (email, WhatsApp, LinkedIn, files)
2. Items are saved to `/Needs_Action/`
3. **Claude Processor** analyzes items and creates `/Plans/`
4. Sensitive actions go to `/Pending_Approval/`
5. Human moves approved items to `/Approved/`
6. **MCP Servers** execute approved actions
7. Completed items move to `/Done/`

## Security

- Never commit `.env` files
- All payments require human approval
- All emails to new contacts require approval
- Audit logs retained for 90 days
- DRY_RUN=true for development/testing

## Tier Progress

### Bronze ✅ Complete
- [x] Obsidian vault setup
- [x] Dashboard.md and Company_Handbook.md
- [x] File system watcher working
- [x] Basic folder structure

### Silver ✅ Complete
- [x] Gmail Watcher
- [x] WhatsApp Watcher (Playwright)
- [x] LinkedIn Watcher with auto-posting
- [x] Master Orchestrator
- [x] Email MCP Server
- [x] Human-in-the-Loop approval workflow
- [x] Claude Processor (Plan.md generation)
- [x] Task Scheduler (cron/Windows support)

### Gold 🔜 Next
- [ ] Odoo Community accounting integration
- [ ] Facebook/Instagram integration
- [ ] Twitter (X) integration
- [ ] Weekly CEO Briefing
- [ ] Ralph Wiggum autonomous loop
