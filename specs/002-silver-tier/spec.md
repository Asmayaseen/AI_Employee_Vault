# Feature Specification: Silver Tier - Multi-Source Intelligence & Orchestration

**Feature Branch**: `002-silver-tier`
**Created**: 2026-02-08
**Status**: Implemented (Retroactive Spec)
**Tier**: Silver - Intelligence Layer
**Depends On**: Bronze Tier (001-bronze-tier)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Source Monitoring (Priority: P1)

As a user, I want the AI Employee to monitor multiple communication channels (Gmail, WhatsApp, LinkedIn) simultaneously so I can centralize all incoming work in one place.

**Why this priority**: Core value proposition of Silver tier - expanding from files to external communications. Without multi-source monitoring, AI Employee is limited to local files only.

**Independent Test**: Can be fully tested by setting up Gmail watcher and verifying emails create action items. Each watcher is independently testable and delivers value even if others aren't configured.

**Acceptance Scenarios**:

1. **Given** Gmail watcher is configured with OAuth credentials, **When** a new unread email arrives, **Then** action file created in Needs_Action/ within check interval
2. **Given** WhatsApp watcher is configured with session, **When** a message arrives, **Then** action file created with message content and sender info
3. **Given** LinkedIn watcher is configured with session, **When** a LinkedIn message arrives, **Then** action file created with lead detection keywords highlighted
4. **Given** multiple watchers running, **When** items arrive across sources simultaneously, **Then** all items detected without conflicts or data loss

---

### User Story 2 - Centralized Orchestration (Priority: P1)

As a user, I want a single orchestrator to manage all watchers so I don't have to manually start/stop/monitor each one individually.

**Why this priority**: Critical for operational simplicity. Managing 4+ separate processes manually is error-prone and time-consuming. Orchestrator enables "start once, forget" operation.

**Independent Test**: Can be tested by starting orchestrator and verifying all configured watchers launch successfully. Delivers immediate operational value.

**Acceptance Scenarios**:

1. **Given** orchestrator is started, **When** configured watchers list is provided, **Then** all enabled watchers start as subprocess
2. **Given** a watcher process crashes, **When** orchestrator health check detects failure, **Then** watcher automatically restarted (up to max_restarts limit)
3. **Given** orchestrator receives SIGTERM/Ctrl+C, **When** shutdown initiated, **Then** all watcher processes stopped gracefully with saved state
4. **Given** orchestrator is running, **When** health check runs, **Then** status report shows each watcher's uptime, restart count, and health

---

### User Story 3 - Human-in-the-Loop Approval (Priority: P1)

As a user, I want to review and approve high-stakes actions before execution so the AI Employee never takes autonomous actions I haven't authorized.

**Why this priority**: Safety-critical feature enforcing Constitution principle #2 (HITL). Without this, system could send emails, make posts, or take actions without oversight - unacceptable for production use.

**Independent Test**: Can be tested by placing approval request in Pending_Approval/ and verifying it's not executed until moved to Approved/. Delivers safety guarantee immediately.

**Acceptance Scenarios**:

1. **Given** Claude Processor generates plan requiring approval, **When** plan is created, **Then** file placed in Pending_Approval/ (not executed)
2. **Given** approval request in Pending_Approval/, **When** human moves file to Approved/, **Then** Approval Watcher detects and triggers appropriate action
3. **Given** approval request in Pending_Approval/, **When** timeout period (24h) expires, **Then** notification sent and item moved to Rejected/
4. **Given** approval is rejected, **When** file moved to Rejected/, **Then** logged to audit trail, no action executed

---

### User Story 4 - Intelligent Planning (Priority: P2)

As a user, I want the system to automatically generate reasoning plans for action items so I get AI analysis before deciding on actions.

**Why this priority**: Important but not blocking - manual planning still possible. Adds intelligence layer that makes action items more actionable with suggested plans.

**Independent Test**: Can be tested by placing action file in Needs_Action/ and running Claude Processor to verify Plan.md generated. Delivers value independently of other stories.

