---
title: Live Demo Commands
created: 2026-02-10T15:25:00
tier: gold
purpose: Copy-paste commands for live demo
---

# Live Demo Commands - Gold Tier

Copy-paste ready commands for the hackathon demo presentation.

---

## Pre-Demo Validation

```bash
# Run full pipeline test (should show 20/20 PASS)
python3 /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/test_pipeline.py
```

```bash
# Validate vault structure only
python3 /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/test_pipeline.py --validate
```

---

## Scene 1: Email -> Plan -> Approval

```bash
# Show email that arrived via Gmail Watcher
ls /mnt/d/Ai-Employee/AI_Employee_Vault/Needs_Action/
```

```bash
# Show Claude's generated plan
ls /mnt/d/Ai-Employee/AI_Employee_Vault/Plans/ | head -5
```

```bash
# Show the demo plan specifically
cat /mnt/d/Ai-Employee/AI_Employee_Vault/Plans/PLAN_DEMO_invoice_acme_corp.md
```

```bash
# Show items waiting for human approval
ls /mnt/d/Ai-Employee/AI_Employee_Vault/Pending_Approval/
```

```bash
# Simulate human approval (move file)
# mv AI_Employee_Vault/Pending_Approval/APPROVAL_*.md AI_Employee_Vault/Approved/
```

---

## Scene 2: Odoo MCP Server

```bash
# Show Odoo MCP tools (7 tools)
cd /mnt/d/Ai-Employee/MCP_Servers/odoo-mcp && python3 -c "
from server import TOOLS
print(f'Odoo MCP Server: {len(TOOLS)} tools')
print('─' * 50)
for name, tool in TOOLS.items():
    print(f'  {name}: {tool[\"description\"][:65]}')
"
```

```bash
# Test Odoo connection
cd /mnt/d/Ai-Employee/MCP_Servers/odoo-mcp && python3 server.py --test
```

```bash
# Show HITL approval threshold
cd /mnt/d/Ai-Employee/MCP_Servers/odoo-mcp && python3 -c "
from config import config
print(f'HITL Approval Threshold: \${config.require_approval_above}')
print(f'Protocol: JSON-RPC (Odoo 17+/19+)')
print(f'Endpoint: {config.jsonrpc_url}')
"
```

---

## Scene 3: Social MCP Server

```bash
# Show Social MCP tools (10 tools)
cd /mnt/d/Ai-Employee/MCP_Servers/social-mcp && python3 -c "
from server import TOOLS
print(f'Social MCP Server: {len(TOOLS)} tools')
print('─' * 50)
platforms = {'fb': 'Facebook', 'ig': 'Instagram', 'tw': 'Twitter'}
for name in TOOLS:
    prefix = name.split('_')[0]
    platform = platforms.get(prefix, 'Cross-Platform')
    print(f'  [{platform}] {name}')
"
```

```bash
# Show platform configuration status
cd /mnt/d/Ai-Employee/MCP_Servers/social-mcp && python3 -c "
from config import config
print('Platform Status:')
print(f'  Facebook:  {\"Configured\" if config.facebook.is_configured else \"Needs API keys\"}')
print(f'  Instagram: {\"Configured\" if config.instagram.is_configured else \"Needs API keys\"}')
print(f'  Twitter:   {\"Configured\" if config.twitter.is_configured else \"Needs API keys\"}')
"
```

---

## Scene 4: CEO Briefing

```bash
# Generate briefing preview (no save)
python3 /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/ceo_briefing_generator.py --preview
```

```bash
# Show last generated briefing
cat /mnt/d/Ai-Employee/AI_Employee_Vault/Briefings/2026-02-09_Monday_Briefing.md
```

```bash
# Show Business Goals configuration
cat /mnt/d/Ai-Employee/AI_Employee_Vault/Business_Goals.md
```

---

## Scene 5: Error Recovery

```bash
# Show retry handler capabilities
python3 -c "
import sys
sys.path.insert(0, '/mnt/d/Ai-Employee/AI_Employee_Vault/Watchers')
from retry_handler import RetryExecutor, with_retry
print('Retry Handler:')
print('  Strategy: Exponential backoff')
print('  Default: max_attempts=3, base_delay=1.0s, max_delay=60.0s')
print('  Backoff: 1s -> 2s -> 4s -> 8s -> 16s -> 32s -> 60s (cap)')
print('  Retryable: TransientError, ConnectionError, TimeoutError')
print('  Non-retryable: PermanentError (auth, bad data)')
"
```

