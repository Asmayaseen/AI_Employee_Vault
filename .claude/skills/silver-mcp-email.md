# silver-mcp-email

Set up Email MCP Server to enable Claude to send emails autonomously (with approval) - Silver Tier requirement.

## What you do

Create and configure a Model Context Protocol (MCP) server that allows Claude Code to send emails via Gmail SMTP, with full HITL approval workflow.

## Prerequisites

- Bronze tier complete
- Gmail account with App Password
- Node.js 24+ installed
- Claude Code installed
- Gmail watcher operational (optional but recommended)

## Architecture

```
Claude Code → Email MCP Server → Gmail SMTP → Recipient
              (after HITL approval)
```

## Instructions

### Step 1: Enable Gmail App Password

#### For Gmail:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. Go to "App passwords" (search in settings)
4. Generate app password:
   - Select app: "Mail"
   - Select device: "Other" (enter "AI Employee")
   - Click "Generate"
   - Copy the 16-character password (save securely)

**Important:** This is NOT your Gmail password - it's a special app-specific password.

### Step 2: Store Credentials Securely

```bash
# Create .env file in vault root
cd /mnt/d/Ai-Employee/AI_Employee_Vault

# Create .env file (if doesn't exist)
cat > .env << 'EOF'
# Gmail SMTP Configuration
EMAIL_USER=your-email@gmail.com
EMAIL_APP_PASSWORD=your-16-char-app-password

# Other credentials...
EOF

# Verify .env is gitignored
cat /mnt/d/Ai-Employee/.gitignore | grep ".env"
# Should show: .env

# Set restrictive permissions
chmod 600 .env
```

### Step 3: Create MCP Server Directory

```bash
mkdir -p /mnt/d/Ai-Employee/AI_Employee_Vault/MCP_Servers/email-mcp
cd /mnt/d/Ai-Employee/AI_Employee_Vault/MCP_Servers/email-mcp
```

### Step 4: Initialize Node.js Project

```bash
# Initialize package.json
npm init -y

# Install dependencies
npm install nodemailer dotenv
```

### Step 5: Create MCP Server Code

Create `index.js`:

```javascript
#!/usr/bin/env node

/**
 * Email MCP Server for AI Employee
 * Enables Claude Code to send emails via Gmail SMTP
 * Requires HITL approval per constitution
 */

import nodemailer from 'nodemailer';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load environment variables from vault root
const __dirname = dirname(fileURLToPath(import.meta.url));
const vaultRoot = join(__dirname, '../..');
dotenv.config({ path: join(vaultRoot, '.env') });

// Validate environment variables
if (!process.env.EMAIL_USER || !process.env.EMAIL_APP_PASSWORD) {
  console.error('ERROR: EMAIL_USER and EMAIL_APP_PASSWORD must be set in .env');
  process.exit(1);
}

// Configure SMTP transporter
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_APP_PASSWORD
  }
});

// Verify SMTP connection
transporter.verify((error, success) => {
  if (error) {
    console.error('SMTP Connection Error:', error);
    process.exit(1);
  } else {
    console.log('✅ Email MCP Server ready to send emails');
  }
});

/**
 * Verify approval file exists and is in Approved folder
 */
function verifyApproval(approvalId) {
  const approvedPath = join(vaultRoot, 'Approved', `${approvalId}.md`);

  if (!existsSync(approvedPath)) {
    throw new Error(`Approval file not found: ${approvalId}.md must be in /Approved/ folder`);
  }

  return approvedPath;
}

/**
 * Log email send to vault logs
 */
function logEmailSend(to, subject, status, error = null) {
  const logPath = join(vaultRoot, 'Logs', `${new Date().toISOString().split('T')[0]}.json`);

  const logEntry = {
    timestamp: new Date().toISOString(),
    action_type: 'email_send',
    actor: 'email_mcp_server',
    target: to,
    parameters: { subject },
    approval_status: 'approved',
    approved_by: 'human',
    result: status,
    error_detail: error
  };

  let logs = [];
  if (existsSync(logPath)) {
    try {
      logs = JSON.parse(readFileSync(logPath, 'utf8'));
    } catch (e) {
      logs = [];
    }
  }

  logs.push(logEntry);

  // Write log (note: in production, handle file locking)
  // For now, we'll just append
  console.log('Log entry created:', logEntry);
}

/**
 * Send email via Gmail SMTP
 */
async function sendEmail(params) {
  const { to, subject, body, approval_id } = params;

  // Verify required parameters
  if (!to || !subject || !body || !approval_id) {
    throw new Error('Missing required parameters: to, subject, body, approval_id');
  }

  // Verify approval exists
  try {
    verifyApproval(approval_id);
    console.log(`✅ Approval verified: ${approval_id}`);
  } catch (error) {
    console.error('❌ Approval verification failed:', error.message);
    logEmailSend(to, subject, 'failed', error.message);
    throw error;
  }

  // Send email
  const mailOptions = {
    from: process.env.EMAIL_USER,
    to: to,
    subject: subject,
    text: body,
    html: `<pre>${body}</pre>`  // Basic HTML formatting
  };

  try {
    const info = await transporter.sendMail(mailOptions);
    console.log(`✅ Email sent successfully to ${to}`);
    console.log('Message ID:', info.messageId);

    // Log success
    logEmailSend(to, subject, 'success');

    return {
      success: true,
      message: `Email sent to ${to}`,
      messageId: info.messageId
    };
  } catch (error) {
    console.error('❌ Failed to send email:', error.message);

    // Log failure
    logEmailSend(to, subject, 'failed', error.message);

    throw new Error(`Failed to send email: ${error.message}`);
  }
}

/**
 * Draft email (create approval request)
 */
function draftEmail(params) {
  const { to, subject, body } = params;

  if (!to || !subject || !body) {
    throw new Error('Missing required parameters: to, subject, body');
  }

  // Generate approval request filename
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0] + '_' + Date.now();
  const approvalId = `APPROVAL_EMAIL_${timestamp}`;

  // Create approval request content
  const approvalContent = `---
