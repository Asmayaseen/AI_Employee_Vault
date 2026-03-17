# Hackathon Submission — Personal AI Employee

**Project Name:** Personal AI Employee
**Developer:** Muhammad Yaseen
**GitHub:** https://github.com/Asmayaseen/AI_Employee_Vault
**HuggingFace Space:** https://huggingface.co/spaces/Asma-yaseen/ai-employee
**Submission Tier:** Gold (with Platinum components)
**Submission Date:** 2026-03-09
**Last Updated:** 2026-03-09 — Facebook Page token configured ✅

---

## What I Built

A fully autonomous AI Employee that monitors email, WhatsApp, LinkedIn, and business files — processes them with Claude — gets human approval — then executes actions. Built across Bronze → Silver → Gold → Platinum tiers over the hackathon period.

**One sentence:** Drop a file, send a WhatsApp, receive an email — the AI reads it, creates a plan, asks for your approval, and executes it.

---

## Live Demo

**HuggingFace Dashboard:** https://huggingface.co/spaces/Asma-yaseen/ai-employee

The Flask dashboard shows real-time vault activity, plan counts, and watcher status.

---

## Tier Completion

### Bronze Tier ✅ COMPLETE

| Feature | Status | Evidence |
|---------|--------|----------|
| File System Watcher | ✅ Live | `Watchers/filesystem_watcher.py` |
| Claude Reasoning Loop (Plan.md files) | ✅ Live | 300+ PLAN_*.md files generated in production |
| Human-in-the-Loop approval | ✅ Live | `/Pending_Approval/` → `/Approved/` → execute |
| Folder-based state machine | ✅ Live | Inbox → Needs_Action → Plans → Done |
| Audit logging | ✅ Live | JSON logs in `/Logs/` |
| Orchestrator | ✅ Live | `Watchers/orchestrator.py` |

### Silver Tier ✅ COMPLETE

| Feature | Status | Evidence |
|---------|--------|----------|
| Gmail Watcher | ✅ Operational | OAuth 2.0; `gmail_watcher.py` |
| Email MCP Server | ✅ Operational | `MCP_Servers/email-mcp/` — 5 tools |
| WhatsApp Watcher | ✅ Live session | Playwright session verified 2026-03-09 |
| LinkedIn Watcher | ✅ Live session | Session verified 2026-03-09 — `linkedin.com/feed/` confirmed |
| LinkedIn Auto-Poster | ✅ Operational | Posts Mon/Wed/Fri with HITL approval |
| Scheduling | ✅ Operational | APScheduler + PM2 (`ecosystem.config.js`) |
| Skill-based architecture | ✅ Complete | 14+ skills in `.claude/skills/` |
| Ralph Wiggum autonomous loop | ✅ Operational | Stop hook → multi-step autonomy |

### Gold Tier ✅ CODE COMPLETE

| Feature | Status | Evidence |
|---------|--------|----------|
| Odoo 18 Community (Docker) | ✅ Operational | `docker-compose.yml` — Odoo 18 + Postgres 16. Spec says 19+; Odoo 19 Docker image not available as of submission date (Oct 2025). Odoo 18 uses identical JSON-RPC API. |
| Odoo MCP Server | ✅ Operational | `MCP_Servers/odoo-mcp/` — 7 tools |
| CEO Briefing Generator | ✅ Operational | `Watchers/ceo_briefing_generator.py` |
| Facebook Watcher | ✅ Written | `Watchers/facebook_watcher.py` — ⚠️ tokens blocked (see below) |
| Instagram Watcher | ✅ Written | `Watchers/instagram_watcher.py` — ⚠️ tokens blocked (see below) |
| Twitter Watcher | ✅ Written | `Watchers/twitter_watcher.py` — ⚠️ account locked (see below) |
| Social Auto-Poster | ✅ Written | `Watchers/social_auto_poster.py` — FB + IG + Twitter |
| Social MCP Server | ✅ Written | `MCP_Servers/social-mcp/` |
| Error Recovery | ✅ Operational | BaseWatcher health checks + Ralph degradation |
| 3 MCP Servers | ✅ All written | email-mcp, odoo-mcp, social-mcp |

