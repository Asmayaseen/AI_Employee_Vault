# whatsapp-monitor

Monitor WhatsApp Web for urgent messages and create action files in the vault.

## What you do

You monitor WhatsApp Web for new messages containing priority keywords (urgent, invoice, payment, help, etc.), extract message details, and create action files for processing.

## When to use

- When user asks to "check WhatsApp" or "check messages"
- When user wants to see "urgent WhatsApp messages"
- As part of automated monitoring workflow
- When keywords like "urgent", "invoice", "payment" are detected

## Prerequisites

- Playwright installed: `playwright install chromium`
- WhatsApp session authenticated (QR code scan done)
- Python WhatsApp watcher script available

## Instructions

### Step 1: Check WhatsApp Session

Verify if WhatsApp session exists:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
test -d .whatsapp_session && echo "✅ Session exists" || echo "❌ Need setup"
```

If not set up, guide user to run:
```bash
python setup_whatsapp_session.py
# This will open browser and show QR code to scan
```

### Step 2: Run WhatsApp Check

Execute the WhatsApp watcher:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python whatsapp_watcher.py --check-once
```

### Step 3: Process Urgent Messages

The watcher will:
1. Open WhatsApp Web in headless browser
2. Scan for unread chats
3. Check messages for priority keywords:
   - urgent, asap, help
   - invoice, payment, billing
   - meeting, deadline, emergency
4. Extract message content and sender
5. Create action files in `/Needs_Action`

### Step 4: Create Action Files

Format: `WHATSAPP_[timestamp]_[contact_name].md`

Content includes:
- Sender name/number
- Message text
- Timestamp
- Priority level
- Suggested actions

### Step 5: Report Findings

Provide summary:
- Number of urgent messages found
- Contact names
- Brief preview of messages
- Priority assessment

## Output format

```
WhatsApp Check Complete:
- Unread chats: X
- Urgent messages: Y
- Action files created: Z

Urgent Messages:
1. From: [Contact] - "[message preview...]" - Priority: HIGH
2. From: [Contact] - "[message preview...]" - Priority: MEDIUM

📁 Files created in: /Needs_Action/

⚠️  Messages marked URGENT require immediate attention
```

## Error handling

**Session expired:**
```bash
rm -rf .whatsapp_session
python setup_whatsapp_session.py
# Scan QR code again
```

**Browser timeout:**
- Increase timeout in watcher script
- Check internet connection
- Verify WhatsApp Web is accessible

**No unread messages:**
- Report "No urgent messages"
- Continue monitoring

## Examples

**Example 1: Urgent invoice request**
```
WhatsApp message: "Hi, can you send me the invoice ASAP?"
→ Detected keyword: "invoice", "ASAP"
→ Created: WHATSAPP_20260208_120000_ClientA.md
→ Priority: HIGH
→ Suggested action: Generate and send invoice
```

**Example 2: Regular check**
```
User: "Check my WhatsApp for urgent messages"
Agent: [Runs whatsapp-monitor skill]
       → Scanned 5 unread chats
       → Found 1 urgent message
       → Created action file
       → Reports to user
```

## Integration points

- **Orchestrator**: Calls this skill every 30 seconds (configurable)
- **Claude Processor**: Processes urgent message action files
- **Email MCP**: May draft response emails
- **Company Handbook**: Follows WhatsApp response rules

## Security notes

⚠️ **Important:**
- WhatsApp session contains authentication data
- Never commit `.whatsapp_session/` to git
- Keep session files secure
- Session expires if not used for 14 days

## Success criteria

✅ WhatsApp session authenticated
✅ Unread messages detected
✅ Priority keywords recognized
✅ Action files created with proper format
✅ User notified of urgent messages

---

**Skill Type:** Watcher
**Tier:** Silver
**Automation:** Runs every 30 seconds when orchestrator active
**Security:** High (contains auth session)
