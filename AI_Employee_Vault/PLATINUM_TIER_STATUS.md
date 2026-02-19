# Platinum Tier Status - Always-On Cloud + Local Executive

## Overview
The Platinum tier implements a dual-agent architecture: a Cloud agent running 24/7 for triage and draft generation, and a Local agent that handles approvals, sensitive operations, and final execution.

## Architecture

### Dual-Agent Model
| Agent | Role | Mode |
|-------|------|------|
| **Cloud** | 24/7 email triage, social scheduling, draft generation | `AGENT_MODE=draft_only` |
| **Local** | Approvals, WhatsApp, payments, final execution | `AGENT_MODE=full` (default) |

### Work Zone Routing
Tasks are routed based on `zones.json` rules:
| Task Type | Routed To |
|-----------|-----------|
| `email_processing` | Active zone |
| `social_media` | Active zone |
| `approvals` | Local only |
| `vault_operations` | Local only |
| `whatsapp` | Local only |
| `payments` | Local only |
| `accounting` | Active zone |
| `system_monitoring` | Both zones |

### Auto-Failover
- Health checks every 2 minutes via scheduler
- After 3 consecutive failures, auto-failover to other zone
- Manual zone switch via `/api/zones/switch`

## Implemented Modules

### 1. Vault Sync (`utils/vault_sync.py`)
- Git-based bidirectional sync between local and cloud
- Local-wins conflict resolution strategy
- Scheduled every 5 minutes via scheduler
- Manual trigger: `POST /api/vault/sync/trigger`
- Status check: `GET /api/vault/sync/status`

### 2. Work Zones (`utils/work_zones.py`)
- Zone configuration in `zones.json`
- `resolve_zone(task_type)` for routing decisions
- `check_and_failover()` for automatic zone switching
- Integrated into orchestrator for zone-aware task handling
- API: `GET /api/zones/status`, `POST /api/zones/switch`, `GET /api/zones/health`

### 3. Health Monitor (`Watchers/health_monitor.py`)
- Monitors Dashboard, Flask API, and Odoo services
- HTTP health checks every 30 seconds
- Consecutive failure tracking with alert thresholds
- Historical health data in `Logs/health/`
- API: `GET /api/health/detailed`, `GET /api/health/detailed?refresh=true`

### 4. Alert Manager (`utils/alert_manager.py`)
- Email alerts via SMTP (configurable)
- Alert levels: INFO, WARNING, CRITICAL
- Alert logging to `Logs/alerts/`
- API: `GET /api/alerts`

### 5. Claim-by-Move Protocol (`utils/claim_task.py`)
- Atomic `os.rename()` prevents race conditions between agents
- `/Needs_Action/<domain>/` → `/In_Progress/<agent>/` → `/Done/`
- JSONL claim logging in `Logs/claims.jsonl`
- API: `GET /api/claims`

### 6. Draft-Only Mode (`approval_watcher.py`)
- Cloud agent blocks execution of: `send_email`, `reply_email`, `forward_email`, `linkedin_post`, `facebook_post`, `instagram_post`, `twitter_post`, `whatsapp_send`, `payment`, `invoice`
- Files left in `/Approved/` for Local to execute after vault sync
- Controlled by `AGENT_MODE=draft_only` env var

### 7. Vault Domain Structure
```
Needs_Action/
  email/
  social/
  accounting/
  general/
Plans/
  email/
  social/
  accounting/
  general/
Pending_Approval/
  email/
  social/
  accounting/
  general/
In_Progress/
  cloud/
  local/
Updates/
Signals/
```

## Cloud Deployment

### Systemd Services
| Service | File | Description |
|---------|------|-------------|
| `ai-employee-api` | Flask dashboard on port 9000 | Core API |
| `ai-employee-dashboard` | Next.js on port 3000 | Web UI |
| `ai-employee-watchers` | Orchestrator with all watchers | Cloud watchers |
| `ai-employee-health-monitor` | Health check loop | Service monitoring |

### Deploy Command
```bash
DOMAIN=ai.example.com sudo bash scripts/cloud/deploy.sh
```

