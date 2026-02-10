# AI Employee Data Flow Specification

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Status:** Gold Tier In Progress

---

## 1. Primary Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          PRIMARY DATA FLOW                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

    EXTERNAL WORLD                    VAULT                      ACTIONS
    ═════════════                    ═════                      ═══════

    ┌─────────┐                 ┌─────────────┐
    │  Gmail  │────────────────▶│   /Inbox/   │
    └─────────┘     (1)         └──────┬──────┘
                                       │
    ┌─────────┐                        │ (2)
    │WhatsApp │────────────────────────┤
    └─────────┘                        │
                                       ▼
    ┌─────────┐                 ┌─────────────────┐
    │LinkedIn │────────────────▶│ /Needs_Action/  │
    └─────────┘                 └────────┬────────┘
                                         │
    ┌─────────┐                          │ (3)
    │FileDrop │──────────────────────────┤
    └─────────┘                          │
                                         ▼
                                ┌─────────────────┐
                                │ CLAUDE PROCESSOR│
                                │   (reasoning)   │
                                └────────┬────────┘
                                         │
                           ┌─────────────┴─────────────┐
                           │ (4)                       │ (5)
                           ▼                           ▼
                    ┌─────────────┐           ┌─────────────────┐
                    │   /Plans/   │           │/Pending_Approval│
                    └──────┬──────┘           └────────┬────────┘
                           │                           │
                           │ (6)              (7)      │
                           │              ┌───────────┴───────────┐
                           │              ▼                       ▼
                           │       ┌─────────────┐        ┌─────────────┐
                           │       │ /Approved/  │        │ /Rejected/  │
                           │       └──────┬──────┘        └─────────────┘
                           │              │
                           └──────────────┤
                                          │ (8)
                                          ▼
                                 ┌─────────────────┐
                                 │   MCP SERVERS   │
                                 │  (email, etc.)  │
                                 └────────┬────────┘
                                          │
                                          │ (9)
                                          ▼
                                 ┌─────────────────┐
                                 │     /Done/      │
                                 │  (archived)     │
                                 └─────────────────┘
```

---

## 2. Flow Steps Explained

| Step | From | To | Description | Trigger |
|------|------|-----|-------------|---------|
| 1 | Gmail | /Inbox/ | New important/unread emails saved | gmail_watcher.py (120s) |
| 2 | /Inbox/ | /Needs_Action/ | Items requiring attention | Watcher creates file |
| 3 | Watchers | /Needs_Action/ | All sources write here | Multiple watchers |
| 4 | Processor | /Plans/ | Generate action plans | claude_processor.py |
| 5 | Processor | /Pending_Approval/ | Sensitive actions queued | HITL workflow |
| 6 | /Plans/ | MCP | Direct safe actions | Auto-execute |
| 7 | Human | /Approved/ or /Rejected/ | Manual file move | User decision |
| 8 | /Approved/ | MCP | Execute approved action | approval_watcher.py |
| 9 | MCP | /Done/ | Archive completed task | Post-execution |

---

## 3. Watcher Data Flow

### 3.1 Gmail Watcher Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                     GMAIL WATCHER FLOW                           │
└──────────────────────────────────────────────────────────────────┘

    Gmail API                     gmail_watcher.py                Vault
    ═════════                    ═════════════════               ═════

    ┌─────────────┐
    │ Gmail Inbox │
    │  (unread)   │
    └──────┬──────┘
           │
           │ (1) OAuth 2.0 API Call
           │     list(userId='me', q='is:unread')
           ▼
    ┌─────────────┐
    │  Message    │
    │  Metadata   │
    └──────┬──────┘
           │
           │ (2) Check processed_ids
           │     Skip if already seen
           ▼
    ┌─────────────┐
    │   Filter    │
    │  Important  │
    └──────┬──────┘
           │
           │ (3) Extract headers
           │     From, Subject, Date
           ▼
    ┌─────────────┐
    │  Generate   │
    │  Markdown   │
    └──────┬──────┘
           │
           │ (4) Write to vault
           │
           ▼
    ┌───────────────────────────────────┐
    │ /Needs_Action/EMAIL_*.md          │
    │                                   │
    │ ---                               │
    │ type: email                       │
    │ from: sender@example.com          │
    │ subject: Important Message        │
    │ received: 2026-02-09T10:30:00     │
    │ priority: high                    │
    │ status: pending                   │
    │ ---                               │
    │                                   │
    │ ## Email Content                  │
    │ [email snippet...]                │
    │                                   │
    │ ## Suggested Actions              │
    │ - [ ] Reply to sender             │
    │ - [ ] Forward to relevant party   │
    └───────────────────────────────────┘
```

