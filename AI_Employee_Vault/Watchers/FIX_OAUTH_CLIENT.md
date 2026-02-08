# Fix OAuth Client Error (401: deleted_client)

This error means the OAuth credentials are either deleted or invalid. Let's fix it!

## 🔧 Solution: Create Fresh OAuth Credentials

### Step 1: Go to Google Cloud Console

Open in Windows browser: https://console.cloud.google.com/

### Step 2: Select Your Project

1. Click on project dropdown (top left, next to "Google Cloud")
2. Select: **"ai-employee-silver-486714"**
3. If project doesn't exist, create new one:
   - Click "New Project"
   - Name: `AI-Employee-Silver`
   - Click "Create"

### Step 3: Enable Gmail API (if not already enabled)

1. Go to: **APIs & Services** → **Library**
2. Search: **"Gmail API"**
3. Click on it
4. Click **"Enable"** (if not already enabled)

### Step 4: Configure OAuth Consent Screen

1. Go to: **APIs & Services** → **OAuth consent screen**
2. If not configured:
   - Select: **"External"**
   - Click **"Create"**
3. Fill in the form:
   - **App name:** `AI Employee Gmail Watcher`
   - **User support email:** asmayaseen9960@gmail.com
   - **Developer contact email:** asmayaseen9960@gmail.com
   - Click **"Save and Continue"**
4. **Scopes:** Skip (click "Save and Continue")
5. **Test users:**
   - Click **"Add Users"**
   - Enter: **asmayaseen9960@gmail.com**
   - Click **"Add"**
   - Click **"Save and Continue"**
6. Click **"Back to Dashboard"**

### Step 5: Create NEW OAuth Credentials

1. Go to: **APIs & Services** → **Credentials**
2. Check if old credentials exist:
   - If you see any OAuth 2.0 Client IDs listed
   - **Delete the old one** (trash icon)
3. Click: **"+ Create Credentials"** (top)
4. Select: **"OAuth client ID"**
5. Application type: **"Desktop app"**
6. Name: `AI Employee Desktop Client`
7. Click **"Create"**

### Step 6: Download Credentials

1. A popup will show with Client ID and Secret
2. Click **"Download JSON"** button
3. File will download as: `client_secret_XXXXX.json`

### Step 7: Replace Old Credentials

In WSL terminal:

```bash
# Navigate to credentials directory
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials

# Backup old credentials (optional)
mv credentials.json credentials.json.old

# Find and copy new credentials from Windows Downloads
# Replace USERNAME with your Windows username
cp "/mnt/c/Users/S com/Downloads/client_secret_*.json" credentials.json

# Verify it was copied
ls -la credentials.json
cat credentials.json | jq '.'
```

### Step 8: Test Authentication

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python3 gmail_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault credentials/credentials.json
```

---

## ✅ What Should Work Now

After completing these steps:

1. Fresh OAuth client created
2. Your email added as test user
3. New credentials downloaded
4. Authentication should work!

---

## 🐛 Alternative: Check if Client Was Actually Deleted

Sometimes the error happens if:

1. **Wrong project selected** - Make sure you're in correct GCP project
2. **Credentials from different project** - credentials.json might be from old/different project
3. **Client ID mismatch** - The client_id in credentials.json doesn't exist in current project

**Quick Check:**

1. Open credentials.json and note the `client_id`
2. Go to GCP Console → Credentials
3. Check if that client_id exists in the list
4. If not, you need to create new one (follow steps above)

---

## 📋 Checklist

- [ ] Correct GCP project selected
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] Test user (asmayaseen9960@gmail.com) added
- [ ] New OAuth client created (Desktop app)
- [ ] Fresh credentials.json downloaded
- [ ] Old credentials.json replaced
- [ ] Test authentication again

---

## 🆘 Still Having Issues?

If you still see error after fresh credentials:

1. **Wait 2-3 minutes** - GCP changes take time to propagate
2. **Clear browser cache** - Old auth data might be cached
3. **Try incognito/private browser window**
4. **Check project billing** - Make sure project isn't suspended

---

**After fixing, run:**

```bash
python3 gmail_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault credentials/credentials.json
```

Good luck! 🚀