**Acceptance Scenarios**:

1. **Given** action file exists in Needs_Action/, **When** Claude Processor runs, **Then** Plan.md generated in Plans/ with analysis and suggested actions
2. **Given** Plan.md generated, **When** plan requires approval, **Then** file created in Pending_Approval/ with frontmatter specifying action type
3. **Given** Claude Processor runs, **When** API errors occur, **Then** errors logged, processing continues for other items
4. **Given** multiple action items pending, **When** --process-all flag used, **Then** all items processed in sequence with plans generated

---

### User Story 5 - Scheduled Automation (Priority: P2)

As a user, I want recurring tasks (daily briefings, weekly reports) to run automatically on schedule so I don't have to remember to trigger them manually.

**Why this priority**: Quality-of-life improvement - adds automation but system works without it. Enables "set and forget" for periodic tasks.

**Independent Test**: Can be tested by setting up cron job or Windows Task Scheduler and verifying briefing generates at scheduled time. Delivers automation value independently.

**Acceptance Scenarios**:

1. **Given** scheduler is configured with cron schedule, **When** scheduled time arrives, **Then** specified task executes (e.g., daily briefing)
2. **Given** briefing task runs, **When** execution completes, **Then** Briefing/[date].md created with stats and summary
3. **Given** scheduler runs on Windows, **When** Task Scheduler invokes script, **Then** works cross-platform without modification
4. **Given** scheduled task fails, **When** error occurs, **Then** error logged, next scheduled run still happens

---

### Edge Cases

- What happens when two watchers detect the same content (e.g., email notification in Gmail and LinkedIn)?
- How does system handle rate limits from external APIs (Gmail API, LinkedIn scraping)?
- What if orchestrator crashes - do watcher processes continue or orphan?
- How does approval timeout work if system is offline for >24 hours?
- What happens during concurrent approval/rejection of same item?
- How does system handle very large emails or messages (>1MB)?
- What if Claude Processor fails mid-processing with partial Plan.md written?

---

## Requirements *(mandatory)*

### Functional Requirements

**Multi-Source Monitoring**:
- **FR-001**: System MUST support Gmail watcher using OAuth 2.0 API authentication
- **FR-002**: System MUST support WhatsApp watcher using Playwright browser automation
- **FR-003**: System MUST support LinkedIn watcher using Playwright browser automation
- **FR-004**: Each watcher MUST inherit from BaseWatcher and implement check_for_updates(), create_action_file()
- **FR-005**: Each watcher MUST log activities to daily JSON files (Logs/[date].json)
- **FR-006**: Watchers MUST deduplicate items using .processed_[source] tracking files

**Orchestration**:
- **FR-007**: System MUST provide Orchestrator class managing multiple watcher processes
- **FR-008**: Orchestrator MUST start enabled watchers as subprocesses with configurable check intervals
- **FR-009**: Orchestrator MUST perform health checks every 60 seconds detecting crashed watchers
- **FR-010**: Orchestrator MUST auto-restart crashed watchers up to max_restarts limit (default: 5)
- **FR-011**: Orchestrator MUST handle graceful shutdown (SIGTERM/Ctrl+C) stopping all watchers cleanly
- **FR-012**: Orchestrator MUST log process lifecycle events (start, stop, restart, crash)

**Approval Workflow**:
- **FR-013**: System MUST provide ApprovalWatcher monitoring Pending_Approval/, Approved/, Rejected/ folders
- **FR-014**: ApprovalWatcher MUST check for approved items every 5 seconds (fast response)
- **FR-015**: ApprovalWatcher MUST execute approved actions via action_handlers mapping
- **FR-016**: ApprovalWatcher MUST implement timeout mechanism (default: 24 hours) for stale approvals
- **FR-017**: ApprovalWatcher MUST send desktop notifications for new approval requests (if plyer available)
- **FR-018**: ApprovalWatcher MUST log all approval decisions to audit trail