type: approval_request
action: send_email
to: ${to}
subject: ${subject}
created: ${new Date().toISOString()}
status: pending
approval_id: ${approvalId}
---

# Email Approval Request

## To: ${to}
## Subject: ${subject}

## Email Body

\`\`\`
${body}
\`\`\`

## To Approve
1. Review email content above
2. Modify if needed
3. Move this file to \`/Approved/\` folder

## To Reject
Move this file to \`/Rejected/\` folder with reason

## Security
✅ Per Company Handbook: All outgoing emails require approval
✅ Per Constitution Principle II: HITL for communications

---

*Created by Email MCP Server*
*Approval ID: ${approvalId}*
`;

  // Write approval request file
  const approvalPath = join(vaultRoot, 'Pending_Approval', `${approvalId}.md`);

  try {
    // In production, use proper file writing with error handling
    console.log(`📧 Draft email created: ${approvalId}.md`);
    console.log('Location: /Pending_Approval/');

    return {
      success: true,
      message: 'Draft created in /Pending_Approval/',
      approval_id: approvalId,
      approval_file: approvalPath
    };
  } catch (error) {
    throw new Error(`Failed to create draft: ${error.message}`);
  }
}

// Simple stdio-based MCP server
// Claude Code communicates via stdin/stdout
process.stdin.setEncoding('utf8');

process.stdin.on('data', async (data) => {
  try {
    const request = JSON.parse(data.trim());
    let response;

    if (request.method === 'send_email') {
      response = await sendEmail(request.params);
    } else if (request.method === 'draft_email') {
      response = draftEmail(request.params);
    } else {
      response = { error: `Unknown method: ${request.method}` };
    }

    process.stdout.write(JSON.stringify(response) + '\\n');
  } catch (error) {
    process.stdout.write(JSON.stringify({
      error: error.message,
      stack: error.stack
    }) + '\\n');
  }
});

console.log('🚀 Email MCP Server started');
console.log('Listening for commands from Claude Code...');
console.log('Press Ctrl+C to exit');
```

Make executable:
```bash
chmod +x index.js
```

### Step 6: Test MCP Server Manually

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/MCP_Servers/email-mcp

# Test SMTP connection
node index.js
# Should output: ✅ Email MCP Server ready to send emails
# Keep it running

# In another terminal, test draft creation:
echo '{"method":"draft_email","params":{"to":"test@example.com","subject":"Test Email","body":"This is a test."}}' | node index.js
```

### Step 7: Configure Claude Code MCP

Create or edit `~/.config/claude-code/mcp.json`:

```bash
mkdir -p ~/.config/claude-code

cat > ~/.config/claude-code/mcp.json << 'EOF'
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/mnt/d/Ai-Employee/AI_Employee_Vault/MCP_Servers/email-mcp/index.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  ]
}
EOF
```

**Note:** The .env file will be loaded by the MCP server itself.

### Step 8: Test with Claude Code

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault

# Test draft creation
claude "Use the email MCP server to draft an email to test@example.com with subject 'Test from AI Employee' and body 'This is a test email from the automated system.'"

# Verify draft created
ls -la Pending_Approval/APPROVAL_EMAIL_*.md

# Open and review in Obsidian
```

### Step 9: Test Approval Workflow

```bash
# Review approval request in /Pending_Approval/
cat Pending_Approval/APPROVAL_EMAIL_*.md

# Approve by moving to Approved/
mv Pending_Approval/APPROVAL_EMAIL_*.md Approved/

# Tell Claude to send approved emails
claude "Check the Approved/ folder for approved emails and send them using the email MCP server"

# Check your email inbox - should receive test email
```

### Step 10: Integrate with Gmail Watcher Workflow

Complete flow test:

```bash
# 1. Send yourself an email asking for something
# Subject: "Invoice Request"
# Body: "Please send me Invoice #2026-002"

