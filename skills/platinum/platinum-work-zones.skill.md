# Platinum Work Zones

## Purpose
Implement cloud/local zone routing with per-task-type rules and automatic health-based failover.

## Prerequisites
- Gold Tier complete
- Cloud deployment operational
- Health monitoring active

## Key Features
- Zone configuration file (`zones.json`)
- Per-task-type routing rules
- Automatic failover on consecutive health check failures
- Configurable failover threshold (default: 3)
- Manual zone override via API
- Zone status visible on dashboard
- Failover event logging and alerting

## Implementation Steps
1. Implement `work_zones.py` with zone management
2. Create default `zones.json` configuration
3. Implement zone health checking
4. Implement automatic failover logic
5. Add API endpoints for zone status and override
6. Add zone status panel to System dashboard page
7. Integrate with alert manager for failover notifications

## Acceptance Criteria
- [ ] Tasks route to correct zone based on rules
- [ ] Failover triggers after 3 consecutive failures
- [ ] Manual zone switch via API works immediately
- [ ] Dashboard shows current active zone
- [ ] Failover events generate alerts
- [ ] Zone configuration persists across restarts
- [ ] Local-only tasks (approvals) never route to cloud

## Estimated Time
4-5 hours
