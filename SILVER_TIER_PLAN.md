---
tier: Silver
status: Starting
estimated_time: 20-30 hours
phase: Planning and Implementation
created: 2026-02-06
---

# Silver Tier Implementation Plan

## 🎯 Objective

Transform the Bronze tier foundation into a **Functional AI Assistant** by adding multiple watchers, MCP servers, and automated workflows.

---

## 📋 Silver Tier Requirements (from Hackathon)

### Must-Have Deliverables
1. ✅ All Bronze requirements (COMPLETE)
2. ⏳ **Two or more watchers** (Gmail + WhatsApp/LinkedIn)
3. ⏳ **Automatically post on LinkedIn** about business to generate sales
4. ⏳ **Claude reasoning loop** that creates Plan.md files (already working ✅)
5. ⏳ **One working MCP server** for external action (e.g., sending emails)
6. ⏳ **Human-in-the-loop approval workflow** (already working ✅)
7. ⏳ **Basic scheduling** via cron or Task Scheduler
8. ✅ **All AI functionality as Agent Skills**

---

## 🗺️ Implementation Roadmap

### Phase 1: Gmail Watcher (Priority: HIGH) ⏰ 5-7 hours
**Why First:** Most valuable for business - email is critical communication channel

**Tasks:**
1. Set up Google Cloud Console project
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download credentials.json
5. Implement gmail_watcher.py (code already exists in repo)
6. Test authentication flow
7. Run with PM2 for continuous operation
8. Verify integration with vault

**Acceptance Criteria:**
- Gmail watcher detects important/unread emails
- Creates action files in /Needs_Action/
- Proper frontmatter with email metadata
- Logs activity to /Logs/
- Runs continuously via PM2

**Blockers to Resolve:**
- Need Google Cloud account (free tier OK)
- Need Gmail API credentials (requires setup)

---

### Phase 2: LinkedIn Auto-Posting (Priority: HIGH) ⏰ 6-8 hours
**Why Important:** Generates sales leads, required for Silver tier

**Approach:**
LinkedIn's official API has restrictions. We'll use one of:
- **Option A:** LinkedIn API (if you have access)
- **Option B:** Playwright automation (web scraping - use carefully)
- **Option C:** RSS-to-LinkedIn service (Zapier/IFTTT as bridge)

**Recommended:** Option B (Playwright) for hackathon demo

**Tasks:**
1. Create linkedin_poster.py using Playwright
2. Implement session management (persistent auth)
3. Create posting templates in vault
4. Build MCP server for LinkedIn posting
5. Add approval workflow for posts
6. Create scheduled job (daily/weekly)
7. Test with sample business posts

**Post Templates Location:** `/AI_Employee_Vault/Templates/LinkedIn/`

**Acceptance Criteria:**
- Can draft LinkedIn posts autonomously
- Posts require HITL approval (per constitution)
- Scheduled posting works (cron/Task Scheduler)
- Activity logged to Dashboard
- Template-based content generation

---

### Phase 3: Email MCP Server (Priority: HIGH) ⏰ 5-7 hours
**Why Critical:** Enables autonomous email sending (with approval)

**Architecture:**
```
Claude → MCP Email Server → SMTP/Gmail API → Recipient
         (after HITL approval)
```

**Tasks:**
1. Create email-mcp-server/ directory
2. Implement Node.js MCP server
3. Add SMTP configuration (Gmail SMTP or API)
4. Implement send_email tool
5. Add draft_email tool
6. Configure Claude Code to use MCP server
7. Test approval → send workflow

**MCP Configuration:** `~/.config/claude-code/mcp.json`

**Acceptance Criteria:**
- MCP server starts successfully
- Claude can invoke send_email tool
- Email sent only after approval
- Sends tracked in logs
- Error handling for failed sends

---

### Phase 4: WhatsApp Watcher (Priority: MEDIUM) ⏰ 7-10 hours
**Why Later:** More complex, requires Playwright, careful with ToS

**Approach:** WhatsApp Web automation via Playwright

**Tasks:**
1. Install Playwright with chromium
2. Create whatsapp_watcher.py
3. Implement session persistence
4. Configure keyword detection
5. Test QR code authentication
6. Verify message detection
7. Run with PM2

**Keywords to Monitor:** 'urgent', 'asap', 'invoice', 'payment', 'help'

**Acceptance Criteria:**
- Detects unread WhatsApp messages
- Filters by keywords
- Creates action files
- Session persists across restarts
- Runs continuously

**Risk:** WhatsApp may detect automation - use carefully, test with personal account first

---

### Phase 5: Scheduling & Orchestration (Priority: MEDIUM) ⏰ 3-4 hours
**Why:** Enables daily briefings, periodic tasks

**Tasks:**
1. Create orchestrator.py (master controller)
2. Set up cron jobs (Linux/Mac) or Task Scheduler (Windows)
3. Implement daily briefing generation
4. Add periodic vault cleanup
5. Create health check routine
6. Test scheduled operations

