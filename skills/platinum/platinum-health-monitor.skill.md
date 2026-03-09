# Platinum Health Monitor

## Purpose
Implement real-time health monitoring for all AI Employee services with alerting, historical tracking, and dashboard integration.

## Prerequisites
- Gold Tier complete
- Alert manager configured
- Services running (Dashboard, API, Odoo)

## Key Features
- HTTP health checks every 30 seconds
- Monitor Dashboard, Flask API, and Odoo services
- Consecutive failure tracking with alert thresholds
- Email alerts via alert manager (warning at 2, critical at 5 failures)
- Recovery notifications
- Historical health data in daily JSONL files
- Dashboard integration for real-time status
- Auto-recovery trigger integration

## Implementation Steps
1. Implement `health_monitor.py` watcher
2. Create service health check functions
3. Implement consecutive failure tracking
4. Integrate with `alert_manager.py` for notifications
5. Add health state file and history logging
6. Add health summary API endpoint
7. Update System dashboard page with health indicators
8. Create systemd service for health monitor

## Acceptance Criteria
- [ ] Health checks run every 30 seconds
- [ ] Unhealthy service detected within 60 seconds
- [ ] Warning alert sent after 2 consecutive failures
- [ ] Critical alert sent after 5 consecutive failures
- [ ] Recovery notification on service restore
- [ ] Health history stored in JSONL files
- [ ] Dashboard shows real-time health status
- [ ] Health monitor runs as systemd service

## Estimated Time
5-6 hours
