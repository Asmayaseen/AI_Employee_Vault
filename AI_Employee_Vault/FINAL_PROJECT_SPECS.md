---
title: Final Project Specifications
created: 2026-02-10T15:25:00
tier: gold
version: 2.0
status: complete
---

# Final Project Specifications - Personal AI Employee (Gold Tier)

**Version:** 2.0
**Tier:** Gold (Autonomous Employee)
**Architecture:** Perception -> Reasoning -> Action -> Audit + HITL

---

## 1. System Overview

The Personal AI Employee is a local-first, autonomous Digital FTE (Full-Time Equivalent) that manages business operations 24/7 using Claude Code, Obsidian Vault, and MCP (Model Context Protocol) servers with human-in-the-loop safety gates.

### 1.1 Architecture Layers

| Layer | Purpose | Components |
|-------|---------|------------|
| **Perception** | Detect external events | 5 Watchers (Gmail, LinkedIn, WhatsApp, Filesystem, Approval) |
| **Memory** | Structured data store | Obsidian Vault with 13 directories |
| **Reasoning** | Analyze and plan | Claude Code + Processor + Orchestrator + CEO Briefing |
| **Action** | Execute operations | 3 MCP Servers (22 tools total) |
| **Safety** | Prevent unauthorized actions | HITL approval gates, Company Handbook rules |
| **Reliability** | Handle failures | Retry, Watchdog, Graceful Degradation |
| **Audit** | Compliance trail | Structured JSON logging, 90-day retention |

### 1.2 Tool Count

| Server | Language | Protocol | Tools |
|--------|----------|----------|-------|
| Odoo MCP | Python | JSON-RPC | 7 |
| Social MCP | Python | REST APIs | 10 |
| Email MCP | Node.js | Gmail API | 5 |
| **Total** | | | **22** |

---

## 2. MCP Server Specifications

### 2.1 Odoo MCP Server

**Location:** `MCP_Servers/odoo-mcp/`
**Protocol:** JSON-RPC (Odoo 17+/19+ compatible)
**Entry Point:** `server.py`

#### Tools

| Tool | Input | Output | HITL Required |
|------|-------|--------|---------------|
| `create_invoice` | customer_name, invoice_lines, due_date | Draft invoice ID, total | Yes (>$500) |
| `get_unpaid_invoices` | status (unpaid/overdue/all), limit | Invoice list with amounts | No |
| `post_invoice` | invoice_id | Posted invoice confirmation | Yes |
| `create_customer` | name, email, phone, company | Customer ID | No |
| `get_financial_summary` | period, company_id | Revenue, expenses, profit | No |
| `record_expense` | vendor, amount, description, category | Expense record ID | Yes |
| `get_subscription_audit` | period_days | Subscription list with cost flags | No |

#### Configuration

```
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=<from .env>
ODOO_API_VERSION=2
ODOO_TIMEOUT=30
ODOO_APPROVAL_THRESHOLD=500
```

#### Client Architecture

- `OdooJSONRPCClient` class
- Services: `common` (auth), `object` (CRUD), `db` (admin)
- `OdooResult` wrapper: `{success, data, error, error_code}`
- Supports `authenticate()`, `version_info()`, `search()`, `search_read()`, `create()`, `write()`, `unlink()`

### 2.2 Social MCP Server

**Location:** `MCP_Servers/social-mcp/`
**Entry Point:** `server.py`

#### Platform Adapters

| Platform | Adapter File | API |
|----------|-------------|-----|
| Facebook | `adapters/facebook.py` | Graph API v18.0 |
| Instagram | `adapters/instagram.py` | Graph API v18.0 (Business) |
| Twitter | `adapters/twitter.py` | API v2 |
| Base | `adapters/base.py` | Abstract base class |

#### Tools

| Tool | Platform | Description | HITL |
|------|----------|-------------|------|
| `fb_post_message` | Facebook | Post message with optional link/hashtags | Yes |
| `fb_fetch_recent_posts` | Facebook | Fetch posts with engagement data | No |
| `fb_generate_summary` | Facebook | Weekly performance summary | No |
| `ig_post_image_caption` | Instagram | Post image with caption | Yes |
| `ig_fetch_recent_posts` | Instagram | Fetch recent posts | No |
| `ig_engagement_summary` | Instagram | Engagement metrics report | No |
| `tw_post_tweet` | Twitter | Post tweet | Yes |
| `tw_fetch_mentions` | Twitter | Fetch mentions/replies | No |
| `tw_generate_weekly_summary` | Twitter | Weekly summary | No |
| `generate_all_summaries` | All | Cross-platform combined report | No |

