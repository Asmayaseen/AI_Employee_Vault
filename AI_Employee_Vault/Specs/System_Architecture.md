# AI Employee System Architecture

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Status:** Gold Tier In Progress

---

## 1. System Overview

The AI Employee is an autonomous digital workforce system that operates 24/7, managing personal and business affairs through a local-first, agent-driven architecture with human-in-the-loop controls.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI EMPLOYEE SYSTEM v1.0                          │
│                     "Your Business on Autopilot"                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   WATCHERS  │───▶│   VAULT     │───▶│   CLAUDE    │                 │
│  │  (Sensors)  │    │  (Memory)   │    │  (Brain)    │                 │
│  └─────────────┘    └─────────────┘    └──────┬──────┘                 │
│        │                   │                   │                        │
│        │                   │                   ▼                        │
│        │                   │           ┌─────────────┐                 │
│        │                   │           │    MCP      │                 │
│        │                   │           │  (Hands)    │                 │
│        │                   │           └──────┬──────┘                 │
│        │                   │                   │                        │
│        ▼                   ▼                   ▼                        │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │              EXTERNAL WORLD                              │           │
│  │  Gmail │ WhatsApp │ LinkedIn │ Facebook │ Odoo │ Bank   │           │
│  └─────────────────────────────────────────────────────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

### 2.1 The Brain (Claude Code)

**Purpose:** Central reasoning engine that processes tasks, makes decisions, and coordinates actions.

**Components:**
- `claude_processor.py` - Main reasoning loop
- Ralph Wiggum Stop Hook - Autonomous iteration until task completion
- Skill-based architecture for modular capabilities

**Capabilities:**
- Read/Write to Obsidian Vault
- Generate Plans for complex tasks
- Execute MCP tools
- Request human approval when needed

### 2.2 The Memory (Obsidian Vault)

**Purpose:** Persistent storage, dashboard, and communication hub.

**Structure:**
```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status overview
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Targets and metrics
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items requiring processing
├── Plans/                    # Generated action plans
├── Pending_Approval/         # HITL approval queue
├── Approved/                 # Approved actions
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
├── Briefings/                # CEO briefing reports
├── Logs/                     # System logs
└── Watchers/                 # Watcher scripts
```

### 2.3 The Senses (Watchers)

**Purpose:** Monitor external systems and create actionable items in the vault.

| Watcher | Status | File | Interval |
|---------|--------|------|----------|
| Gmail | ✅ OPERATIONAL | `gmail_watcher.py` | 120s |
| WhatsApp | ✅ Ready | `whatsapp_watcher.py` | 30s |
| LinkedIn | ✅ Ready | `linkedin_watcher.py` | 15min |
| FileSystem | ✅ OPERATIONAL | `filesystem_watcher.py` | 10s |
| Approval | ✅ Ready | `approval_watcher.py` | 5s |
| Facebook | ❌ NOT IMPLEMENTED | - | - |
| Instagram | ❌ NOT IMPLEMENTED | - | - |
| Twitter | ❌ NOT IMPLEMENTED | - | - |

### 2.4 The Hands (MCP Servers)

**Purpose:** Execute actions in external systems.

| MCP Server | Status | Capabilities |
|------------|--------|--------------|
| email-mcp | ✅ OPERATIONAL | send_email, draft_email, read_inbox, search_emails, get_email |
| social-mcp | ❌ NOT IMPLEMENTED | post_content, read_messages, fetch_notifications |
| odoo-mcp | ❌ NOT IMPLEMENTED | create_invoice, fetch_summary, manage_customers |
| browser-mcp | ❌ NOT IMPLEMENTED | web automation, payments |

---

## 3. Detailed Architecture Diagram

