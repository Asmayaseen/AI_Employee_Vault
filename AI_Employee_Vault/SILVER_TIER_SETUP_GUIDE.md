# Silver Tier Setup Guide
## AI Employee - Complete Implementation Guide

**Status:** ✅ Implementation Complete - Ready for Setup
**Date:** 2026-02-07
**Tier:** Silver Tier (Functional Assistant)

---

## 🎯 What You Have

Your AI Employee is fully implemented for Silver Tier! Here's what's ready:

### Components Built ✅

| Component | Status | File | Purpose |
|-----------|--------|------|---------|
| **Base Watcher** | ✅ | `base_watcher.py` | Foundation for all watchers |
| **FileSystem Watcher** | ✅ | `filesystem_watcher.py` | Monitors Inbox folder |
| **Gmail Watcher** | ✅ | `gmail_watcher.py` | Monitors email |
| **WhatsApp Watcher** | ✅ | `whatsapp_watcher.py` | Monitors WhatsApp messages |
| **LinkedIn Watcher** | ✅ | `linkedin_watcher.py` | Monitors LinkedIn + auto-posting |
| **Orchestrator** | ✅ | `orchestrator.py` | Manages all watchers |
| **Approval Watcher** | ✅ | `approval_watcher.py` | HITL workflow |
| **Claude Processor** | ✅ | `claude_processor.py` | Reasoning loop + Plans |
| **Scheduler** | ✅ | `scheduler.py` | Cron/Task Scheduler |
| **Email MCP** | ✅ | `email_mcp.py` | Send emails via Gmail |

### Silver Tier Requirements ✅