### 2.3 Email MCP Server

**Location:** `MCP_Servers/email-mcp/`
**Runtime:** Node.js
**Entry Point:** `index.js`

#### Tools

| Tool | Description | HITL |
|------|-------------|------|
| `send_email` | Send approved email drafts | Yes |
| `draft_email` | Create email draft | No |
| `search_emails` | Search Gmail with query | No |
| `get_email` | Get email details by ID | No |
| `list_labels` | List Gmail labels | No |

#### Configuration

```
GMAIL_CREDENTIALS_PATH=<path to credentials.json>
DRY_RUN=true|false
VAULT_PATH=<path to vault>
```

---

## 3. Watcher Specifications

### 3.1 Watcher Architecture

All watchers extend `BaseWatcher` (`base_watcher.py`):
- Polling-based with configurable intervals
- Creates structured `.md` files in `/Needs_Action/`
- Maintains `.processed_*` tracking files
- Logging to `/Logs/`

### 3.2 Individual Watchers

| Watcher | Interval | Source | Output | Technology |
|---------|----------|--------|--------|------------|
| Gmail | 120s | Gmail API | Email .md files | OAuth2 + Google APIs |
| LinkedIn | 300s | LinkedIn web | Message/notification .md | Playwright browser |
| WhatsApp | 180s | WhatsApp Web | Message .md files | Playwright browser |
| Filesystem | Realtime | `/Inbox/` folder | File .md records | Watchdog observer |
| Approval | 5s | `/Approved/` | Action triggers | File polling |

### 3.3 Approval Watcher HITL Flow

```
Needs_Action -> Claude Processor -> Plan
    -> Pending_Approval (if approval needed)
    -> Human reviews in Obsidian
    -> Moves to Approved OR Rejected
    -> Approval Watcher detects move
    -> Triggers MCP action
    -> Moves to Done
    -> Audit log written
```

**Action Handlers:**
- `email_send` -> Email MCP
- `payment` -> Odoo MCP (HITL mandatory)
- `social_post` -> Social MCP
- `general` -> Default handler

**Timeout:** 24 hours (configurable via `APPROVAL_TIMEOUT_HOURS`)

---

## 4. Error Recovery Specifications

### 4.1 Retry Handler

