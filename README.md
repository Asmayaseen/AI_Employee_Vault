---
title: AI Employee
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Personal AI Employee - Platinum Tier Implementation

**Hackathon 0: Building Autonomous FTEs in 2026**
**Tier: Platinum - Always-On Cloud + Local Executive**

> Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

An autonomous Digital FTE (Full-Time Equivalent) that manages personal and business affairs 24/7 using Claude Code as the reasoning engine and Obsidian as the management dashboard. The Platinum tier adds a dual-agent cloud/local architecture with automatic failover and vault synchronization.

---

## Architecture

```
External Sources (Gmail, WhatsApp, LinkedIn, Facebook, Instagram, Twitter/X, Odoo)
        |
        v
+-----------------------------+
|    PERCEPTION LAYER         |  Python Watcher scripts
|  Gmail | WhatsApp | LinkedIn|  monitor external sources
|  FB | IG | Twitter | Files  |  and create action files
+-------------+---------------+
              |
              v
+-----------------------------+
|    OBSIDIAN VAULT (Local)   |  /Needs_Action -> /Plans ->
|  Dashboard | Company Rules  |  /Pending_Approval -> /Done
|  Business Goals | Briefings |  Claim-by-move prevents races
+-------------+---------------+
              |
       +------+------+
       |             |
       v             v
+-------------+  +-------------------+
| CLOUD AGENT |  |   LOCAL AGENT     |
| (draft_only)|  | (full execution)  |
| Email triage|  | Approvals, HITL   |
| Social draft|  | WhatsApp, payments|
+------+------+  +--------+----------+
       |     Vault Sync   |
       +------ Git -------+
              |
              v
+-----------------------------+
|    REASONING LAYER          |  Claude Code processes tasks,
|    Claude Code + Ralph Loop |  generates plans, creates
|    Read -> Think -> Plan    |  approval requests
+-------------+---------------+
              |
              v
+-----------------------------+
|    ACTION LAYER (MCP)       |  MCP Servers execute approved
|  Email | Odoo | Social      |  actions via external APIs
|  HITL Approval Required     |
+-----------------------------+
```

---

## Features by Tier

### Bronze (Complete)
- Obsidian vault with Dashboard.md, Company_Handbook.md
- Gmail + Filesystem Watcher scripts
- Claude Code reading/writing vault files
- Folder structure: /Inbox, /Needs_Action, /Done
- Agent Skills for all AI functionality

### Silver (Complete)
- Gmail + WhatsApp + LinkedIn + Filesystem Watchers
- LinkedIn auto-poster (Mon/Wed/Fri)
- Claude reasoning loop generating Plan.md files
- Email MCP Server (send, draft, search)
- Human-in-the-loop approval workflow
- Cron scheduling for all automation

### Gold (Complete)
- **Odoo MCP Server** (JSON-RPC) — Invoices, customers, financial summaries
- **Social MCP Server** — Facebook, Instagram, Twitter/X posting + summaries
- **Facebook Watcher** — Monitor inbox/comments via Graph API v19.0
- **Instagram Watcher** — Monitor DMs/mentions, auto-post via container model
- **Twitter/X Watcher** — Monitor DMs/mentions, auto-post via API v2
- **Social Auto-Poster** — Unified content generation for FB/IG/TW
- **Error Recovery** — Retry handler with exponential backoff, watchdog, graceful degradation
- **Structured Audit Logging** — Section 6.3 compliant JSON logs with 90-day retention
- **CEO Briefing with Accounting Audit** — Odoo financial integration, subscription audit
- **Ralph Wiggum Loop** — Autonomous multi-step task completion via Stop hook
- End-to-end pipeline tested

### Platinum (Complete — Cloud Deployment Pending)
- **Dual-Agent Architecture** — Cloud (draft_only) + Local (full execution)
- **Vault Sync** — Git-based bidirectional sync, local-wins conflict resolution
- **Work Zone Routing** — Task routing rules in `zones.json`, auto-failover after 3 failures
- **Claim-by-Move Protocol** — Atomic `os.rename()` prevents race conditions between agents
- **Health Monitor** — HTTP health checks every 30s, SMTP alerts on failure
- **Draft-Only Mode** — Cloud agent drafts; Local agent sends after human approval
- **Domain Vault Structure** — `/Needs_Action/email/`, `/social/`, `/accounting/`, `/general/`
- **Next.js Web Dashboard** — Real-time dashboard with dark mode, approvals, logs, system health
- **Systemd Services** — 4 production service units for cloud VPS deployment
- **Platinum Demo Gate** — Email arrives offline → Cloud drafts → Vault sync → Local approves → MCP sends

---

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js v24+ LTS
- Claude Code (active subscription)
- Obsidian v1.10.6+
- Docker (for Odoo)

### Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd Ai-Employee

# 2. Install Python dependencies
pip install -r AI_Employee_Vault/Watchers/requirements.txt
playwright install chromium