**Intelligent Planning**:
- **FR-019**: System MUST provide Claude Processor script for AI-powered plan generation
- **FR-020**: Claude Processor MUST read action files from Needs_Action/ and generate Plan.md files
- **FR-021**: Claude Processor MUST use Claude API (via MCP or direct) for reasoning
- **FR-022**: Claude Processor MUST support --process-all flag for batch processing
- **FR-023**: Claude Processor MUST support --briefing flag for daily CEO briefing generation
- **FR-024**: Generated plans MUST use frontmatter to specify action_type for approval routing

**Scheduling**:
- **FR-025**: System MUST provide Scheduler script for recurring task automation
- **FR-026**: Scheduler MUST support cron schedule syntax (Linux/macOS)
- **FR-027**: Scheduler MUST support Windows Task Scheduler XML configuration
- **FR-028**: Scheduler MUST execute specified command at scheduled times
- **FR-029**: Scheduler MUST log execution results (success/failure, timestamp)

### Non-Functional Requirements

**Performance**:
- **NFR-001**: Each watcher must check interval between 5-300 seconds (configurable)
- **NFR-002**: Orchestrator health checks must complete in <5 seconds
- **NFR-003**: Approval Watcher response time <10 seconds after file moved to Approved/
- **NFR-004**: Claude Processor must handle API rate limits gracefully (exponential backoff)
- **NFR-005**: Total memory footprint for all watchers <500MB

**Reliability**:
- **NFR-006**: System must survive individual watcher crashes without affecting others
- **NFR-007**: Orchestrator must auto-restart failed watchers within 30 seconds
- **NFR-008**: All state (tracking files, logs) must persist across restarts
- **NFR-009**: System must handle network outages gracefully (retry, queue)

**Security**:
- **NFR-010**: OAuth credentials must be stored securely, never logged
- **NFR-011**: Browser session data (.session folders) must be excluded from git
- **NFR-012**: Approval workflow must be tamper-resistant (no auto-approval)
- **NFR-013**: All actions must be auditable via log files

**Usability**:
- **NFR-014**: Orchestrator must start all watchers with single command
- **NFR-015**: Health status must be viewable via Dashboard.md updates
- **NFR-016**: Setup process must be documented with SILVER_TIER_SETUP_GUIDE.md

### Key Entities

**Watcher Process**:
- name: Human-readable name (e.g., "Gmail Watcher")
- script: Python file to execute
- process: subprocess.Popen object
- start_time: When watcher started
- restart_count: Number of restarts
- is_healthy: Current health status
- check_interval: Seconds between checks

**Action Item**:
- source: Where item came from (gmail, whatsapp, linkedin, file)
- type: email, message, connection_request, file_drop
- priority: normal, high, urgent
- status: pending, processing, approved, rejected, done
- created: Timestamp
- action_file: Path to markdown file

**Approval Request**:
- action_type: email_send, payment, social_post, general
- requested_at: Timestamp
- approved_by: Human identifier (optional)
- approved_at: Timestamp (optional)
- timeout_at: Expiry timestamp
- action_data: JSON with action-specific details

**Plan**:
- source_action: Reference to original action item
- analysis: AI reasoning about the situation
- suggested_actions: List of recommended steps
- requires_approval: Boolean flag
- confidence: AI confidence score (optional)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Multi-Source Monitoring**:
- **SC-001**: Gmail watcher detects 95%+ of unread emails within check interval (120s)
- **SC-002**: WhatsApp watcher detects messages within 30 seconds
- **SC-003**: LinkedIn watcher detects new messages within 60 seconds
- **SC-004**: Zero duplicate action files created across all sources

**Orchestration**:
- **SC-005**: Orchestrator starts all enabled watchers in <10 seconds
- **SC-006**: Crashed watchers auto-restart within 30 seconds
- **SC-007**: Orchestrator uptime >99% over 7-day period
- **SC-008**: Graceful shutdown completes in <15 seconds with all state saved

