# Platinum Tier Specification

## Overview
The Platinum Tier extends AI Employee from a local-only Gold system to a cloud-capable, always-on platform with vault synchronization, work zone routing, health monitoring, and cloud Odoo deployment.

## Prerequisites
- Gold Tier fully complete and operational
- Ubuntu 22.04+ VPS with minimum 2GB RAM, 2 vCPU, 40GB disk
- Domain name pointed to VPS IP
- SSH access to VPS

## Features

### 1. Cloud Deployment
Deploy the full AI Employee stack to a cloud Ubuntu VPS.

**Requirements:**
- Automated deployment script (`deploy.sh`)
- Systemd service units for: Dashboard (Next.js), API (Flask), Watchers
- Nginx reverse proxy with SSL via Let's Encrypt
- Environment-based configuration
- Automated backup system (daily, 7-day retention)

**Success Criteria:**
- `curl https://ai.example.com/api/health` returns 200
- Dashboard accessible at `https://ai.example.com`
- All services auto-restart on failure
- SSL certificate auto-renews

### 2. Vault Sync
Git-based bidirectional synchronization between local and cloud vaults.

**Requirements:**
- Auto-commit and push every 5 minutes
- Pull and rebase from remote
- Conflict resolution: local always wins
- Secrets exclusion (`.env`, tokens, credentials)
- Sync status exposed via API endpoint
- Manual sync trigger support

**Success Criteria:**
- File created locally appears on cloud within 5 minutes
- File created on cloud appears locally within 5 minutes
- Conflicting edits resolved without data loss (local version preserved)
- Sync status visible on dashboard

### 3. Work Zones
Route tasks between local and cloud environments based on configuration.

**Requirements:**
- Zone configuration file (`zones.json`)
- Per-task-type routing rules (email → active, approvals → local, monitoring → both)
- Automatic failover when active zone health check fails
- Configurable failover threshold (default: 3 consecutive failures)
- Manual zone override via API
- Zone status visible on dashboard

**Success Criteria:**
- Tasks route to correct zone based on rules
- Failover triggers within 90 seconds of zone failure
- Manual override takes effect immediately
- Dashboard shows current active zone

### 4. Health Monitoring
Real-time health checks with alerting for all services.

**Requirements:**
- HTTP health checks every 30 seconds
- Monitor: Dashboard, Flask API, Odoo
- Consecutive failure tracking with thresholds
- Email alerts on warning (2 failures) and critical (5 failures)
- Recovery notifications when service comes back
- Historical health data logging (daily JSONL files)
- Dashboard integration

**Success Criteria:**
- Unhealthy service triggers alert within 2 minutes
- Recovery triggers info notification
- Health history queryable for past 7 days
- Dashboard shows real-time service status

### 5. Odoo Cloud Deployment
Deploy Odoo Community edition on cloud VPS via Docker.

**Requirements:**
- Docker Compose with Odoo 17 + PostgreSQL 15
- Nginx reverse proxy with SSL
- Automated database backups
- Accessible only via reverse proxy (port 8069 bound to localhost)
- Performance tuning for 2GB RAM environment

**Success Criteria:**
- Odoo accessible at `https://odoo.example.com`
- Database backup runs daily
- Odoo restarts automatically on failure

## Non-Functional Requirements
- **Security:** No secrets in version control, firewall configured, fail2ban
- **Performance:** API response < 500ms p95, dashboard load < 3s
- **Reliability:** Auto-restart on failure, health monitoring, alerting
- **Observability:** Centralized logging via journald, health dashboard
