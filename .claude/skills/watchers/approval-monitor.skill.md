# approval-monitor

Monitor approval folders and execute approved actions with human-in-the-loop workflow.

## What you do

You watch the approval workflow folders (`/Pending_Approval`, `/Approved`, `/Rejected`) and execute actions once they receive human approval.

## When to use

- Continuously running as part of orchestrator
- When sensitive actions need human approval
- Before sending emails, making payments, or posting on social media
- As safety mechanism for AI Employee actions

## Prerequisites

- Approval folder structure exists
- Email MCP server configured (for email actions)
- Orchestrator running

## Instructions

### Step 1: Verify Approval Folders

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault
mkdir -p Pending_Approval Approved Rejected Done
```

### Step 2: Start Approval Watcher

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python approval_watcher.py
```

This will:
1. Monitor `/Pending_Approval` for new items
2. Monitor `/Approved` for approved items
3. Monitor `/Rejected` for rejected items
4. Execute approved actions
5. Log all decisions

### Step 3: Approval Workflow

```
┌──────────────────────────────────────┐
│  Claude creates sensitive action     │
│  (email send, payment, post)         │
└─────────────┬────────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│  Draft saved in /Pending_Approval    │
│  with all action details             │
└─────────────┬────────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│  Human reviews draft                 │
│  - Check content                     │
│  - Verify recipient/amount           │
│  - Edit if needed                    │
└─────────────┬────────────────────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
  Approve        Reject
  (Move to       (Move to
  /Approved)     /Rejected)
       │             │
       │             └──> Logged, moved to /Done
       │
       ▼
┌──────────────────────────────────────┐
│  Approval Watcher detects             │
│  Executes action via MCP/script      │
└─────────────┬────────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│  Action completed                     │
│  Result logged                        │
│  File moved to /Done                  │
└──────────────────────────────────────┘
```

### Step 4: Action Types

The watcher handles these approval types:

**Email Actions:**
```yaml
type: email_draft
action: send_email
to: client@example.com
subject: Invoice for January
approval_required: true
```

**Payment Actions:**
```yaml
type: payment_request
action: send_payment
recipient: Vendor XYZ
amount: 500.00
approval_required: true
```

**Social Media Posts:**
```yaml
type: social_post
action: post_linkedin
content: "..."
approval_required: true
```

**File Operations:**
```yaml
type: file_operation
action: delete_file
path: /old_data.csv
approval_required: true
```

### Step 5: Execute Approved Actions

When file moves to `/Approved`:

1. **Parse action file** - Extract action type and parameters
2. **Validate** - Ensure all required fields present
3. **Execute** - Call appropriate MCP server or script
4. **Log result** - Record success/failure
5. **Move to Done** - Archive completed action

## Output format

```
Approval Monitor Active
Watching: /Pending_Approval, /Approved, /Rejected

Pending Approvals: 3
1. EMAIL_draft_client_update.md (2 minutes ago)
2. LINKEDIN_post_friday.md (1 hour ago)
3. PAYMENT_vendor_invoice.md (3 hours ago)

⏳ Waiting for human approval...

[User approves EMAIL_draft_client_update.md]

✅ Approved action detected!
- Type: email_draft
- To: client@example.com
- Subject: Project Update

Executing...
✅ Email sent successfully via Gmail API
✅ Logged to /Logs/email-mcp.log
✅ Moved to /Done/EMAIL_draft_client_update.md

Remaining pending: 2
```

## Error handling

**Execution failed:**
- Log error details
- Move back to /Pending_Approval
- Add error note to file
- Alert user

**Invalid action file:**
- Move to /Rejected with reason
- Log validation error
- Alert user

**MCP server unavailable:**
- Retry 3 times with backoff
- If still failing, alert user
- Keep in /Approved for manual retry

**Timeout:**
- Approvals expire after 24 hours
- Auto-move to /Rejected with note
- Alert user of expired approvals

## Examples

**Example 1: Email approval**
```
Draft created: /Pending_Approval/EMAIL_invoice_client.md

Content:
---
type: email_draft
to: client@example.com
subject: January Invoice
---
Dear Client,
Please find attached...

User reviews and approves (moves to /Approved)
→ Approval watcher detects
→ Calls Email MCP send_email tool
→ Email sent via Gmail
→ Result logged
→ File moved to /Done
```

**Example 2: Payment rejection**
```
Request: /Pending_Approval/PAYMENT_vendor_500.md
User reviews: "This is duplicate payment!"
→ Moves to /Rejected
→ Approval watcher logs rejection
→ No action taken
→ File archived to /Done/Rejected/
```

**Example 3: Edited approval**
```
Draft: /Pending_Approval/LINKEDIN_post.md
User: Opens file, edits content, saves
User: Moves to /Approved
→ Watcher reads edited version
→ Posts edited content (not original)
→ Human can modify before approval
```

## Integration points

- **Email MCP**: Executes email sends
- **Claude Processor**: Creates approval requests
- **Orchestrator**: Runs watcher continuously
- **Company Handbook**: Follows approval rules
- **Dashboard**: Updates approval stats

## Security features

✅ **Human-in-the-loop** - No auto-execution of sensitive actions
✅ **Edit before approve** - Can modify content before execution
✅ **Audit trail** - All approvals/rejections logged
✅ **Expiration** - Stale approvals auto-reject
✅ **Validation** - Action files validated before execution

## Company Handbook rules

According to Company_Handbook.md:

| Action | Auto-Approve | Requires Approval |
|--------|--------------|-------------------|
| Read emails | ✅ Yes | - |
| Draft email | ✅ Yes | - |
| Send email | - | ✅ Yes |
| Reply WhatsApp | - | ✅ Yes |
| Create invoice | ✅ Yes | - |
| Send invoice | - | ✅ Yes |
| Any payment | - | ✅ Always |
| Delete files | - | ✅ Always |
| Post on social media | - | ✅ Yes |

## Success criteria

✅ Approval watcher running
✅ Folders monitored continuously
✅ Approved actions executed correctly
✅ Rejected actions logged and archived
✅ All actions have audit trail
✅ Errors handled gracefully

## Performance

- Detection time: < 1 second
- Execution time: Depends on action (emails ~2s, posts ~5s)
- CPU usage: < 2%
- Memory: < 50MB

---

**Skill Type:** Watcher + Executor
**Tier:** Silver (Critical safety feature)
**Automation:** Always running
**Security:** High (HITL enforcement)