### 3.2 FileSystem Watcher Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                   FILESYSTEM WATCHER FLOW                        │
└──────────────────────────────────────────────────────────────────┘

    Drop Folder                filesystem_watcher.py              Vault
    ═══════════               ═════════════════════              ═════

    ┌─────────────┐
    │ User drops  │
    │ file to     │
    │ /Inbox/     │
    └──────┬──────┘
           │
           │ (1) watchdog detects
           │     FileCreatedEvent
           ▼
    ┌─────────────┐
    │  Read file  │
    │  metadata   │
    └──────┬──────┘
           │
           │ (2) Determine file type
           │     (invoice, report, etc.)
           ▼
    ┌─────────────┐
    │  Generate   │
    │ action file │
    └──────┬──────┘
           │
           │ (3) Write to Needs_Action
           │
           ▼
    ┌───────────────────────────────────┐
    │ /Needs_Action/FILE_*.md           │
    │                                   │
    │ ---                               │
    │ type: file_drop                   │
    │ original_name: invoice.pdf        │
    │ size: 45678                       │
    │ detected: 2026-02-09T10:30:00     │
    │ ---                               │
    │                                   │
    │ New file dropped for processing.  │
    └───────────────────────────────────┘
```

---

## 4. Processing Flow

### 4.1 Claude Processor Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                   CLAUDE PROCESSOR FLOW                          │
└──────────────────────────────────────────────────────────────────┘

    /Needs_Action/              claude_processor.py              Output
    ══════════════             ═════════════════════            ══════

    ┌─────────────┐
    │ Scan folder │
    │ for *.md    │
    └──────┬──────┘
           │
           │ (1) For each file:
           ▼
    ┌─────────────┐
    │ Read content│
    │ + frontmatt │
    └──────┬──────┘
           │
           │ (2) Classify item:
           │     - email_reply
           │     - file_processing
           │     - notification
           │     - action_required
           ▼
    ┌─────────────┐
    │  Determine  │
    │  priority   │
    └──────┬──────┘
           │
           │ (3) Generate Plan.md
           │
           ▼
    ┌─────────────────────────────────────────┐
    │ /Plans/PLAN_*.md                        │
    │                                         │
    │ # Action Plan                           │
    │                                         │
    │ ## Summary                              │
    │ [What needs to be done]                 │
    │                                         │
    │ ## Steps                                │
    │ 1. [ ] First action                     │
    │ 2. [ ] Second action                    │
    │                                         │
    │ ## Risk Assessment                      │
    │ - Sensitivity: HIGH/LOW                 │
    │ - Requires Approval: YES/NO             │
    └─────────────────────────────────────────┘
           │
           │ (4) Decision:
           │
           ├───────────────────┐
           │                   │
           ▼                   ▼
    ┌─────────────┐    ┌─────────────────┐
    │ Safe Action │    │ Sensitive Action│
    │ (auto-exec) │    │ (needs approval)│
    └──────┬──────┘    └────────┬────────┘
           │                    │
           ▼                    ▼
    ┌─────────────┐    ┌─────────────────┐
    │ MCP Execute │    │/Pending_Approval│
    └─────────────┘    └─────────────────┘
```

---

