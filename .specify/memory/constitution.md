<!--
Sync Impact Report:
- Version Change: [NEW] → 1.0.0
- New Constitution: Personal AI Employee system principles established
- Modified Principles: N/A (initial version)
- Added Sections: Core Principles (9), Security Architecture, Error Handling & Recovery, Development Tiers, Governance
- Removed Sections: N/A
- Templates Status:
  ✅ plan-template.md - Constitution Check section applies
  ✅ spec-template.md - User scenarios align with tier deliverables
  ✅ tasks-template.md - Task organization supports phased tier implementation
- Follow-up TODOs: None
- Rationale: MINOR version (1.0.0) - Initial constitution establishing foundational principles for autonomous AI Employee system
-->

# Personal AI Employee Constitution

## Core Principles

### I. Local-First Architecture (NON-NEGOTIABLE)

**Privacy and Data Sovereignty MUST be paramount:**

- All sensitive data (credentials, personal communications, financial records) MUST be stored locally on user's machine
- Obsidian vault as the single source of truth for state, memory, and audit trails
- API calls to external services (Claude, Gmail, WhatsApp) MUST be minimized and logged
- Secrets MUST NEVER be committed to version control or stored in plain text
- User retains full ownership and control of all data

**Rationale:** Users entrust this system with banking, personal communications, and business operations. Local-first architecture ensures privacy, enables offline operation, and eliminates vendor lock-in.

### II. Human-in-the-Loop for Sensitive Actions (NON-NEGOTIABLE)

**The AI Employee MUST NOT take irreversible actions without explicit human approval:**

- All payments, financial transactions, and banking operations require approval
- Emails to new contacts or bulk sends require approval
- Social media posts and direct messages require approval
- File deletions outside the vault require approval
- Any action involving >$50 or new recipients requires approval

**Implementation Pattern:**
- AI creates approval request file in `/Pending_Approval/`
- Human reviews and moves to `/Approved/` or `/Rejected/`
- Orchestrator executes only approved actions
- All approvals and rejections are logged with timestamps

**Rationale:** Autonomous systems will make mistakes. HITL safeguards prevent financial loss, reputational damage, and irreversible errors while maintaining system utility.

### III. Comprehensive Audit Logging (NON-NEGOTIABLE)

**Every action the AI takes MUST be logged and traceable:**

- JSON-formatted logs stored in `/Vault/Logs/YYYY-MM-DD.json`
- Minimum retention: 90 days
- Required fields: timestamp, action_type, actor, target, parameters, approval_status, approved_by, result
- Logs MUST be human-readable and machine-parseable
- Failed actions and errors MUST be logged with full context

**Log Entry Schema:**
```json
{
  "timestamp": "ISO-8601",
  "action_type": "email_send|payment|post|file_operation",
  "actor": "claude_code|watcher|orchestrator",
  "target": "recipient_identifier",
  "parameters": {},
  "approval_status": "approved|rejected|auto_approved",
  "approved_by": "human|system_rule",
  "result": "success|failure|pending",
  "error_detail": "optional"
}
```

**Rationale:** Audit trails enable debugging, compliance, security incident response, and user oversight of autonomous operations.

### IV. Agent Skills as Implementation Standard

**All AI functionality MUST be implemented as Agent Skills:**

- Every tier deliverable MUST have corresponding skills (e.g., `/gmail-watcher`, `/whatsapp-monitor`, `/ceo-briefing`)
- Skills MUST be modular, independently testable, and well-documented
- Skills MUST follow Claude Code Agent Skills specification
- Skills MUST include clear success criteria and error handling
- Skills MUST be versioned and tracked in `/skills/` directory

**Rationale:** Agent Skills provide structure, reusability, testability, and maintainability. They transform ad-hoc prompts into production-grade capabilities.

### V. Graceful Degradation and Error Recovery

**System MUST continue operating when components fail:**

- **Gmail API down:** Queue outgoing emails locally, process when restored
- **Banking API timeout:** Never retry payments automatically, require fresh approval
- **Claude Code unavailable:** Watchers continue collecting, queue grows for later processing
- **Obsidian vault locked:** Write to temporary folder, sync when available
- **MCP server failure:** Log error, alert human, continue non-dependent operations