- [x] Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn) ✅ **3 watchers**
- [x] Automatically Post on LinkedIn about business to generate sales ✅ **linkedin_watcher.py has auto-posting**
- [x] Claude reasoning loop that creates Plan.md files ✅ **claude_processor.py**
- [x] One working MCP server for external action (e.g., sending emails) ✅ **email_mcp.py**
- [x] Human-in-the-loop approval workflow for sensitive actions ✅ **approval_watcher.py**
- [x] Basic scheduling via cron or Task Scheduler ✅ **scheduler.py**
- [x] All AI functionality should be implemented as Agent Skills ✅ **See .claude/skills/**

---

## 📋 Setup Steps (30-60 minutes)

### Step 1: Install Dependencies (5 minutes)

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 2: Configure Environment (10 minutes)

Your `.env` file already exists. Update it with your actual credentials:

```bash
# Edit the .env file
nano /mnt/d/Ai-Employee/AI_Employee_Vault/.env
```

**Required updates:**
```env
# Change from true to false when ready for production
DRY_RUN=true  # Keep as 'true' for testing, change to 'false' for live actions

# Gmail API (after you get credentials from Google Cloud)
GMAIL_CLIENT_ID=your_actual_client_id
GMAIL_CLIENT_SECRET=your_actual_client_secret

# Your contact info (already filled)
USER_EMAIL=asmayaseen9960@gmail.com
USER_NAME=Asma Yaseen
```

### Step 3: Gmail API Setup (15 minutes)

**You need Google Cloud credentials to enable Gmail integration.**

#### 3.1 Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Project name: `AI-Employee-Silver`
4. Click "Create"

#### 3.2 Enable Gmail API

1. In Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Enable"

#### 3.3 Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. If prompted, configure consent screen:
   - Click "Configure Consent Screen"
   - Select "External"
   - App name: `AI Employee Gmail Watcher`
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue" through all screens
   - Add your Gmail address as a test user
3. Click "Create Credentials" → "OAuth client ID"
4. Application type: "Desktop app"
5. Name: `AI Employee Desktop`
6. Click "Create"
7. **Download JSON** - save as `credentials.json`

#### 3.4 Place Credentials

```bash
# Create credentials directory
mkdir -p /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials

# Move the downloaded file (adjust path to your download location)
mv ~/Downloads/credentials.json /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials/
```

### Step 4: Test Individual Watchers (20 minutes)

#### 4.1 Test FileSystem Watcher

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Start filesystem watcher (monitors Inbox folder)
python filesystem_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault
```

**In another terminal:**
```bash
# Create a test file
echo "Test client request" > /mnt/d/Ai-Employee/AI_Employee_Vault/Inbox/test_request.txt
```

**Expected:** Watcher detects file and creates action item in `Needs_Action/`

Press Ctrl+C to stop the watcher.

#### 4.2 Test Gmail Watcher (First-time authentication)

```bash
# Run gmail watcher (will open browser for OAuth)
python gmail_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials/credentials.json
```

**What happens:**
1. Browser opens automatically
2. Select your Google account
3. Warning appears: "Google hasn't verified this app"
   - Click "Advanced"
   - Click "Go to AI Employee (unsafe)" - this is safe, it's YOUR app
4. Click "Allow" for Gmail permissions
5. Terminal shows: "Gmail API authenticated successfully"
6. Token saved to `token.json`

**Test:** Send yourself an email to verify detection.

Press Ctrl+C to stop.

#### 4.3 Test WhatsApp Watcher (QR Code Scan)

```bash
# Run WhatsApp watcher (will show QR code)
python whatsapp_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault
```

**What happens:**
1. Browser opens (not headless on first run)
2. WhatsApp Web loads
3. Scan QR code with your phone
4. Session saved to `.whatsapp_session`
5. Watcher starts monitoring

Press Ctrl+C to stop.

#### 4.4 Test LinkedIn Watcher (Login)

```bash
# Run LinkedIn watcher (will prompt for login)
python linkedin_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault
```

**What happens:**
1. Browser opens
2. Login to LinkedIn
3. Session saved to `.linkedin_session`
4. Watcher starts monitoring

Press Ctrl+C to stop.

---

## 🚀 Running the Full System

### Option A: Start All Watchers with Orchestrator (Recommended)

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Start orchestrator (manages all watchers)
python orchestrator.py
```

**This will:**
- Start all enabled watchers
- Monitor their health
- Auto-restart if they crash
- Coordinate between watchers

**View logs:**
```bash
# Watch orchestrator log
tail -f orchestrator.log

# Watch individual watcher logs
tail -f filesystem_watcher.log
tail -f gmail_watcher.log
```

### Option B: Use PM2 for Always-On Operation

```bash
# Install PM2 globally
npm install -g pm2

# Start orchestrator with PM2
pm2 start orchestrator.py --name "ai-employee" --interpreter python3

# Save PM2 configuration
pm2 save

# Set PM2 to start on boot
pm2 startup
# Follow the command it outputs

# View status
pm2 status

# View logs
pm2 logs ai-employee

# Stop
pm2 stop ai-employee

# Restart
pm2 restart ai-employee
```

---

## 🧪 Testing the Complete Workflow

### Test 1: Email Processing

1. **Send yourself an email** with subject: "Invoice Request - Test"
2. **Wait 2 minutes** (Gmail watcher check interval)
3. **Check Needs_Action folder:**
   ```bash
   ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Needs_Action/
   ```
4. **Process with Claude:**
   ```bash
   cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
   python claude_processor.py --process-all
   ```
5. **Check Plans folder:**
   ```bash
   ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Plans/
   ```
6. **Check Pending_Approval folder:**
   ```bash
   ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Pending_Approval/
   ```

### Test 2: File Drop Processing

1. **Drop a file in Inbox:**
   ```bash
   echo "New client inquiry about services" > /mnt/d/Ai-Employee/AI_Employee_Vault/Inbox/client_inquiry.txt
   ```
2. **Watcher detects instantly** (if orchestrator running)
3. **Process:**
   ```bash
   python claude_processor.py --process-all
   ```

### Test 3: Approval Workflow

1. **Find approval request** in `Pending_Approval/`
2. **Review the file** (open in Obsidian or text editor)
3. **To approve:** Move file to `Approved/` folder
   ```bash
   mv /mnt/d/Ai-Employee/AI_Employee_Vault/Pending_Approval/EMAIL_*.md /mnt/d/Ai-Employee/AI_Employee_Vault/Approved/
   ```
4. **Approval watcher** will detect and execute the action
5. **Check logs:**
   ```bash
   cat /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
   ```

---

## 📊 Scheduling (Automated Daily Briefings)

### Setup Daily Briefing

The scheduler can run automated tasks like daily briefings.

#### Option 1: Built-in Scheduler

```bash
# Run scheduler (runs in foreground)
python scheduler.py --run
```

**Or with PM2:**
```bash
pm2 start scheduler.py --name "ai-scheduler" --interpreter python3
pm2 save
```

#### Option 2: System Cron (Linux/Mac)

```bash
# Generate crontab entries
python scheduler.py --generate-cron

# Example output:
# 0 8 * * * cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers && python claude_processor.py --briefing

# Add to your crontab
crontab -e
# Paste the generated lines
```

#### Option 3: Windows Task Scheduler

```bash
# Generate Task Scheduler commands
python scheduler.py --generate-windows

# Follow the instructions to create scheduled tasks
```

---

## 📁 Folder Structure (What Each Folder Does)

```
AI_Employee_Vault/
├── Inbox/                    # Drop files here (watched by filesystem_watcher)
├── Needs_Action/            # New items detected by watchers (read by claude_processor)
├── Plans/                   # Generated plans with action steps (created by claude_processor)
├── Pending_Approval/        # Actions requiring human approval (watched by approval_watcher)
├── Approved/                # Approved actions (executed by approval_watcher → MCP)
├── Rejected/                # Rejected actions (archived)
├── Done/                    # Completed actions (archived)
├── Logs/                    # JSON audit logs by date
├── Briefings/               # Daily/weekly CEO briefings
├── Dashboard.md             # Real-time status dashboard
├── Company_Handbook.md      # Rules and policies
├── Business_Goals.md        # KPIs and objectives
└── Watchers/
    ├── *.py                 # All watcher scripts
    ├── requirements.txt     # Python dependencies
    ├── .env                 # Your credentials (DO NOT COMMIT)
    ├── credentials/         # Gmail OAuth credentials
    └── MCP_Servers/
        └── email_mcp.py     # Email sending capability
```

---

## 🔍 Verification Checklist

### Before Going Live

- [ ] All dependencies installed (`pip list | grep google-api-python-client`)
- [ ] Gmail credentials configured and authenticated (check for `token.json`)
- [ ] WhatsApp session saved (check for `.whatsapp_session` folder)
- [ ] LinkedIn session saved (check for `.linkedin_session` folder)
- [ ] `.env` file configured with correct paths
- [ ] Test email processed successfully
- [ ] Test file drop processed successfully
- [ ] Approval workflow tested (move file to Approved and verify action)
- [ ] Logs being created in `/Logs/` folder
- [ ] Dashboard.md updating with recent activity

### Security Checks

- [ ] `.env` file is NOT committed to git (check `.gitignore`)
- [ ] `DRY_RUN=true` for initial testing
- [ ] All sensitive credentials in `.env`, not hardcoded
- [ ] Approval workflow working for emails and payments
- [ ] Rate limits configured in `.env`

---

## 🎓 Usage Guide

### Daily Operations

**Morning:**
```bash
# Generate morning briefing
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python claude_processor.py --briefing

# View dashboard
cat /mnt/d/Ai-Employee/AI_Employee_Vault/Dashboard.md
```

**Check for pending actions:**
```bash
# Process all pending items
python claude_processor.py --process-all

# Check what needs approval
ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Pending_Approval/
```

**Review logs:**
```bash
# Today's activity
cat /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq
```

### Obsidian Integration

1. **Open Obsidian**
2. **Open vault:** `/mnt/d/Ai-Employee/AI_Employee_Vault`
3. **View Dashboard.md** for real-time status
4. **Navigate folders** in file explorer
5. **Review approval requests** by opening files in `Pending_Approval/`
6. **Drag to approve:** Drag file from `Pending_Approval/` to `Approved/`

---

## 🐛 Troubleshooting

### Gmail Watcher Issues

**Problem:** "credentials.json not found"
```bash
# Check if credentials exist
ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials/credentials.json

# If missing, download from Google Cloud Console
```

**Problem:** "Token expired"
```bash
# Delete old token and re-authenticate
rm /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/token.json
python gmail_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials/credentials.json
```

### WhatsApp Watcher Issues

**Problem:** "Session expired" or "Not logged in"
```bash
# Delete old session and re-scan QR
rm -rf /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/.whatsapp_session
python whatsapp_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault
```

### LinkedIn Watcher Issues

**Problem:** "Login required"
```bash
# Delete session and re-login
rm -rf /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/.linkedin_session
python linkedin_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault
```

### Orchestrator Issues

**Problem:** Watchers not starting
```bash
# Check orchestrator logs
tail -f /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/orchestrator.log

# Check if required environment variables are set
cat /mnt/d/Ai-Employee/AI_Employee_Vault/.env

# Manually test each watcher
python filesystem_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault
```

### Claude Processor Issues

**Problem:** Not generating plans
```bash
# Check if items exist in Needs_Action
ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Needs_Action/

# Check handbook exists
cat /mnt/d/Ai-Employee/AI_Employee_Vault/Company_Handbook.md

# Run with debug
python claude_processor.py --process-all --verbose
```

---

## 🚦 Next Steps (Gold Tier)

Once Silver Tier is running smoothly, you can progress to Gold Tier:

- [ ] Odoo Community Edition integration (accounting)
- [ ] Facebook/Instagram integration
- [ ] Twitter (X) integration
- [ ] Weekly CEO Briefing with financial analysis
- [ ] Ralph Wiggum loop (autonomous multi-step completion)
- [ ] Comprehensive error recovery system

---

## 📞 Support & Resources

- **Hackathon Document:** `/mnt/d/Ai-Employee/0-hackathon.md`
- **Constitution:** `/mnt/d/Ai-Employee/.specify/memory/constitution.md`
- **Skills:** `/mnt/d/Ai-Employee/.claude/skills/`
- **Weekly Meeting:** Wednesdays 10:00 PM (check hackathon doc for link)

---

## ✅ Silver Tier Completion Checklist

Mark these when complete:

- [ ] All dependencies installed
- [ ] Gmail authenticated and working
- [ ] WhatsApp authenticated and monitoring
- [ ] LinkedIn authenticated and monitoring
- [ ] Orchestrator running all watchers
- [ ] Claude processor generating plans
- [ ] Approval workflow tested
- [ ] Email MCP sending emails (in dry-run)
- [ ] Scheduler configured
- [ ] Daily briefing tested
- [ ] Documentation complete
- [ ] Demo video recorded (5-10 minutes)

**When all checked, Silver Tier is COMPLETE! 🎉**

---

*Generated: 2026-02-07*
*Your AI Employee is ready to work!*