```
                              ┌──────────────────────────────────────┐
                              │         CRON SCHEDULER               │
                              │  (setup_cron.sh / scheduler.py)      │
                              └──────────────────┬───────────────────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                    ▼                            ▼                            ▼
         ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
         │  DAILY BRIEFING  │       │   LINKEDIN POST  │       │  RALPH AUTO      │
         │   (8:00 AM)      │       │  (Mon/Wed/Fri)   │       │  (Every 5 min)   │
         └──────────────────┘       └──────────────────┘       └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              WATCHER LAYER                                          │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────────────────┤
│    Gmail     │   WhatsApp   │   LinkedIn   │  FileSystem  │     Approval            │
│   Watcher    │   Watcher    │   Watcher    │   Watcher    │     Watcher             │
│  (120s)      │   (30s)      │   (15min)    │  (realtime)  │     (5s)                │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┴─────────┬───────────────┘
       │              │              │              │                 │
       └──────────────┴──────────────┴──────────────┴─────────────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────────┐
                    │         /Needs_Action/             │
                    │   EMAIL_*.md  FILE_*.md  MSG_*.md  │
                    └────────────────┬───────────────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────────┐
                    │       CLAUDE PROCESSOR             │
                    │     (claude_processor.py)          │
                    │                                    │
                    │  1. Read item from Needs_Action    │
                    │  2. Analyze content                │
                    │  3. Generate Plan.md              │
                    │  4. Determine if action needed    │
                    └────────────────┬───────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌───────────────────┐            ┌───────────────────┐
        │   SAFE ACTION     │            │ SENSITIVE ACTION  │
        │   (Auto-execute)  │            │ (Needs Approval)  │
        └─────────┬─────────┘            └─────────┬─────────┘
                  │                                │
                  │                                ▼
                  │                    ┌───────────────────┐
                  │                    │ /Pending_Approval │
                  │                    │ APPROVAL_*.md     │
                  │                    └─────────┬─────────┘
                  │                              │
                  │                    ┌─────────┴─────────┐
                  │                    │                   │
                  │                    ▼                   ▼
                  │          ┌──────────────┐    ┌──────────────┐
                  │          │  /Approved/  │    │  /Rejected/  │
                  │          └──────┬───────┘    └──────────────┘
                  │                 │
                  └────────────────┬┘
                                   │
                                   ▼
                    ┌────────────────────────────────────┐
                    │           MCP SERVERS              │
                    ├──────────────┬─────────────────────┤
                    │  email-mcp   │  [future servers]   │
                    │  - send      │  - social-mcp       │
                    │  - draft     │  - odoo-mcp         │
                    │  - read      │  - browser-mcp      │
                    └──────────────┴──────────┬──────────┘
                                              │
                                              ▼
                              ┌────────────────────────────┐
                              │          /Done/            │
                              │   Completed tasks archive  │
                              └────────────────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Reasoning | Claude Code (Sonnet 4.5) | AI decision making |
| Memory | Obsidian (Markdown) | Local knowledge base |
| Watchers | Python 3.10+ | System monitoring |
| MCP | Node.js / Python | External actions |
| Automation | Cron / Playwright | Scheduling & browser |
| Hooks | Python (Ralph Wiggum) | Autonomous loops |

---

## 5. File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Email | `EMAIL_YYYYMMDD_HHMMSS_Subject.md` | `EMAIL_20260208_083356_Sales_Consultant.md` |
| File | `FILE_YYYYMMDD_HHMMSS_filename.md` | `FILE_20260205_175742_test_invoice.md` |
| Plan | `PLAN_YYYYMMDD_SourceFile.md` | `PLAN_20260208_EMAIL_Sales.md` |
| Approval | `APPROVAL_YYYYMMDD_action_description.md` | `APPROVAL_20260206_send_invoice.md` |
| Briefing | `YYYY-MM-DD_Monday_Briefing.md` | `2026-02-09_Monday_Briefing.md` |

---

## 6. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CREDENTIALS LAYER                                       │
│     ├── .env files (never committed)                        │
│     ├── credentials.json (OAuth)                            │
│     └── token.json (session tokens)                         │
│                                                             │
│  2. HUMAN-IN-THE-LOOP                                       │
│     ├── /Pending_Approval/ queue                            │
│     ├── approval_watcher.py                                 │
│     └── Manual file move to /Approved/                      │
│                                                             │
│  3. ACTION LIMITS                                           │
│     ├── Max iterations (Ralph Wiggum)                       │
│     ├── Rate limiting on API calls                          │
│     └── Dollar thresholds in Company_Handbook               │
│                                                             │
│  4. AUDIT LOGGING                                           │
│     ├── /Logs/ directory                                    │
│     ├── Daily JSON logs                                     │
│     └── Ralph loop logs                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Current Implementation Status

### Tier Completion

| Tier | Status | Completion |
|------|--------|------------|
| Bronze | ✅ COMPLETE | 100% |
| Silver | ✅ COMPLETE | 100% |
| Gold | ⚠️ IN PROGRESS | 60% |
| Platinum | ❌ NOT STARTED | 0% |

### Gold Tier Gaps

| Requirement | Status | Priority |
|-------------|--------|----------|
| Odoo Integration | ❌ Missing | P1 - HIGH |
| Facebook Watcher | ❌ Missing | P2 - MEDIUM |
| Instagram Watcher | ❌ Missing | P2 - MEDIUM |
| Twitter Watcher | ❌ Missing | P2 - MEDIUM |
| Social MCP Server | ❌ Missing | P2 - MEDIUM |
| Advanced Logging | ⚠️ Partial | P3 - LOW |
| Error Recovery | ⚠️ Partial | P3 - LOW |

---

## 8. Integration Points

### External APIs

| Service | API Type | Status |
|---------|----------|--------|
| Gmail | OAuth 2.0 + REST | ✅ Connected |
| LinkedIn | Playwright Automation | ✅ Ready |
| WhatsApp | Playwright Automation | ✅ Ready |
| Facebook | Graph API | ❌ Not Connected |
| Instagram | Graph API | ❌ Not Connected |
| Twitter | API v2 | ❌ Not Connected |
| Odoo | JSON-RPC | ❌ Not Connected |

---

## 9. Skill-Based Architecture

All AI functionality is implemented as Agent Skills:

```
.claude/skills/
├── watchers/
│   ├── gmail-monitor.skill.md
│   ├── whatsapp-monitor.skill.md
│   ├── linkedin-monitor.skill.md
│   ├── filesystem-monitor.skill.md
│   └── approval-monitor.skill.md
├── processing/
│   └── claude-processor.skill.md
├── orchestration/
│   └── orchestrator.skill.md
├── ralph-loop.skill.md
└── ceo-briefing.skill.md
```

---

## 10. Next Steps (Gold Tier Completion)

### Phase 1: Odoo Integration
1. Design odoo-mcp architecture
2. Implement JSON-RPC client
3. Create invoice/payment tools
4. Integrate with CEO Briefing

### Phase 2: Social Media
1. Create social-mcp server
2. Implement Facebook watcher
3. Implement Instagram watcher
4. Implement Twitter watcher

### Phase 3: Advanced Features
1. Enhanced audit logging
2. Error recovery system
3. Retry queue implementation

---

*Document generated by AI Employee System - SpecifyPlus Methodology*
