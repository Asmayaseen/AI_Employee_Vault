# Gold Tier Architecture — AI Employee System

**Version:** 2.0 (Gold)
**Date:** 2026-02-16
**Author:** AI Employee Architect

---

## 1. Architecture Overview

The AI Employee is an autonomous business operations system built on a **file-based event-driven architecture**. It uses an Obsidian vault as the central state store, MCP (Model Context Protocol) servers for external integrations, and Claude Code as the AI processor.

### Core Principle
> Files are events. Folder movement is state transition. The vault is the single source of truth.

### Tier Progression
| Tier | Capabilities |
|------|-------------|
| **Bronze** | Gmail watcher, file watcher, vault structure, base processing |
| **Silver** | LinkedIn monitoring/posting, WhatsApp watcher, orchestrator, scheduler |
| **Gold** | Odoo accounting, multi-platform social, CEO briefing, Ralph Wiggum loop, error recovery |

### System Boundary

```
External World                    AI Employee System                     Human
─────────────────    ┌──────────────────────────────────────┐    ─────────────
                     │                                      │
 Gmail ──────────────│──▶ Gmail Watcher ──▶ /Needs_Action   │
 LinkedIn ───────────│──▶ LinkedIn Watcher ──▶ /Needs_Action│
 WhatsApp ───────────│──▶ WhatsApp Watcher ──▶ /Needs_Action│
 File System ────────│──▶ File Watcher ──▶ /Needs_Action    │
                     │                          │           │
                     │         ┌────────────────▼────────┐  │
                     │         │    Claude Processor      │  │
                     │         │  (Plan → Execute → Log)  │  │
                     │         └────────────┬─────────────┘  │
                     │                      │                │
                     │    ┌─────────────────▼──────────┐     │
                     │    │   /Pending_Approval        │─────│──▶ Obsidian Review
                     │    └─────────────────┬──────────┘     │     (HITL)
                     │                      │                │
                     │    ┌─────────────────▼──────────┐     │
                     │    │   /Approved → Execute       │     │
                     │    └─────────────────┬──────────┘     │
                     │                      │                │
                     │         MCP Servers  │                │
                     │    ┌────┬────┬───────▼────┐           │
                     │    │Email│Odoo│Social│File │           │
                     │    └────┴────┴────┴──────┘           │
                     │                      │                │
                     │    ┌─────────────────▼──────────┐     │
                     │    │   /Done + /Logs             │     │
                     │    └────────────────────────────┘     │
                     │                                      │
                     └──────────────────────────────────────┘
```

---

## 2. Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         WATCHERS LAYER                           │
│                                                                  │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────────┐  │
│  │ GmailWatcher │  │ LinkedInWatcher │  │ WhatsAppWatcher   │  │
│  │ (Gmail API)  │  │ (Playwright)    │  │ (Playwright)      │  │
│  └──────┬───────┘  └───────┬─────────┘  └────────┬──────────┘  │
│         │                  │                      │              │
│  ┌──────┴───────┐  ┌──────┴──────────┐  ┌───────┴───────────┐  │
│  │ FileWatcher  │  │ ApprovalWatcher │  │ LinkedInPoster    │  │
│  │ (watchdog)   │  │ (folder poll)   │  │ (Playwright)      │  │
│  └──────┬───────┘  └───────┬─────────┘  └───────┬───────────┘  │
│         │                  │                     │               │
│         └─────────────┬────┴─────────────────────┘               │
│                       ▼                                          │
│              ┌─────────────────┐                                 │
│              │  BaseWatcher    │  (abstract base class)          │
│              │  - check_for_updates()                            │
│              │  - create_action_file()                           │
│              │  - run() loop                                     │
│              │  - log_action()                                   │
│              └─────────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                         │
│                                                                  │
│  ┌──────────────────┐  ┌───────────────┐  ┌──────────────────┐  │
│  │   Orchestrator   │  │   Scheduler   │  │ Ralph Controller │  │
│  │  - start/stop    │  │  - cron jobs  │  │  - loop mgmt     │  │
│  │  - health check  │  │  - briefings  │  │  - self-healing  │  │
│  │  - graceful deg. │  │  - post check │  │  - escalation    │  │
│  └──────────────────┘  └───────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         MCP LAYER                                │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  Email MCP   │  │  Odoo MCP    │  │  Social MCP           │  │
│  │  (IMAP/SMTP) │  │  (JSON-RPC)  │  │  (FB/IG/Twitter API)  │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      REPORTING LAYER                             │
│                                                                  │
│  ┌─────────────────────┐  ┌────────────────┐                    │
│  │ CEO Briefing Gen    │  │   Dashboard    │                    │
│  │ - task analysis     │  │  - real-time   │                    │
│  │ - Odoo financials   │  │  - health viz  │                    │
│  │ - recommendations   │  │  - metrics     │                    │
│  └─────────────────────┘  └────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Event Flow

