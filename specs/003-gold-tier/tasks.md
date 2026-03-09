---
description: "Task list for Gold Tier implementation"
---

# Tasks: Gold Tier - Autonomous Cross-Domain Integration

**Input**: Design documents from `/specs/003-gold-tier/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)
**Status**: All tasks completed (retroactive documentation)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- All tasks marked [x] as this is retroactive documentation of completed work

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Gold tier structure

- [x] T001 Create MCP_Servers/odoo-mcp/ directory structure per plan
- [x] T002 [P] Create MCP_Servers/social-mcp/ directory structure per plan
- [x] T003 [P] Configure odoo-mcp requirements.txt (mcp, xmlrpc, python-dotenv)
- [x] T004 [P] Configure social-mcp requirements.txt (mcp, httpx, tweepy, facebook-sdk)
- [x] T005 [P] Set up .env.example files for both MCP servers

**Checkpoint**: MCP server scaffolding ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before user story work

**Critical**: Error recovery and audit logging are prerequisites for all autonomous operations.

- [x] T006 [US3] Implement retry_handler.py with exponential backoff in AI_Employee_Vault/Watchers/
  - TransientError, PermanentError, RetryExhaustedError exception classes
  - `with_retry` decorator (max_attempts, base_delay, max_delay, retryable_exceptions)
  - RetryExecutor class for imperative retry usage
- [x] T007 [P] [US3] Implement graceful_degradation.py in AI_Employee_Vault/Watchers/
  - ServiceStatus enum (HEALTHY, DEGRADED, UNAVAILABLE)
  - ServiceState dataclass with failure tracking and thresholds
  - DegradationManager with report_failure(), is_available(), queue_action()
  - Action queue stored in /Queued_Actions/ as JSON files
- [x] T008 [P] [US5] Implement audit_logger.py in AI_Employee_Vault/Watchers/
  - AuditLogger class with thread-safe JSON log writing
  - Daily log files: /Logs/YYYY-MM-DD.json
  - Schema per Constitution Principle III (timestamp, action_type, actor, target, result, etc.)
  - 90-day retention with automatic cleanup
  - Query methods: get_logs_by_date(), get_logs_by_action()
- [x] T009 [US3] Implement watchdog.py process monitoring in AI_Employee_Vault/Watchers/
  - Monitor watcher processes for crashes
  - Auto-restart up to max_restarts limit
  - Alert human when restart limit exceeded

**Checkpoint**: Foundation ready - error recovery and audit operational

---

## Phase 3: User Story 1 - Odoo Accounting Integration (P1) MVP

**Goal**: Create Odoo MCP server enabling invoice, customer, expense, and financial operations

**Independent Test**: Deploy Odoo via docker-compose, run test_connection.py, create test invoice

- [x] T010 [US1] Create odoo_client.py JSON-RPC client in MCP_Servers/odoo-mcp/
  - XML-RPC connection to Odoo (authenticate, execute_kw)
  - Connection pooling and health checks
  - Error translation (Odoo faults -> TransientError/PermanentError)
- [x] T011 [US1] Create config.py for Odoo MCP configuration
  - Load from .env: ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
  - Validation on startup
- [x] T012 [P] [US1] Implement invoice.py tools in MCP_Servers/odoo-mcp/tools/
  - create_invoice: Create account.move with partner, lines, due_date
  - list_unpaid_invoices: Query unpaid account.move records
  - post_invoice: Confirm draft invoice
  - get_invoice: Fetch invoice by ID
- [x] T013 [P] [US1] Implement customer.py tools in MCP_Servers/odoo-mcp/tools/
  - add_customer: Create/update res.partner record
  - search_customer: Search by name/email
  - get_customer: Fetch by ID
- [x] T014 [P] [US1] Implement financial.py tools in MCP_Servers/odoo-mcp/tools/
  - fetch_financial_summary: Aggregate revenue, expenses, profit for period
- [x] T015 [P] [US1] Implement expense.py tools in MCP_Servers/odoo-mcp/tools/
  - record_expense: Create hr.expense record
  - list_expenses: Query expenses by date/category
- [x] T016 [US1] Create server.py main MCP entry point in MCP_Servers/odoo-mcp/
  - Register all tool handlers
  - MCP server initialization with stdio transport
- [x] T017 [US1] Create docker-compose.yml for Odoo + PostgreSQL deployment
- [x] T018 [US1] Create test_connection.py for connection validation

**Checkpoint**: Odoo MCP server fully functional and testable independently

---

## Phase 4: User Story 2 - Social Media Integration (P2)

**Goal**: Create Social MCP server with Facebook, Instagram, Twitter adapters

**Independent Test**: Configure one adapter, post test content, verify via platform

- [x] T019 [US2] Create base.py abstract adapter in MCP_Servers/social-mcp/adapters/
  - Abstract methods: post(), read_messages(), get_notifications(), get_analytics()
  - Common error handling and rate limiting
- [x] T020 [P] [US2] Implement facebook.py adapter (Graph API)
- [x] T021 [P] [US2] Implement instagram.py adapter (Graph API)
- [x] T022 [P] [US2] Implement twitter.py adapter (API v2)
- [x] T023 [US2] Create social_tools.py tool handlers in MCP_Servers/social-mcp/tools/
  - post_content, read_messages, fetch_notifications, get_analytics, schedule_post
- [x] T024 [US2] Create server.py Social MCP entry point
- [x] T025 [US2] Create config.py for Social MCP configuration

**Checkpoint**: Social MCP server functional for all 3 platforms

---

## Phase 5: User Story 4 - CEO Briefing Generation (P2)

**Goal**: Automated daily briefing aggregating all system data

**Independent Test**: Run briefing generator, verify Markdown output in /Briefings/

- [x] T026 [US4] Implement ceo_briefing_generator.py in AI_Employee_Vault/Watchers/
  - Aggregate data from: Needs_Action, Done, Logs, Pending_Approval
  - Financial summary section (from Odoo if available)
  - Email/message summary section
  - Pending items and approval queue
- [x] T027 [US4] Add briefing templates and formatting
  - Date-stamped filename: BRIEFING_YYYY-MM-DD.md
  - Sections: Executive Summary, Action Items, Financial, Communications, System Health
- [x] T028 [US4] Integrate with scheduler for daily 8:00 AM execution

**Checkpoint**: CEO briefing generates automatically with multi-source data

---

## Phase 6: User Story 6 - End-to-End Pipeline Testing (P2)

**Goal**: Validate complete pipeline from Needs_Action through Done

**Independent Test**: Run test_pipeline.py --validate, all stages pass

- [x] T029 [US6] Implement test_pipeline.py in AI_Employee_Vault/Watchers/
  - Stage 1: Validate vault folder structure
  - Stage 2: Create test item in Needs_Action
  - Stage 3: Verify plan generation
  - Stage 4: Verify approval request creation
  - Stage 5: Simulate approval (move to Approved/)
  - Stage 6: Verify action execution
  - Stage 7: Verify item in Done/ and audit log written
- [x] T030 [US6] Add test result reporting
  - PASS/FAIL per stage with timestamps
  - Generate validation report in /Reports/

**Checkpoint**: Full pipeline validated end-to-end

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Integration, shared infrastructure, and documentation

- [x] T031 [P] Create models/ directory with centralized data models
  - ActionItem, ApprovalRequest, Plan, WatcherConfig, LogEntry, ServiceState
- [x] T032 [P] Create utils/ directory with shared helpers
  - vault_helpers.py, file_helpers.py, config.py
- [x] T033 [P] Create tests/ directory with unit tests
  - test_models.py, test_vault_structure.py, test_watchers.py
- [x] T034 [P] Create scripts/ directory with maintenance scripts
  - health_check.py, vault_cleanup.py, export_logs.py
- [x] T035 [P] Create schedulers/ directory with schedule configurations
  - schedule_config.py with all cron definitions
- [x] T036 Update orchestrator.py to manage new MCP servers
- [x] T037 Update scheduler.py with Gold tier task definitions
- [x] T038 Create gold_tier_validation_report.md in /Reports/
- [x] T039 Integrate all components for full Gold tier demo

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user stories
- **US1 Odoo (Phase 3)**: Depends on Phase 2 (retry handler, audit logger)
- **US2 Social (Phase 4)**: Depends on Phase 2 (retry handler, audit logger)
- **US4 Briefing (Phase 5)**: Depends on Phase 3 (needs Odoo data for financial section)
- **US6 Pipeline (Phase 6)**: Depends on Phases 3-5 (validates entire system)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Odoo)**: Can start after Phase 2 - Independent of US2
- **US2 (Social)**: Can start after Phase 2 - Independent of US1, can run parallel with US1
- **US3 (Error Recovery)**: IS Phase 2 - No dependencies on other stories
- **US4 (Briefing)**: Depends on US1 for financial data, but works partially without it
- **US5 (Audit)**: IS Phase 2 - No dependencies on other stories
- **US6 (Pipeline)**: Depends on US1, US3, US5 - Tests the integrated system

### Parallel Opportunities

- T003, T004, T005 can all run in parallel (different MCP servers)
- T007, T008 can run in parallel (different files, no shared dependencies)
- T012-T015 can all run in parallel (different Odoo tool modules)
- T020-T022 can all run in parallel (different platform adapters)
- T031-T035 can all run in parallel (different directories)

---

## Implementation Strategy

### MVP First (Phase 2 + Phase 3)

1. Complete Phase 1: Setup scaffolding
2. Complete Phase 2: Error recovery + audit (CRITICAL foundation)
3. Complete Phase 3: Odoo MCP (primary business value)
4. **STOP and VALIDATE**: Test Odoo integration independently
5. Demo: Invoice creation + financial summary

### Incremental Delivery

1. Setup + Foundational -> Error recovery operational
2. Add Odoo MCP -> Financial automation (MVP!)
3. Add Social MCP -> Social media automation
4. Add CEO Briefing -> Daily executive summary
5. Add Pipeline Testing -> Quality validation
6. Polish -> Shared infrastructure, tests, scripts