# 3. Configure environment
cp AI_Employee_Vault/.env.example AI_Employee_Vault/.env
# Edit .env with your credentials

# 4. Start Odoo (Docker)
cd MCP_Servers/odoo-mcp
docker-compose up -d
cd ../..

# 5. Setup Email MCP
cd MCP_Servers/email-mcp
npm install
cd ../..

# 6. Start all watchers + orchestrator + health monitor
bash start_everything.sh

# 7. Start Web Dashboard (optional)
cd AI_Employee_Vault/web-ui
npm install
npm run dev
# Open http://localhost:3000

# 8. Run pipeline test
python AI_Employee_Vault/Watchers/test_pipeline.py
```

### MCP Server Configuration

Add to `~/.claude.json` (Claude Code settings):
```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["/path/to/MCP_Servers/email-mcp/index.js"]
    },
    "odoo": {
      "command": "python3",
      "args": ["/path/to/MCP_Servers/odoo-mcp/server.py"]
    },
    "social": {
      "command": "python3",
      "args": ["/path/to/MCP_Servers/social-mcp/server.py"]
    }
  }
}
```

### Platinum: Dual-Agent Setup

```bash
# Local agent (full execution) — runs on your laptop
AGENT_MODE=full AGENT_NAME=local bash start_everything.sh

# Cloud agent (draft only) — runs on VPS
# AGENT_MODE=draft_only AGENT_NAME=cloud bash start_everything.sh
# (Requires VPS with VAULT_SYNC_REMOTE and git configured)
```

---

## Project Structure

```
Ai-Employee/
├── AI_Employee_Vault/              # Obsidian Vault (Memory/GUI)
│   ├── Dashboard.md                # Real-time status
│   ├── Company_Handbook.md         # Rules of engagement
│   ├── Business_Goals.md           # Revenue targets & metrics
│   ├── zones.json                  # Zone routing configuration
│   ├── Needs_Action/               # Incoming tasks (email/, social/, accounting/, general/)
│   ├── Plans/                      # Generated action plans
│   ├── Pending_Approval/           # HITL approval queue
│   ├── In_Progress/                # Claimed tasks (cloud/, local/)
│   ├── Approved/                   # Approved actions
│   ├── Done/                       # Completed tasks
│   ├── Briefings/                  # CEO briefing reports
│   ├── Updates/                    # Cloud agent writes here
│   ├── Logs/                       # Structured audit logs + health/ + alerts/
│   ├── Watchers/                   # Python watcher scripts
│   │   ├── orchestrator.py         # Master control + zone-aware routing
│   │   ├── scheduler.py            # APScheduler (vault_sync, zone_failover every 2min)
│   │   ├── health_monitor.py       # HTTP health checks + alert integration (Platinum)
│   │   ├── gmail_watcher.py        # Email monitoring
│   │   ├── linkedin_watcher.py     # LinkedIn monitoring
│   │   ├── linkedin_auto_poster.py # Auto-post Mon/Wed/Fri
│   │   ├── whatsapp_watcher.py     # WhatsApp monitoring
│   │   ├── facebook_watcher.py     # Facebook monitoring (Graph API)
│   │   ├── instagram_watcher.py    # Instagram monitoring
│   │   ├── twitter_watcher.py      # Twitter/X monitoring (API v2)
│   │   ├── social_auto_poster.py   # Unified social content generation
│   │   ├── filesystem_watcher.py   # File drop monitoring
│   │   ├── approval_watcher.py     # HITL approval + draft-only mode
│   │   ├── claude_processor.py     # AI reasoning engine
│   │   ├── ceo_briefing_generator.py # Weekly CEO briefing + Odoo audit
│   │   ├── dashboard.py            # Flask API (Gold + 9 Platinum endpoints)
│   │   ├── base_watcher.py         # Abstract base class
│   │   ├── retry_handler.py        # Exponential backoff
│   │   ├── graceful_degradation.py # Service fallback queues
│   │   ├── watchdog.py             # Process health monitor
│   │   ├── audit_logger.py         # Structured JSON logging
│   │   ├── utils/
│   │   │   ├── vault_sync.py       # Git-based bidirectional vault sync (Platinum)
│   │   │   ├── work_zones.py       # Zone routing + auto-failover (Platinum)
│   │   │   ├── claim_task.py       # Atomic claim-by-move protocol (Platinum)
│   │   │   └── alert_manager.py    # SMTP alert system (Platinum)
│   │   └── test_pipeline.py        # E2E pipeline test
│   └── web-ui/                     # Next.js Web Dashboard (Platinum)
│       ├── app/                    # Pages: Dashboard, Approvals, Vault, Logs, System
│       └── components/             # Header, Sidebar, WatcherCard, etc.
├── MCP_Servers/                    # Action Layer
│   ├── email-mcp/                  # Gmail MCP (Node.js, OAuth 2.0)
│   ├── odoo-mcp/                   # Odoo ERP MCP (Python, JSON-RPC)
│   │   ├── server.py
│   │   ├── odoo_client.py          # JSON-RPC client
│   │   └── docker-compose.yml      # Odoo 18 + PostgreSQL 17
│   └── social-mcp/                 # Social Media MCP (Python)
│       ├── server.py
│       └── adapters/               # Facebook, Instagram, Twitter
├── skills/                         # Agent Skill definitions
│   ├── bronze/                     # Bronze tier skills
│   ├── silver/                     # Silver tier skills
│   ├── gold/                       # Gold tier skills (7 skills)
│   └── platinum/                   # Platinum tier skills (5 skills)
├── .claude/                        # Claude Code config
│   ├── hooks/stop.py               # Ralph Wiggum loop
│   └── skills/                     # Claude Code agent skills
├── start_everything.sh             # Master startup script v3.0
├── SECURITY_DISCLOSURE.md          # Credential handling details
└── 0-hackathon.md                  # Hackathon architecture reference
```

---

## Key Design Decisions

1. **JSON-RPC over XML-RPC** for Odoo — Odoo 19+ compatible architecture
2. **File-based HITL** — Approval via folder moves (Obsidian-native, no extra UI needed)
3. **MCP per domain** — Separate servers for email, ERP, social (clean separation)
4. **Claim-by-move protocol** — `os.rename()` is atomic; prevents two agents processing same task
5. **Local-wins conflict resolution** — Vault sync always favors local changes (safe for HITL)
6. **Graceful degradation** — Queue actions when services are down, never auto-retry payments
7. **Structured audit logs** — JSON with 90-day retention, query/filter support
8. **Ralph Wiggum Loop** — Stop hook keeps Claude iterating until task complete
9. **Draft-only Cloud Agent** — Cloud never executes sensitive actions; only Local can send/post/pay

---

## Dashboard (Web UI)

The Next.js dashboard runs on `http://localhost:3000` and provides:

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Live stats, watcher status, pending actions, recent logs |
| Approvals | `/approvals` | Review and approve/reject pending HITL requests |
| Vault | `/vault` | Browse vault files and directories |
| Logs | `/logs` | Full audit log viewer with filtering |
| System | `/system` | CPU/memory/disk, service health, Cloud/Zone/Vault sync status |

