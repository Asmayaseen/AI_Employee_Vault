# Contract: Orchestrator Process Management API

**Feature**: 002-silver-tier
**Created**: 2026-02-08
**Type**: Internal API Contract

## Overview

The Orchestrator manages the lifecycle of all watcher processes. This contract defines how watchers are configured, started, monitored, and stopped.

## WatcherConfig Schema

```python
@dataclass
class WatcherConfig:
    name: str               # Human-readable name ("Gmail Watcher")
    script: str             # Python script filename ("gmail_watcher.py")
    enabled: bool = True    # Whether to start this watcher
    check_interval: int = 60  # Seconds between checks
    max_restarts: int = 5   # Max auto-restarts before giving up
    restart_delay: int = 30 # Seconds to wait before restart
    required_env: list = [] # Required env vars (e.g., ["GMAIL_CREDENTIALS_PATH"])
    args: list = []         # Additional CLI arguments
```

## Registered Watchers

| ID | Name | Script | Interval | Required Env |
|----|------|--------|----------|-------------|
| `filesystem` | FileSystem Watcher | `filesystem_watcher.py` | 10s | - |
| `gmail` | Gmail Watcher | `gmail_watcher.py` | 120s | `GMAIL_CREDENTIALS_PATH` |
| `whatsapp` | WhatsApp Watcher | `whatsapp_watcher.py` | 30s | `WHATSAPP_SESSION_DIR` |
| `linkedin` | LinkedIn Watcher | `linkedin_watcher.py` | 900s | `LINKEDIN_SESSION_DIR` |
| `approval` | Approval Watcher | `approval_watcher.py` | 5s | - |

## Lifecycle Protocol

```
1. INIT: Validate required_env vars exist
2. START: Launch subprocess: python <script> from Watchers/ dir
3. MONITOR: Health check every 60s (poll process.poll())
4. RESTART: If process died AND restart_count < max_restarts:
   - Wait restart_delay seconds
   - Increment restart_count
   - Go to step 2
5. ALERT: If restart_count >= max_restarts:
   - Log critical error
   - Mark watcher as FAILED
   - Continue managing other watchers
6. SHUTDOWN: On SIGTERM/Ctrl+C:
   - Send SIGTERM to all child processes
   - Wait 10s for graceful shutdown
   - SIGKILL any remaining processes
```

## Health Check Response

```json
{
  "watcher_id": "gmail",
  "status": "running|stopped|failed",
  "pid": 12345,
  "uptime_seconds": 3600,
  "restart_count": 0,
  "last_error": null
}
```

## Approval Watcher Contract

### Approval Request File Format

```markdown
---
type: approval_request
action: send_email|create_invoice|social_post|payment
priority: high|medium|low
risk_level: low|medium|high|critical
created: 2026-02-09T10:30:00
source: EMAIL_20260209.md
status: pending
---

# Approval Request: [Description]

## Details
- **To:** recipient@example.com
- **Subject:** Re: Invoice

## Instructions
To approve: Move this file to `/Approved/`
To reject: Move this file to `/Rejected/`
```

### Action Handlers

| action_type | Handler | MCP Tool |
|-------------|---------|----------|
| `send_email` | Email handler | `email-mcp:send_email` |
| `draft_email` | Email handler | `email-mcp:draft_email` |
| `create_invoice` | Odoo handler | `odoo-mcp:create_invoice` |
| `social_post` | Social handler | `social-mcp:post_content` |

## Invariants

1. Orchestrator MUST NOT start a watcher if its `required_env` vars are missing
2. Orchestrator MUST log every process lifecycle event (start, stop, restart, crash)
3. Orchestrator MUST continue running even if individual watchers fail
4. Graceful shutdown MUST stop all child processes within 10 seconds
5. Health check MUST complete within 5 seconds