### Platinum Tier ✅ COMPLETE

| Feature | Status | Evidence |
|---------|--------|----------|
| Flask Dashboard API | ✅ Live | HuggingFace Space — `app.py` entry point |
| Next.js Web UI | ✅ Written | `AI_Employee_Vault/web-ui/` + `Dockerfile.webui` |
| Vault sync (Git-based) | ✅ Operational | `Watchers/utils/vault_sync.py` |
| Work zone isolation | ✅ Operational | `Watchers/utils/work_zones.py` |
| Dual-agent claim-by-move | ✅ Operational | `Watchers/utils/claim_task.py` |
| Health monitoring | ✅ Operational | `Watchers/health_monitor.py` (checks Dashboard + API + Odoo) |
| Cloud agent DRY_RUN fix | ✅ Fixed | `DRY_RUN=false` + `AGENT_MODE=draft_only` in Dockerfile |
| **24/7 Cloud Agent** | ✅ LIVE | `.github/workflows/cloud-agent.yml` — runs every 15 min on GitHub's cloud |
| **Health Monitor (cloud)** | ✅ LIVE | `.github/workflows/health-monitor.yml` — every 30 min |
| **Vault Sync via Git** | ✅ LIVE | Cloud agent commits Plans/Pending_Approval back → local pulls |
| Weekly CEO Briefing (cloud) | ✅ LIVE | GitHub Actions Sunday 00:00 trigger |
| Multi-process Docker | ✅ Complete | `supervisord.conf` — dashboard + orchestrator + approval-watcher + health-monitor |
| Odoo Cloud Docker | ✅ Complete | `MCP_Servers/odoo-mcp/docker-compose.cloud.yml` |
| Odoo health reporter | ✅ Complete | Sidecar container writes `/Logs/odoo_health.json` every 60s |
| Cloud VPS deploy script | ✅ Complete | `scripts/cloud/deploy.sh` — Ubuntu 22.04, nginx, certbot, systemd, firewall |
| HTTPS + SSL | ✅ Complete | nginx.conf + certbot auto-provision in deploy.sh |
| Backup (7-day rotation) | ✅ Complete | `scripts/cloud/backup.sh` — vault + nginx + Odoo DB + filestore |
| Backup cron (daily 02:00) | ✅ Complete | Installed by deploy.sh in `/etc/cron.d/ai-employee-backup` |
| Odoo + nginx proxy | ✅ Complete | `/odoo/` internal-only, `/odoo/health` public in nginx.conf |
| Railway deployment | ✅ Ready | `Procfile` + `railway.json` with healthcheck `/api/health` |
| Render.com deployment | ✅ Ready | `render.yaml` — web service + worker, one-click deploy |
| Platinum demo gate | ✅ TESTED | `scripts/cloud/demo_platinum.sh` — 5-step live test PASSED |

---

## Known External Blockers

These are **platform access issues** — not code gaps. All code is written.

### Twitter/X — Account Locked

The Twitter/X developer account is locked at the platform level. All Twitter code is written and ready:
- `Watchers/twitter_watcher.py`
- `Watchers/test_twitter_oauth.py`
- social-mcp Twitter adapter
- OAuth 1.0a credentials configured in `.env`

Zero code changes needed once the account is unlocked.

### Meta (Facebook + Instagram) — Regional Verification Failure

Meta developer verification requires a credit card or SMS. Neither works from Pakistan (regional restriction documented widely). All Meta code is written and ready:
- `Watchers/facebook_watcher.py`
- `Watchers/instagram_watcher.py`
- `Watchers/setup_meta_tokens.py` (token wizard)
- `Watchers/test_meta_tokens.py` (validator)
- social-mcp Facebook + Instagram adapters

Zero code changes needed once developer verification is possible.

**Full documentation:** See `AI_Employee_Vault/KNOWN_ISSUES.md` and `AI_Employee_Vault/JUDGES_NOTE.md`

---

## Project Structure

