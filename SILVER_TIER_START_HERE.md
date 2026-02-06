---
tier: Silver
status: Ready to Implement
created: 2026-02-06
estimated_time: 20-30 hours
---

# 🚀 Silver Tier - START HERE

## 📊 Current Status

✅ **Bronze Tier:** COMPLETE (100%)
🔄 **Silver Tier:** READY TO START (0%)

## 🎯 Quick Start Guide

### What You're Building

Transform your Bronze tier AI Employee into a **Functional AI Assistant** with:
- **Gmail monitoring** (continuous email detection)
- **LinkedIn auto-posting** (generate sales leads)
- **Email automation** (autonomous sending with approval)
- **WhatsApp monitoring** (urgent message detection)
- **Scheduling** (daily briefings, automated tasks)

### Time Investment

- **Minimum:** 20 hours (core features)
- **Recommended:** 25-30 hours (polished implementation)
- **Timeline:** 2-3 weeks (part-time) or 1 week (full-time)

---

## 🗺️ Implementation Roadmap

### Phase 1: Gmail Watcher (Day 1-2) ⏰ 5-7 hours

**Priority: HIGHEST** - Most valuable for business

#### What to Do:
```bash
# 1. Read the skill
cat /mnt/d/Ai-Employee/.claude/skills/silver-gmail-setup.md

# 2. Set up Google Cloud Console (15 min)
# - Go to https://console.cloud.google.com/
# - Create project: "AI-Employee-Silver"
# - Enable Gmail API
# - Create OAuth 2.0 credentials
# - Download credentials.json

# 3. Install dependencies (2 min)
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 4. Set up credentials (5 min)
mkdir -p /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials
# Move credentials.json to this directory

# 5. Authenticate (5 min)
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python gmail_watcher.py \
  /mnt/d/Ai-Employee/AI_Employee_Vault \
  credentials/credentials.json
# Browser opens → Login → Grant permissions

# 6. Test detection (10 min)
# Send yourself a test email marked "Important"
# Watch watcher create action file in Needs_Action/

# 7. Deploy with PM2 (10 min)
pm2 start gmail_watcher.py \
  --name "ai-employee-gmail" \
  --interpreter python3 \
  -- /mnt/d/Ai-Employee/AI_Employee_Vault credentials/credentials.json

pm2 save
pm2 logs ai-employee-gmail

# 8. Test with Claude (30 min)
claude "Check Needs_Action for new emails and create response plans"
```

**Success Criteria:**
- [ ] Gmail API enabled
- [ ] OAuth authentication successful
- [ ] Test email detected
- [ ] Action file created in Needs_Action/
- [ ] PM2 deployment working
- [ ] Claude processes emails successfully

---

### Phase 2: Email MCP Server (Day 3-4) ⏰ 5-7 hours

**Priority: HIGH** - Enables autonomous email sending

#### What to Do:
```bash
# 1. Read the skill
cat /mnt/d/Ai-Employee/.claude/skills/silver-mcp-email.md

# 2. Get Gmail App Password (10 min)
# - Go to https://myaccount.google.com/security
# - Enable 2-Step Verification
# - Generate App Password for "AI Employee"
# - Copy 16-character password

# 3. Configure .env (5 min)
cd /mnt/d/Ai-Employee/AI_Employee_Vault
cat >> .env << 'EOF'
EMAIL_USER=your-email@gmail.com
EMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
EOF

chmod 600 .env

# 4. Create MCP server (30 min)
mkdir -p MCP_Servers/email-mcp
cd MCP_Servers/email-mcp
npm init -y
npm install nodemailer dotenv
# Copy index.js code from skill

# 5. Test MCP server (20 min)
node index.js
# Should show: ✅ Email MCP Server ready

# 6. Configure Claude Code (10 min)
mkdir -p ~/.config/claude-code
# Create mcp.json (see skill for template)

# 7. Test with Claude (1 hour)
cd /mnt/d/Ai-Employee/AI_Employee_Vault
claude "Draft an email to test@example.com with subject 'Test' and body 'This is a test'"

# Review in Pending_Approval/
# Move to Approved/
claude "Send approved emails"
# Check your inbox
```

**Success Criteria:**
- [ ] Gmail App Password obtained
- [ ] .env configured
- [ ] MCP server created and tested
- [ ] Claude Code MCP config complete
- [ ] Draft email works
- [ ] Approval workflow works
- [ ] Send email works
- [ ] Email received

---

### Phase 3: LinkedIn Auto-Posting (Day 5-7) ⏰ 6-8 hours

**Priority: MEDIUM-HIGH** - Required for Silver tier, generates leads