### Standard Item Processing

```
1. DETECT    → Watcher detects external event (email, message, file)
2. INGEST    → Creates markdown file in /Needs_Action with frontmatter
3. PLAN      → Claude reads item, creates plan in /Plans
4. DECIDE    → If safe: execute directly. If risky: route to /Pending_Approval
5. APPROVE   → Human reviews in Obsidian, moves to /Approved or /Rejected
6. EXECUTE   → ApprovalWatcher triggers MCP action (email, post, invoice)
7. COMPLETE  → File moves to /Done with processing metadata appended
8. LOG       → Action logged to /Logs daily JSON + watcher-specific logs
```

### File as State Machine

```
/Inbox          → Raw ingested items (optional staging)
/Needs_Action   → Items requiring AI processing
/Plans          → AI-generated action plans
/Pending_Approval → Items awaiting human review (HITL)
/Approved       → Human-approved, ready for execution
/Rejected       → Human-rejected items
/Done           → Completed items (with processing metadata)
/Logs           → Audit trail (daily JSON, per-service logs)
/Briefings      → Generated CEO briefing reports
```

---

## 4. MCP Rationale

### Why MCP (Model Context Protocol)?

**Decision:** Use MCP servers as the integration layer between Claude and external services.

**Rationale:**
- **Standardized interface**: MCP provides a uniform tool-calling contract. Each external service (email, Odoo, social media) exposes the same JSON-RPC interface to Claude.
- **Security boundary**: MCP servers run as separate processes with their own credentials. Claude never directly holds API keys.
- **Composability**: New integrations (Slack, Jira, etc.) can be added as new MCP servers without modifying the core system.
- **Testability**: MCP servers can be mocked independently for testing.

**Alternatives considered:**
| Option | Rejected Because |
|--------|-----------------|
| Direct API calls from Claude | No credential isolation, hard to test |
| Webhook-based | Requires public endpoint, complex setup |
| Plugin system | Non-standard, no ecosystem support |

**Trade-off:** MCP adds operational complexity (separate processes to manage) but provides the cleanest separation of concerns.

---

## 5. Dapr Rationale

### Why Dapr Components (Future State)?

**Decision:** Design for Dapr sidecar integration as the system scales beyond single-machine deployment.

**Rationale:**
- **Service invocation**: Dapr provides service-to-service calls with built-in retries, timeouts, and circuit breakers.
- **Pub/Sub**: File-based events can be replaced with Dapr pub/sub for multi-node deployments.
- **State management**: Vault folder state can be backed by Dapr state stores (Redis, CosmosDB) for durability.
- **Bindings**: Input/output bindings replace custom watcher code for standard integrations.

**Current status:** Not yet implemented. The file-based architecture serves as the foundation that maps cleanly to Dapr concepts:

| Current (Files) | Future (Dapr) |
|-----------------|---------------|
| /Needs_Action folder | Dapr pub/sub topic: `needs-action` |
| /Pending_Approval | Dapr state store with workflow |
| Watcher polling | Dapr input bindings (Gmail, etc.) |
| MCP server calls | Dapr service invocation |

---

## 6. Kafka Rationale

### Why Kafka/KRaft (Future State)?

**Decision:** Target Strimzi Kafka (KRaft mode) for event streaming when the system needs guaranteed delivery and event replay.

**Rationale:**
- **Event sourcing**: Every item transition (Needs_Action → Plan → Approval → Done) becomes a Kafka event, enabling full replay and audit.
- **Guaranteed delivery**: At-least-once semantics ensure no business events are lost.
- **Scalability**: Multiple Claude instances can consume from the same topic for parallel processing.
- **KRaft mode**: Eliminates ZooKeeper dependency, simpler operations.

