# gmail-monitor

Monitor Gmail for important/unread emails and create action files in the vault.

## What you do

You check Gmail for new unread or important emails, extract relevant information, and create properly formatted action files in `/Needs_Action` for the AI Employee to process.

## When to use

- When user asks to "check email" or "check Gmail"
- When user wants to see "unread emails" or "important emails"
- As part of the automated monitoring workflow
- When orchestrator triggers email check

## Prerequisites

- Gmail API credentials configured at `AI_Employee_Vault/Watchers/credentials.json`
- OAuth token exists at `AI_Employee_Vault/Watchers/token.json`
- Python Gmail watcher script available

## Instructions

### Step 1: Verify Gmail Authentication

Check if Gmail authentication is set up:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
test -f token.json && echo "✅ Authenticated" || echo "❌ Need authentication"
```

If not authenticated, run:
```bash
python authenticate_gmail.py
```

### Step 2: Run Gmail Check

Execute the Gmail watcher to check for new emails:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python gmail_watcher.py --check-once
```

### Step 3: Process Results

The watcher will:
1. Query Gmail for unread/important emails
2. Filter by priority keywords (urgent, invoice, payment, etc.)
3. Create action files in `/Needs_Action` with format:
   ```
   EMAIL_[timestamp]_[message_id].md
   ```

### Step 4: Report Findings

Read the created files and report to user:
- Number of new emails detected
- Priority level (high/medium/low)
- Quick summary of subjects
- Location of action files

### Step 5: Suggest Next Actions

Based on findings, suggest:
- "Process these with Claude processor?"
- "Create plans for urgent items?"
- "Mark specific emails for immediate attention?"

## Output format

```
Gmail Check Complete:
- Total unread: X
- New high-priority: Y
- Action files created: Z

High Priority Items:
1. From: [sender] - Subject: [subject]
2. From: [sender] - Subject: [subject]

📁 Files created in: /Needs_Action/

Next steps:
- Run claude_processor.py to generate plans
- Review /Needs_Action folder
```

## Error handling

If authentication fails:
```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
rm token.json
python authenticate_gmail.py
```

If API quota exceeded:
- Wait 1 minute and retry
- Check rate limits in Google Cloud Console

If no credentials:
- Guide user to set up Gmail API credentials
- Point to setup documentation

## Examples

**Example 1: Manual check**
```
User: "Check my Gmail for new emails"
Agent: [Runs gmail-monitor skill]
       → Found 3 new unread emails
       → Created 3 action files
       → Reports summary
```

**Example 2: Automated monitoring**
```
Orchestrator triggers gmail-monitor every 10 minutes
→ Continuously monitors Gmail
→ Creates action files for new important emails
```

## Integration points

- **Orchestrator**: Calls this skill on schedule
- **Claude Processor**: Processes created action files
- **Dashboard**: Updates email count statistics
- **Company Handbook**: Follows email priority rules

## Success criteria

✅ Gmail authenticated successfully
✅ Unread emails detected
✅ Action files created with proper format
✅ Processed IDs tracked to avoid duplicates
✅ User notified of findings

---

**Skill Type:** Watcher
**Tier:** Silver
**Automation:** Can run continuously or on-demand