## 5. Approval Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                      APPROVAL FLOW                               │
└──────────────────────────────────────────────────────────────────┘

    Processor                   Human                        Watcher
    ═════════                  ═════                        ═══════

         │
         │ (1) Create approval request
         ▼
    ┌─────────────────────────────────────────┐
    │ /Pending_Approval/APPROVAL_*.md         │
    │                                         │
    │ ---                                     │
    │ type: approval_request                  │
    │ action: send_email                      │
    │ recipient: client@example.com           │
    │ created: 2026-02-09T10:30:00           │
    │ expires: 2026-02-10T10:30:00           │
    │ status: pending                         │
    │ ---                                     │
    │                                         │
    │ ## Action Details                       │
    │ [Description of what will happen]       │
    │                                         │
    │ ## To Approve                           │
    │ Move this file to /Approved/            │
    │                                         │
    │ ## To Reject                            │
    │ Move this file to /Rejected/            │
    └─────────────────────────────────────────┘
         │
         │ (2) Human reviews in Obsidian
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼ (3a) Approve                        ▼ (3b) Reject
    ┌─────────────┐                     ┌─────────────┐
    │ /Approved/  │                     │ /Rejected/  │
    │ APPROVAL_*  │                     │ APPROVAL_*  │
    └──────┬──────┘                     └─────────────┘
           │
           │ (4) approval_watcher.py detects
           ▼
    ┌─────────────┐
    │ Parse file  │
    │ get action  │
    └──────┬──────┘
           │
           │ (5) Execute via MCP
           ▼
    ┌─────────────┐
    │ MCP Server  │
    │ (email-mcp) │
    └──────┬──────┘
           │
           │ (6) Archive
           ▼
    ┌─────────────┐
    │   /Done/    │
    └─────────────┘
```

---

## 6. Ralph Wiggum Loop Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                   RALPH WIGGUM LOOP FLOW                         │
└──────────────────────────────────────────────────────────────────┘

    Start                       Loop                          Exit
    ═════                      ════                          ════

    ┌─────────────┐
    │ ralph_ctrl  │
    │   start     │
    └──────┬──────┘
           │
           │ (1) Create state file
           │     .ralph_state.json
           ▼
    ┌─────────────┐
    │ Claude runs │
    │   task      │
    └──────┬──────┘
           │
           │ (2) Claude tries to exit
           ▼
    ┌─────────────┐
    │  stop.py    │◀───────────────────┐
    │  (hook)     │                    │
    └──────┬──────┘                    │
           │                           │
           │ (3) Check completion      │
           │                           │
           ├─────────────┐             │
           │             │             │
           ▼             ▼             │
    ┌─────────────┐ ┌─────────────┐    │
    │  COMPLETE   │ │NOT COMPLETE │    │
    │             │ │             │    │
    │ - Promise   │ │ iteration++ │    │
    │ - File move │ │             │    │
    │ - Custom    │ │ Re-inject   │────┘
    └──────┬──────┘ │ prompt      │
           │        └─────────────┘
           │
           │ (4) Allow exit
           ▼
    ┌─────────────┐
    │   EXIT      │
    │  (code 0)   │
    └─────────────┘
```

---

