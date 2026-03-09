# Platinum Tier Architecture Plan

## 1. Cloud Infrastructure

### Stack
- **OS:** Ubuntu 22.04 LTS
- **Process Manager:** systemd
- **Reverse Proxy:** nginx with Let's Encrypt
- **Runtime:** Node.js 20 (dashboard), Python 3.11+ (API, watchers)
- **Container Runtime:** Docker (Odoo only)

### Key Decision: systemd vs Docker for Services
**Chosen: systemd** for core services (dashboard, API, watchers)
- Rationale: Lower overhead, native journal logging, simpler debugging, no container networking complexity
- Docker reserved for Odoo (pre-built image, database isolation)

### Deployment Architecture
```
Internet → nginx (443) → Dashboard (3000)
                       → Flask API (9000)
                       → Odoo (8069)
```

### Systemd Services
| Service | Unit Name | Port | Restart |
|---------|-----------|------|---------|
| Dashboard | ai-employee-dashboard | 3000 | on-failure, 5s |
| Flask API | ai-employee-api | 9000 | on-failure, 5s |
| Watchers | ai-employee-watchers | - | on-failure, 5s |

## 2. Vault Sync Architecture

### Key Decision: Git vs rsync
**Chosen: Git**
- Rationale: Built-in conflict detection, history tracking, works with existing vault structure, supports offline operation
- Trade-off: Larger storage footprint than rsync, but vault is text-heavy (ideal for git)

### Sync Flow
```
Local:  commit → push → (every 5 min)
Cloud:  fetch → rebase → push → (every 5 min)
Conflict: abort rebase → merge with ours strategy (local wins)
```

### State Management
- `.vault_sync_state.json` tracks last sync time, status, error details
- API endpoint `/api/vault/sync/status` exposes state
- API endpoint `/api/vault/sync/trigger` for manual sync

## 3. Work Zones Architecture

### Zone Configuration (`zones.json`)
```json
{
  "active_zone": "local",
  "auto_failover": true,
  "failover_threshold": 3,
  "zones": {
    "local": { "api_url": "http://localhost:9000" },
    "cloud": { "api_url": "https://ai.example.com" }
  },
  "routing_rules": {
    "email_processing": "active",
    "approvals": "local",
    "system_monitoring": "both"
  }
}
```

### Failover Detection
1. Health check active zone every 30s
2. Track consecutive failures
3. At threshold (3), check standby zone health
4. If standby healthy, switch active zone
5. Log failover event, send alert

## 4. Health Monitor Architecture

### Check Pipeline
```
health_monitor.py (loop every 30s)
  → check_service("dashboard")
  → check_service("api")
  → check_service("odoo")
  → update state file
  → log to daily JSONL
  → trigger alerts if thresholds met
```

### Alert Thresholds
| Failures | Level | Action |
|----------|-------|--------|
| 2 consecutive | WARNING | Email alert |
| 5 consecutive | CRITICAL | Email alert + log |
| Recovery | INFO | Recovery notification |

## 5. Odoo Cloud Architecture

### Docker Compose Stack
- `odoo:17.0` container (port 8069, localhost only)
- `postgres:15-alpine` container
- Named volumes for data persistence
- Bridge network for inter-container communication

### Key Decision: nginx vs Caddy for Odoo
**Chosen: nginx** (consistency with main reverse proxy)

### Backup Strategy
- Daily pg_dump of Odoo database
- Daily tar of Odoo filestore
- 7-day retention, compressed with timestamp
- Optional S3 upload

## 6. Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| VPS disk full | Service outage | Log rotation, backup retention limits, disk monitoring |
| Git merge conflicts | Data inconsistency | Local-wins strategy, no force-push on main files |
| SSL cert expiry | HTTPS failure | certbot auto-renewal, health check on cert validity |
