# LinkedIn Watcher - Status & Setup Guide

**Date:** 2026-02-08
**Status:** ⚠️ READY (Requires Login Setup)

## Current Status

✅ **Installed:** LinkedIn watcher code is present
✅ **Dependencies:** Playwright and Chromium installed
✅ **Configuration:** Watcher initialized successfully
⚠️ **Session:** No saved LinkedIn login session yet
⚠️ **WSL Issue:** Browser display requires X Server setup

## What It Does

The LinkedIn watcher can:
- 📬 Monitor LinkedIn messages in real-time
- 🔔 Track notifications and connection requests
- 💼 Detect potential leads using keyword matching
- 📝 Create action files for each new item
- 🤖 Enable auto-posting (with scheduled queue)
- 💾 Persist login session for automatic monitoring

## WSL Challenge

You're running on WSL (Windows Subsystem for Linux). LinkedIn watcher needs to display a browser, which requires:

### Option 1: Use X Server (Recommended)

1. **Install VcXsrv on Windows:**
   - Download: https://sourceforge.net/projects/vcxsrv/
   - Install and run "XLaunch"
   - Choose "Multiple windows" → "Start no client" → **Disable access control**

2. **Set DISPLAY variable in WSL:**
   ```bash
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk "{print \$2}"):0' >> ~/.bashrc
   ```

3. **Test X Server:**
   ```bash
   sudo apt install x11-apps
   xeyes  # Should show eyes following cursor on Windows
   ```

4. **Run LinkedIn watcher:**
   ```bash
   cd AI_Employee_Vault/Watchers
   python test_linkedin.py --full
   ```

### Option 2: Use WSLg (Windows 11 Only)

If you have Windows 11:
```bash
wslg --version  # Check if available
# If available, browser will automatically display
python test_linkedin.py --full
```

### Option 3: Run on Windows Native Python

Most reliable for LinkedIn automation:

1. **Install Python on Windows:**
   - Download from python.org
   - Check "Add to PATH" during installation

2. **Install dependencies on Windows:**
   ```powershell
   pip install playwright python-dotenv
   playwright install chromium
   ```

3. **Run from Windows Command Prompt:**
   ```powershell
   cd D:\Ai-Employee\AI_Employee_Vault\Watchers
   python test_linkedin.py --full
   ```

### Option 4: Headless Mode (Not Recommended)

LinkedIn may detect and block headless browsers:
```python
# Modify linkedin_watcher.py line 94:
headless=True  # Instead of False
```

⚠️ This may trigger LinkedIn security checks and CAPTCHA.

## Testing Sequence

### 1. Configuration Test (No Browser)
```bash
cd AI_Employee_Vault/Watchers
python test_linkedin.py
```

Expected output:
```
✅ Playwright is installed
✅ Watcher initialized
⚠️  No saved session found
```

### 2. Full Browser Test (Requires Display)
```bash
python test_linkedin.py --full
```

What happens:
1. Browser window opens
2. LinkedIn loads
3. You login manually (first time only)
4. Session is saved to `.linkedin_session/`
5. Watcher checks for messages/notifications
6. Creates action files in `Needs_Action/`

### 3. Continuous Monitoring
```bash
python linkedin_watcher.py ../
```

Runs every 60 seconds checking for new items.

## Features

### Message Monitoring
Detects new LinkedIn messages and creates action files:

```markdown
---
type: linkedin_message
source: linkedin
priority: high
date: 2026-02-08 12:34
---

# LinkedIn Message: John Doe

**From:** John Doe (CEO at Tech Corp)
**Time:** 2 hours ago
**Lead Score:** High 🎯

## Message

"Hi! I saw your profile and I'm interested in discussing
a potential project..."

## Detected Keywords
- interested ✓
- project ✓

## Suggested Actions
1. Review sender profile
2. Assess opportunity
3. Draft response

---
*Created by: LinkedInWatcher*
```

### Lead Detection
Automatically flags messages containing keywords:
- interested, pricing, services, hire, project
- consultant, developer, quote, proposal, budget
- opportunity, collaboration, partnership

### Auto-Posting (Coming Soon)
Queue posts in `Plans/linkedin_posts_queue.json`:
```json
{
  "posts": [
    {
      "text": "Excited to announce...",
      "scheduled_for": "2026-02-10T09:00:00",
      "posted": false
    }
  ]
}
```

## Configuration

### Check Interval
Default: 60 seconds (to avoid rate limiting)

