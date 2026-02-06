# silver-gmail-setup

Set up Gmail Watcher for continuous email monitoring - Silver Tier requirement.

## What you do

Configure Gmail API, authenticate, and deploy a continuous watcher that monitors important emails and creates action files in the vault.

## Prerequisites

- Bronze tier complete
- Google account
- Python 3.13+
- Basic command line knowledge

## Instructions

### Step 1: Google Cloud Console Setup (15 minutes)

#### Create Project
1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Project name: `AI-Employee-Silver`
4. Click "Create"
5. Wait for project creation (30 seconds)

#### Enable Gmail API
1. In the console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Gmail API" result
4. Click "Enable"
5. Wait for API to enable (~30 seconds)

#### Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted to configure consent screen:
   - Click "Configure Consent Screen"
   - Select "External"
   - Fill in:
     - App name: `AI Employee Gmail Watcher`
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Skip (click "Save and Continue")
   - Test users: Add your Gmail address
   - Click "Save and Continue"
   - Click "Back to Dashboard"
4. Return to "Credentials" tab
5. Click "Create Credentials" → "OAuth client ID"
6. Application type: "Desktop app"
7. Name: `AI Employee Gmail Watcher`
8. Click "Create"
9. Click "Download JSON"
10. Save as `credentials.json`

### Step 2: Install Python Dependencies

```bash
pip install --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 3: Prepare Credentials Directory

```bash
# Create credentials directory
mkdir -p /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials

# Move downloaded credentials.json here
# (Replace path with your actual download location)
mv ~/Downloads/credentials.json /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials/
```

### Step 4: Verify Gmail Watcher Code Exists

```bash
# Check if gmail_watcher.py exists
ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/gmail_watcher.py

# If not, create it using the watcher-setup skill template
```

### Step 5: First Run (Authentication)

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Run gmail watcher for first time
python gmail_watcher.py \
  /mnt/d/Ai-Employee/AI_Employee_Vault \
  credentials/credentials.json
```

**What Happens:**
1. Browser window opens
2. Select your Google account
3. Warning: "Google hasn't verified this app" → Click "Advanced" → "Go to AI Employee Gmail Watcher (unsafe)"
4. Click "Allow" for Gmail API permissions
5. Browser shows "The authentication flow has completed"
6. Terminal shows: "Starting GmailWatcher"
7. `token.json` file created in credentials/ directory

**Keep this terminal open** - watcher is now monitoring your Gmail.

### Step 6: Test Detection

In another terminal:

```bash
# Send yourself a test email
# Mark it as "Important" in Gmail
# Subject: "Test Invoice Request"
# Body: "Please send me invoice #123"

# Watch the watcher terminal for output:
# "Found 1 new item(s)"
# "Created: EMAIL_20260206_XXXXXX_Test_Invoice_Request.md"

# Verify file created
ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Needs_Action/
```

### Step 7: Deploy with PM2 (Continuous Operation)

```bash
# Stop the manual run (Ctrl+C in watcher terminal)

# Install PM2 if not already installed
npm install -g pm2

# Start gmail watcher with PM2
pm2 start gmail_watcher.py \
  --name "ai-employee-gmail" \
  --interpreter python3 \
  -- /mnt/d/Ai-Employee/AI_Employee_Vault /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials/credentials.json

# Save PM2 configuration
pm2 save

# Set PM2 to start on system boot
pm2 startup
# Follow the command it outputs

# Check status
pm2 status

# View logs
pm2 logs ai-employee-gmail

# Check for errors
pm2 logs ai-employee-gmail --err
```

### Step 8: Configure Filtering (Optional)

Edit `gmail_watcher.py` to customize:

```python
# Line ~160: Change query to filter different emails
results = self.service.users().messages().list(
    userId='me',
    q='is:unread is:important',  # Modify this query
    maxResults=10
).execute()

# Alternative queries:
# 'is:unread label:client-emails'  # Custom label
# 'is:unread from:specific@email.com'  # Specific sender
# 'is:unread subject:invoice OR subject:payment'  # Keywords
# 'is:unread newer_than:1d'  # Last 24 hours
```

Restart after changes:
```bash
pm2 restart ai-employee-gmail
```

### Step 9: Verify Integration with Claude

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault

# Check for new email action files
ls -la Needs_Action/EMAIL_*.md

# Process with Claude
claude "Check Needs_Action folder for new emails. Create plans for any email requests."

# Verify plan created
ls -la Plans/

# Check Dashboard update
cat Dashboard.md | grep "Recent Activity" -A 10
```

### Step 10: Set Check Interval

Edit `gmail_watcher.py`:

```python
# Line ~133: Adjust check interval (seconds)
def __init__(self, vault_path: str, credentials_path: str):
    super().__init__(vault_path, check_interval=120)  # 2 minutes
    # Increase to 300 (5 min) or 600 (10 min) to reduce API calls
