# vault-setup

Initialize Obsidian vault structure for Personal AI Employee with all required folders and foundational markdown files.

## What you do

Set up the complete foundation of the AI Employee system by creating the Obsidian vault directory structure, core markdown files, and workflow folders.

## Instructions

### 1. Create Vault Directory Structure

```bash
mkdir -p ~/AI_Employee_Vault/{Needs_Action,Plans,Pending_Approval,Approved,Rejected,Done,Logs,Briefings,Accounting}
```

### 2. Verify Structure

```bash
ls -la ~/AI_Employee_Vault/
```

You should see 9 folders created.

### 3. Create Dashboard.md

```bash
cat > ~/AI_Employee_Vault/Dashboard.md << 'EOF'
---
type: dashboard
last_updated: 2026-02-05T00:00:00Z
---

# AI Employee Dashboard

## Status Overview
- **System Status:** 🟢 Operational
- **Last Activity:** Not yet started
- **Active Tasks:** 0
- **Tier:** Bronze (Foundation)

## Financial Summary
- **Current Balance:** $0.00
- **Pending Transactions:** 0
- **This Month Revenue:** $0.00
- **This Month Expenses:** $0.00

## Communications
- **Unread Emails:** 0
- **Pending WhatsApp:** 0
- **Awaiting Response:** 0

## Active Projects
- No active projects yet

## Recent Activity
_AI Employee will populate this section automatically_

## Alerts & Notifications
- ✅ System initialized
- ⏳ Waiting for first watcher to be configured

---
*Last updated: 2026-02-05*
EOF
```

### 4. Create Company_Handbook.md

```bash
cat > ~/AI_Employee_Vault/Company_Handbook.md << 'EOF'
---
type: handbook
version: 1.0.0
last_updated: 2026-02-05
---

# Company Handbook: Rules of Engagement

## Communication Guidelines

### Email Protocol
- **Response Time:** Reply to important emails within 24 hours
- **Tone:** Always professional and polite
- **Auto-Approve:** ❌ None (Bronze tier)
- **Require Approval:** ✅ All outgoing emails

### WhatsApp Protocol (Silver+ Tier)
- **Response Time:** Urgent (<1 hour), routine (<4 hours)
- **Keywords:** "urgent", "asap", "invoice", "payment", "help"
- **Auto-Approve:** ❌ None
- **Require Approval:** ✅ All messages

## Financial Guidelines

### Payment Approval Rules
- **Auto-Approve:** ❌ None
- **Require Approval:** ✅ ALL payments
- **Flag for Review:** >$500
- **Never Auto-Approve:** Transfers, wires, crypto

## Task Prioritization

### P1 (Critical - Same Day)
- Client requests with deadlines
- Payment/billing issues
- Security alerts
- Time-sensitive opportunities

### P2 (High - Within 48 Hours)
- New project inquiries
- Routine client communication
- Scheduled content
- Admin tasks with near deadlines

### P3 (Normal - Within 1 Week)
- General maintenance
- Documentation updates
- Process improvements

### P4 (Low - When Available)
- Nice-to-have features
- Long-term planning
- Archive and cleanup

## AI Behavior Guidelines

### ✅ Act Autonomously
- Moving files between folders
- Creating summaries and reports
- Logging activities
- Categorizing items

### 🔒 Request Approval (HITL)
- Sending emails/messages
- Making payments
- Posting to social media
- Deleting files
- Making commitments

### 🚨 Alert Immediately
- Security issues
- System errors
- Payment failures
- Client complaints
- Opportunities with deadlines
- Anything >$500

---
*This handbook guides AI Employee behavior*
EOF
```

### 5. Create Business_Goals.md

```bash
cat > ~/AI_Employee_Vault/Business_Goals.md << 'EOF'
---
type: business_goals
quarter: Q1 2026
last_updated: 2026-02-05
review_frequency: weekly
---

# Business Goals: Q1 2026

## Revenue Target
- **Monthly Goal:** $10,000
- **Quarterly Goal:** $30,000
- **Current MTD:** $0
- **Current QTD:** $0

## Key Metrics to Track

| Metric | Target | Current | Alert | Status |
|--------|--------|---------|-------|--------|
| Response Time | <24h | - | >48h | 🟡 Setup |
| Payment Rate | >90% | - | <80% | 🟡 Setup |
| Software Costs | <$500/mo | - | >$600 | 🟡 Setup |
| Active Projects | 3-5 | 0 | <2/>7 | 🔴 Low |

## Quarterly Objectives

### Objective 1: AI Employee Foundation (Bronze)
- **Description:** Set up vault, watcher, Claude integration
- **Success Criteria:**
  - ✅ Vault structure created
  - ⏳ One watcher operational
  - ⏳ Claude Code integration tested
  - ⏳ Demo video recorded
- **Deadline:** Week 2 of Q1
- **Actions:**
  - [x] Run /vault-setup
  - [ ] Complete /watcher-setup
  - [ ] Complete /claude-integration
  - [ ] Record demo

---
*AI Employee uses these goals for prioritization*
EOF
```

### 6. Create README

```bash
cat > ~/AI_Employee_Vault/README.md << 'EOF'
# Personal AI Employee Vault

Central nervous system of your Personal AI Employee.

## Structure

- **Dashboard.md** - Real-time status
- **Company_Handbook.md** - Rules and behavior
- **Business_Goals.md** - Objectives and KPIs

### Workflow Folders
- **Needs_Action/** - New items from watchers
- **Plans/** - AI-generated plans
- **Pending_Approval/** - HITL actions
- **Approved/** - Ready for execution
- **Rejected/** - Rejected actions
- **Done/** - Completed tasks
- **Logs/** - Audit logs (90 days)
- **Briefings/** - CEO briefings (Gold+)
- **Accounting/** - Financial records

## How It Works

1. Watchers → Needs_Action/
2. Claude Code → Plans/
3. Claude → Pending_Approval/
4. Human → Approved/ or Rejected/
5. Orchestrator → Done/

## Current Tier: Bronze
- [x] Vault structure
- [ ] First watcher
- [ ] Claude integration
- [ ] Demo video

---
**Version:** 1.0.0 | **Created:** 2026-02-05
EOF
```

### 7. Test in Obsidian

Open Obsidian and select "Open folder as vault", then navigate to `~/AI_Employee_Vault`.

### 8. Test Claude Code Access

```bash
cd ~/AI_Employee_Vault
claude "Read Dashboard.md and summarize the current status"
```

## Success Criteria

- [ ] 9 folders created
- [ ] 4 markdown files created
- [ ] Valid YAML frontmatter
- [ ] Obsidian opens vault
- [ ] Claude Code can read/write

## Next Steps

- `/watcher-setup` - Configure first watcher
- `/claude-integration` - Test operations