**Retry Logic:**
- Transient errors (network timeout, rate limit): Exponential backoff retry (max 3 attempts)
- Authentication errors (expired token): Alert human, pause operations
- Logic errors (AI misinterpretation): Human review queue
- Data errors (corrupted file): Quarantine + alert
- System errors (crash): Watchdog auto-restart

**Rationale:** Autonomous systems operate 24/7 across unreliable networks and services. Graceful degradation maintains utility during partial failures.

### VI. Security Boundaries and Credential Management

**Credentials and secrets MUST be protected using defense-in-depth:**

- Use environment variables for API keys (never hardcode)
- Use OS-native secrets managers (macOS Keychain, Windows Credential Manager, 1Password CLI)
- `.env` files MUST be in `.gitignore` immediately upon creation
- Rotate credentials monthly and after any suspected breach
- Development mode MUST use separate test/sandbox accounts
- All action scripts MUST support `--dry-run` flag during development

**Sandboxing Requirements:**
- `DRY_RUN` environment variable defaults to `true` during development
- Rate limiting: Maximum 10 emails/hour, 3 payments/day during development
- Separate test accounts for Gmail, banking, social media during development
- Production credentials stored separately from development credentials

**Rationale:** This system handles banking, email, and personal communications. A security breach could be catastrophic. Defense-in-depth minimizes attack surface.

### VII. Tier-Based Progressive Enhancement

**System MUST be built incrementally across defined tiers:**

- **Bronze (Foundation):** Obsidian vault + 1 watcher + Claude Code integration + Agent Skills
- **Silver (Functional):** Multiple watchers + MCP servers + HITL workflow + scheduling + Agent Skills
- **Gold (Autonomous):** Full cross-domain integration + Ralph Wiggum loop + CEO briefing + Odoo integration + Agent Skills
- **Platinum (Production):** 24/7 cloud deployment + work-zone specialization + vault sync + health monitoring + Agent Skills

**Tier Gates:**
- Cannot proceed to next tier until current tier fully functional and documented
- Each tier MUST include demo video and documentation
- Each tier MUST pass security review (credential handling, HITL verification)
- Each tier MUST implement all functionality as Agent Skills

**Rationale:** Incremental development reduces risk, enables early feedback, and provides natural stopping points for different user needs and skill levels.

### VIII. Watcher Pattern for Continuous Perception

**External event monitoring MUST follow the Watcher pattern:**

- Lightweight Python scripts run continuously (not Claude Code)
- Base class: `BaseWatcher` with `check_for_updates()` and `create_action_file()` methods
- Watchers create `.md` files in `/Needs_Action/` with structured frontmatter
- Watchers MUST be managed by process supervisor (PM2, supervisord, or systemd)
- Watchers MUST log health checks and errors
- Watchdog process monitors and auto-restarts failed watchers

**Required Watchers by Tier:**
- Bronze: 1 watcher (Gmail OR filesystem)
- Silver: 2+ watchers (Gmail + WhatsApp/LinkedIn)
- Gold: 3+ watchers (Gmail + WhatsApp + Banking + Social)
- Platinum: All watchers + health monitoring

**Rationale:** Claude Code cannot continuously monitor external systems. Watchers decouple perception from reasoning, enabling 24/7 autonomous operation.

### IX. Obsidian Vault as State Machine

**The Obsidian vault structure defines system state and workflow:**

**Required Folders:**
- `/Needs_Action/` - New items detected by watchers (AI reads from here)
- `/Plans/` - Claude-generated plans with task checklists
- `/Pending_Approval/` - Actions requiring human approval
- `/Approved/` - Human-approved actions ready for execution
- `/Rejected/` - Human-rejected actions (for learning)
- `/Done/` - Completed tasks (archival + audit)
- `/Logs/` - JSON audit logs organized by date
- `/Briefings/` - CEO briefings and reports
- `/Accounting/` - Financial transactions and records

**Required Files:**
- `Dashboard.md` - Real-time status (bank balance, pending messages, active projects)
- `Company_Handbook.md` - Rules of engagement and AI behavior guidelines
- `Business_Goals.md` - Quarterly objectives, KPIs, and success metrics

**File Movement Protocol:**
- Watchers write to `/Needs_Action/`
- Claude reads `/Needs_Action/`, creates plans in `/Plans/`, writes approval requests to `/Pending_Approval/`
- Human moves files from `/Pending_Approval/` to `/Approved/` or `/Rejected/`
- Orchestrator detects approved files, executes via MCP, logs result, moves to `/Done/`