#### What to Do:
```bash
# 1. Read the skill
cat /mnt/d/Ai-Employee/.claude/skills/silver-linkedin-poster.md

# 2. Install Playwright (10 min)
pip install playwright
playwright install chromium

# 3. Create LinkedIn poster script (1 hour)
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
# Copy linkedin_poster.py code from skill
chmod +x linkedin_poster.py

# 4. Authenticate (15 min)
python linkedin_poster.py auth
# Browser opens → Login to LinkedIn
# Press Enter after logged in

# 5. Create test draft (10 min)
python linkedin_poster.py draft "🎯 Test post from AI Employee! #AI #Automation"

# Review in Pending_Approval/

# 6. Test posting (20 min)
# Move draft to Approved/
python linkedin_poster.py check
# Verify post appears on LinkedIn

# 7. Set up scheduling (30 min)
# Option A: Cron (Linux/Mac)
crontab -e
# Add: 0 9,15 * * * cd /path && python linkedin_poster.py check

# Option B: PM2
# Create linkedin_scheduler.py (see skill)
pm2 start linkedin_scheduler.py --name "ai-employee-linkedin"

# 8. Test with Claude (1 hour)
claude "Generate a professional LinkedIn post about our business progress this week"
```

**Success Criteria:**
- [ ] Playwright installed
- [ ] LinkedIn authentication successful
- [ ] Test post created
- [ ] Test post published to LinkedIn
- [ ] Scheduling configured
- [ ] Claude can generate posts
- [ ] Approval workflow functional

---

### Phase 4: WhatsApp Watcher (Day 8-10) ⏰ 7-10 hours

**Priority: MEDIUM** - More complex, careful with Terms of Service

#### What to Do:
```bash
# 1. Use watcher-setup skill
cat /mnt/d/Ai-Employee/.claude/skills/watcher-setup.md
# Look for WhatsApp Watcher section

# 2. Install Playwright (if not done)
pip install playwright
playwright install chromium

# 3. Create whatsapp_watcher.py
# Copy code from watcher-setup skill

# 4. Authenticate (QR code)
python whatsapp_watcher.py \
  /mnt/d/Ai-Employee/AI_Employee_Vault \
  whatsapp_session
# Scan QR code with phone

# 5. Configure keywords
# Edit whatsapp_watcher.py
# Keywords: ['urgent', 'asap', 'invoice', 'payment', 'help']

# 6. Test detection
# Send yourself WhatsApp with keyword "urgent"
# Watch for action file creation

# 7. Deploy with PM2
pm2 start whatsapp_watcher.py \
  --name "ai-employee-whatsapp" \
  --interpreter python3

# 8. Monitor and adjust
pm2 logs ai-employee-whatsapp
```

**Success Criteria:**
- [ ] WhatsApp Web automation working
- [ ] Session persists
- [ ] Keywords detected
- [ ] Action files created
- [ ] PM2 deployment stable
- [ ] No ToS violations (reasonable frequency)

---

### Phase 5: Orchestrator & Scheduling (Day 11-13) ⏰ 5-6 hours

**Priority: MEDIUM** - Glues everything together

#### What to Do:
```bash
# 1. Create orchestrator.py
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
# See SILVER_TIER_PLAN.md for orchestrator code

# 2. Test orchestrator
python orchestrator.py
# Drop test file in Inbox/
# Watch orchestrator trigger Claude automatically

# 3. Set up scheduled tasks
# Daily 8 AM briefing:
crontab -e
# Add:
0 8 * * * cd /mnt/d/Ai-Employee/AI_Employee_Vault && claude "Generate morning briefing"

# 4. Create briefing script
cat > /mnt/d/Ai-Employee/AI_Employee_Vault/Scripts/morning_briefing.sh << 'EOF'
#!/bin/bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault
claude "Read Dashboard, Business_Goals, and recent activity. Create a morning briefing in Briefings/ folder."
EOF
chmod +x Scripts/morning_briefing.sh

# 5. Test scheduled briefing
./Scripts/morning_briefing.sh
# Check Briefings/ folder
```

**Success Criteria:**
- [ ] Orchestrator auto-triggers Claude
- [ ] Daily briefing scheduled
- [ ] Briefings generated automatically
- [ ] All components working together

---

## 🎯 Silver Tier Checklist

### Core Requirements (Must-Have)
- [ ] Gmail watcher operational (continuous monitoring)
- [ ] LinkedIn auto-posting working (with approval)
- [ ] Email MCP server functional (send approved emails)
- [ ] Orchestrator triggers Claude automatically
- [ ] Basic scheduling (daily briefings)
- [ ] All functionality as Agent Skills ✅ (skills created)
- [ ] HITL approval workflow (already working ✅)
- [ ] Claude reasoning loop (already working ✅)

### Optional (Nice-to-Have)
- [ ] WhatsApp watcher operational
- [ ] Weekly business reports
- [ ] Advanced scheduling (multiple daily tasks)

---

## 📊 Progress Tracking

Update Dashboard.md as you complete each phase:

```markdown
## Silver Tier Progress
- [x] Gmail Watcher - COMPLETE
- [ ] Email MCP Server - IN PROGRESS
- [ ] LinkedIn Poster - TODO
- [ ] WhatsApp Watcher - TODO
- [ ] Orchestrator - TODO
```

---

## 🎬 When You're Done

### Integration Testing (2-3 hours)

Test complete workflow:

```bash
# 1. Send yourself an email asking for something
# 2. Gmail watcher detects (2 min)
# 3. Claude creates plan
# 4. Claude drafts response via MCP
# 5. You approve in Pending_Approval/
# 6. Claude sends via MCP
# 7. Verify email received

# Test LinkedIn workflow:
# 1. Claude generates post
# 2. Draft in Pending_Approval/
# 3. You approve
# 4. Scheduled job posts to LinkedIn
# 5. Verify post live

# Test orchestration:
# 1. Drop file in Inbox/
# 2. Orchestrator auto-triggers Claude
# 3. Plan created
# 4. Dashboard updated
```

### Create Silver Demo Video (2-3 hours)

Record 10-15 minute demo showing:
1. Bronze recap (1 min)
2. Gmail watcher detecting email (2 min)
3. Email MCP drafting and sending (3 min)
4. LinkedIn auto-post workflow (3 min)
5. Orchestrator automation (2 min)
6. Dashboard showing all components (2 min)
7. Conclusion and next steps (1 min)

### Submit Silver Tier

1. Update GitHub repo
2. Record demo video
3. Submit via form: https://forms.gle/JR9T1SJq5rmQyGkGA
4. Tier: Silver

---

## 🚧 Common Issues & Solutions

### Gmail API Quota Exceeded
**Solution:** Increase check_interval to 300+ seconds

### LinkedIn Login Fails
**Solution:** Re-authenticate with `python linkedin_poster.py auth`

### MCP Server Not Responding
**Solution:** Check ~/.config/claude-code/mcp.json, restart Claude Code

### WhatsApp Session Expired
**Solution:** Delete session folder, re-authenticate

### Orchestrator Not Triggering
**Solution:** Check watchdog is monitoring correct folder, verify Claude command works manually

---

## 📚 Resources

### Skills Available
- `/silver-gmail-setup` - Gmail configuration
- `/silver-linkedin-poster` - LinkedIn automation
- `/silver-mcp-email` - Email MCP server
- `/watcher-setup` - WhatsApp watcher (Step 2B)

### Documentation
- Silver Tier Plan: `/mnt/d/Ai-Employee/SILVER_TIER_PLAN.md`
- Constitution: `.specify/memory/constitution.md`
- Hackathon Doc: `0-hackathon.md`

### External Links
- Gmail API: https://developers.google.com/gmail/api
- Playwright: https://playwright.dev/python/
- MCP Spec: https://modelcontextprotocol.io/

---

## 🎯 Your Next Actions

### Right Now (Next 30 minutes):
1. ☐ Read `/silver-gmail-setup.md` skill
2. ☐ Go to https://console.cloud.google.com/
3. ☐ Create "AI-Employee-Silver" project
4. ☐ Enable Gmail API
5. ☐ Download credentials.json

### Today (Next 4-6 hours):
6. ☐ Complete Gmail watcher setup
7. ☐ Test Gmail detection with real email
8. ☐ Deploy with PM2
9. ☐ Test Claude processing emails

### This Week (Next 20-30 hours):
10. ☐ Complete all 5 phases
11. ☐ Integration testing
12. ☐ Record demo video
13. ☐ Submit Silver tier

---

## 💡 Pro Tips

1. **Start Small:** Get Gmail working perfectly before moving to next feature
2. **Test Frequently:** Don't wait until end to test integration
3. **Document Issues:** Keep notes of problems and solutions
4. **Use PM2:** Makes process management much easier
5. **Backup Regularly:** Git commit after each working feature
6. **Monitor Logs:** Check PM2 logs daily for errors
7. **Rate Limiting:** Keep API calls reasonable (Gmail, LinkedIn)
8. **Security First:** Never commit credentials, always use .env

---

## 🎓 Getting Help

### Wednesday Zoom Meetings
- **Every Wednesday 10 PM**
- Meeting ID: 871 8870 7642
- Share progress, ask questions, learn from others

### Stuck on Something?
1. Check the relevant skill document
2. Review Silver Tier Plan
3. Check troubleshooting sections
4. Ask on Wednesday Zoom
5. Re-read hackathon doc (0-hackathon.md)

---

**Status:** Ready to Start ✅
**First Task:** Gmail Watcher Setup
**Estimated Completion:** 2-3 weeks
**You've Got This!** 💪

---

*Silver Tier Implementation Guide*
*Created: 2026-02-06*
*Bronze Tier: ✅ COMPLETE*
*Silver Tier: 🚀 STARTING NOW*
