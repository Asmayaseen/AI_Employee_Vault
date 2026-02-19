# claude-processor

Process action items from /Needs_Action and generate intelligent plans with Claude Code reasoning.

## What you do

You read action files from `/Needs_Action`, analyze them using Claude's reasoning capabilities, generate step-by-step plans in `/Plans`, and create approval requests when needed.

## When to use

- When new items appear in `/Needs_Action` folder
- When user asks to "process pending actions"
- When user wants to "generate plans for tasks"
- As part of automated workflow after watchers detect items
- When briefing or summary generation is requested

## Prerequisites

- Claude Code installed and accessible
- Vault folder structure set up
- Company_Handbook.md exists with business rules
- Business_Goals.md exists with objectives

## Instructions

### Step 1: Check Pending Actions

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault
ls -1 Needs_Action/ | wc -l
```

### Step 2: Run Claude Processor

**Process all pending items:**
```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python claude_processor.py --process-all
```

**Process specific item:**
```bash
python claude_processor.py --file "Needs_Action/EMAIL_20260208_client.md"
```

**Generate daily briefing:**
```bash
python claude_processor.py --briefing
```

### Step 3: Processing Logic

For each action file:

1. **Read and understand** - Parse YAML frontmatter and content
2. **Classify** - Determine type (email, payment, lead, support, etc.)
3. **Check rules** - Reference Company_Handbook.md for guidelines
4. **Reason** - Apply Claude's reasoning to determine best approach
5. **Generate plan** - Create step-by-step plan with checkboxes
6. **Create approval** - If sensitive action, create approval request
7. **Move file** - Move processed item to `/Plans` or `/Pending_Approval`

### Step 4: Plan Generation Format

```markdown
---
created: 2026-02-08T12:30:00Z
source: EMAIL_20260208_client.md
type: client_inquiry
priority: high
estimated_time: 30 minutes
status: pending
---

## Objective

Respond to client inquiry about project status and send updated timeline.

## Context

Client sent email asking about Project Alpha delivery timeline.
Previous update sent 2 weeks ago showed 80% completion.

## Analysis

According to Business_Goals.md:
- Project Alpha due: Jan 15, 2026
- Current status: 85% complete
- On track for on-time delivery

According to Company_Handbook.md:
- Client response time target: < 24 hours
- Project updates require professional tone
- Email send requires approval

## Plan

- [x] Review current project status
- [x] Check project timeline
- [ ] Draft professional email response
- [ ] Include updated timeline
- [ ] Request approval for sending
- [ ] Send email once approved
- [ ] Log completion

## Draft Email

**To:** client@example.com
**Subject:** Project Alpha Status Update

Dear [Client],

Thank you for reaching out. I'm pleased to report that Project Alpha
is now 85% complete and remains on track for delivery by January 15.

[... rest of email ...]

## Next Steps

1. Human reviews and approves email draft
2. Move to /Approved to send
3. Log completion once sent

**Estimated completion:** Today, 2:00 PM
```

### Step 5: Classification Rules

The processor auto-classifies based on keywords:

**Sales/Lead:**
- Keywords: pricing, quote, interested, services, proposal
- Action: Create proposal draft, move to approval

**Support/Issue:**
- Keywords: problem, bug, issue, not working, help
- Action: Create support plan, prioritize

**Invoice/Payment:**
- Keywords: invoice, payment, receipt, billing
- Action: Generate invoice or process payment

**Meeting/Scheduling:**
- Keywords: meeting, call, schedule, availability
- Action: Check calendar, propose times

**General Inquiry:**
- Default for unmatched
- Action: Create standard response

## Output format

```
Claude Processor Running...

Processing: /Needs_Action/

Found 6 pending actions:
1. EMAIL_20260208_client.md → Client inquiry
2. WHATSAPP_20260208_vendor.md → Invoice request
3. FILE_20260208_contract.md → Document review
4. LINKEDIN_MSG_20260208_lead.md → Sales lead
5. EMAIL_20260208_support.md → Bug report
6. FILE_20260208_invoice.md → Payment processing