**Approval Workflow**:
- **SC-009**: Approved actions execute within 10 seconds of approval
- **SC-010**: Zero unauthorized actions (100% HITL compliance)
- **SC-011**: Timeout mechanism triggers correctly after 24 hours
- **SC-012**: Desktop notifications delivered within 5 seconds (when enabled)

**Intelligent Planning**:
- **SC-013**: Claude Processor generates plans for 90%+ of action items
- **SC-014**: Plan generation completes in <30 seconds per item
- **SC-015**: API errors handled gracefully without data loss

**Scheduling**:
- **SC-016**: Daily briefing generates at scheduled time ±2 minutes
- **SC-017**: Scheduler works cross-platform (Linux, macOS, Windows)

---

## Technical Context

### Technology Stack
- **Language**: Python 3.10+
- **Core Libraries**:
  - `subprocess` - Process management for orchestrator
  - `signal` - Graceful shutdown handling
  - `threading` - Concurrent health checks
  - `google-auth`, `google-api-python-client` - Gmail API
  - `playwright` - WhatsApp/LinkedIn browser automation
  - `plyer` - Desktop notifications (optional)
  - `anthropic` - Claude API for planning (via MCP or SDK)
- **External APIs**:
  - Gmail API (OAuth 2.0)
  - Claude API (for plan generation)
  - LinkedIn (browser automation, no official API)
  - WhatsApp Web (browser automation)

### Platform Support
- Linux/Ubuntu (primary development)
- macOS 10.15+ (tested)
- Windows 10/11 via WSL (Gmail working, browser automation partial)
- Windows native (browser automation preferred)

### Architecture Pattern
```
Orchestrator (master process)
├── FileSystem Watcher (subprocess)
├── Gmail Watcher (subprocess)
├── WhatsApp Watcher (subprocess)
├── LinkedIn Watcher (subprocess)
└── Approval Watcher (subprocess)

All watchers inherit from BaseWatcher (Bronze Tier)
All watchers write to Needs_Action/ → Claude Processor reads
Plans requiring approval go to Pending_Approval/ → ApprovalWatcher monitors
```

### Integration Points
- **Obsidian Vault**: All watchers read/write to vault folders
- **Gmail API**: OAuth 2.0 authentication, Gmail API v1
- **Browser Automation**: Playwright with persistent contexts
- **Claude API**: Plan generation via MCP server or direct SDK
- **File System**: Folder-based workflow (Inbox → Needs_Action → Pending_Approval → Approved → Done)

---

## Assumptions

### Documented Assumptions
1. **Gmail Credentials Available**: User has Google Cloud project with Gmail API enabled and OAuth credentials downloaded
2. **Browser Sessions Persistent**: WhatsApp and LinkedIn sessions persist in .session folders across restarts
3. **Claude API Access**: User has Anthropic API key or Claude Code MCP server configured
4. **Network Connectivity**: Stable internet connection for API calls and web scraping
5. **Single User**: System designed for single-user operation (no multi-tenant support)
6. **English Language**: Primary language for email/message processing
7. **Moderate Volume**: Designed for <1000 items/day per source

### Technical Assumptions
8. **Python 3.10+**: Modern Python with async/await support
9. **Disk Space**: 1GB+ available for logs and browser sessions
10. **Process Permissions**: Ability to spawn subprocesses and bind ports
11. **GUI Available**: For browser automation (headless mode limited)

---

## Risks & Constraints

### Technical Risks
- **Browser Automation Fragility**: LinkedIn/WhatsApp may change UI, breaking selectors
- **API Rate Limits**: Gmail API quota (1B/day), Claude API rate limits
- **Session Expiry**: Browser sessions may expire requiring re-login
- **Memory Leaks**: Long-running processes may accumulate memory over days
- **Concurrent Access**: Multiple processes writing to vault simultaneously

### Mitigation Strategies
- Use flexible CSS selectors with fallbacks for browser automation
- Implement exponential backoff and queue for API calls
- Monitor session health, provide re-authentication flow
- Restart watchers daily via scheduler to prevent leaks
- Use file locking or timestamp-based conflict resolution

