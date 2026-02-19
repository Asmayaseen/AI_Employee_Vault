# Gmail Setup - Quick Guide

## Problem
Script failed with: `❌ Error: EOF when reading a line`

This happens because shell script can't read input properly in some terminals.

---

## Solution: Use Python Script Instead

### Step 1: Run Authentication Script

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python authenticate_gmail.py
```

### Step 2: Follow Prompts

The script will show you a URL like:
```
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...
```

### Step 3: Open URL in Browser

1. **Copy the URL** from terminal
2. **Paste in browser** (Windows browser, not WSL)
3. **Login** to your Google account

### Step 4: Authorize App

You'll see: **"Google hasn't verified this app"**

Don't worry! This is YOUR app. Click:
1. **Advanced**
2. **Go to AI Employee (unsafe)**
3. **Allow** (give Gmail permissions)

### Step 5: Copy Redirect URL

After clicking "Allow":
- Browser tries to go to: `http://localhost:8080/?code=4/0Af...`
- Page shows: **"This site can't be reached"** ← THIS IS NORMAL!
- Look at **address bar** in browser
- Copy the **FULL URL** (it has the code in it)

Example:
```
http://localhost:8080/?code=4/0AfrH98dKJH...&scope=https://...
```

### Step 6: Paste URL Back

Return to terminal and paste the full URL when prompted:
```
Paste redirect URL here: http://localhost:8080/?code=4/0Af...
```

### Step 7: Done! ✅

You'll see:
```
✅ SUCCESS! Authentication complete!
Token saved to: /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/token.json
```

---

## Test Authentication

```bash
python test_gmail_connection.py
```

Should show:
```
✅ Connected to Gmail!
   Email: your.email@gmail.com
   Total messages: 1,234
   Unread messages: 5
```

---

## Start Gmail Watcher

```bash
# Test mode (30 seconds)
timeout 30 python gmail_watcher.py ../

# Full mode (runs continuously)
python gmail_watcher.py ../
```

---

## Troubleshooting

### Error: "EOF when reading a line"
→ Use `python authenticate_gmail.py` instead of shell script

### Error: "Invalid URL"
→ Make sure URL contains `?code=` and starts with `http://localhost:8080/`

### Browser shows: "This site can't be reached"
→ This is NORMAL! Just copy the URL from address bar

### Error: "redirect_uri_mismatch"
→ In Google Cloud Console, add redirect URI: `http://localhost:8080/`

### Already have token.json from another setup?
→ Just copy it to `/mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/token.json`

---

## Complete Command Sequence

```bash
# Navigate to Watchers folder
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Run authentication
python authenticate_gmail.py

# (Follow the prompts above)

# Test connection
python test_gmail_connection.py

# Start watching Gmail
python gmail_watcher.py ../
```

---

## What Happens After Setup

Gmail watcher will:
1. Check Gmail every 2 minutes
2. Find unread emails
3. Create action files in `/Needs_Action/`
4. Claude processes them → generates plans
5. You approve → Email MCP sends replies

---

## Files

- `authenticate_gmail.py` ← **Use this** (not the .sh script)
- `test_gmail_connection.py` ← Test after authentication
- `gmail_watcher.py` ← Main watcher (runs 24/7)
- `credentials/credentials.json` ← OAuth client (already present ✅)
- `token.json` ← Will be created after authentication

---

**Ready?** Run: `python authenticate_gmail.py`