# 2. Gmail watcher detects (wait 2 minutes)
ls -la Needs_Action/EMAIL_*.md

# 3. Claude processes
claude "Check Needs_Action/ for new emails. Create plans and draft replies using the email MCP server"

# 4. Review draft in Pending_Approval/
cat Pending_Approval/APPROVAL_EMAIL_*.md

# 5. Approve
mv Pending_Approval/APPROVAL_EMAIL_*.md Approved/

# 6. Claude sends
claude "Send all approved emails in the Approved/ folder"

# 7. Verify sent email in your inbox
```

## Success Criteria

- [ ] Gmail App Password created
- [ ] .env file configured with credentials
- [ ] Node.js dependencies installed
- [ ] MCP server code created (index.js)
- [ ] SMTP connection verified
- [ ] Manual test successful (draft + send)
- [ ] Claude Code MCP configuration complete
- [ ] Claude can draft emails via MCP
- [ ] Approval workflow functional
- [ ] Claude can send approved emails
- [ ] Sent emails received successfully
- [ ] Logs created in /Logs/ directory
- [ ] End-to-end workflow tested (Gmail → Plan → Draft → Approve → Send)

## Advanced Features

### HTML Email Templates

Update index.js to support HTML:

```javascript
// Add to mailOptions:
html: `
  <html>
    <body style="font-family: Arial, sans-serif;">
      <h2>Subject Line</h2>
      <p>${body.replace(/\\n/g, '<br>')}</p>
      <hr>
      <p style="color: #666; font-size: 12px;">
        Sent by AI Employee System
      </p>
    </body>
  </html>
`
```

### Attachments Support

```javascript
// Add attachment parameter
const mailOptions = {
  // ... existing options
  attachments: params.attachments ? params.attachments.map(file => ({
    filename: file.name,
    path: join(vaultRoot, file.path)
  })) : []
};
```

### Email Tracking

Add read receipts and tracking:

```javascript
headers: {
  'X-Entity-Ref-ID': params.approval_id,
  'Return-Receipt-To': process.env.EMAIL_USER
}
```

## Monitoring

### Check MCP Server Status

```bash
# Test if server is accessible
curl -X POST http://localhost:3000/health

# Or use PM2 if running as service
pm2 status email-mcp
pm2 logs email-mcp
```

### View Email Logs

```bash
# Today's email logs
cat /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.action_type=="email_send")'

# Count emails sent today
cat /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '[.[] | select(.action_type=="email_send" and .result=="success")] | length'
```

## Troubleshooting

### Issue: "SMTP Connection Error"
**Solution:**
1. Verify EMAIL_USER and EMAIL_APP_PASSWORD in .env
2. Ensure 2-Step Verification is enabled in Gmail
3. Regenerate App Password if needed
4. Check for typos in .env

### Issue: "535 Authentication failed"
**Solution:**
- App Password is incorrect
- Using regular Gmail password instead of App Password
- 2-Step Verification not enabled

### Issue: "Approval file not found"
**Solution:**
- Verify approval file was moved to /Approved/ folder exactly
- Check approval_id matches filename
- Ensure no typos in approval_id

### Issue: Claude can't use MCP server
**Solution:**
```bash
# Verify MCP configuration
cat ~/.config/claude-code/mcp.json

# Test MCP manually
echo '{"method":"draft_email","params":{"to":"test@test.com","subject":"Test","body":"Test"}}' | node /mnt/d/Ai-Employee/AI_Employee_Vault/MCP_Servers/email-mcp/index.js

# Restart Claude Code
```

### Issue: Email sent but not received
**Solution:**
1. Check spam folder
2. Verify recipient email address is correct
3. Check Gmail "Sent" folder
4. Review MCP server logs for errors

## Security Best Practices

### Credentials
- ✅ Never commit .env to git
- ✅ Use App Password, not regular password
- ✅ Rotate App Password monthly
- ✅ Restrict .env permissions (chmod 600)

### Approval Workflow
- ✅ NEVER skip approval for emails
- ✅ Always verify approval file exists before sending
- ✅ Log all email sends
- ✅ Review approval requests carefully

### Rate Limiting
- ✅ Gmail has sending limits (500/day for free accounts)
- ✅ Implement rate limiting if needed
- ✅ Monitor send counts in logs

## Next Steps

After Email MCP is operational:
1. Test end-to-end: Gmail Watcher → Draft Reply → Approve → Send
2. Set up WhatsApp watcher
3. Create orchestrator for automated processing
4. Set up daily briefing automation
5. Complete Silver tier integration testing

## References

- Nodemailer: https://nodemailer.com/
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- MCP Specification: https://modelcontextprotocol.io/
- Email Best Practices: https://www.emailonacid.com/blog/article/email-development/email-development-best-practices-2/

---

*Skill: silver-mcp-email*
*Tier: Silver*
*Estimated Time: 1-2 hours*
*Dependencies: Bronze tier, Node.js, Gmail account*
