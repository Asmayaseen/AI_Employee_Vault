# Personal AI Employee - Gold Tier Implementation

**Hackathon 0: Building Autonomous FTEs in 2026**
**Tier: Gold - Autonomous Employee**

> Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

An autonomous Digital FTE (Full-Time Equivalent) that manages personal and business affairs 24/7 using Claude Code as the reasoning engine and Obsidian as the management dashboard.

---

## Architecture

```
External Sources (Gmail, WhatsApp, LinkedIn, Odoo, Social Media)
        |
        v
+-----------------------------+
|    PERCEPTION LAYER         |  Python Watcher scripts
|  Gmail | WhatsApp | LinkedIn|  monitor external sources
|  FileSystem | Approval      |  and create action files
+-------------+---------------+
              |
              v
+-----------------------------+
|    OBSIDIAN VAULT (Local)   |  /Needs_Action -> /Plans ->
|  Dashboard | Company Rules  |  /Pending_Approval -> /Done
|  Business Goals | Briefings |
+-------------+---------------+
              |
              v
+-----------------------------+
|    REASONING LAYER          |  Claude Code processes tasks,
|    Claude Code + Ralph Loop |  generates plans, creates
|    Read -> Think -> Plan    |  approval requests
+-------------+---------------+
              |
              v
+-----------------------------+
|    ACTION LAYER (MCP)       |  MCP Servers execute approved
|  Email | Odoo | Social      |  actions via external APIs
|  HITL Approval Required     |
+-----------------------------+
```

## Features by Tier

### Bronze (Complete)
- Obsidian vault with Dashboard.md, Company_Handbook.md
- Gmail + Filesystem Watcher scripts
- Claude Code reading/writing vault files
- Folder structure: /Inbox, /Needs_Action, /Done
- Agent Skills for all AI functionality

### Silver (Complete)
- Gmail + WhatsApp + LinkedIn + Filesystem Watchers
- LinkedIn auto-poster (Mon/Wed/Fri)
- Claude reasoning loop generating Plan.md files
- Email MCP Server (send, draft, search)
- Human-in-the-loop approval workflow
- Cron scheduling for all automation

### Gold (Complete)
- **Odoo MCP Server** (JSON-RPC) - Invoices, customers, financial summaries
- **Social MCP Server** - Facebook, Instagram, Twitter/X posting + summaries
- **Error Recovery** - Retry handler with exponential backoff, watchdog process, graceful degradation
- **Structured Audit Logging** - Section 6.3 compliant JSON logs with 90-day retention
- **CEO Briefing with Accounting Audit** - Odoo financial integration, subscription audit
- **Ralph Wiggum Loop** - Autonomous multi-step task completion
- End-to-end pipeline tested

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js v24+ LTS
- Claude Code (active subscription)
- Obsidian v1.10.6+
- Docker (for Odoo)

### Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd Ai-Employee

# 2. Install Python dependencies
pip install -r AI_Employee_Vault/Watchers/requirements.txt

# 3. Configure environment
cp AI_Employee_Vault/.env.example AI_Employee_Vault/.env
# Edit .env with your credentials

# 4. Start Odoo (Docker)
cd MCP_Servers/odoo-mcp
docker-compose up -d

# 5. Setup Email MCP
cd MCP_Servers/email-mcp
npm install

# 6. Start watchers
bash start_everything.sh

# 7. Run pipeline test
python AI_Employee_Vault/Watchers/test_pipeline.py
```

### MCP Server Configuration

Add to Claude Code settings:
```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/MCP_Servers/email-mcp/index.js"]
    },
    {
      "name": "odoo",
      "command": "python3",
      "args": ["/path/to/MCP_Servers/odoo-mcp/server.py"]
    },
    {
      "name": "social",
      "command": "python3",
      "args": ["/path/to/MCP_Servers/social-mcp/server.py"]
    }
  ]
}
```

## Project Structure

```
Ai-Employee/
|-- AI_Employee_Vault/           # Obsidian Vault (Memory/GUI)
|   |-- Dashboard.md             # Real-time status
|   |-- Company_Handbook.md      # Rules of engagement
|   |-- Business_Goals.md        # Revenue targets & metrics
|   |-- Needs_Action/            # Incoming tasks
|   |-- Plans/                   # Generated action plans
|   |-- Pending_Approval/        # HITL approval queue
|   |-- Approved/                # Approved actions
|   |-- Done/                    # Completed tasks
|   |-- Briefings/               # CEO briefing reports
|   |-- Logs/                    # Structured audit logs
|   +-- Watchers/                # Python watcher scripts
|       |-- orchestrator.py      # Master control
|       |-- gmail_watcher.py     # Email monitoring
|       |-- linkedin_watcher.py  # LinkedIn monitoring
|       |-- whatsapp_watcher.py  # WhatsApp monitoring
|       |-- filesystem_watcher.py# File drop monitoring
|       |-- approval_watcher.py  # Approval workflow
|       |-- claude_processor.py  # AI reasoning engine
|       |-- ceo_briefing_generator.py # Weekly CEO briefing + Odoo audit
|       |-- retry_handler.py     # Exponential backoff retry
|       |-- watchdog.py          # Process health monitor
|       |-- graceful_degradation.py # Service fallback queues
|       |-- audit_logger.py      # Structured JSON logging
|       +-- test_pipeline.py     # E2E pipeline test
|-- MCP_Servers/                 # Action Layer
|   |-- email-mcp/               # Gmail MCP (Node.js)
|   |-- odoo-mcp/                # Odoo ERP MCP (Python, JSON-RPC)
|   |   |-- server.py
|   |   |-- odoo_client.py       # JSON-RPC client
|   |   |-- docker-compose.yml   # Odoo deployment
|   |   +-- tools/
|   |       |-- invoice_tools.py # Create/post/list invoices
|   |       +-- accounting_tools.py # Financial summary, expenses, audit
|   +-- social-mcp/              # Social Media MCP (Python)
|       |-- server.py
|       |-- adapters/            # Facebook, Instagram, Twitter
|       +-- tools/
|           +-- social_tools.py  # Post, fetch, summarize
+-- .claude/                     # Claude Code config
    |-- hooks/stop.py            # Ralph Wiggum loop
    +-- skills/                  # Agent Skills
```

## Key Design Decisions

1. **JSON-RPC over XML-RPC** for Odoo - Odoo 19+ compatible architecture
2. **File-based HITL** - Approval via folder moves (Obsidian-native)
3. **MCP per domain** - Separate servers for email, ERP, social
4. **Graceful degradation** - Queue actions when services are down, never auto-retry payments
5. **Structured audit logs** - JSON with 90-day retention, query/filter support
6. **Ralph Wiggum Loop** - Stop hook keeps Claude iterating until task complete

## Security

See SECURITY_DISCLOSURE.md for credential handling details.

- Credentials stored in .env (gitignored)
- All sensitive actions require HITL approval
- Payments never auto-approved above threshold
- Audit logs track every action with actor/approval status
- DRY_RUN mode for safe development

## Owner

Built by Asma Yaseen for the Personal AI Employee Hackathon 0.
