# Platinum Tier Skills Index

## Required Skills

### platinum-cloud-deploy.skill.md
**Purpose:** Deploy AI Employee system to Ubuntu cloud VPS
**Time:** 6-8 hours
**Key Features:**
- Ubuntu VPS provisioning with systemd
- Nginx reverse proxy with SSL
- Let's Encrypt certificate automation
- Automated deployment script
- Health endpoint verification
- Zero-downtime deployment support
- Firewall and security hardening

### platinum-vault-sync.skill.md
**Purpose:** Git-based vault synchronization between local and cloud
**Time:** 4-5 hours
**Key Features:**
- Bidirectional git-based sync
- Conflict resolution (local wins)
- Scheduled sync every 5 minutes
- Sync status API endpoint
- Manual trigger support
- Secrets exclusion (.env, tokens)

### platinum-work-zones.skill.md
**Purpose:** Cloud/Local zone routing with automatic failover
**Time:** 4-5 hours
**Key Features:**
- Zone configuration management
- Automatic task routing
- Health-based failover detection
- Zone status dashboard panel
- Manual zone override
- Per-task-type routing rules

### platinum-health-monitor.skill.md
**Purpose:** Real-time health monitoring with alerting
**Time:** 5-6 hours
**Key Features:**
- HTTP health checks every 30 seconds
- Email alerts via alert manager
- Dashboard integration
- Historical health data logging
- Auto-recovery triggers
- Consecutive failure tracking

### platinum-odoo-cloud.skill.md
**Purpose:** Deploy Odoo to cloud with Docker
**Time:** 4-5 hours
**Key Features:**
- Docker Compose with PostgreSQL
- Nginx reverse proxy configuration
- Automated database backups
- SSL termination
- Performance tuning
- Cloud-local Odoo sync

## Total Platinum Tier Time
Estimated: 25-30 hours

## Platinum Tier Deliverables Checklist
- [x] All Gold requirements complete
- [x] Cloud deployment scripts ready (deploy.sh with requirements.txt + zones.json provisioning)
- [x] Systemd service units created (4 services: api, dashboard, watchers, health-monitor)
- [x] Nginx reverse proxy configured (SSL-ready with security headers)
- [x] Vault sync module implemented + wired into scheduler (every 5 min)
- [x] Work zones routing implemented + wired into orchestrator
- [x] Health monitor watcher created + separate systemd service
- [x] Alert manager system built (email SMTP + logging)
- [x] Odoo cloud Docker config ready
- [x] Dashboard updated with Platinum API endpoints (9 new routes)
- [x] Claim-by-move protocol implemented (claim_task.py)
- [x] Draft-only mode for Cloud agent (approval_watcher.py)
- [x] Vault domain subdirectory structure created
- [x] zones.json configuration file created
- [x] Zone failover check in scheduler (every 2 min)
- [x] .env.example updated with Platinum tier variables
- [x] start_everything.sh updated (v3.0 with health monitor)
- [x] Backup script with 7-day rotation (backup.sh)
- [x] PLATINUM_TIER_STATUS.md documentation complete
- [ ] Cloud VPS provisioned and running
- [ ] SSL certificates installed
- [ ] Production deployment tested
- [ ] Demo video (15-20 min)

## Platinum Demo Gate
**Minimum passing scenario:**
1. Email arrives while Local offline
2. Cloud drafts reply + writes approval file
3. Local returns, user approves
4. Local executes send via MCP
5. Logs action, moves task to /Done