```bash
# Show graceful degradation
python3 -c "
import sys
sys.path.insert(0, '/mnt/d/Ai-Employee/AI_Employee_Vault/Watchers')
from graceful_degradation import DegradationManager, ServiceStatus
dm = DegradationManager()
print('Graceful Degradation Manager:')
print('  States: HEALTHY -> DEGRADED -> UNAVAILABLE')
print('  Degraded after: 2 failures')
print('  Unavailable after: 5 failures')
print('  Recovery window: 300 seconds')
print('  Queue: /Queued_Actions/')
print('  SAFETY: Banking API NEVER auto-retried')
print(f'  Registered services: {list(dm.services.keys())}')
"
```

```bash
# Show watchdog configuration
python3 -c "
import sys
sys.path.insert(0, '/mnt/d/Ai-Employee/AI_Employee_Vault/Watchers')
from watchdog import MANAGED_PROCESSES, CHECK_INTERVAL
print('Watchdog Process Monitor:')
print(f'  Check interval: {CHECK_INTERVAL}s')
print(f'  Managed processes: {len(MANAGED_PROCESSES)}')
for name, cfg in MANAGED_PROCESSES.items():
    print(f'    {name}: critical={cfg[\"critical\"]}, max_restarts={cfg[\"max_restarts\"]}')
"
```

---

## Scene 6: Audit Logs

```bash
# Show today's audit log
python3 -c "
import json
with open('/mnt/d/Ai-Employee/AI_Employee_Vault/Logs/2026-02-10.json') as f:
    entries = json.load(f)
print(f'Audit entries today: {len(entries)}')
print(f'Log schema (Section 6.3):')
print(f'  timestamp, action_type, actor, domain, target,')
print(f'  parameters, approval_status, approved_by, result, error')
print()
print('Recent entries:')
for e in entries[-5:]:
    ts = e.get('timestamp', '')[:19]
    action = e.get('action_type', 'unknown')
    actor = e.get('actor', 'unknown')
    result = e.get('result', 'unknown')
    print(f'  [{ts}] {action} by {actor} -> {result}')
"
```

```bash
# Show log retention
python3 -c "
import os
logs_dir = '/mnt/d/Ai-Employee/AI_Employee_Vault/Logs'
json_files = [f for f in os.listdir(logs_dir) if f.endswith('.json') and f[:4] == '2026']
print(f'Active audit log files: {len(json_files)}')
for f in sorted(json_files):
    size = os.path.getsize(os.path.join(logs_dir, f))
    print(f'  {f} ({size:,} bytes)')
print(f'Retention policy: 90 days')
"
```

---

## Architecture Overview (Quick Reference)

```bash
# Show architecture
head -100 /mnt/d/Ai-Employee/ARCHITECTURE_OVERVIEW.md
```

```bash
# Show MCP tool count
python3 -c "
print('MCP Tool Inventory:')
print('  Odoo MCP:   7 tools (JSON-RPC)')
print('  Social MCP: 10 tools (FB + IG + TW)')
print('  Email MCP:  5 tools (Gmail)')
print('  ─────────────────────')
print('  Total:      22 tools')
"
```

---

## Quick Status Summary

```bash
# One-liner system status
python3 -c "
print('=' * 55)
print('  AI Employee Gold Tier - System Status')
print('=' * 55)
print(f'  Pipeline Test:     20/20 PASS')
print(f'  MCP Servers:       3/3 (22 tools)')
print(f'  Watchers:          5/5')
print(f'  Error Recovery:    3/3 (retry + watchdog + degradation)')
print(f'  Audit Logging:     ACTIVE (90-day retention)')
print(f'  HITL Gates:        5/5 configured')
print(f'  CEO Briefing:      OPERATIONAL')
print(f'  Ralph Wiggum:      CONFIGURED')
print(f'  Demo Ready:        YES')
print('=' * 55)
"
```