**Rationale:** File-based state machine is simple, debuggable, auditable, and survives process crashes. Human can inspect and intervene at any stage.

## Security Architecture

### Credential Storage Matrix

| Credential Type | Storage Method | Access Pattern | Rotation Policy |
|-----------------|---------------|----------------|-----------------|
| Gmail API keys | `.env` + OS keychain | Load on watcher start | Monthly |
| Banking tokens | OS keychain only | Load per-request | Weekly |
| WhatsApp session | Encrypted file outside vault | Mount on local agent only | Per-session |
| Claude API key | `.env` + environment variable | Load on orchestrator start | Monthly |
| Social media tokens | OS keychain only | Load per-request | Monthly |

### Permission Boundaries

| Action Category | Auto-Approve Threshold | Always Require Approval |
|-----------------|------------------------|-------------------------|
| Email replies | Known contacts only | New contacts, bulk sends |
| Payments | <$50 recurring bills | All new payees, >$100 |
| Social media | Scheduled posts (drafts) | Replies, DMs, live posts |
| File operations | Create, read within vault | Delete, move outside vault |

### Vault Sync Security (Platinum Tier)

**Claim-by-Move Rule:**
- First agent to move item from `/Needs_Action/` to `/In_Progress/<agent>/` owns it
- Other agents MUST ignore items in `/In_Progress/`

**Secrets Never Sync:**
- `.env` files excluded from sync
- WhatsApp sessions excluded (Local agent only)
- Banking credentials excluded (Local agent only)
- Payment tokens excluded (Local agent only)

**Cloud Agent Restrictions:**
- Can draft emails, social posts, reports (write-only to `/Pending_Approval/`)
- Cannot execute sends, posts, payments (requires Local approval)
- Cannot access WhatsApp, banking, payment systems

## Error Handling & Recovery

### Error Categories and Responses

| Error Category | Examples | Recovery Strategy | Alert Human? |
|----------------|----------|-------------------|--------------|
| Transient | Network timeout, rate limit | Exponential backoff retry (max 3) | After 3 failures |
| Authentication | Expired token, revoked access | Pause operations, alert immediately | Yes (immediate) |
| Logic | AI misinterprets message | Queue for human review | Yes (daily digest) |
| Data | Corrupted file, missing field | Quarantine file, alert | Yes (immediate) |
| System | Orchestrator crash, disk full | Watchdog restart, alert | Yes (immediate) |

### Health Monitoring Requirements

**Watchdog Process MUST monitor:**
- Watcher process PIDs (restart if dead)
- Orchestrator process PID (restart if dead)
- MCP server process PIDs (restart if dead)
- Disk space (alert if <1GB free)
- Memory usage (alert if >80%)
- API rate limits (alert if >80% consumed)
- Log file sizes (rotate if >100MB)

**Health Check Frequency:**
- Process checks: Every 60 seconds
- Resource checks: Every 5 minutes
- API quota checks: Every 15 minutes

## Development Tiers

### Bronze Tier: Foundation (8-12 hours)

**Deliverables:**
- Obsidian vault with folder structure
- `Dashboard.md`, `Company_Handbook.md`, `Business_Goals.md`
- One working watcher (Gmail OR filesystem)
- Claude Code reads/writes vault successfully
- All functionality as Agent Skills
- Documentation and demo video

**Skills Required:**
- `/bronze-vault-setup` - Initialize vault structure
- `/bronze-watcher` - Single watcher implementation
- `/bronze-claude-integration` - Claude Code vault integration

### Silver Tier: Functional Assistant (20-30 hours)

**Deliverables:**
- All Bronze requirements
- 2+ watchers (Gmail + WhatsApp/LinkedIn)
- Claude reasoning loop creating `Plan.md` files
- One working MCP server (email send)
- HITL approval workflow functional
- Basic scheduling (cron/Task Scheduler)
- All functionality as Agent Skills
- Documentation and demo video

**Skills Required:**
- `/silver-multi-watcher` - Multiple watcher orchestration
- `/silver-mcp-email` - Email MCP server
- `/silver-hitl-workflow` - Human approval workflow
- `/silver-scheduler` - Cron/Task Scheduler setup

### Gold Tier: Autonomous Employee (40+ hours)

