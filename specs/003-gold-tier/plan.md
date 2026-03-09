# Implementation Plan: Gold Tier - Autonomous Cross-Domain Integration

**Branch**: `003-gold-tier` | **Date**: 2026-02-09 | **Spec**: `/specs/003-gold-tier/spec.md`
**Input**: Feature specification from `/specs/003-gold-tier/spec.md`

## Summary

Gold tier adds autonomous cross-domain integration to the Silver tier's multi-source monitoring and orchestration. It introduces two new MCP servers (Odoo accounting and social media), enterprise-grade error recovery (retry with exponential backoff, graceful degradation, process watchdog), comprehensive audit logging per Constitution Principle III, automated CEO briefing generation, and end-to-end pipeline validation. All financial and social actions are routed through the human-in-the-loop approval workflow.

## Technical Context

**Language/Version**: Python 3.10+, Node.js 18+ (existing email-mcp)
**Primary Dependencies**: python-dotenv, apscheduler, xmlrpc.client (stdlib), mcp SDK, httpx, tweepy, facebook-sdk, flask (dashboard)
**Storage**: Obsidian Vault (Markdown), Odoo PostgreSQL (via XML-RPC), JSON logs
**Testing**: Custom pipeline tests (test_pipeline.py), unit tests (tests/), manual validation
**Target Platform**: Linux (WSL2) / Windows
**Project Type**: Single project with MCP microservices
**Performance Goals**: Process items within 60s, MCP calls <5s, watcher intervals 5s-15min
**Constraints**: Local-first (<500MB memory), human approval for financial/social actions, 90-day log retention

## Constitution Check

*GATE: All checks must PASS before implementation.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Local-First Architecture | PASS | All data in local vault, Odoo self-hosted via Docker, no cloud storage |
| II. Human-in-the-Loop | PASS | FR-021/FR-022: All financial and social actions require approval |
| III. Comprehensive Audit Logging | PASS | audit_logger.py with structured JSON, 90-day retention |
| IV. Agent Skills Standard | PASS | Skills defined in .claude/skills/ for all Gold components |
| V. Graceful Degradation | PASS | graceful_degradation.py tracks service health, queues actions |
| VI. Security Boundaries | PASS | .env for credentials, DRY_RUN default, rate limits |
| VII. Tier-Based Enhancement | PASS | Builds on Silver tier, all Silver features operational |
| VIII. Watcher Pattern | PASS | 5+ watchers managed by orchestrator.py |
| IX. Vault as State Machine | PASS | File movement protocol: Needs_Action -> Plans -> Approval -> Done |

## Project Structure

### Documentation (this feature)

```text
specs/003-gold-tier/
├── spec.md              # This feature specification
├── plan.md              # This file (implementation plan)
├── tasks.md             # Task breakdown
├── checklists/          # Validation checklists
└── contracts/           # API contracts
```

### Source Code (repository root)

```text
AI_Employee_Vault/
├── Watchers/
│   ├── orchestrator.py              # Master coordinator (updated for Gold)
│   ├── claude_processor.py          # AI reasoning loop
│   ├── base_watcher.py              # Abstract watcher base class
│   ├── filesystem_watcher.py        # File drop monitoring
│   ├── gmail_watcher.py             # Gmail monitoring
│   ├── whatsapp_watcher.py          # WhatsApp monitoring
│   ├── linkedin_watcher.py          # LinkedIn monitoring
│   ├── approval_watcher.py          # Approval workflow monitoring
│   ├── audit_logger.py              # [NEW] Structured JSON audit logging
│   ├── retry_handler.py             # [NEW] Exponential backoff retry
│   ├── graceful_degradation.py      # [NEW] Service health & action queueing
│   ├── watchdog.py                  # [NEW] Process crash monitoring
│   ├── ceo_briefing_generator.py    # [NEW] Daily briefing generation
│   ├── test_pipeline.py             # [NEW] E2E pipeline validation
│   ├── scheduler.py                 # Task scheduling (updated)
│   └── dashboard.py                 # Web dashboard (updated)
├── models/                          # [NEW] Centralized data models
│   ├── __init__.py
│   ├── action_item.py               # ActionItem dataclass
│   ├── approval_request.py          # ApprovalRequest dataclass
│   ├── plan.py                      # Plan and PlanStep dataclasses
│   ├── watcher_config.py            # WatcherConfig, WatcherState
│   ├── log_entry.py                 # LogEntry, AuditEntry
│   └── service_state.py             # ServiceState, ServiceStatus
├── utils/                           # [NEW] Shared utilities
│   ├── __init__.py
│   ├── vault_helpers.py             # Vault path/dir/frontmatter helpers
│   ├── file_helpers.py              # Safe write, atomic move, filename gen
│   └── config.py                    # Centralized config loading
├── tests/                           # [NEW] Test suite
│   ├── __init__.py
│   ├── test_models.py               # Data model unit tests
│   ├── test_vault_structure.py      # Vault validation tests
│   └── test_watchers.py             # Watcher behavior tests
├── scripts/                         # [NEW] Utility scripts
│   ├── __init__.py
│   ├── health_check.py              # System health diagnostic
│   ├── vault_cleanup.py             # Log/file cleanup
│   └── export_logs.py               # Audit log export (CSV/JSON)
└── schedulers/                      # [NEW] Schedule configurations
    ├── __init__.py
    └── schedule_config.py           # Cron definitions and task configs

MCP_Servers/
├── email-mcp/                       # [EXISTING] Gmail integration (Node.js)
│   ├── index.js
│   └── package.json
├── odoo-mcp/                        # [NEW] Odoo accounting integration
│   ├── server.py                    # Main MCP server entry point
│   ├── odoo_client.py               # XML-RPC/JSON-RPC client
│   ├── config.py                    # Odoo connection configuration
│   ├── docker-compose.yml           # Odoo + PostgreSQL deployment
│   ├── requirements.txt             # Python dependencies
│   ├── test_connection.py           # Connection validation
│   └── tools/
│       ├── __init__.py
│       ├── invoice.py               # create_invoice, list_unpaid, post_invoice
│       ├── customer.py              # add_customer, search_customer
│       ├── financial.py             # fetch_financial_summary
│       └── expense.py               # record_expense, list_expenses
└── social-mcp/                      # [NEW] Social media integration
    ├── server.py                    # Main MCP server entry point
    ├── config.py                    # Platform credentials configuration
    ├── requirements.txt             # Python dependencies
    ├── adapters/
    │   ├── __init__.py
    │   ├── base.py                  # Abstract platform adapter
    │   ├── facebook.py              # Facebook Graph API adapter
    │   ├── instagram.py             # Instagram Graph API adapter
    │   └── twitter.py               # Twitter API v2 adapter
    └── tools/
        ├── __init__.py
        └── social_tools.py          # post_content, read_messages, etc.
```

**Structure Decision**: Single project with MCP microservices pattern. Each external integration gets its own MCP server directory for independent deployment and testing. Shared code extracted to models/, utils/, tests/, scripts/, schedulers/ under the vault root.

## Complexity Tracking

| Component | Complexity | Justification |
|-----------|-----------|---------------|
| Odoo MCP (5 tool types) | Medium | Standard CRUD over XML-RPC, well-documented Odoo API |
| Social MCP (3 adapters) | High | Each platform has different API, rate limits, auth flows |
| Retry + Degradation | Medium | Well-known patterns (exponential backoff, circuit breaker) |
| Audit Logger | Low | JSON append to daily files, thread lock |
| CEO Briefing | Medium | Data aggregation from multiple sources, template formatting |
| Pipeline Testing | Low | Sequential stage validation with assertions |
