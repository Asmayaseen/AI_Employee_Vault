# Architecture Overview - Personal AI Employee (Gold Tier)

## System Design

The Personal AI Employee follows a four-layer architecture:
**Perception -> Reasoning -> Action -> Audit**, with Human-in-the-Loop
gates at every sensitive action boundary.

```
+===========================================================================+
|                        EXTERNAL WORLD                                      |
|  Gmail   WhatsApp   LinkedIn   Facebook   Instagram   Twitter   Odoo ERP  |
+====+========+=========+==========+===========+=========+=========+=======+
     |        |         |          |           |         |         |
     v        v         v          v           v         v         v
+===========================================================================+
|                    LAYER 1: PERCEPTION (Watchers)                          |
|                                                                            |
|  gmail_watcher.py      Polls Gmail API every 120s for unread/important    |
|  whatsapp_watcher.py   Playwright browser automation, keyword triggers    |
|  linkedin_watcher.py   Playwright monitoring, messages + notifications    |
|  filesystem_watcher.py Watchdog observer on /Inbox folder                 |
|  approval_watcher.py   Monitors /Approved for HITL-approved actions       |
|                                                                            |
|  Pattern: Each watcher creates .md files in /Needs_Action/                |
+====================================+======================================+
                                     |
                                     v
+===========================================================================+
|                    LAYER 2: MEMORY (Obsidian Vault)                        |
|                                                                            |
|  /Needs_Action/       Incoming tasks from all watchers                    |
|  /Plans/              Claude-generated action plans                       |
|  /Pending_Approval/   HITL approval queue                                 |
|  /Approved/           Human-approved actions                              |
|  /Done/               Completed tasks (full audit trail)                  |
|  /Briefings/          CEO weekly briefing reports                         |
|  /Logs/               Structured JSON audit logs                          |
|  /Accounting/         Financial records                                    |
|  /Queued_Actions/     Degradation queue (service offline)                 |
|                                                                            |
|  Dashboard.md         Real-time system status                             |
|  Company_Handbook.md  Rules of engagement (autonomy boundaries)           |
|  Business_Goals.md    Revenue targets, project tracking                   |
+====================================+======================================+
                                     |
                                     v
+===========================================================================+
|                    LAYER 3: REASONING (Claude Code)                        |
|                                                                            |
|  claude_processor.py   Reads /Needs_Action, generates /Plans              |
|                        Identifies required actions and approvals           |
|                        References Company_Handbook.md for rules            |
|                                                                            |
|  Ralph Wiggum Loop     Stop hook (.claude/hooks/stop.py)                  |
|                        Keeps Claude iterating until task complete          |
|                        Max 10 iterations, file_movement strategy           |
|                        Controller: ralph_controller.py                     |
|                                                                            |
|  ceo_briefing_generator.py                                                |
|                        Weekly analysis: tasks + goals + Odoo accounting   |
|                        Generates proactive suggestions                     |
+====================================+======================================+
                                     |
                                     v
+===========================================================================+
|                    LAYER 4: ACTION (MCP Servers)                           |
|                                                                            |
|  email-mcp (Node.js)       5 tools                                        |
|    send_email, draft_email, search_emails, get_email, list_labels         |
|                                                                            |
|  odoo-mcp (Python)         7 tools     [JSON-RPC protocol]               |
|    create_invoice, get_unpaid_invoices, post_invoice,                     |
|    create_customer, get_financial_summary,                                 |
|    record_expense, get_subscription_audit                                  |
|                                                                            |
|  social-mcp (Python)       10 tools                                       |
|    fb_post_message, fb_fetch_recent_posts, fb_generate_summary,           |
|    ig_post_image_caption, ig_fetch_recent_posts, ig_engagement_summary,   |
|    tw_post_tweet, tw_fetch_mentions, tw_generate_weekly_summary,          |
|    generate_all_summaries                                                  |
|                                                                            |
|  Total: 22 MCP tools across 3 servers                                     |
+===========================================================================+

                                     |
                                     v
+===========================================================================+
|                    CROSS-CUTTING: SAFETY + RELIABILITY                     |
|                                                                            |
|  HUMAN-IN-THE-LOOP                                                         |
|    Approval files in /Pending_Approval/                                   |
|    Human moves to /Approved or /Rejected in Obsidian                      |
|    Thresholds: $500 invoices, all payments, all social posts              |
|                                                                            |
|  ERROR RECOVERY                                                            |
|    retry_handler.py       Exponential backoff (1s -> 2s -> 4s -> ...)     |
|    watchdog.py            Process health monitor, auto-restart            |
|    graceful_degradation.py Service health tracking, action queuing        |
|                            NEVER queues payments (safety rule)            |
|                                                                            |
|  AUDIT LOGGING                                                             |
|    audit_logger.py        JSON structured logs per Section 6.3            |
|                            /Logs/YYYY-MM-DD.json                           |
|                            90-day retention policy                         |
|                            Fields: timestamp, action_type, actor,          |
|                            domain, target, approval_status, result         |
|                                                                            |
|  ORCHESTRATION                                                             |
|    orchestrator.py        Master process: starts/stops all watchers       |
|    scheduler.py           Cross-platform cron/Task Scheduler setup        |
|    setup_cron.sh          Daily briefings, 2h processing, health checks   |
+===========================================================================+
```

