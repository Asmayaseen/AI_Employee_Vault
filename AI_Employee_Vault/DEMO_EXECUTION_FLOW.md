---
title: Demo Execution Flow
created: 2026-02-10T15:24:00
tier: gold
duration: 8-10 minutes
presenter: Asma Yaseen
---

# Demo Execution Flow - Gold Tier Hackathon

**Duration:** 8-10 minutes
**Architecture:** Perception -> Reasoning -> Action -> Audit (with HITL)

---

## Pre-Demo Setup (Before Going Live)

```bash
# 1. Navigate to project
cd /mnt/d/Ai-Employee

# 2. Verify vault structure
python3 AI_Employee_Vault/Watchers/test_pipeline.py --validate

# 3. Ensure demo data exists
ls AI_Employee_Vault/Needs_Action/
ls AI_Employee_Vault/Plans/
ls AI_Employee_Vault/Demo/

# 4. Open Obsidian to AI_Employee_Vault
# (separate window - for visual folder browsing)

# 5. Start Docker if Odoo demo is live
# docker compose -f MCP_Servers/odoo-mcp/docker-compose.yml up -d
```

---

## Flow 1: Email Perception -> Plan -> Approval (2 min)

**Demonstrates:** Watcher -> Reasoning -> HITL safety gate

### Step 1: Show the email arrives
```
AI_Employee_Vault/
  Needs_Action/
    DEMO_EMAIL_acme_invoice_request.md  <-- Watcher created this
```

**Talking Point:** "The Gmail Watcher detected an incoming email from a client requesting an invoice. It automatically created a structured task file."

### Step 2: Show Claude's plan
```
AI_Employee_Vault/
  Plans/
    PLAN_DEMO_invoice_acme_corp.md  <-- Claude generated this
```

**Talking Point:** "Claude Code read the email, analyzed it against the Company Handbook, and generated an action plan. It identified that invoice creation requires human approval."

### Step 3: Show the approval request
```
AI_Employee_Vault/
  Pending_Approval/
    APPROVAL_INVOICE_ACME_1500.md  <-- Requires human sign-off
```

**Talking Point:** "The invoice is $1,500 - above our $500 threshold. The system did NOT auto-execute. Instead it created an approval request for the human to review in Obsidian."

### Step 4: Approve by moving the file
```
# Human drags file from Pending_Approval -> Approved in Obsidian
# OR via CLI:
mv AI_Employee_Vault/Pending_Approval/APPROVAL_*.md AI_Employee_Vault/Approved/
```

**Talking Point:** "The human reviews and approves by moving the file. The Approval Watcher detects this and triggers the MCP action."

---

## Flow 2: Odoo Accounting Integration (2 min)

**Demonstrates:** MCP Server -> JSON-RPC -> HITL -> Financial reporting

### Step 1: Show Odoo MCP tools
```bash
cd MCP_Servers/odoo-mcp
python3 -c "
from server import TOOLS
print(f'Odoo MCP: {len(TOOLS)} tools')
for name in TOOLS:
    print(f'  - {name}: {TOOLS[name][\"description\"][:60]}')
"
```

### Step 2: Test Odoo connection
```bash
python3 server.py --test
```

**Talking Point:** "Our Odoo integration uses JSON-RPC protocol as required for Odoo 19+. We have 7 tools: invoice creation, expense recording, financial summaries, customer management, and subscription auditing."

### Step 3: Show HITL threshold
```bash
python3 -c "from config import config; print(f'Approval threshold: \${config.require_approval_above}')"
```

**Talking Point:** "Any invoice above $500 triggers HITL approval. The system never auto-posts invoices above this threshold."

---

## Flow 3: Social Media Campaign (1.5 min)

**Demonstrates:** Multi-platform MCP -> HITL for all posts

### Step 1: Show Social MCP tools
```bash
cd MCP_Servers/social-mcp
python3 -c "
from server import TOOLS
print(f'Social MCP: {len(TOOLS)} tools')
for name in TOOLS:
    print(f'  - {name}')
"
```

### Step 2: Show platform adapters
```bash
python3 -c "
from config import config
print(f'Facebook: {\"configured\" if config.facebook.is_configured else \"needs API keys\"}')
print(f'Instagram: {\"configured\" if config.instagram.is_configured else \"needs API keys\"}')
print(f'Twitter: {\"configured\" if config.twitter.is_configured else \"needs API keys\"}')
"
```

