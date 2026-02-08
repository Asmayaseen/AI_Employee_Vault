# Fix: OAuth Access Blocked (Error 403)

**Error:** "AI-Employee-silver-tier has not completed the Google verification process"
**Reason:** Your email is not added as a test user in Google Cloud Console

---

## Quick Fix (5 minutes)

### Step 1: Go to OAuth Consent Screen

Open this URL in your browser:
```
https://console.cloud.google.com/apis/credentials/consent
```

Or manually:
1. Go to: https://console.cloud.google.com/
2. Select your project (AI-Employee-silver-tier or similar)
3. Left menu: **APIs & Services** → **OAuth consent screen**

---

### Step 2: Add Test Users

1. Scroll down to **"Test users"** section
2. Click **"+ ADD USERS"**
3. Enter your email: `asmayaseen9960@gmail.com`
4. Click **"SAVE"**

![Test Users Section](https://i.imgur.com/example.png)

---

### Step 3: Verify Settings

Check these settings on the OAuth consent screen:

| Setting | Required Value |
|---------|---------------|
| **User Type** | External |
| **Publishing status** | Testing |
| **Test users** | asmayaseen9960@gmail.com (must be added!) |

**Important:** App must be in **"Testing"** mode, NOT "In Production"

---

### Step 4: Try Authentication Again

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python authenticate_gmail.py
```

Now it should work! ✅

---

## Alternative: Use Internal User Type

If you only want to use this with your own Google Workspace account:

### Step 1: Change User Type

1. Go to OAuth consent screen
2. Click **"EDIT APP"**
3. User Type: Select **"Internal"** (if available)
4. Save

**Note:** "Internal" is only available if you have a Google Workspace account.
For regular Gmail, use "External" + add yourself as test user.

---

## Complete OAuth Setup Checklist

### In Google Cloud Console:

1. **Project Created** ✅
2. **Gmail API Enabled** ✅
3. **OAuth Credentials Created** ✅
4. **Credentials Downloaded** ✅ (credentials.json)

### OAuth Consent Screen Configuration:

- [ ] **App Name:** AI-Employee-silver-tier (or your chosen name)
- [ ] **User support email:** Your email
- [ ] **Developer contact:** Your email
- [ ] **User Type:** External
- [ ] **Publishing status:** Testing
- [ ] **Test users:** `asmayaseen9960@gmail.com` ← **MUST ADD THIS!**

### Scopes (Required):

- [ ] `.../auth/gmail.readonly` (Read Gmail emails)

### OAuth Client (Desktop App):

- [ ] **Application type:** Desktop app
- [ ] **Redirect URI:** `http://localhost` (auto-configured)

---

## Detailed Steps with Screenshots

### 1. Navigate to OAuth Consent Screen

```
Google Cloud Console
  └─ APIs & Services
      └─ OAuth consent screen  ← Click here
```

### 2. OAuth Consent Screen Page

You'll see:

```
┌─────────────────────────────────────────┐
│ OAuth consent screen                     │
├─────────────────────────────────────────┤
│ User Type: External                      │
│ Publishing status: Testing               │
│                                          │
│ [EDIT APP]  [PUBLISH APP]               │
└─────────────────────────────────────────┘

Test users
Add the email addresses of users who can access your app while it's in testing mode.

[+ ADD USERS]

Test users:
(empty) ← THIS IS YOUR PROBLEM!
```

### 3. Click "+ ADD USERS"

A popup appears:
```
┌─────────────────────────────────┐
│ Add test users                   │
├─────────────────────────────────┤
│ Email addresses (one per line)   │
│                                  │
│ ┌─────────────────────────────┐ │
│ │ asmayaseen9960@gmail.com    │ │  ← TYPE YOUR EMAIL HERE
│ └─────────────────────────────┘ │
│                                  │
│     [CANCEL]          [ADD]      │
└─────────────────────────────────┘
```

### 4. After Adding

```
Test users:
┌─────────────────────────────────┐
│ asmayaseen9960@gmail.com        │  ← NOW IT SHOWS YOUR EMAIL
│ [DELETE]                         │
└─────────────────────────────────┘

[+ ADD USERS]
```

### 5. Click "SAVE" at Bottom

Scroll to bottom of page and click **"SAVE"**

---

## Now Test Again

```bash
python authenticate_gmail.py
```

This time when you authorize:
- ✅ No more "Access blocked" error
- ✅ You'll see permissions screen
- ✅ Click "Allow"
- ✅ Get redirect URL with code
- ✅ Authentication succeeds!

---

## Common Questions

### Q: Why do I need to add myself as test user?
**A:** When app is in "Testing" mode, only approved test users can access it. This is Google's security feature.

### Q: Can I add multiple emails?
**A:** Yes! Add up to 100 test users. Great if you want to test with team members.

### Q: What if I want to make it public?
**A:** You'd need to verify your app with Google (takes weeks). For personal use, stay in "Testing" mode.

### Q: How long does this take?
**A:** Instant! As soon as you add test user and save, you can authenticate.

### Q: Do I need to re-authenticate after adding test user?
**A:** Yes, run `python authenticate_gmail.py` again.

---

## Verification Steps

After adding test user, verify:

```bash
# 1. Check credentials are still there
ls -la credentials/credentials.json
# Should show: -rwxrwxrwx ... credentials.json

# 2. Run authentication
python authenticate_gmail.py
# Should show: OAuth URL (open in browser)

# 3. Open URL in browser
# Should show: Gmail permissions (NOT "Access blocked")

# 4. After allowing
# Should get: redirect URL with code

# 5. Paste code
# Should show: ✅ SUCCESS! Authentication complete!

# 6. Test connection
python test_gmail_connection.py
# Should show: ✅ Connected to Gmail!
```

---

## If Still Not Working

### Check Project Selection

Make sure you're in the RIGHT project:

1. Top-left of Google Cloud Console
2. Click project name dropdown
3. Find project with your OAuth credentials
4. Select it
5. Then go to OAuth consent screen

### Verify API is Enabled

```
APIs & Services → Library → Search "Gmail API" → Should say "MANAGE" (not "ENABLE")
```

### Check Credentials Type

```
APIs & Services → Credentials → Should see:
- OAuth 2.0 Client IDs
  - Name: AI-Employee (or similar)
  - Type: Desktop app  ← MUST be Desktop, not Web
```

### Try Incognito Mode

Sometimes browser cache causes issues:
1. Open browser in incognito/private mode
2. Paste OAuth URL
3. Complete authorization
4. Copy redirect URL

---

## What Happens After Fix

Once test user is added:

1. **Authentication works** ✅
2. **token.json is created** ✅
3. **Gmail watcher can run** ✅
4. **Emails are monitored** ✅
5. **Action files created** ✅
6. **Claude processes them** ✅

---

## Summary

**Problem:** Error 403: access_denied
**Root Cause:** Email not in test users list
**Solution:** Add `asmayaseen9960@gmail.com` to test users in OAuth consent screen
**Time to Fix:** 2 minutes
**Steps:**
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Click "+ ADD USERS"
3. Enter: asmayaseen9960@gmail.com
4. Click "ADD" and "SAVE"
5. Run: `python authenticate_gmail.py`

**Result:** ✅ OAuth works perfectly!

---

## Next Steps After Fixing

```bash
# 1. Authenticate
python authenticate_gmail.py
# → Follow prompts, should work now!

# 2. Test
python test_gmail_connection.py
# → Should show: Connected to Gmail!

# 3. Run watcher
python gmail_watcher.py ../
# → Monitors Gmail every 2 minutes

# 4. Check it's working
# Send yourself a test email
# Wait 2 minutes
# Check: ls -la ../Needs_Action/
# Should see: GMAIL_*.md file
```

---

**Go fix it now:** https://console.cloud.google.com/apis/credentials/consent

Add test user → Save → Run `python authenticate_gmail.py` → Done! 🎉