---

## API Endpoints (Flask, port 9000)

### Gold Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /api/status` | System status + watcher health + statistics |
| `GET /api/logs` | Today's audit logs |
| `GET /api/tasks` | Task tracking |
| `GET /api/health` | Overall health |

### Platinum Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /api/vault/sync/status` | Current git sync status |
| `POST /api/vault/sync/trigger` | Manual sync trigger |
| `GET /api/zones/status` | Zone configuration and state |
| `POST /api/zones/switch` | Switch active zone `{"zone": "cloud"}` |
| `GET /api/zones/health` | Health of both zones |
| `GET /api/health/detailed` | Detailed per-service health |
| `GET /api/alerts` | Recent alert history |
| `GET /api/claims` | Task claim status |
| `GET /api/platinum/status` | All Platinum module status |

---

## Security

See [SECURITY_DISCLOSURE.md](./SECURITY_DISCLOSURE.md) for full credential handling details.

- Credentials stored in `.env` (gitignored, never committed)
- Browser sessions (WhatsApp, LinkedIn) in gitignored session directories
- All sensitive actions require HITL approval before execution
- Cloud agent operates in `draft_only` mode — cannot send emails, post, or make payments
- Payments never auto-approved above $100 threshold
- Audit logs track every action with actor, target, approval status, and result
- `DRY_RUN=true` mode for safe development without external side effects
- Vault sync excludes `.env`, credentials, and browser sessions

---

## Tier Declaration

**Platinum Tier — Always-On Cloud + Local Executive**

| Requirement | Status |
|-------------|--------|
| All Gold requirements | ✅ Complete |
| Cloud 24/7 health monitoring | ✅ `health_monitor.py` |
| Work-Zone Specialization (Cloud=draft, Local=execute) | ✅ `work_zones.py` |
| Delegation via Synced Vault (Git) | ✅ `vault_sync.py` |
| Claim-by-move rule (atomic, no double-work) | ✅ `claim_task.py` |
| Draft-only Cloud mode | ✅ `approval_watcher.py` |
| Domain vault subdirectory structure | ✅ `/Needs_Action/email/` etc. |
| Systemd service units (4 services) | ✅ `scripts/cloud/systemd/` |
| Next.js Web Dashboard | ✅ `web-ui/` |
| Alert Manager (SMTP) | ✅ `alert_manager.py` |
| Backup script (7-day rotation) | ✅ `scripts/cloud/backup.sh` |
| Cloud VPS deployed | ⏳ Infrastructure pending |
| SSL certificates | ⏳ Pending VPS provisioning |

---

## Owner

Built by Asma Yaseen for the Personal AI Employee Hackathon 0.

**Stack:** Claude Code · Python 3.13 · Node.js v24 · Obsidian · Flask · Next.js · Playwright · Odoo 18 · Docker · APScheduler · MCP
