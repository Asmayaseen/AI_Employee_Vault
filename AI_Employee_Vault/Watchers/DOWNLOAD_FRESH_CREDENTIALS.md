# Download Fresh Credentials - Quick Guide

Since "AI-Employee-desktop" already exists in Google Cloud Console, let's download fresh credentials.

## 🚀 Quick Steps (5 minutes)

### Step 1: Open Google Cloud Console

Browser mein: https://console.cloud.google.com/apis/credentials

**Direct link to credentials page**

### Step 2: Find Your OAuth Client

You should see in the list:
- **Name:** AI-Employee-desktop (or similar)
- **Type:** OAuth 2.0 Client ID
- **Client ID:** 509554651020-...

### Step 3: Download Fresh Credentials

**Option A: Download from existing client**
1. Find "AI-Employee-desktop" in the list
2. Click the **download icon** (⬇️) on the right side
3. File will download: `client_secret_XXXXX.json`

**Option B: If no download icon, create new**
1. Click on "AI-Employee-desktop" to open details
2. Look for **"DOWNLOAD JSON"** button
3. OR delete old client and create new one:
   - Delete the old client (trash icon)
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   - Type: "Desktop app"
   - Name: "AI-Employee-Desktop-Fresh"
   - Click "CREATE"
   - Click "DOWNLOAD JSON"

### Step 4: Verify Downloaded File

The JSON file should look like:
```json
{
  "installed": {
    "client_id": "XXXXX.apps.googleusercontent.com",
    "project_id": "ai-employee-silver-486714",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "GOCSPX-XXXXX",
    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
  }
}
```

### Step 5: Replace Old Credentials

In WSL terminal:

```bash
# Go to credentials directory
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/credentials

# Backup old
mv credentials.json credentials.json.backup

# Copy new credentials
# Find the downloaded file first
ls -la "/mnt/c/Users/S com/Downloads/"client_secret*.json

# Copy the newest one
cp "/mnt/c/Users/S com/Downloads/client_secret_XXXXX.json" credentials.json

# Verify
cat credentials.json
```

### Step 6: Test Authentication

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python3 gmail_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault credentials/credentials.json
```

---

## ⚠️ Important: OAuth Consent Screen

Make sure test user is added:

1. Go to: **APIs & Services** → **OAuth consent screen**
2. Scroll down to **"Test users"**
3. Check if **asmayaseen9960@gmail.com** is listed
4. If not, click **"+ ADD USERS"**
5. Enter: asmayaseen9960@gmail.com
6. Click **"Save"**

**Without test user, authentication will fail!**

---

## 🔍 Why "deleted_client" Error?

Possible reasons:
1. **Credentials file has old/wrong client_id** - Download fresh one
2. **Client was deleted and recreated** - New download needed
3. **Different project** - Make sure same project in console and credentials
4. **Cached browser data** - Try incognito/private window

---

## ✅ After Fresh Download

Fresh credentials should have:
- ✅ Matching client_id in GCP Console
- ✅ Same project_id
- ✅ Valid client_secret
- ✅ Correct redirect_uris

Test again and it should work!

---

## 🆘 Still Not Working?

If still getting "deleted_client":

1. **Delete the OAuth client completely in GCP Console**
2. **Create brand new one:**
   - Type: Desktop app
   - Name: AI-Employee-Fresh-2026
   - Download immediately
3. **Replace credentials.json**
4. **Test in incognito browser window**

---

**Ready to download fresh credentials?** Follow steps above! 🚀
