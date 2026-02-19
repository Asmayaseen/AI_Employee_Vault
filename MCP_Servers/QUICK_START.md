# MCP Servers - Quick Start Guide

## Email MCP Server ✅

**Status:** Installed & Configured
**Location:** `/mnt/d/Ai-Employee/MCP_Servers/email-mcp/`

### Quick Commands

```bash
# Install (already done)
cd /mnt/d/Ai-Employee/MCP_Servers/email-mcp
npm install

# Test
npm test

# Run setup
./setup.sh

# View logs
tail -f /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/email-mcp.log
```

### Usage in Claude Code

Just ask Claude naturally:

```
"Draft an email to client@example.com about the project update"
"Search my unread emails from last week"
"Get details of email ID 18d1234abcd"
```

Claude will automatically use the appropriate MCP tool.

### Approval Workflow

```
1. Claude creates draft → /Pending_Approval/EMAIL_DRAFT_*.md
2. You review it
3. Move to /Approved/ to send
4. Orchestrator sends via Gmail API
5. Done!
```

### Available Tools

- ✅ `send_email` - Send via Gmail (requires approval)
- ✅ `draft_email` - Create draft for approval
- ✅ `search_emails` - Search Gmail
- ✅ `get_email` - Get email details
- ✅ `list_labels` - List Gmail labels

---

## Configuration

**Claude Code MCP Config:** `~/.config/claude-code/mcp.json`

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

---

## Troubleshooting

### MCP not loading?
```bash
# Check config exists
cat ~/.config/claude-code/mcp.json

# Restart Claude Code
claude --reload-mcp
```

### Authentication issues?
```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python authenticate_gmail.py
```

### Want to test safely?
```bash
# Set DRY_RUN=true in mcp.json or .env
DRY_RUN=true npm test
```

---

## Next Steps

1. ✅ Email MCP - Complete
2. 🎯 Browser MCP - For payments (coming soon)
3. 🎯 Calendar MCP - For scheduling (future)
4. 🎯 Slack MCP - For team comms (future)

---

**Last Updated:** 2026-02-08
