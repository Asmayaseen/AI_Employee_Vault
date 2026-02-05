# Platinum Tier Skills Index

## Required Skills

### platinum-cloud-deploy.skill.md
**Purpose:** Deploy AI Employee on cloud VM (24/7 operation)
**Time:** 8-10 hours
**Key Features:**
- Oracle Cloud Free Tier setup (or AWS/GCP)
- Ubuntu server configuration
- Python environment setup
- Systemd services for watchers
- HTTPS/SSL configuration
- Firewall and security hardening
- Automated backups

### platinum-vault-sync.skill.md
**Purpose:** Synchronize vault between Cloud and Local agents
**Time:** 6-8 hours
**Key Features:**
- Git-based sync (Phase 1)
- Syncthing alternative
- Conflict resolution
- Claim-by-move protocol
- Single-writer rule for Dashboard
- Secrets exclusion (.env, tokens)
- Selective folder sync

### platinum-work-zones.skill.md
**Purpose:** Cloud/Local work-zone specialization
**Time:** 6-8 hours
**Key Features:**
- Cloud owns: Email triage, draft replies, social post drafts
- Local owns: Approvals, WhatsApp, payments, final sends
- Delegation via /Needs_Action/<domain>/
- /In_Progress/<agent>/ claim protocol
- /Updates/ folder for Cloud→Local communication
- Agent coordination rules
- A2A messaging (Phase 2 optional)

### platinum-health-monitor.skill.md
**Purpose:** 24/7 health monitoring and alerting
**Time:** 4-5 hours
**Key Features:**
- Uptime monitoring
- Resource usage tracking (CPU, memory, disk)
- Process watchdog
- API quota monitoring
- Log rotation
- Alert notifications (email/SMS)
- Auto-recovery triggers
- Status dashboard

### platinum-odoo-cloud.skill.md
**Purpose:** Deploy Odoo Community on cloud VM
**Time:** 6-8 hours
**Key Features:**
- Cloud VM Odoo installation
- HTTPS with Let's Encrypt
- Database backups
- Cloud agent MCP integration
- Draft-only operations from Cloud
- Local approval for posting invoices/payments
- Multi-company support (optional)

## Total Platinum Tier Time
Estimated: 60+ hours

## Platinum Tier Deliverables Checklist
- [ ] All Gold requirements complete
- [ ] Cloud VM deployed and operational 24/7
- [ ] Vault sync working (Git or Syncthing)
- [ ] Work-zone specialization implemented
- [ ] Cloud: drafts emails/posts (no sends)
- [ ] Local: approvals and final actions
- [ ] Odoo Cloud deployed with HTTPS
- [ ] Cloud agent MCP to Odoo (draft-only)
- [ ] Local agent approves Odoo posts
- [ ] Health monitoring operational
- [ ] Auto-restart on failures
- [ ] Security hardened (secrets never sync)
- [ ] Full documentation
- [ ] Demo video (15-20 min)
- [ ] Production-ready architecture

## Platinum Demo Gate
**Minimum passing scenario:**
1. Email arrives while Local offline
2. Cloud drafts reply + writes approval file
3. Local returns, user approves
4. Local executes send via MCP
5. Logs action, moves task to /Done