**File:** `retry_handler.py`
**Strategy:** Exponential backoff with jitter

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_attempts` | 3 | Maximum retry count |
| `base_delay` | 1.0s | Initial delay |
| `max_delay` | 60.0s | Maximum delay cap |
| Retryable | `TransientError, ConnectionError, TimeoutError, OSError` | |
| Non-retryable | `PermanentError` | Auth failures, invalid data |

**Custom Exceptions:**
- `TransientError` - May succeed on retry
- `PermanentError` - Will not benefit from retry
- `RetryExhaustedError` - All attempts failed

### 4.2 Watchdog Process Monitor

**File:** `watchdog.py`
**Check Interval:** 60 seconds

| Process | Critical | Max Restarts | Window |
|---------|----------|-------------|--------|
| `gmail_watcher` | Yes | 5 | 300s |
| `linkedin_watcher` | No | 3 | 300s |
| `filesystem_watcher` | Yes | 10 | 300s |
| `approval_watcher` | Yes | 5 | 300s |

### 4.3 Graceful Degradation

**File:** `graceful_degradation.py`
**Service States:** HEALTHY -> DEGRADED -> UNAVAILABLE

| Parameter | Value |
|-----------|-------|
| Degraded threshold | 2 failures |
| Unavailable threshold | 5 failures |
| Recovery window | 300 seconds |
| Queue directory | `/Queued_Actions/` |

**Safety Rules:**
- Gmail API down: Queue outgoing emails locally
- Banking API timeout: NEVER retry payments automatically
- Claude Code unavailable: Watchers continue, queue grows
- Obsidian vault locked: Write to temp, sync later

---

## 5. Audit Logging Specification

**File:** `audit_logger.py`
**Schema:** Section 6.3 compliant

### Log Entry Schema

```json
{
  "timestamp": "ISO-8601",
  "action_type": "string",
  "actor": "string (claude_code|human|pipeline_test|watcher)",
  "domain": "string (gmail|vault|odoo|social|system)",
  "target": "string (filename or identifier)",
  "parameters": {},
  "approval_status": "string (pending|approved|rejected|null)",
  "approved_by": "string (human|null)",
  "result": "string (success|failure|queued)",
  "error": "string (null or error message)"
}
```

### Retention Policy

| Parameter | Value |
|-----------|-------|
| Format | JSON array per day |
| Filename | `YYYY-MM-DD.json` |
| Retention | 90 days |
| Cleanup | Automatic on logger init |
| Thread Safety | `threading.Lock` |
| Directory | `AI_Employee_Vault/Logs/` |

---

## 6. CEO Briefing Specification

**File:** `ceo_briefing_generator.py`
**Schedule:** Sunday 8:00 PM (cron)
**Output:** `Briefings/YYYY-MM-DD_Monday_Briefing.md`

### Data Sources

| Source | Type | Data |
|--------|------|------|
| `/Done/` folder | Vault | Completed task metrics |
| `Business_Goals.md` | Vault | Revenue targets, project status |
| Odoo MCP | API | Revenue, expenses, profit, receivables |
| Subscription audit | API | Recurring costs, cost-increase flags |
| `/Pending_Approval/` | Vault | Bottleneck items |

### Briefing Sections

1. **Executive Summary** - Period, tasks completed, completion rate
2. **Revenue Tracking** - Target vs actual, progress percentage
3. **Financial Summary** - Revenue, expenses, profit margin (from Odoo)
4. **Subscription Audit** - Recurring costs, flagged increases
5. **Task Breakdown** - By type (email, file, plan, etc.)
6. **Bottleneck Analysis** - Stale items in Pending_Approval
7. **Proactive Suggestions** - AI-generated recommendations
8. **System Health** - Watcher status, error counts

### Data Classes

- `TaskInfo` - filename, title, completed_date, task_type, priority
- `BusinessGoals` - revenue_target, metrics, active_projects
- `AccountingData` - revenue, expenses, profit, receivables, subscriptions
- `BriefingData` - period_start, period_end, all aggregated data

---

## 7. Vault Structure Specification

```
AI_Employee_Vault/
  .env                          # Environment variables
  .env.example                  # Configuration template
  Dashboard.md                  # System status dashboard
  Company_Handbook.md           # Autonomy rules & boundaries
  Business_Goals.md             # Revenue targets & metrics
  Inbox/                        # Raw inbound items
  Needs_Action/                 # Watcher-created tasks
  Plans/                        # Claude-generated action plans
  Pending_Approval/             # HITL approval queue
  Approved/                     # Human-approved actions
  Rejected/                     # Human-rejected actions
  Done/                         # Completed task archive
  Logs/                         # Structured audit logs (JSON)
  Accounting/                   # Financial records
  Briefings/                    # CEO briefing reports
  Reports/                      # Generated reports
  Queued_Actions/               # Graceful degradation queue
  Demo/                         # Demo scenario files
  Watchers/                     # Watcher scripts
  Specs/                        # Technical specifications
  History/                      # Execution history
  MCP_Servers/                  # MCP server references
  models/                       # Data models
  schedulers/                   # Scheduling logic
  scripts/                      # Utility scripts
  tests/                        # Test files
  utils/                        # Utility modules
```

---

## 8. Security Specification

### 8.1 Secret Management
- All secrets via `.env` files (never hardcoded)
- `.env` excluded from git via `.gitignore`
- OAuth tokens stored locally
- API keys per platform in environment variables

### 8.2 HITL Safety Gates

| Gate | Condition | Action |
|------|-----------|--------|
| Invoice creation | Amount > $500 | Require human approval |
| All payments | Always | Require human approval |
| Social media posts | Always | Require human approval |
| Email sending | Always | Require human approval |
| Banking API retry | Always | NEVER auto-retry |

### 8.3 Audit Compliance
- Every action logged with structured JSON
- 90-day retention with automatic cleanup
- Full approval chain recorded (who requested, who approved)
- Thread-safe concurrent logging

---

## 9. Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Reasoning Engine | Claude Code | Latest |
| Knowledge Base | Obsidian Vault | Markdown files |
| Accounting API | Odoo Community | 17+/19+ (JSON-RPC) |
| Social APIs | Meta Graph, Twitter v2 | v18.0, v2 |
| Email API | Gmail API | v1 (OAuth2) |
| Browser Automation | Playwright | Python |
| Process Monitor | Custom watchdog | Python 3.10+ |
| Deployment | WSL2 + Docker | Linux |

---

## 10. Validation Results

| Validation | Result |
|------------|--------|
| Pipeline Test | 20/20 PASS |
| Gold Tier Requirements | 11/11 PASS |
| Security Audit | PASS |
| Demo Readiness | 9/10 |
| MCP Tool Count | 22/22 |
| Watcher Count | 5/5 |
| Error Recovery | 3/3 |
| Audit Logging | Active |