**Scheduled Tasks:**
- **Daily 8:00 AM:** Morning briefing
- **Every 2 hours:** Process /Needs_Action/
- **Daily 11:00 PM:** End-of-day summary
- **Weekly Sunday:** Business audit prep

**Acceptance Criteria:**
- Scheduler triggers Claude at specified times
- Briefings generated automatically
- No missed scheduled runs
- Logs all scheduled executions

---

### Phase 6: Additional Skills (Priority: LOW) ⏰ 2-3 hours
**Why:** Complete Silver tier requirements

**New Skills to Create:**
1. `/silver-gmail-setup` - Gmail watcher setup guide
2. `/silver-linkedin-poster` - LinkedIn automation setup
3. `/silver-mcp-email` - Email MCP server setup
4. `/silver-scheduler` - Scheduling configuration
5. `/silver-demo` - Silver tier demo video script

---

## 🔧 Technical Implementation Details

### Gmail Watcher Setup

**Google Cloud Console Steps:**
```bash
# 1. Go to https://console.cloud.google.com/
# 2. Create new project: "AI-Employee-Silver"
# 3. Enable Gmail API:
#    - APIs & Services → Library → Search "Gmail API" → Enable
# 4. Create credentials:
#    - APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
#    - Application type: Desktop app
#    - Name: "AI Employee Gmail Watcher"
#    - Download credentials.json
# 5. Save to: /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials/
```

**Install Dependencies:**
```bash
pip install --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**Run First Time (Authentication):**
```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python gmail_watcher.py \
  /mnt/d/Ai-Employee/AI_Employee_Vault \
  credentials/credentials.json
# Browser will open for OAuth - grant access
# token.json will be created for future use
```

**Run with PM2:**
```bash
pm2 start gmail_watcher.py \
  --name "ai-employee-gmail" \
  --interpreter python3 \
  -- /mnt/d/Ai-Employee/AI_Employee_Vault credentials/credentials.json

pm2 save
pm2 logs ai-employee-gmail
```

---

### LinkedIn Poster (Playwright Approach)

**Install Playwright:**
```bash
pip install playwright
playwright install chromium
```

**Create Script:**
```python
# linkedin_poster.py
from playwright.sync_api import sync_playwright
from pathlib import Path
import json
from datetime import datetime

class LinkedInPoster:
    def __init__(self, session_path: str):
        self.session_path = Path(session_path)

    def authenticate(self):
        # Persistent browser session
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                self.session_path,
                headless=False  # Show browser first time
            )
            page = browser.pages[0]
            page.goto('https://www.linkedin.com/login')
            # Manual login first time
            input('Press Enter after logging in...')
            browser.close()

    def create_post(self, content: str, image_path: str = None):
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                self.session_path,
                headless=True
            )
            page = browser.pages[0]
            page.goto('https://www.linkedin.com/feed/')

            # Click "Start a post"
            page.click('button[aria-label="Start a post"]')

            # Type content
            page.fill('div[role="textbox"]', content)

            # Optional: Upload image
            if image_path:
                page.set_input_files('input[type="file"]', image_path)

            # Note: Don't click Post - require approval
            # Save draft instead

            browser.close()

    def post_with_approval(self, approval_file: Path):
        # Read approved content
        content = approval_file.read_text()
        # Extract content from approval file
        # Post to LinkedIn
        # Log result
        pass
```

---

### Email MCP Server Setup

**Directory Structure:**
```
/mnt/d/Ai-Employee/AI_Employee_Vault/MCP_Servers/
└── email-mcp/
    ├── package.json
    ├── index.js
    └── README.md
```

**package.json:**
```json
{
  "name": "email-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@anthropic-ai/sdk": "^0.20.0",
    "nodemailer": "^6.9.0"
  }
}
```

**index.js:**
```javascript
#!/usr/bin/env node
import { Server } from '@anthropic-ai/sdk/mcp';
import nodemailer from 'nodemailer';

const server = new Server({
  name: 'email-mcp-server',
  version: '1.0.0'
});

// Configure SMTP
const transporter = nodemailer.createTransporter({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_APP_PASSWORD
  }
});

// Define send_email tool
server.tool('send_email', {
  description: 'Send an email (requires prior approval)',
  input_schema: {
    type: 'object',
    properties: {
      to: { type: 'string', description: 'Recipient email' },
      subject: { type: 'string', description: 'Email subject' },
      body: { type: 'string', description: 'Email body' },
      approval_id: { type: 'string', description: 'Approval request ID' }
    },
    required: ['to', 'subject', 'body', 'approval_id']
  },
  handler: async (input) => {
    // Verify approval exists in /Approved/ folder
    // Send email
    // Log to /Logs/
    // Return success/failure
  }
});

