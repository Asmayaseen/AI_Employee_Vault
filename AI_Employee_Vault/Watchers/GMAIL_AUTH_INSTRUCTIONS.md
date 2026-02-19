# Gmail Authentication Instructions (WSL)

Since you're using WSL (Windows Subsystem for Linux), the browser won't open automatically. Follow these steps for manual authentication:

## Step 1: Run Gmail Watcher

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python3 gmail_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault credentials/credentials.json
```

## Step 2: Manual Authentication

The watcher will print a URL that looks like:

```
Please visit this URL to authorize this application:
https://accounts.google.com/o/oauth2/auth?client_id=...
```

## Step 3: Open URL in Windows Browser

1. **Copy the full URL** from terminal
2. **Open in Windows browser** (Chrome, Edge, Firefox)
3. **Select your Google account** (asmayaseen9960@gmail.com)

## Step 4: Handle Security Warning

You'll see: **"Google hasn't verified this app"**

**This is normal!** This is YOUR app, not a third-party app.

To proceed:
1. Click **"Advanced"** (small text at bottom)
2. Click **"Go to AI Employee Gmail Watcher (unsafe)"**

## Step 5: Grant Permissions

You'll see permission request:
- **"Read your email messages and settings"**

Click **"Allow"**

## Step 6: Get Authorization Code

After allowing, you'll see a page with text like:

```
The authentication flow has completed.
```

Or it might show an authorization code like:

```
4/0AanRRrvQx...
```

## Step 7: Enter Code in Terminal

1. **Copy the authorization code** from browser
2. **Paste in terminal** where it says:
   ```
   Enter the authorization code:
   ```
3. Press **ENTER**

## Step 8: Success!

You should see:
```
2026-02-07 XX:XX:XX - GmailWatcher - INFO - Token saved to /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/token.json
2026-02-07 XX:XX:XX - GmailWatcher - INFO - Gmail API authenticated successfully
2026-02-07 XX:XX:XX - GmailWatcher - INFO - Starting watcher loop (check interval: 120 seconds)
```

**Token saved!** Next time, authentication won't be needed.

## Testing

After authentication:
1. **Send yourself a test email**
2. **Mark it as Important** in Gmail
3. **Wait 2 minutes** (check interval)
4. **Watcher will detect it** and create file in `/Needs_Action/`

Press **Ctrl+C** to stop the watcher.

---

## Troubleshooting

### Problem: URL is too long to copy

**Solution:** The URL will be printed in terminal. Carefully select and copy the ENTIRE URL.

### Problem: "redirect_uri_mismatch" error

**Solution:** In Google Cloud Console:
1. Go to Credentials → OAuth 2.0 Client IDs
2. Click your client ID
3. Add authorized redirect URIs:
   - `http://localhost`
   - `http://localhost:8080`
   - `urn:ietf:wg:oauth:2.0:oob`

### Problem: "Access blocked: This app's request is invalid"

**Solution:**
1. OAuth consent screen → Edit
2. Add test user: asmayaseen9960@gmail.com
3. Save

### Problem: No authorization code shown

**Solution:**
1. Check if URL redirected to localhost
2. Copy the `code=` parameter from URL bar
3. Paste in terminal

---

## Next Steps After Authentication

```bash
# Test file detection
echo "Test" > /mnt/d/Ai-Employee/AI_Employee_Vault/Inbox/test.txt

# Process pending items
python3 claude_processor.py --process-all

# Check results
ls -la ../Needs_Action/
ls -la ../Plans/
```

**Your Gmail watcher is ready!** 🎉
