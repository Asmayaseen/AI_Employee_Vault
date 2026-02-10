---
title: Gold Tier Hackathon Demo Script
duration: 8-10 minutes
created: 2026-02-10
tier: gold
---

# Gold Tier Demo Script - Personal AI Employee

**Duration:** 8-10 minutes
**Presenter:** Asma Yaseen
**System:** Personal AI Employee (Gold Tier - Autonomous Employee)

---

## Opening (30 seconds)

> "This is my Personal AI Employee - a local-first, autonomous Digital FTE
> that manages my business 24/7 using Claude Code, Obsidian, and MCP servers.
> It follows the Perception-Reasoning-Action architecture with human-in-the-loop
> safety. Let me walk you through a real business day."

---

## Scene 1: Email Arrives (2 minutes)

**What Happens:**
A client email arrives asking for an invoice.

**Show:**
1. Open terminal - the Gmail Watcher is running
2. Show `/Needs_Action/` folder - new email file appears:
   `EMAIL_CLIENT_INVOICE_REQUEST.md`
3. Claude Processor reads it, generates a Plan:
   `Plans/PLAN_invoice_acme_corp.md`
4. Plan identifies: "Invoice creation required - HITL approval needed"
5. Approval file created in `/Pending_Approval/`:
   `APPROVAL_INVOICE_ACME_1500.md`

**Key Points:**
- Watcher detected the email automatically
- Claude reasoned about what action is needed
- It did NOT send the invoice - it asked for approval first

**Command to demonstrate:**
```bash
# Show the Needs_Action item
cat AI_Employee_Vault/Needs_Action/DEMO_EMAIL_acme_invoice_request.md

# Show the generated plan
cat AI_Employee_Vault/Plans/PLAN_DEMO_invoice_acme_corp.md
```

---

## Scene 2: Odoo Accounting Integration (2 minutes)

**What Happens:**
Demonstrate the Odoo MCP creating an invoice via JSON-RPC.

**Show:**
1. Odoo running on Docker (port 8069)
2. MCP server connected via JSON-RPC (not XML-RPC)
3. `create_invoice` tool creates a draft invoice in Odoo
4. Amount exceeds $500 threshold - HITL approval file created
5. After approval, `post_invoice` confirms it

**Key Points:**
- JSON-RPC protocol (hackathon requirement for Odoo 19+)
- HITL prevents auto-posting invoices above threshold
- Financial data feeds into CEO Briefing

**Command to demonstrate:**
```bash
# Test Odoo connection
cd MCP_Servers/odoo-mcp
python3 server.py --test

# Show the 7 available tools
python3 -c "from server import TOOLS; [print(f'  - {t}') for t in TOOLS]"
```

---

## Scene 3: Social Media Campaign (1.5 minutes)

**What Happens:**
AI Employee posts a business update across Facebook, Instagram, and Twitter.

**Show:**
1. Social MCP server with 10 tools across 3 platforms
2. `fb_post_message` with HITL approval enabled
3. Approval file appears in `/Pending_Approval/`
4. After approval, post goes live
5. `generate_all_summaries` produces cross-platform report

**Key Points:**
- All posts require approval by default (Company Handbook rule)
- Supports Facebook Graph API, Instagram Business, Twitter API v2
- Summary data feeds into CEO Briefing

**Command to demonstrate:**
```bash
cd MCP_Servers/social-mcp
python3 server.py --test
python3 -c "from server import TOOLS; [print(f'  - {t}') for t in TOOLS]"
```

---

## Scene 4: CEO Weekly Briefing (2 minutes)

**What Happens:**
Generate the Monday Morning CEO Briefing with accounting audit.

**Show:**
1. Run `ceo_briefing_generator.py --preview`
2. Report shows:
   - Executive summary with task metrics
   - Revenue tracking from Business_Goals.md
   - Financial Summary from Odoo (revenue, expenses, profit)
   - Subscription audit with cost-increase flags
   - Bottleneck analysis
   - Proactive suggestions
3. Open the generated briefing in Obsidian

**Key Points:**
- Integrates vault data + Odoo accounting + subscription audit
- Proactive suggestions: "Revenue behind target", "Overdue receivables"
- This is the "Business Handover" feature from the hackathon spec

**Command to demonstrate:**
```bash
python3 AI_Employee_Vault/Watchers/ceo_briefing_generator.py --preview
```

---

## Scene 5: Error Recovery + Audit (1 minute)

**What Happens:**
Show the system's resilience.

**Show:**
1. `watchdog.py --status` shows process health
2. Demonstrate retry handler with exponential backoff
3. Show graceful degradation: if Gmail goes down, actions are queued
4. Open today's audit log: structured JSON per Section 6.3
5. Show 90-day retention policy

**Command to demonstrate:**
```bash
# Watchdog status
python3 AI_Employee_Vault/Watchers/watchdog.py --status

# Today's audit log
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | python3 -m json.tool | head -30
```

---

## Scene 6: End-to-End Pipeline (1 minute)

**What Happens:**
Run the full pipeline test proving the architecture works.

**Show:**
1. `test_pipeline.py` runs 7 stages
2. All 20 checks pass
3. Files move: Needs_Action -> Plan -> Pending_Approval -> Approved -> Done
4. Audit logs written for every step

**Command to demonstrate:**
```bash
python3 AI_Employee_Vault/Watchers/test_pipeline.py
# Expected: 20/20 PASS
```

---

## Closing (30 seconds)

> "This AI Employee works almost 9,000 hours a year versus a human's 2,000.
> It costs under $500/month instead of $4,000-8,000. Every sensitive action
> requires my approval. Every action is logged. When things break, it
> recovers gracefully. This is the future of work automation - not replacing
> humans, but giving every person a tireless, reliable digital colleague."

---

## Backup Commands (if demo goes wrong)

```bash
# Quick health check
python3 AI_Employee_Vault/Watchers/test_pipeline.py --validate

# Show all MCP tools available
cd MCP_Servers/odoo-mcp && python3 -c "from server import TOOLS; print(f'{len(TOOLS)} Odoo tools')"
cd MCP_Servers/social-mcp && python3 -c "from server import TOOLS; print(f'{len(TOOLS)} Social tools')"

# Show Ralph Wiggum is configured
cat AI_Employee_Vault/.ralph_state.json
python3 -c "import json; c=json.load(open('.claude/settings.local.json')); print(c.get('ralph_config'))"
```