server.start();
```

**Claude Code MCP Configuration:**
```json
// ~/.config/claude-code/mcp.json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/mnt/d/Ai-Employee/AI_Employee_Vault/MCP_Servers/email-mcp/index.js"],
      "env": {
        "EMAIL_USER": "your-email@gmail.com",
        "EMAIL_APP_PASSWORD": "your-app-password"
      }
    }
  ]
}
```

---

### Orchestrator (Master Controller)

**Purpose:** Automatically trigger Claude when new files appear

```python
# orchestrator.py
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import logging

class OrchestratorHandler(FileSystemEventHandler):
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.needs_action = vault_path / 'Needs_Action'

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return

        # New action file detected
        logging.info(f'New action detected: {event.src_path}')

        # Trigger Claude to process
        self.trigger_claude()

    def trigger_claude(self):
        # Call Claude to process Needs_Action folder
        cmd = [
            'claude',
            'Process all new items in Needs_Action/ folder. Create plans, identify approvals needed, update Dashboard.'
        ]
        subprocess.run(cmd, cwd=str(self.vault_path))

# Run orchestrator
if __name__ == '__main__':
    vault_path = Path('/mnt/d/Ai-Employee/AI_Employee_Vault')
    handler = OrchestratorHandler(vault_path)
    observer = Observer()
    observer.schedule(handler, str(vault_path / 'Needs_Action'), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

---

## 📊 Implementation Priority Order

### Week 1 (High Priority)
1. **Gmail Watcher** (Day 1-2) - Most valuable
2. **Email MCP Server** (Day 3-4) - Enables autonomous email
3. **LinkedIn Poster** (Day 5-7) - Required for Silver tier

### Week 2 (Medium Priority)
4. **WhatsApp Watcher** (Day 8-10) - More complex
5. **Scheduling** (Day 11-12) - Automated operations
6. **Orchestrator** (Day 13) - Glue everything together

### Week 3 (Finalization)
7. **Skills Documentation** (Day 14-15)
8. **Integration Testing** (Day 16-17)
9. **Demo Video** (Day 18-19)
10. **Submission** (Day 20)

---

## 🎯 Success Criteria

### Silver Tier Complete When:
- [ ] Gmail watcher operational (continuous monitoring)
- [ ] LinkedIn auto-posting works (with approval)
- [ ] Email MCP server functional (approved emails sent)
- [ ] WhatsApp watcher operational (keyword detection)
- [ ] Scheduling working (daily briefings)
- [ ] Orchestrator triggers Claude automatically
- [ ] All functionality as Agent Skills
- [ ] Integration test passed (all components working together)
- [ ] Demo video recorded (10-15 minutes)
- [ ] Documentation complete

---

## 🚧 Potential Blockers

### Technical Blockers
1. **Gmail API:** Requires Google Cloud account (free tier OK)
2. **LinkedIn:** May require manual authentication, API restrictions
3. **WhatsApp:** May detect automation, use carefully
4. **MCP Server:** Requires Node.js knowledge

### Solutions:
- Gmail: Follow Google Cloud setup guide
- LinkedIn: Use Playwright for automation (hackathon context)
- WhatsApp: Test with personal account first, lower frequency
- MCP: Use provided template code, test incrementally

---

## 📝 Next Immediate Steps

### Right Now (Next 30 minutes):
1. Create skills for Silver tier
2. Set up Gmail API project
3. Download credentials.json
4. Test gmail_watcher.py

### Today (Next 4-6 hours):
1. Get Gmail watcher running with PM2
2. Create email MCP server structure
3. Test email send workflow
4. Begin LinkedIn poster implementation

### This Week:
1. Complete all Silver tier watchers
2. Integration testing
3. Create orchestrator
4. Set up scheduling

---

## 🎓 Learning Resources

- Gmail API: https://developers.google.com/gmail/api/quickstart/python
- MCP Servers: https://modelcontextprotocol.io/quickstart
- Playwright: https://playwright.dev/python/docs/intro
- PM2: https://pm2.keymetrics.io/docs/usage/quick-start/
- Cron: https://crontab.guru/

---

## 🎬 Demo Video Plan (Silver Tier)

**Length:** 10-15 minutes

**Content:**
1. Recap Bronze (1 min)
2. Gmail watcher demo (2 min)
3. LinkedIn posting demo (3 min)
4. Email MCP server demo (2 min)
5. WhatsApp watcher demo (2 min)
6. Orchestrator & scheduling (2 min)
7. Dashboard showing all components (2 min)
8. Conclusion (1 min)

---

**Status:** Ready to begin Silver tier implementation
**First Task:** Set up Gmail API and get credentials
**Estimated Completion:** 2-3 weeks (20-30 hours)

---

*Silver Tier Plan by Claude AI Employee*
*Date: 2026-02-06*
*Based on Hackathon Requirements and Constitution Principles*