Processing [1/6]: EMAIL_20260208_client.md
→ Type: client_inquiry
→ Priority: HIGH
→ Reasoning: Response needed within 24h per handbook
→ Generated: PLAN_20260208_client_response.md
→ Created approval: EMAIL_DRAFT_client_response.md
✅ Moved to /Plans

Processing [2/6]: WHATSAPP_20260208_vendor.md
→ Type: invoice_request
→ Priority: MEDIUM
→ Reasoning: Generate invoice from Business_Goals.md rates
→ Generated: PLAN_20260208_vendor_invoice.md
→ Created approval: INVOICE_vendor_jan2026.md
✅ Moved to /Plans

[... continues for all items ...]

Processing complete!
- Plans created: 6
- Approvals needed: 4
- Auto-processed: 2

Next steps:
→ Review /Pending_Approval folder (4 items)
→ Check /Plans folder for completed plans (6 items)
```

## Advanced features

### Briefing Generation

```bash
python claude_processor.py --briefing
```

Creates daily briefing at `/Briefings/[date]_daily.md`:

```markdown
# Daily Briefing - February 8, 2026

## Summary
- Pending actions: 6
- Awaiting approval: 4
- Completed today: 8
- Priority items: 2

## Priority Items (Require Immediate Attention)
1. ⚠️ Client A - Project deadline inquiry (< 24h response needed)
2. ⚠️ Payment overdue - Vendor B invoice (3 days overdue)

## Pending Approvals
1. Email to Client A (project update)
2. Invoice to Client C ($1,500)
3. LinkedIn post (Friday motivation)
4. Payment to Vendor D ($450)

## Completed Today
- Responded to 3 client emails
- Posted 1 LinkedIn update
- Processed 2 invoices
- Resolved 2 support tickets

## Upcoming Deadlines
- Project Alpha: Jan 15 (7 days)
- Q1 Tax Prep: Jan 31 (23 days)

## Suggestions
- Consider following up with Client B (no response in 2 weeks)
- Subscription "Notion" unused for 45 days - review?
```

### Context-Aware Processing

The processor uses these context sources:

1. **Company_Handbook.md** - Business rules and policies
2. **Business_Goals.md** - Revenue targets and projects
3. **Dashboard.md** - Current system status
4. **/Plans** folder - Previous completed plans
5. **/Done** folder - Historical actions

## Integration points

- **All Watchers**: Create action files for processor
- **Email MCP**: Executes approved email sends
- **Orchestrator**: Triggers processor on schedule
- **Dashboard**: Displays processing stats

## Error handling

**No action files:**
```
No pending actions found in /Needs_Action
System idle - all caught up!
```

**Claude Code unavailable:**
- Log error
- Retry in 5 minutes
- Alert user if persistent

**Malformed action file:**
- Skip and log error
- Move to /Errors folder
- Continue processing others

**Rate limit hit:**
- Pause processing
- Wait for rate limit reset
- Resume automatically

## Examples

**Example 1: Client email**
```
Input: EMAIL_20260208_client_question.md
→ Classified as: client_inquiry
→ Priority: HIGH (VIP client)
→ Plan generated with email draft
→ Approval request created
→ Human approves
→ Email sent via MCP
→ Logged to /Done
```

**Example 2: Support ticket**
```
Input: EMAIL_20260208_bug_report.md
→ Classified as: support_issue
→ Priority: P1 (critical bug)
→ Plan: Debug steps, fix approach, testing
→ Auto-processed (no approval needed for research)
→ Solution drafted
→ Approval for response email
```

## Success criteria

✅ All pending actions processed
✅ Plans generated with reasoning
✅ Classification accurate
✅ Approvals created for sensitive actions
✅ Files organized properly
✅ Briefings generated on schedule

## Performance

- Processing speed: ~5-10 seconds per item
- Concurrent processing: Up to 3 items
- Memory efficient: Processes one at a time
- Queue management: FIFO with priority override

---

**Skill Type:** Processor
**Tier:** Silver (Core reasoning engine)
**Automation:** Triggered by orchestrator or manual
**Intelligence:** Claude Code reasoning