### Cloud Environment Variables
```
AGENT_MODE=draft_only
AGENT_NAME=cloud
VAULT_PATH=/opt/ai-employee/AI_Employee_Vault
CLOUD_API_URL=https://ai.example.com
VAULT_SYNC_REMOTE=origin
VAULT_SYNC_BRANCH=main
ALERTS_ENABLED=true
ALERT_SMTP_HOST=smtp.gmail.com
ALERT_SMTP_USER=...
ALERT_SMTP_PASS=...
ALERT_TO_EMAIL=...
```

## Dashboard API Endpoints (Platinum)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vault/sync/status` | GET | Current sync status |
| `/api/vault/sync/trigger` | POST | Manual sync trigger |
| `/api/zones/status` | GET | Zone configuration and state |
| `/api/zones/switch` | POST | Switch active zone `{"zone": "cloud"}` |
| `/api/zones/health` | GET | Health of both zones |
| `/api/health/detailed` | GET | Detailed service health |
| `/api/alerts` | GET | Recent alert history |
| `/api/claims` | GET | Task claim status |
| `/api/platinum/status` | GET | Overall Platinum module status |

## Scheduler Tasks (Platinum)

| Task | Cron | Description |
|------|------|-------------|
| `vault_sync` | `*/5 * * * *` | Sync vault every 5 minutes |
| `zone_failover_check` | `*/2 * * * *` | Check zone health, failover if needed |

## Demo Gate Scenario
1. Email arrives while Local is offline
2. Cloud agent (draft-only) triages email, creates draft reply in `/Pending_Approval/`
3. Vault sync pushes changes to git
4. Local agent returns, pulls changes via vault sync
5. User approves draft in dashboard
6. Local agent executes send via MCP (approval_watcher)
7. Action logged, task moved to `/Done/`

## Key Files
| File | Role |
|------|------|
| `utils/vault_sync.py` | Git-based bidirectional sync |
| `utils/work_zones.py` | Zone routing + failover |
| `utils/claim_task.py` | Atomic claim-by-move protocol |
| `utils/alert_manager.py` | Email alert system |
| `Watchers/health_monitor.py` | Service health monitoring |
| `Watchers/orchestrator.py` | Master process manager + zone routing |
| `Watchers/scheduler.py` | Cron-based task scheduling |
| `Watchers/dashboard.py` | Flask API with Platinum endpoints |
| `Watchers/approval_watcher.py` | Draft-only mode + execution |
| `zones.json` | Zone configuration |
| `scripts/cloud/deploy.sh` | Cloud VPS deployment |
| `scripts/cloud/systemd/*.service` | Systemd service units |

## Acceptance Criteria
- [x] Vault sync module with local-wins conflict resolution
- [x] Work zones routing with auto-failover
- [x] Health monitor with alert integration
- [x] Claim-by-move protocol for multi-agent
- [x] Draft-only mode for Cloud agent (approval_watcher + gmail_watcher + Odoo MCP)
- [x] Vault domain subdirectory structure (/Needs_Action/email/, /Pending_Approval/email/, etc.)
- [x] Dashboard API endpoints for all Platinum modules
- [x] Scheduler tasks for vault sync + zone failover
- [x] Orchestrator zone-aware task routing
- [x] Systemd service units (4 services)
- [x] Cloud deployment script with Odoo docker-compose + certbot SSL automation
- [x] Backup cron auto-installed by deploy.sh
- [x] zones.json configuration file
- [x] .env.example includes Platinum tier variables
- [x] start_everything.sh updated to v3.0 (health monitor included)
- [x] Backup script with 7-day rotation
- [x] Gmail watcher generates draft replies in /Pending_Approval/email/ when AGENT_MODE=draft_only
- [x] Odoo MCP blocks post_invoice + record_expense in draft-only mode
- [ ] Cloud VPS provisioned and running
- [ ] SSL certificates installed (auto-provisioned by deploy.sh when DNS ready)
- [ ] Production deployment tested (demo gate scenario)
