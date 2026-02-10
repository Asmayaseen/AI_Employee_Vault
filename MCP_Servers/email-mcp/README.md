# Email MCP Server

Email integration for AI Employee using Gmail API and Model Context Protocol (MCP).

## Features

- ✅ Send emails via Gmail API
- ✅ Create email drafts with approval workflow
- ✅ Search Gmail messages
- ✅ Fetch email details
- ✅ List Gmail labels
- ✅ Human-in-the-loop approval system
- ✅ Dry-run mode for testing
- ✅ Comprehensive logging

## Prerequisites

1. **Gmail API Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or use existing)
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download as `credentials.json`
   - Place in: `AI_Employee_Vault/Watchers/credentials.json`

2. **Authentication**
   ```bash
   cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
   python authenticate_gmail.py
   ```
   This will open a browser for authentication (first time only).

3. **Node.js Dependencies**
   ```bash
   cd /mnt/d/Ai-Employee/MCP_Servers/email-mcp
   npm install
   ```

## Installation

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Claude Code

Add to `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["/mnt/d/Ai-Employee/MCP_Servers/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "/mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials.json",
        "VAULT_PATH": "/mnt/d/Ai-Employee/AI_Employee_Vault",
        "DRY_RUN": "false"
      }
    }
  }
}
```

### 3. Test the Server
```bash
npm test
```

## Available Tools

### 1. `send_email`
Send an email via Gmail.

**Parameters:**
- `to` (string, required): Recipient email
- `subject` (string, required): Email subject
- `body` (string, required): Email body (HTML or plain text)
- `cc` (string, optional): CC recipients
- `bcc` (string, optional): BCC recipients

**Example:**
```javascript
{
  "name": "send_email",
  "arguments": {
    "to": "client@example.com",
    "subject": "Invoice for January 2026",
    "body": "<p>Please find attached your invoice.</p>"
  }
}
```

### 2. `draft_email`
Create email draft for human approval.

**Parameters:**
- `to` (string, required): Recipient email
- `subject` (string, required): Email subject
- `body` (string, required): Email body
- `context` (string, optional): Reason for email

**Example:**
```javascript
{
  "name": "draft_email",
  "arguments": {
    "to": "client@example.com",
    "subject": "Follow-up on Project Alpha",
    "body": "Hi, just checking in on the project status...",
    "context": "Client requested follow-up in WhatsApp"
  }
}
```

### 3. `search_emails`
Search Gmail messages.

**Parameters:**
- `query` (string, required): Gmail search query
- `maxResults` (number, optional): Max results (default: 10)

**Example:**
```javascript
{
  "name": "search_emails",
  "arguments": {
    "query": "is:unread from:important@client.com",
    "maxResults": 5
  }
}
```

### 4. `get_email`
Get email details by message ID.

**Parameters:**
- `messageId` (string, required): Gmail message ID

### 5. `list_labels`
List all Gmail labels/folders.

## Approval Workflow

When Claude creates an email draft using `draft_email`, the flow is:

1. Draft file created in `/Pending_Approval/`
2. Human reviews the draft
3. **To approve:** Move file to `/Approved/`
4. **To reject:** Move file to `/Rejected/`
5. Orchestrator detects approved file
6. Calls `send_email` via MCP

## Configuration

### Environment Variables

Set in `AI_Employee_Vault/.env`:

```bash
# Gmail API
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret

# Paths
VAULT_PATH=/mnt/d/Ai-Employee/AI_Employee_Vault
LOG_PATH=/mnt/d/Ai-Employee/AI_Employee_Vault/Logs

# Safety
DRY_RUN=false  # Set to true for testing
DEV_MODE=false

# Rate Limits
MAX_EMAILS_PER_HOUR=10
```

## Security

- ✅ OAuth 2.0 authentication (no password storage)
- ✅ Tokens stored locally in `token.json`
- ✅ Human-in-the-loop for all sends
- ✅ Rate limiting
- ✅ Dry-run mode for testing
- ✅ Comprehensive audit logging

## Logging

All actions logged to: `AI_Employee_Vault/Logs/email-mcp.log`

Log format:
```
[2026-02-08T12:00:00Z] [INFO] Sending email to: client@example.com
[2026-02-08T12:00:01Z] [INFO] Email sent successfully. Message ID: 18d1234abcd
```

## Troubleshooting

### "Token not found" error
Run Gmail authentication first:
```bash
cd AI_Employee_Vault/Watchers
python authenticate_gmail.py
```

### "Credentials not found" error
1. Download `credentials.json` from Google Cloud Console
2. Place in `AI_Employee_Vault/Watchers/`

### "Permission denied" error
Re-authenticate with correct scopes:
```bash
rm token.json
python authenticate_gmail.py
```

### Test in dry-run mode
```bash
DRY_RUN=true npm test
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EMAIL MCP SERVER                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Claude Code ──► MCP Request ──► Email MCP Server          │
│                                      │                      │
│                                      ▼                      │
│                                  Gmail API                  │
│                                      │                      │
│                                      ▼                      │
│                              Send/Search/Draft              │
│                                      │                      │
│                                      ▼                      │
│                           Log to email-mcp.log              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  APPROVAL WORKFLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Claude calls draft_email                                │
│  2. Draft created in /Pending_Approval/                     │
│  3. Human reviews and moves to /Approved/                   │
│  4. Orchestrator detects approved file                      │
│  5. Calls send_email with approved content                  │
│  6. Email sent via Gmail API                                │
│  7. File moved to /Done/                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Integration with AI Employee

### From Claude Code

Claude can now use email tools directly:

```
User: "Send an invoice email to client@example.com"
Claude: [Calls draft_email MCP tool]
       Creates draft in /Pending_Approval/
Human: [Reviews and approves]
Claude: [Orchestrator calls send_email MCP tool]
       Email sent!
```

### From Orchestrator

```python
import subprocess
import json

def send_approved_email(draft_file):
    # Read approved draft
    draft = parse_draft(draft_file)

    # Call MCP server
    request = {
        "method": "tools/call",
        "params": {
            "name": "send_email",
            "arguments": {
                "to": draft['to'],
                "subject": draft['subject'],
                "body": draft['body']
            }
        }
    }

    # Execute
    proc = subprocess.Popen(
        ['node', 'index.js'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    response = proc.communicate(json.dumps(request).encode())
    return json.loads(response)
```

## License

MIT

## Author

Asma Yaseen (AI Employee Project)

---

**Status:** ✅ Production Ready
**Last Updated:** 2026-02-08
