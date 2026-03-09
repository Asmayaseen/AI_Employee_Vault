# Feature Specification: Gold Tier - Autonomous Cross-Domain Integration

**Feature Branch**: `003-gold-tier`
**Created**: 2026-02-09
**Status**: Implemented (Retroactive Spec)
**Tier**: Gold - Autonomous Integration Layer
**Depends On**: Silver Tier (002-silver-tier)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Odoo Accounting Integration (Priority: P1)

As a user, I want the AI Employee to manage invoices, customers, expenses, and financial summaries through Odoo so I can automate my accounting workflows without switching tools.

**Why this priority**: Core business value - automated accounting is the primary Gold tier differentiator. Financial visibility directly impacts business decisions and CEO briefings.

**Independent Test**: Can be fully tested by deploying Odoo via Docker, connecting the MCP server, and creating a test invoice. Delivers value even without social media integration.

**Acceptance Scenarios**:

1. **Given** Odoo MCP server is configured with valid credentials, **When** `create_invoice` is called with customer and line items, **Then** invoice created in Odoo with correct totals and returned invoice_id
2. **Given** Odoo has existing invoices, **When** `fetch_financial_summary` is called for this_month, **Then** summary returned with revenue, expenses, profit, and invoice counts
3. **Given** a new customer name, **When** `add_customer` is called, **Then** customer created in Odoo res.partner model with returned customer_id
4. **Given** unpaid invoices exist, **When** `list_unpaid_invoices` is called, **Then** all unpaid invoices returned with amounts and due dates
5. **Given** an expense report, **When** `record_expense` is called, **Then** expense recorded in Odoo hr.expense with category and amount

---

### User Story 2 - Social Media Integration (Priority: P2)

As a user, I want the AI Employee to post content and monitor messages across Facebook, Instagram, and Twitter so I can maintain a consistent social media presence automatically.

**Why this priority**: Extends AI Employee reach to social channels. Lower priority than accounting since social media is less time-critical than financial operations.

**Independent Test**: Can be tested by configuring one platform adapter (e.g., Twitter) and posting a test tweet. Each platform adapter works independently.

**Acceptance Scenarios**:

1. **Given** social MCP server is configured, **When** `post_content` is called with text and platform list, **Then** content posted to each specified platform with returned post IDs
2. **Given** Facebook adapter is configured, **When** `read_messages` is called, **Then** unread DMs returned with sender info and timestamps
3. **Given** scheduled post parameters, **When** `schedule_post` is called, **Then** post queued for specified datetime
4. **Given** active social accounts, **When** `get_analytics` is called, **Then** engagement metrics returned per platform

---

### User Story 3 - Enterprise Error Recovery (Priority: P1)

As a user, I want the system to handle failures gracefully with automatic retry and degradation so it continues operating even when external services are down.

**Why this priority**: Critical for autonomous operation. Without error recovery, any service failure stops the entire system. Constitution Principle V mandates graceful degradation.

**Independent Test**: Can be tested by simulating service failures (disconnect network) and verifying system queues actions and recovers automatically.

**Acceptance Scenarios**:

1. **Given** an API call fails with a transient error (timeout), **When** retry handler is invoked, **Then** operation retried with exponential backoff up to max_attempts
2. **Given** a service has failed 5+ times, **When** degradation manager checks status, **Then** service marked UNAVAILABLE and actions queued locally
3. **Given** an unavailable service recovers, **When** next health check succeeds, **Then** status restored and queued actions replayed
4. **Given** a permanent error (bad credentials), **When** retry handler detects PermanentError, **Then** no retry attempted, human alerted
5. **Given** a watcher process crashes, **When** watchdog detects missing process, **Then** process auto-restarted up to max_restarts limit

---

### User Story 4 - CEO Briefing Generation (Priority: P2)

As a user, I want a daily automated briefing summarizing all system activity, pending items, and financial status so I can start each day with a complete overview.

**Why this priority**: High user value for daily operations but not system-critical. Depends on other data sources (email, files, Odoo) being operational.

**Independent Test**: Can be tested by running briefing generator with existing vault data. Works with whatever data is available.

**Acceptance Scenarios**:

1. **Given** vault has items in various folders, **When** briefing generator runs, **Then** Markdown briefing created in /Briefings/ with date-stamped filename
2. **Given** Odoo is connected, **When** briefing includes financial data, **Then** revenue, outstanding invoices, and expense summary included
3. **Given** emails were processed today, **When** briefing generated, **Then** email summary section shows count, senders, and action items

---

### User Story 5 - Comprehensive Audit Logging (Priority: P1)

As a user, I want every AI action logged in a structured, queryable format so I can review what the system did and debug issues.

**Why this priority**: Constitution Principle III (NON-NEGOTIABLE). Required before any autonomous action execution. Enables compliance and debugging.