**Current status:** Not implemented. Current file-based system provides adequate throughput for single-operator use. Kafka is the path when:
- Processing volume exceeds 100+ items/day
- Multiple AI agents need to coordinate
- Event replay for compliance/debugging is required

---

## 7. Error Recovery

### Strategy: Graceful Degradation with 6 Levels

| Level | Condition | System Behavior |
|-------|-----------|----------------|
| **L0** | All healthy | Full autonomous processing |
| **L1** | Single service down | Skip service, process rest |
| **L2** | Multiple errors | Conservative mode (slower, more logging) |
| **L3** | Loop detected | Break loop, escalate stuck item |
| **L4** | Error spiral | Stop processing, escalate all |
| **L5** | Critical failure | Emergency stop, incident report |

### Recovery Patterns

**Transient errors** (network, timeout):
- Exponential backoff: 5s → 10s → 20s → 40s → 80s
- Max 5 retries per operation
- Circuit breaker after 3 consecutive failures

**Service degradation**:
- Each watcher has independent health status
- Orchestrator tracks health via `service_health` dict
- Unhealthy services are skipped, not retried continuously

**Browser crashes** (Playwright):
- `_cleanup_browser()` resets all Playwright state
- `_init_browser()` wrapped in try/catch with cleanup on failure
- Page crash detected via `page.url` check after operations

### Health Monitoring

```python
# Orchestrator health thresholds
HEALTH_THRESHOLDS = {
    'gmail': {'max_consecutive_failures': 3, 'restart_delay': 300},
    'linkedin': {'max_consecutive_failures': 2, 'restart_delay': 600},
    'whatsapp': {'max_consecutive_failures': 2, 'restart_delay': 600},
    'file': {'max_consecutive_failures': 5, 'restart_delay': 60},
    'approval': {'max_consecutive_failures': 3, 'restart_delay': 120},
    'odoo': {'max_consecutive_failures': 3, 'restart_delay': 300}
}
```

---

## 8. Security Model

### Credential Management

| Credential | Storage | Access Pattern |
|-----------|---------|---------------|
| Gmail OAuth | `token.json` + `credentials.json` | Gmail API library |
| LinkedIn session | `.linkedin_session/` (Playwright) | Browser context |
| WhatsApp session | `.whatsapp_session/` (Playwright) | Browser context |
| Odoo password | `.env` file | `OdooConfig` dataclass |
| Social API keys | `.env` file | `os.getenv()` per handler |

### Security Boundaries

1. **No secrets in code**: All credentials in `.env` or token files
2. **No secrets in git**: `.gitignore` covers all credential paths
3. **MCP isolation**: Each MCP server has its own credential scope
4. **HITL gate**: External-facing actions require human approval
5. **DRY_RUN default**: System defaults to `DRY_RUN=true` to prevent accidental actions
6. **Audit trail**: Every action logged with actor, timestamp, and result

### HITL (Human-in-the-Loop) Policy

Per the Company Constitution:
- **Always approve**: Payments, external emails, social media posts
- **Auto-safe**: Internal file processing, log generation, plan creation
- **Escalate**: Unknown action types, high-value transactions (> $500)

---

## 9. Observability

### Logging Architecture

```
/Logs/
├── YYYY-MM-DD.json          # Daily action audit log (all watchers)
├── GmailWatcher.log         # Gmail-specific log
├── LinkedInWatcher.log      # LinkedIn-specific log
├── WhatsAppWatcher.log      # WhatsApp-specific log
├── orchestrator.log         # Orchestrator lifecycle
├── scheduler.log            # Scheduled task execution
├── ralph.log                # Ralph loop iterations
├── ralph_metrics_YYYY-MM-DD.json  # Ralph recovery metrics
├── odoo_mcp.log             # Odoo MCP operations
└── approval_watcher.log     # Approval workflow
```

### Key Metrics

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| Items processed/day | Daily JSON log | < 1 (system idle) |
| Avg processing time | Ralph metrics | > 300s per item |
| Error rate | Error count / total | > 10% |
| Pending backlog | /Needs_Action count | > 20 items |
| Approval wait time | Timestamp diff | > 24 hours |
| Odoo connection | Health check | 3 failures |
| Browser health | Playwright state | 2 crashes |

### Dashboard

The `dashboard.py` provides real-time system status:
- Watcher health (up/down/degraded)
- Processing pipeline counts (per folder)
- Recent activity feed
- Error summary

---