## 7. CEO Briefing Generation Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                 CEO BRIEFING GENERATION FLOW                     │
└──────────────────────────────────────────────────────────────────┘

    Trigger                    Process                       Output
    ═══════                   ═══════                       ══════

    ┌─────────────┐
    │   Cron      │
    │ Sunday 8PM  │
    └──────┬──────┘
           │
           │ (1) Run ceo_briefing_generator.py
           ▼
    ┌─────────────┐    ┌─────────────┐
    │ Scan /Done/ │───▶│ Count tasks │
    │  (7 days)   │    │ completed   │
    └─────────────┘    └──────┬──────┘
                              │
    ┌─────────────┐           │
    │ Read Goals  │───────────┤
    │ .md file    │           │
    └─────────────┘           │
                              │
    ┌─────────────┐           │
    │ Scan        │───────────┤
    │ Pending     │           │
    └─────────────┘           │
                              │
                              ▼
                    ┌─────────────────┐
                    │ Generate Report │
                    └────────┬────────┘
                             │
                             │ (2) Write briefing
                             ▼
    ┌─────────────────────────────────────────────────────┐
    │ /Briefings/YYYY-MM-DD_Monday_Briefing.md            │
    │                                                     │
    │ # Monday Morning CEO Briefing                       │
    │                                                     │
    │ ## Executive Summary                                │
    │ [Week assessment]                                   │
    │                                                     │
    │ ## Revenue                                          │
    │ - Target: $X                                        │
    │ - Current: $Y                                       │
    │                                                     │
    │ ## Completed Tasks                                  │
    │ - [x] Task 1                                        │
    │ - [x] Task 2                                        │
    │                                                     │
    │ ## Bottlenecks                                      │
    │ | Task | Expected | Actual |                        │
    │                                                     │
    │ ## Proactive Suggestions                            │
    │ 1. [Recommendation]                                 │
    └─────────────────────────────────────────────────────┘
```

---

## 8. MCP Server Data Flow

### 8.1 Email MCP Flow

```
    Request                     MCP                        External
    ═══════                    ═══                        ════════

    ┌─────────────┐
    │ Claude Code │
    │ tool call:  │
    │ send_email  │
    └──────┬──────┘
           │
           │ (1) JSON-RPC request
           ▼
    ┌─────────────────────────────────────┐
    │ email-mcp/index.js                  │
    │                                     │
    │ Tool: send_email                    │
    │ Params:                             │
    │   to: "client@example.com"          │
    │   subject: "Re: Your Inquiry"       │
    │   body: "Hello..."                  │
    └──────────────┬──────────────────────┘
                   │
                   │ (2) Gmail API call
                   ▼
    ┌─────────────────────────────────────┐
    │ Gmail API                           │
    │ messages.send()                     │
    └──────────────┬──────────────────────┘
                   │
                   │ (3) Response
                   ▼
    ┌─────────────────────────────────────┐
    │ {                                   │
    │   "success": true,                  │
    │   "messageId": "abc123",            │
    │   "threadId": "xyz789"              │
    │ }                                   │
    └─────────────────────────────────────┘
```

---

## 9. Future Data Flows (Gold Tier)

### 9.1 Odoo MCP Flow (Planned)

```
    Claude                     odoo-mcp                      Odoo
    ══════                    ════════                      ════

    ┌─────────────┐
    │ create_     │
    │ invoice     │
    └──────┬──────┘
           │
           │ (1) Tool call
           ▼
    ┌─────────────────┐
    │ odoo-mcp        │
    │ JSON-RPC client │
    └────────┬────────┘
             │
             │ (2) Odoo API call
             │     models.execute_kw()
             ▼
    ┌─────────────────┐
    │ Odoo Community  │
    │ 19+             │
    │ account.move    │
    └────────┬────────┘
             │
             │ (3) Invoice created
             ▼
    ┌─────────────────┐
    │ Invoice ID: 123 │
    │ Total: $500     │
    └─────────────────┘
```

### 9.2 Social MCP Flow (Planned)

```
    Claude                    social-mcp                   Platforms
    ══════                   ══════════                   ═════════

    ┌─────────────┐
    │ post_       │
    │ content     │
    └──────┬──────┘
           │
           │ (1) Tool call
           ▼
    ┌───────────────────────────────────────────┐
    │ social-mcp                                │
    │                                           │
    │ platform: "facebook"                      │
    │ content: "New product launch..."          │
    │ media: [image_url]                        │
    └──────────────────┬────────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Facebook │ │Instagram │ │ Twitter  │
    │ Graph API│ │ Graph API│ │ API v2   │
    └──────────┘ └──────────┘ └──────────┘
```

---

*Document generated by AI Employee System - SpecifyPlus Methodology*