Modify in `linkedin_watcher.py:41`:
```python
def __init__(self, vault_path: str = None, session_path: str = None, check_interval: int = 60):
```

### Lead Keywords
Customize in `linkedin_watcher.py:52-56`:
```python
self.lead_keywords = [
    'interested', 'pricing', 'services', 'hire', 'project',
    'consultant', 'developer', 'quote', 'proposal', 'budget',
    'opportunity', 'collaboration', 'partnership'
]
```

Add your industry-specific keywords!

### Session Path
Sessions stored in: `Watchers/.linkedin_session/`

Contains:
- Browser cookies
- Local storage
- Login state
- User preferences

⚠️ Keep this secure - it's like your login token!

## File Structure

```
AI_Employee_Vault/
├── Watchers/
│   ├── linkedin_watcher.py       # Main watcher
│   ├── test_linkedin.py          # Test script
│   ├── .linkedin_session/        # Browser session (created on login)
│   └── base_watcher.py
├── .processed_linkedin           # Tracking file
├── Needs_Action/                 # Action files created here
│   └── LINKEDIN_*.md
├── Logs/                         # Activity logs
└── Plans/
    └── linkedin_posts_queue.json # Scheduled posts
```

## Security & Best Practices

### LinkedIn Terms of Service
⚠️ Be aware of LinkedIn's automation policies:
- Don't spam connections
- Don't scrape data excessively
- Use reasonable check intervals (60s minimum)
- Respect rate limits

### Session Security
- `.linkedin_session/` contains your login
- Add to `.gitignore`
- Never commit to version control
- Treat like a password

### Rate Limiting
LinkedIn may throttle if:
- Too many requests per minute
- Unusual access patterns detected
- Headless browser detected

**Recommendation:** Keep check_interval ≥ 60 seconds

## Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### "Cannot open display"
Set up X Server (Option 1 above) or run on Windows native Python.

### "LinkedIn security challenge"
- Use non-headless browser (headless=False)
- Complete CAPTCHA manually
- Wait before retrying
- Session will be saved after successful login

### "Session expired"
```bash
rm -rf Watchers/.linkedin_session/
python test_linkedin.py --full  # Login again
```

### Browser crashes on WSL
Try:
```bash
# Increase shared memory
sudo mount -o remount,size=2G /dev/shm
```

Or run on Windows native Python.

## Next Steps

1. **Setup Display:**
   - Install VcXsrv OR
   - Use Windows native Python

2. **First Login:**
   ```bash
   python test_linkedin.py --full
   ```

3. **Run Monitoring:**
   ```bash
   python linkedin_watcher.py ../
   ```

4. **Add to Startup:**
   Create systemd service or Windows Task Scheduler

5. **Test Lead Detection:**
   - Have someone send you a message with "interested in hiring"
   - Check `Needs_Action/` for action file

## Comparison: LinkedIn vs Gmail

| Feature | Gmail Watcher | LinkedIn Watcher |
|---------|--------------|------------------|
| Authentication | OAuth (easy) | Browser session (complex) |
| Setup | ✅ Simple | ⚠️ Needs X Server on WSL |
| Status | ✅ Working | ⚠️ Pending login |
| Rate Limits | High | Moderate |
| Lead Detection | Email keywords | Message keywords |
| Auto-response | Not yet | Possible |

## Environment Variables

Add to `.env`:
```bash
# LinkedIn Configuration
LINKEDIN_SESSION_PATH=/full/path/to/.linkedin_session

# Watcher Settings
DRY_RUN=true
CHECK_INTERVAL=60

# Display (WSL)
DISPLAY=:0
```

## Performance

- **Memory:** ~200MB (includes browser)
- **CPU:** Minimal between checks
- **Network:** ~1MB per check cycle
- **LinkedIn API:** No official API used (web automation)

## Summary

✅ **Code Ready:** LinkedIn watcher implemented
✅ **Dependencies:** Playwright installed
⚠️ **Next Step:** Setup X Server or use Windows Python
⚠️ **Then:** Run `test_linkedin.py --full` for first login

Once setup is complete, LinkedIn watcher will:
- Monitor messages 24/7
- Detect potential leads automatically
- Create action files for review
- Track all activity in logs

---

**Quick Command Reference:**

```bash
# Test configuration
python test_linkedin.py

# Full test with browser
python test_linkedin.py --full

# Run continuously
python linkedin_watcher.py ../

# Check logs
cat ../Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.watcher=="LinkedInWatcher")'

# Clear session (re-login)
rm -rf .linkedin_session/
```
