# Contract: Audit Log Schema

**Feature**: 003-gold-tier
**Created**: 2026-02-09
**Type**: Data Contract
**Reference**: Constitution Principle III (Comprehensive Audit Logging)

## Overview

Every action the AI Employee takes MUST be logged in this structured format. Logs are stored as JSON arrays in daily files: `/Logs/YYYY-MM-DD.json`.

## Schema

```json
{
  "timestamp": "string (ISO-8601, required)",
  "action_type": "string (required)",
  "actor": "string (required)",
  "domain": "string (required)",
  "target": "string (required)",
  "parameters": "object (required, may be empty {})",
  "approval_status": "string (required)",
  "approved_by": "string (required)",
  "result": "string (required)",
  "error": "string (optional, only on failure)"
}
```

## Field Definitions

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `timestamp` | string | YES | ISO-8601 | When the action occurred |
| `action_type` | string | YES | See below | What was done |
| `actor` | string | YES | `claude_code`, `watcher`, `orchestrator`, `scheduler` | Who performed it |
| `domain` | string | YES | `gmail`, `odoo`, `social`, `filesystem`, `vault`, `system` | Which system |
| `target` | string | YES | Identifier | Target of the action (email, invoice ID, etc.) |
| `parameters` | object | YES | Any | Action-specific parameters |
| `approval_status` | string | YES | `approved`, `rejected`, `auto_approved`, `not_required` | Approval state |
| `approved_by` | string | YES | `human`, `system_rule`, `n/a` | Who approved |
| `result` | string | YES | `success`, `failure`, `pending`, `skipped` | Outcome |
| `error` | string | NO | Error message | Only present on failure |

## Action Types

| action_type | Domain | Description |
|-------------|--------|-------------|
| `email_send` | gmail | Email sent via MCP |
| `email_draft` | gmail | Email draft created |
| `email_read` | gmail | Email fetched/read |
| `invoice_create` | odoo | Invoice created |
| `invoice_post` | odoo | Invoice confirmed |
| `customer_create` | odoo | Customer added |
| `expense_record` | odoo | Expense recorded |
| `financial_query` | odoo | Financial summary fetched |
| `social_post` | social | Content posted to platform |
| `social_read` | social | Messages/notifications read |
| `file_detect` | filesystem | New file detected by watcher |
| `file_process` | vault | Action file processed |
| `file_move` | vault | File moved between folders |
| `plan_create` | vault | Plan.md generated |
| `approval_create` | vault | Approval request created |
| `approval_decide` | vault | Approval approved/rejected |
| `briefing_generate` | system | CEO briefing generated |
| `watcher_start` | system | Watcher process started |
| `watcher_stop` | system | Watcher process stopped |
| `watcher_restart` | system | Watcher auto-restarted |
| `health_check` | system | System health check |
| `log_cleanup` | system | Old logs cleaned |

## Example Entries

```json
[
  {
    "timestamp": "2026-02-09T10:30:00.000Z",
    "action_type": "email_send",
    "actor": "claude_code",
    "domain": "gmail",
    "target": "client@acme.com",
    "parameters": {"subject": "Invoice attached", "has_attachment": true},
    "approval_status": "approved",
    "approved_by": "human",
    "result": "success"
  },
  {
    "timestamp": "2026-02-09T10:31:00.000Z",
    "action_type": "invoice_create",
    "actor": "claude_code",
    "domain": "odoo",
    "target": "INV/2026/0042",
    "parameters": {"customer": "Acme Corp", "amount": 1500.00},
    "approval_status": "approved",
    "approved_by": "human",
    "result": "success"
  },
  {
    "timestamp": "2026-02-09T10:32:00.000Z",
    "action_type": "social_post",
    "actor": "claude_code",
    "domain": "social",
    "target": "twitter:post_12345",
    "parameters": {"platforms": ["twitter", "facebook"], "text": "Quarterly update..."},
    "approval_status": "approved",
    "approved_by": "human",
    "result": "failure",
    "error": "Facebook API timeout after 3 retries"
  }
]
```

## Retention Policy

- **Minimum retention**: 90 days (Constitution Principle III)
- **Cleanup**: Daily at midnight via `vault_cleanup.py`
- **Archive**: Old logs deleted (not archived) after retention period
- **Storage**: Estimated ~1MB per active day

## Invariants

1. Every action MUST have a corresponding audit log entry
2. Log writes MUST be thread-safe (use locking)
3. Log entries MUST NOT contain credentials, tokens, or secrets
4. Failed log writes MUST NOT block the action itself (log best-effort)
5. Logs MUST be valid JSON (parseable by standard tools)
6. Retention cleanup MUST NOT delete logs newer than 90 days