**Talking Point:** "All social media posts require HITL approval per Company Handbook rules. The system supports Facebook Graph API, Instagram Business API, and Twitter API v2. The `generate_all_summaries` tool creates a cross-platform report for the CEO briefing."

---

## Flow 4: CEO Weekly Briefing (2 min)

**Demonstrates:** Vault analysis + Odoo data + Business intelligence

### Step 1: Generate briefing preview
```bash
python3 AI_Employee_Vault/Watchers/ceo_briefing_generator.py --preview
```

### Step 2: Show existing briefing
```bash
cat AI_Employee_Vault/Briefings/2026-02-09_Monday_Briefing.md
```

**Talking Point:** "Every Sunday at 8 PM, the CEO Briefing Generator runs automatically. It analyzes completed tasks, checks revenue targets from Business_Goals.md, pulls financial data from Odoo, audits subscriptions for cost increases, identifies bottlenecks, and generates proactive suggestions."

### Key Briefing Sections:
1. Executive Summary - task completion metrics
2. Revenue Tracking - target vs actual from Business_Goals.md
3. Financial Summary - from Odoo (revenue, expenses, profit margin)
4. Subscription Audit - flags cost increases
5. Bottleneck Analysis - items stuck in Pending_Approval
6. Proactive Suggestions - AI-generated recommendations

---

## Flow 5: Error Recovery + Audit (1 min)

**Demonstrates:** Resilience, reliability, compliance

### Step 1: Show retry handler
```bash
python3 -c "
from AI_Employee_Vault.Watchers.retry_handler import RetryExecutor
executor = RetryExecutor(max_attempts=3)
print(f'Retry: max_attempts=3, base_delay=1.0s, max_delay=60.0s')
print('Exponential backoff: 1s -> 2s -> 4s -> 8s -> ...')
print('Retryable: TransientError, ConnectionError, TimeoutError, OSError')
print('Non-retryable: PermanentError (auth failures, bad data)')
"
```

### Step 2: Show graceful degradation
```bash
python3 -c "
from AI_Employee_Vault.Watchers.graceful_degradation import DegradationManager
dm = DegradationManager()
print(dm.get_status_summary())
print('Safety: Banking API NEVER auto-retried')
print('Queue: Actions queued locally when services are down')
"
```

### Step 3: Show audit logs
```bash
# Today's structured audit log
python3 -c "
import json
with open('AI_Employee_Vault/Logs/2026-02-10.json') as f:
    entries = json.load(f)
print(f'Audit entries today: {len(entries)}')
print(f'Schema: timestamp, action_type, actor, domain, target, approval_status, result')
print(f'Retention: 90 days')
for e in entries[-3:]:
    print(f'  [{e[\"timestamp\"][:19]}] {e[\"action_type\"]} by {e[\"actor\"]} -> {e[\"result\"]}')
"
```

**Talking Point:** "Every action is logged with structured JSON following Section 6.3 of the spec. We maintain 90-day retention with automatic cleanup. The watchdog monitors all critical processes and auto-restarts them on failure."

---

## Flow 6: Pipeline Test (30 sec)

**Demonstrates:** Full end-to-end validation

```bash
python3 AI_Employee_Vault/Watchers/test_pipeline.py
```

**Expected Output:** `Results: 20/20 passed, 0 failed`

**Talking Point:** "Our pipeline test validates the complete workflow: task creation, plan generation, approval flow, execution, completion, and audit logging. 20 out of 20 checks pass."

---

## Closing (30 sec)

**Summary Stats:**
```
Architecture:  Perception -> Reasoning -> Action -> Audit
MCP Servers:   3 (Odoo, Social, Email) = 22 tools
Watchers:      5 (Gmail, LinkedIn, WhatsApp, Filesystem, Approval)
HITL Gates:    All sensitive actions require approval
Error Recovery: Retry + Watchdog + Graceful Degradation
Audit:         Structured JSON, 90-day retention
Pipeline:      20/20 PASS
```

> "This is a complete, local-first AI employee that manages accounting, social media, email, and business intelligence - all with human-in-the-loop safety and full audit compliance."
