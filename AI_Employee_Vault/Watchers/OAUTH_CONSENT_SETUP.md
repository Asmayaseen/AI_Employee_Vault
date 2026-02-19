# Fix OAuth Error - Complete Setup Guide

## Problem: "deleted_client" Error

Even with fresh credentials, you're getting error. This means OAuth Consent Screen needs proper configuration.

---

## ✅ Solution: Complete OAuth Consent Screen Setup

### Step 1: Go to OAuth Consent Screen

**Direct Link:**
```
https://console.cloud.google.com/apis/credentials/consent?project=ai-employee-silver-486714
```

Or manually:
1. Google Cloud Console
2. Left menu: **APIs & Services** → **OAuth consent screen**

---

### Step 2: Check Publishing Status

At the top, you'll see:

**Publishing status: Testing** ← This is CORRECT (you want Testing mode)

If it says "In Production" or "Not Configured", you need to set it to Testing.

---

### Step 3: Verify App Information

You should see:

**App information:**
- App name: `AI Employee Gmail Watcher` (or similar)
- User support email: `asmayaseen9960@gmail.com`
- App logo: (optional)

**App domain:** (can be blank for testing)

**Developer contact information:**
- Email: `asmayaseen9960@gmail.com`

**If any of this is missing or wrong:**
- Click **"EDIT APP"** button
- Fill in the information
- Click **"SAVE AND CONTINUE"**

---

### Step 4: CRITICAL - Add Test Users

**This is the most important step!**

Scroll down to: **Test users**

You should see:
```
Test users (1)
asmayaseen9960@gmail.com
```

**If you DON'T see your email:**

1. Click **"+ ADD USERS"** button
2. Enter: `asmayaseen9960@gmail.com`
3. Click **"Add"**
4. Click **"SAVE"** at bottom of page

**Without test user, authentication will ALWAYS fail in Testing mode!**

---

### Step 5: Verify Scopes

Click **"EDIT APP"** → Next to Scopes section

Make sure you have:
- `.../auth/gmail.readonly` (Read all Gmail data)

If not present:
1. Click **"ADD OR REMOVE SCOPES"**
2. Search: "Gmail API"
3. Check: `.../auth/gmail.readonly`
4. Click **"UPDATE"**
5. Click **"SAVE AND CONTINUE"**

---

### Step 6: Clear Browser Data

**In the browser you're testing with:**

1. Open browser settings
2. Go to Privacy/Security
3. **Clear browsing data**
4. Select:
   - ✅ Cookies and site data
   - ✅ Cached images and files
5. Time range: **Last hour** (or All time)
6. Click **"Clear data"**

**OR use Incognito/Private window for testing**

---

### Step 7: Verify Credentials Match

Go back to Credentials page:
```
https://console.cloud.google.com/apis/credentials?project=ai-employee-silver-486714
```

Find your OAuth client and verify:
- **Name:** Should match what you created
- **Client ID:** Should start with `509554651020-o197cnime...`
- **Type:** Desktop

**If you see OLD client with different ID:**
- Delete it (trash icon)
- Use only the new one

---

### Step 8: Test Authentication Again

**In WSL Terminal:**

```bash
# Make sure using new credentials
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Clear any cached tokens
rm -f token.json

# Verify credentials
cat credentials/credentials.json | grep client_id

# Should show: 509554651020-o197cnime41ra1pao1h9hfoloekab4b7

# Test authentication
python3 gmail_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault credentials/credentials.json
```

**Use INCOGNITO/PRIVATE browser window for the URL!**

---

## 🐛 Still Getting "deleted_client"?

### Option 1: Wait and Retry

GCP changes take 2-5 minutes to propagate:
1. Wait 5 minutes
2. Clear browser cache again
3. Try in incognito window

### Option 2: Create Completely New Client

1. **Delete ALL existing OAuth clients:**
   - Go to Credentials page
   - Delete "AI-Employee-desktop" and any others
   - Confirm deletion

2. **Create fresh client:**
   - Click "+ CREATE CREDENTIALS"
   - Select "OAuth client ID"
   - Type: **Desktop app**
   - Name: `AI-Employee-Fresh-$(date +%H%M)`
   - Click "CREATE"

3. **IMMEDIATELY download JSON:**
   - Click "DOWNLOAD JSON" in popup
   - Save as `credentials_new.json`

4. **Replace in terminal:**
   ```bash
   cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials
   cp "/mnt/c/Users/S com/Downloads/client_secret_*.json" credentials.json
   ```

5. **Test immediately** (within 1 minute of creation)

---

## 📋 Complete Checklist

Before testing again, verify ALL these:

- [ ] OAuth consent screen configured
- [ ] Publishing status: **Testing**
- [ ] Test user added: `asmayaseen9960@gmail.com`
- [ ] Scopes include: `gmail.readonly`
- [ ] Credentials.json has NEW client_id
- [ ] Old token.json deleted
- [ ] Browser cache cleared OR using incognito
- [ ] Waiting 2-3 minutes after any GCP changes

---

## ✅ What Should Work

After completing ALL steps above:

1. Run gmail_watcher.py
2. Copy URL to **INCOGNITO window**
3. Login → Advanced → Allow
4. Copy redirect URL
5. Paste in terminal
6. **Authentication succeeds!**

---

## 🆘 Last Resort

If NOTHING works:

**Create NEW Google Cloud Project:**

1. Create project: `ai-employee-test-$(date +%Y%m%d)`
2. Enable Gmail API
3. Configure OAuth consent (Testing mode)
4. Add test user
5. Create OAuth client (Desktop)
6. Download credentials
7. Test immediately

Fresh project = no cached/conflicting data!

---

**Most Common Issues:**
1. ❌ Test user not added
2. ❌ Browser cache not cleared
3. ❌ Old client ID still being used
4. ❌ Not waiting for GCP propagation

**Fix all these and it should work!** 🚀