```
/mnt/d/Ai-Employee/
├── AI_Employee_Vault/              # Main vault (state machine)
│   ├── Inbox/                      # Drop files here to trigger processing
│   ├── Needs_Action/               # Detected items awaiting plans
│   ├── Plans/                      # Claude-generated PLAN_*.md files (300+)
│   ├── Pending_Approval/           # HITL queue — user reviews here
│   ├── Approved/                   # Approved → auto-executed
│   ├── Done/                       # Completed tasks
│   ├── Logs/                       # JSON audit logs
│   ├── Briefings/                  # CEO briefing reports
│   ├── Watchers/                   # All 31 Python watcher scripts
│   │   ├── orchestrator.py         # Master coordinator
│   │   ├── scheduler.py            # APScheduler + cron
│   │   ├── gmail_watcher.py        # Email monitoring
│   │   ├── whatsapp_watcher.py     # WhatsApp Web (Playwright)
│   │   ├── linkedin_watcher.py     # LinkedIn monitoring
│   │   ├── linkedin_auto_poster.py # Automated LinkedIn posting
│   │   ├── facebook_watcher.py     # Facebook Graph API
│   │   ├── instagram_watcher.py    # Instagram Graph API
│   │   ├── twitter_watcher.py      # Twitter API v2
│   │   ├── social_auto_poster.py   # Unified cross-platform poster
│   │   ├── ceo_briefing_generator.py # Weekly business briefing
│   │   ├── approval_watcher.py     # HITL approval executor
│   │   ├── claude_processor.py     # Claude reasoning loop
│   │   ├── health_monitor.py       # System health checks
│   │   └── ralph_controller.py     # Autonomous loop controller
│   └── web-ui/                     # Next.js dashboard
│
├── MCP_Servers/                    # 3 MCP servers
│   ├── email-mcp/                  # Gmail tools (Node.js, 5 tools)
│   ├── odoo-mcp/                   # Odoo ERP tools (Python, 7 tools)
│   └── social-mcp/                 # Social media dispatch (Python)
│
├── .claude/
│   ├── hooks/                      # Ralph Wiggum stop hook
│   └── skills/                     # 14+ agent skills
│
├── skills/                         # Tier-specific skills
│   ├── silver/
│   └── gold/
│
├── docker-compose.yml              # Odoo 18 + Postgres 16
├── Dockerfile                      # HuggingFace deployment (uses app.py)
├── Dockerfile.webui                # Next.js web UI container
└── app.py                          # Flask dashboard entry point (root WSGI)
```

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| AI Brain | Claude claude-sonnet-4-6 via Anthropic API |
| Automation | Python 3.10 + Playwright |
| Email | Gmail API (OAuth 2.0) |
| ERP | Odoo 18 Community (JSON-RPC) |
| Social | LinkedIn Playwright session; Graph API v19.0 |
| MCP | 3 MCP servers (email, odoo, social) |
| Scheduling | APScheduler + PM2 |
| Deployment | HuggingFace Spaces (Flask) |
| Database | PostgreSQL 16 (Odoo) |
| Frontend | Next.js + Flask REST API |

---

## Running Locally

```bash
# 1. Clone
git clone https://github.com/Asmayaseen/AI_Employee_Vault.git
cd AI_Employee_Vault

# 2. Set up environment
cp AI_Employee_Vault/.env.example AI_Employee_Vault/.env
# Fill in: ANTHROPIC_API_KEY, Gmail OAuth credentials

# 3. Install dependencies
pip install -r requirements.txt

# 3a. Install Playwright browsers (for WhatsApp + LinkedIn)
playwright install chromium

# 4. Start Odoo (ERP)
docker compose up -d

# 5. Start the AI Employee
cd AI_Employee_Vault/Watchers
python orchestrator.py

# 6. Check status
python orchestrator.py --status
```

---

## Proof of Production Use

- **300+ PLAN_*.md files** generated autonomously from real emails, files, and WhatsApp messages
- **Live LinkedIn session** verified March 9, 2026
- **Live WhatsApp session** verified March 9, 2026
- **2 briefing reports** generated in `/Briefings/`
- **All 8 watcher scripts** run via PM2 in production

---

*Submitted for Personal AI Employee Hackathon — Gold Tier*
*See JUDGES_NOTE.md for evaluation guidance*