## 10. Lessons Learned

### 1. File-Based Architecture Scales Surprisingly Well
Using markdown files as events with folder movement as state transitions proved elegant for single-operator use. Obsidian provides a free, powerful UI. The system processes 50+ items/day without performance issues.

### 2. Playwright Requires Careful Lifecycle Management
Browser automation is fragile. Key learnings:
- Always implement `_cleanup_browser()` that handles partial state
- Wrap `_init_browser()` in try/catch with cleanup on failure
- Detect page crashes by checking `page.url` after operations
- Use persistent contexts for session preservation
- Headless mode with Xvfb is more reliable than headed mode on WSL

### 3. DRY_RUN Should Be the Default
Defaulting to `DRY_RUN=true` prevented multiple accidental social media posts and emails during development. The explicit opt-in to live mode (`DRY_RUN=false`) is a critical safety net.

### 4. HITL Approval via File Movement Is Intuitive
Moving files between folders in Obsidian is natural for human reviewers. No special UI needed. The markdown frontmatter provides machine-readable metadata while the body is human-readable.

### 5. BaseWatcher Abstraction Pays Off
The `BaseWatcher` class with `check_for_updates()` and `create_action_file()` abstract methods made adding new watchers trivial. Each watcher only implements its unique detection logic.

### 6. Odoo JSON-RPC Over XML-RPC
Odoo 18+ JSON-RPC is cleaner than XML-RPC. The unified `/jsonrpc` endpoint handles auth, CRUD, and reporting through a single interface. Standard `urllib` is sufficient — no need for `xmlrpc.client`.

---

## 11. Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| File-based events | Simple, observable, Obsidian UI | Not scalable beyond single machine |
| Playwright for social | Works without API access | Fragile, needs browser |
| MCP for integrations | Clean separation | Extra processes to manage |
| DRY_RUN default | Safety | Must explicitly enable live mode |
| Single orchestrator | Simple coordination | Single point of failure |
| Markdown frontmatter | Human + machine readable | Parsing is fragile |
| Python + asyncio | Fast development | GIL limits true parallelism |
| Obsidian as UI | Free, powerful | Requires desktop app |

### Known Limitations

1. **Single machine**: No multi-node support without Kafka/Dapr
2. **No real-time**: Polling-based watchers (5-300s intervals)
3. **Browser dependency**: LinkedIn/WhatsApp need Playwright + display
4. **No built-in backup**: Vault data relies on git or manual backup
5. **Sequential processing**: One item at a time per watcher

---

## 12. Production Readiness Checklist

### Infrastructure
- [x] Docker Compose for Odoo + Postgres
- [x] Odoo 18+ with JSON-RPC
- [x] Postgres 17 for Odoo backend
- [x] PM2/systemd for process management
- [ ] Automated backup for vault data
- [ ] Monitoring dashboard (Grafana/similar)

### Security
- [x] All secrets in .env files
- [x] .gitignore covers credentials
- [x] DRY_RUN default enabled
- [x] HITL approval for external actions
- [x] Audit logging for all operations
- [ ] Secret rotation schedule
- [ ] Network segmentation for MCP servers

### Reliability
- [x] BaseWatcher with health checks
- [x] Orchestrator graceful degradation
- [x] Browser crash recovery
- [x] Ralph loop self-healing
- [x] Error categorization and retry logic
- [x] Escalation to human on failure
- [ ] Automated health check alerts
- [ ] Runbook for common failures

### Observability
- [x] Per-service log files
- [x] Daily JSON audit log
- [x] Ralph recovery metrics
- [x] Dashboard with system status
- [x] CEO Briefing with metrics summary
- [ ] Centralized log aggregation
- [ ] Alerting on error thresholds

### Testing
- [x] Unit tests for LinkedIn watcher/poster (30 tests)
- [x] Unit tests for base watchers (7 tests)
- [x] DRY_RUN mode for safe testing
- [ ] Integration tests for MCP servers
- [ ] End-to-end pipeline test
- [ ] Load testing for batch processing

### Documentation
- [x] Skill files for all Gold features
- [x] Architecture document (this file)
- [x] Project structure guide
- [x] Environment setup (.env.example files)
- [x] GOLD_SKILLS_INDEX.md
- [ ] Runbook for operations
- [ ] Video walkthrough

---

*Generated for AI Employee Gold Tier — February 2026*