## Data Flow: Invoice Request (End-to-End)

```
1. Client sends email: "Please send January invoice"
              |
2. gmail_watcher.py detects unread email
              |
3. Creates: /Needs_Action/EMAIL_client_invoice.md
              |
4. claude_processor.py reads the file
              |
5. Creates: /Plans/PLAN_invoice_client.md
   (Steps: find customer, calculate total, create invoice, get approval)
              |
6. Total $2,250 > $500 threshold
              |
7. Creates: /Pending_Approval/INVOICE_ACME_2250.md
              |
8. Human reviews in Obsidian, moves to /Approved/
              |
9. approval_watcher.py detects approved file
              |
10. Calls odoo-mcp: create_invoice -> post_invoice
              |
11. Calls email-mcp: send_email (invoice PDF)
              |
12. audit_logger: logs action with approval_status="approved"
              |
13. All files moved to /Done/
              |
14. Dashboard.md updated
```

## Ralph Wiggum Loop

The Ralph Wiggum pattern keeps Claude Code working autonomously until a
multi-step task is complete.

```
Orchestrator creates state file with prompt
              |
       Claude works on task
              |
       Claude tries to exit
              |
    Stop hook checks: Is task in /Done?
         /              \
       YES               NO
        |                 |
   Allow exit        Block exit
   (complete)        Re-inject prompt
                     Continue working
                          |
                     Repeat (max 10x)
```

**Configuration:**
- Hook: `.claude/hooks/stop.py`
- Strategy: `file_movement` (checks if task file moved to /Done)
- Max iterations: 10
- State: `.ralph_state.json`

## Security Model

```
+-------------------+     +-------------------+     +-------------------+
|   SECRETS LAYER   |     |   APPROVAL LAYER  |     |   AUDIT LAYER     |
|                   |     |                   |     |                   |
| .env (gitignored) |     | Company_Handbook  |     | /Logs/YYYY-MM-DD  |
| credentials.json  |     | Approval thresholds|    | JSON structured   |
| token.json        |     | /Pending_Approval |     | 90-day retention  |
| Session dirs      |     | /Approved         |     | Every action      |
|                   |     | /Rejected         |     | logged with actor |
| NEVER in git      |     | Human-in-the-loop |     | and approval_status|
| NEVER in vault    |     | for all sensitive  |     |                   |
+-------------------+     +-------------------+     +-------------------+
```

**Rules:**
- All payments: always require human approval
- Invoices >= $500: require approval before posting
- Social media: all posts require approval (configurable)
- Payments are NEVER auto-queued by graceful degradation
- DRY_RUN mode prevents real external actions in development

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Brain | Claude Code (Sonnet/Opus) | Reasoning, planning, decision-making |
| Memory | Obsidian (local markdown) | Dashboard, rules, task tracking |
| Email | Gmail API + Node.js MCP | Read/send/draft emails |
| ERP | Odoo Community + Docker | Invoices, customers, accounting |
| Social | Meta Graph API + Twitter v2 | Post, fetch, summarize |
| WhatsApp | Playwright automation | Message monitoring |
| LinkedIn | Playwright automation | Messages + auto-posting |
| Persistence | Ralph Wiggum stop hook | Autonomous multi-step completion |
| Reliability | retry + watchdog + degradation | Error recovery |
| Audit | JSON structured logger | Compliance and traceability |
| Scheduling | Cron (Linux) / Task Scheduler | Automated briefings, processing |