### Constraints
- Gmail API quota: 1 billion requests/day (plenty for personal use)
- WhatsApp Web: No official API, must use browser automation
- LinkedIn: No official messaging API, must scrape
- Claude API: Rate limits and cost per request
- Obsidian Vault: Must not corrupt vault with invalid markdown

---

## Out of Scope

### Explicitly Excluded from Silver Tier
- **Autonomous Execution**: No auto-approval (wait for Gold tier "Ralph Wiggum loop")
- **Multi-User Support**: Single user only (no collaboration features)
- **Mobile App**: Desktop/server only (no iOS/Android)
- **Database**: Using file system and JSON logs (no SQL/NoSQL)
- **Advanced NLP**: Basic keyword matching only (no sentiment analysis)
- **Real-time WebSockets**: Polling-based (no push notifications)
- **Advanced Scheduling**: Basic cron/Task Scheduler only (no complex DAGs)
- **Content Moderation**: No filtering of inappropriate content
- **Encryption**: Relies on OS-level encryption (no application-level crypto)

### Future Enhancements (Gold/Platinum Tiers)
- **Gold Tier**: Odoo integration, Facebook/Instagram/Twitter, weekly CEO briefing
- **Platinum Tier**: Full autonomous loop with confidence thresholds
- **Diamond Tier**: Multi-user collaboration, advanced NLP, predictive analytics

---

## Implementation Notes

### Files Structure
```
AI_Employee_Vault/
├── Watchers/
│   ├── orchestrator.py              # C1: Master coordinator
│   ├── approval_watcher.py          # C2: HITL workflow
│   ├── claude_processor.py          # C3: AI planning
│   ├── scheduler.py                 # C4: Recurring tasks
│   ├── gmail_watcher.py             # C5: Email monitoring
│   ├── whatsapp_watcher.py          # C6: WhatsApp monitoring
│   ├── linkedin_watcher.py          # C7: LinkedIn monitoring
│   ├── base_watcher.py              # Bronze tier foundation
│   ├── filesystem_watcher.py        # Bronze tier file monitoring
│   ├── requirements.txt             # Dependencies
│   └── .env                         # Configuration
│
├── Needs_Action/                    # Action items from all sources
├── Pending_Approval/                # Items awaiting human review
├── Approved/                        # Human-approved actions
├── Rejected/                        # Rejected actions
├── Done/                            # Completed actions
├── Plans/                           # AI-generated plans
├── Briefings/                       # Daily/weekly reports
├── Logs/                            # Activity logs (JSON)
├── Dashboard.md                     # System status
└── .processed_*                     # Deduplication tracking
```

### Configuration (.env)
```bash
# Vault
VAULT_PATH=/path/to/AI_Employee_Vault

# Watchers
CHECK_INTERVAL=60
DRY_RUN=true

# Gmail
GMAIL_CREDENTIALS_PATH=credentials.json

# Approval
APPROVAL_TIMEOUT_HOURS=24

# Claude API
ANTHROPIC_API_KEY=sk-...
```

---

## Definition of Done

### Silver Tier Complete When:
- [x] Orchestrator manages 4+ watchers
- [x] Gmail watcher working with OAuth
- [x] WhatsApp watcher implemented (needs QR setup)
- [x] LinkedIn watcher implemented (needs login setup)
- [x] Approval workflow functional (Pending → Approved → Done)
- [x] Claude Processor generates plans
- [x] Scheduler supports cron and Windows Task Scheduler
- [x] All components tested (8/8 tests passed per Dashboard)
- [x] Documentation complete (SILVER_TIER_SETUP_GUIDE.md)
- [ ] Spec/Plan/Tasks retroactively documented
- [ ] PHRs created for audit trail

---

**Status**: ✅ Implemented, ⏳ Documentation Pending
**Implementation Date**: 2026-02-05 to 2026-02-07
**Next Step**: Create implementation plan and tasks
**Next Tier**: Gold (Odoo, social media, CEO briefing)

