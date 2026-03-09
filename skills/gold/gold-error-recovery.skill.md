# Skill: Error Recovery & Graceful Degradation (Gold Tier)

## Overview
Comprehensive error handling system with retry logic, exponential backoff, service health monitoring, and automatic recovery strategies.

## Prerequisites
- Base watcher infrastructure (Silver tier)
- Audit logging system
- Vault Queued_Actions/ directory

## Capabilities
- **Retry Logic**: Configurable retry with exponential backoff
- **Error Categorization**: Transient vs permanent error classification
- **Service Health Monitoring**: Track service availability over time
- **Graceful Degradation**: Continue operating when components fail
- **Auto-Recovery**: Automatically restore services when available
- **Watchdog Process**: Monitor all watchers and restart if crashed
- **Alert System**: Notify on critical failures

## Implementation Details

### Components
| File | Purpose |
|------|---------|
| `retry_handler.py` | Retry decorator with backoff |
| `graceful_degradation.py` | Service state management |
| `watchdog.py` | Process health monitor |
| `audit_logger.py` | Error event logging |

### Degradation Strategies
- **Gmail API down**: Queue emails in Queued_Actions/, process when restored
- **Banking API timeout**: Never auto-retry payments, alert user
- **Claude unavailable**: Watchers continue collecting, queue processing
- **Vault locked**: Write to temp folder, sync when available

### Retry Configuration
| Error Type | Max Retries | Backoff | Action |
|-----------|-------------|---------|--------|
| Network timeout | 5 | Exponential (2s base) | Retry |
| Auth failure | 0 | None | Alert user |
| Rate limit | 3 | Fixed (wait period) | Retry after window |
| Data validation | 0 | None | Log and skip |

### Watchdog Process
- Polls every 30 seconds
- Checks each watcher process is alive
- Restarts crashed watchers (max 3 restarts per hour)
- Logs all restart events to audit trail

## Acceptance Criteria
- [ ] Retry handler works for transient errors
- [ ] Permanent errors are not retried
- [ ] Degradation manager tracks service states
- [ ] Watchdog detects and restarts crashed processes
- [ ] Queued actions are processed on recovery
- [ ] All events logged to audit trail