**Deliverables:**
- All Silver requirements
- Full cross-domain integration (Personal + Business)
- Odoo Community integration (self-hosted, Odoo 19+, JSON-RPC APIs)
- Facebook, Instagram, Twitter (X) integration
- Multiple MCP servers for different actions
- Weekly Business Audit with CEO Briefing generation
- Error recovery and graceful degradation
- Comprehensive audit logging
- Ralph Wiggum loop for autonomous multi-step tasks
- All functionality as Agent Skills
- Full documentation and demo video

**Skills Required:**
- `/gold-odoo-integration` - Odoo MCP server
- `/gold-social-media` - Social media MCP servers
- `/gold-ceo-briefing` - Weekly audit and briefing generation
- `/gold-ralph-wiggum` - Autonomous task loop
- `/gold-error-recovery` - Comprehensive error handling

### Platinum Tier: Always-On Production (60+ hours)

**Deliverables:**
- All Gold requirements
- 24/7 cloud deployment (Oracle/AWS/etc.)
- Work-zone specialization (Cloud: drafts, Local: approvals/sends)
- Vault sync via Git or Syncthing
- Claim-by-move protocol for delegation
- Cloud Odoo deployment with HTTPS and backups
- Health monitoring and auto-restart
- Security hardening (secrets never sync)
- All functionality as Agent Skills
- Production documentation and demo video

**Skills Required:**
- `/platinum-cloud-deploy` - Cloud VM setup and deployment
- `/platinum-vault-sync` - Git/Syncthing synchronization
- `/platinum-work-zones` - Cloud/Local delegation protocol
- `/platinum-health-monitor` - 24/7 monitoring system
- `/platinum-odoo-cloud` - Cloud Odoo deployment

## Development Workflow

### Before Starting Any Tier

1. **Prerequisites Check:** Verify all required software installed (Claude Code, Obsidian, Python 3.13+, Node.js 24+, Git)
2. **Security Setup:** Configure `.env` file, add to `.gitignore`, test credential isolation
3. **Vault Initialization:** Create Obsidian vault, initialize folder structure, create required files
4. **Skill Planning:** Identify which Agent Skills need to be created for the tier

### Tier Development Cycle

1. **Skill Creation:** Implement required Agent Skills for the tier
2. **Component Build:** Implement watchers, MCP servers, orchestrator components
3. **Integration Test:** Test end-to-end workflow with dry-run enabled
4. **Security Review:** Verify credential handling, HITL workflow, audit logging
5. **Production Test:** Test with real credentials in controlled environment
6. **Documentation:** Write setup instructions, architecture overview, lessons learned
7. **Demo Video:** Record 5-10 minute demo showing key features
8. **Tier Gate Review:** Verify all deliverables complete before proceeding to next tier

### Code Standards

- **Clarity over cleverness:** Prefer readable code to clever one-liners
- **Error messages MUST be actionable:** Include what failed and how to fix it
- **No silent failures:** Log all errors, alert on critical failures
- **Dry-run MUST be default:** Production execution requires explicit opt-in
- **Type hints required:** All Python functions MUST have type annotations
- **Docstrings required:** All public functions/classes MUST have docstrings

## Governance

### Constitution Authority

This constitution supersedes all other development practices, coding standards, and architectural decisions. When in conflict, constitution principles take precedence.

### Amendment Process

1. **Proposal:** Document proposed change with rationale and impact analysis
2. **Review:** Assess impact on existing tiers, skills, and components
3. **Migration Plan:** Document required changes to existing code/skills
4. **Approval:** Required for MAJOR version changes
5. **Implementation:** Update constitution, increment version, update dependent templates

### Version Semantics

- **MAJOR (X.0.0):** Backward-incompatible principle changes, principle removals
- **MINOR (0.X.0):** New principles added, existing principles materially expanded
- **PATCH (0.0.X):** Clarifications, wording improvements, typo fixes

### Compliance Verification

- All code reviews MUST verify compliance with applicable principles
- Each tier gate MUST include constitution compliance check
- Security reviews MUST verify principles II (HITL), III (Audit Logging), and VI (Security)
- Complexity MUST be justified against principle VII (Progressive Enhancement)

### Runtime Guidance

For day-to-day development decisions not explicitly covered by this constitution:
- Refer to `CLAUDE.md` for agent-specific execution guidance
- Refer to tier-specific skill documentation for implementation patterns
- Refer to template files in `.specify/templates/` for structural guidance
- When in doubt, bias toward simplicity, security, and user control

---

**Version**: 1.0.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-05