**Independent Test**: Can be tested by logging sample actions and querying the log files. No external dependencies.

**Acceptance Scenarios**:

1. **Given** any action is taken, **When** audit logger is called, **Then** JSON entry written with timestamp, action_type, actor, target, result
2. **Given** log files older than 90 days exist, **When** retention cleanup runs, **Then** old files deleted per retention policy
3. **Given** audit logs exist, **When** queried by date range and action_type, **Then** matching entries returned
4. **Given** concurrent log writes, **When** multiple threads write simultaneously, **Then** no data corruption (thread-safe)

---

### User Story 6 - End-to-End Pipeline Validation (Priority: P2)

As a user, I want to validate that the entire pipeline (Needs_Action -> Plan -> Approval -> Done) works correctly so I can trust the system before running it autonomously.

**Why this priority**: Quality assurance for the Gold tier. Validates all components work together before production use.

**Independent Test**: Can be tested by running test_pipeline.py which simulates the full workflow with test data.

**Acceptance Scenarios**:

1. **Given** test item placed in Needs_Action, **When** pipeline test runs, **Then** item processed through all stages to Done
2. **Given** sensitive test item, **When** pipeline processes it, **Then** approval request created in Pending_Approval
3. **Given** all stages complete, **When** test report generated, **Then** all stages show PASS with timestamps

---

### Edge Cases

- What happens when Odoo server is unreachable during invoice creation?
- How does the system handle partial social media post failures (e.g., Twitter succeeds but Facebook fails)?
- What if briefing generator runs with no data available?
- How does retry handler behave when max_attempts is reached?
- What if approval file is moved to both Approved/ and Rejected/ simultaneously?
- How does the system handle Odoo API rate limiting?
- What if log disk is full during audit write?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create invoices in Odoo via MCP server with customer, line items, and due date
- **FR-002**: System MUST fetch financial summaries from Odoo for configurable time periods
- **FR-003**: System MUST add/update customer records in Odoo res.partner model
- **FR-004**: System MUST list unpaid invoices with amounts and due dates
- **FR-005**: System MUST record expenses in Odoo hr.expense with categories
- **FR-006**: System MUST post content to Facebook, Instagram, and Twitter via platform adapters
- **FR-007**: System MUST read direct messages from social platforms
- **FR-008**: System MUST schedule posts for future publication
- **FR-009**: System MUST retrieve engagement analytics per platform
- **FR-010**: System MUST retry transient failures with exponential backoff (max 3 attempts, base 1s, max 60s)
- **FR-011**: System MUST distinguish transient errors (timeout, rate-limit) from permanent errors (auth, bad data)
- **FR-012**: System MUST track service health status (HEALTHY, DEGRADED, UNAVAILABLE)
- **FR-013**: System MUST queue actions locally when target service is unavailable
- **FR-014**: System MUST replay queued actions when service recovers
- **FR-015**: System MUST auto-restart crashed watcher processes via watchdog (max 5 restarts)
- **FR-016**: System MUST write structured JSON audit logs per Constitution Principle III schema
- **FR-017**: System MUST enforce 90-day log retention with automatic cleanup
- **FR-018**: System MUST support log queries by date range, action_type, and actor
- **FR-019**: System MUST generate daily CEO briefing aggregating all data sources
- **FR-020**: System MUST validate end-to-end pipeline from Needs_Action through Done
- **FR-021**: All financial actions (invoices, payments, expenses) MUST require human approval per Constitution Principle II
- **FR-022**: All social media posts MUST require human approval per Constitution Principle II

### Key Entities

- **Invoice**: Odoo account.move record with customer, line items, amount, status (draft/posted/paid)
- **Customer**: Odoo res.partner record with name, email, phone, company
- **Expense**: Odoo hr.expense record with category, amount, description
- **SocialPost**: Cross-platform content with text, media, platform targets, schedule
- **ServiceState**: Health tracker per external service (status, failure_count, queued_actions)
- **AuditEntry**: Structured log entry (timestamp, action_type, actor, target, result, approval_status)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Invoice creation via Odoo MCP completes in under 5 seconds
- **SC-002**: Financial summary fetch returns data in under 3 seconds
- **SC-003**: Social media post published to all 3 platforms in under 10 seconds
- **SC-004**: System recovers from transient failures within 3 retry attempts
- **SC-005**: Watchdog restarts crashed processes within 30 seconds
- **SC-006**: Audit logs written within 100ms of action completion
- **SC-007**: CEO briefing generated within 60 seconds
- **SC-008**: End-to-end pipeline test passes all 7 validation stages
- **SC-009**: Zero data loss during graceful degradation (all queued actions eventually processed)
- **SC-010**: All financial/social actions routed through approval workflow (100% HITL compliance)