```

Restart:
```bash
pm2 restart ai-employee-gmail
```

## Configuration Options

### Email Query Examples

```python
# Only from specific senders
q='is:unread from:(client1@example.com OR client2@example.com)'

# Emails with attachments
q='is:unread has:attachment'

# Specific labels (create in Gmail first)
q='is:unread label:ai-employee'

# Subject keywords
q='is:unread subject:(invoice OR payment OR urgent)'

# Exclude promotional/social
q='is:unread -category:promotions -category:social'

# Combine multiple filters
q='is:unread is:important -from:noreply@'
```

### Check Interval Guidelines

| Frequency | Seconds | Use Case |
|-----------|---------|----------|
| Aggressive | 60 | High-volume business |
| Normal | 120 | Standard business |
| Conservative | 300 | Low-volume, API quota conscious |
| Minimal | 600 | Very low-volume |

**Note:** Gmail API has quota limits. Check at: https://console.cloud.google.com/apis/api/gmail.googleapis.com/quotas

## Troubleshooting

### Issue: "Invalid client secrets"
**Solution:** Verify credentials.json is correct file, not a renamed file

### Issue: "Access denied" during OAuth
**Solution:**
1. Ensure your email is added as test user in OAuth consent screen
2. Re-download credentials.json
3. Delete token.json and re-authenticate

### Issue: "Token expired"
**Solution:**
```bash
# Delete token and re-authenticate
rm credentials/token.json
pm2 restart ai-employee-gmail
# Browser will open for re-authentication
```

### Issue: "Rate limit exceeded"
**Solution:**
- Increase check_interval to 300 or higher
- Check quota usage in Google Cloud Console
- Reduce maxResults from 10 to 5

### Issue: "Watcher not detecting emails"
**Solution:**
1. Verify email matches query filter
2. Check logs: `pm2 logs ai-employee-gmail`
3. Test query in Gmail search bar first
4. Ensure token.json exists and is valid

### Issue: "PM2 process crashes"
**Solution:**
```bash
# Check error logs
pm2 logs ai-employee-gmail --err

# Common fixes:
# 1. Verify Python path
which python3

# 2. Verify dependencies installed
pip list | grep google

# 3. Restart with explicit Python path
pm2 delete ai-employee-gmail
pm2 start gmail_watcher.py \
  --name "ai-employee-gmail" \
  --interpreter /usr/bin/python3 \
  -- /mnt/d/Ai-Employee/AI_Employee_Vault credentials/credentials.json
```

## Success Criteria

- [ ] Google Cloud project created
- [ ] Gmail API enabled
- [ ] OAuth credentials downloaded
- [ ] Python dependencies installed
- [ ] First authentication successful (token.json created)
- [ ] Test email detected and action file created
- [ ] PM2 deployment successful
- [ ] Watcher runs continuously without crashes
- [ ] Action files appear in /Needs_Action/
- [ ] Claude successfully processes email action files
- [ ] Logs show regular checks

## Monitoring & Maintenance

### Daily Checks
```bash
# Check watcher status
pm2 status ai-employee-gmail

# View recent logs
pm2 logs ai-employee-gmail --lines 50

# Check action files created today
find /mnt/d/Ai-Employee/AI_Employee_Vault/Needs_Action/ -name "EMAIL_*.md" -mtime -1
```

### Weekly Maintenance
1. Review processed_ids size (memory usage)
2. Check API quota usage in Google Cloud Console
3. Verify no error patterns in logs
4. Clean up old action files (move to Done/)

### Monthly Tasks
1. Rotate logs: `pm2 flush`
2. Review and adjust email query filters
3. Optimize check_interval based on usage
4. Update Google OAuth consent screen if needed

## Security Notes

- ✅ `credentials.json` is in `.gitignore`
- ✅ `token.json` is in `.gitignore`
- ✅ Never commit these files to GitHub
- ✅ HITL approval still required for email replies
- ✅ Watcher only reads emails (read-only access)
- ✅ Logs may contain email metadata - protect access

## Next Steps

After Gmail watcher is operational:
1. `/silver-mcp-email` - Enable autonomous email sending
2. `/silver-linkedin-poster` - Set up LinkedIn auto-posting
3. Test end-to-end: Gmail → Plan → Approval → MCP Send

## References

- Gmail API: https://developers.google.com/gmail/api
- OAuth Setup: https://developers.google.com/gmail/api/quickstart/python
- Query Syntax: https://support.google.com/mail/answer/7190
- Quota Limits: https://developers.google.com/gmail/api/reference/quota

---

*Skill: silver-gmail-setup*
*Tier: Silver*
*Estimated Time: 30-45 minutes*
*Dependencies: Bronze tier complete*
