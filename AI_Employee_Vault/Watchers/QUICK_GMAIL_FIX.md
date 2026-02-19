# Quick Gmail Fix - OAuth Playground (10 Minutes)

## Step 1: Open OAuth Playground

**Link:** https://developers.google.com/oauthplayground/

## Step 2: Configure Settings

1. Click **gear icon (⚙️)** on top right
2. Check: **☑ Use your own OAuth credentials**
3. Fill in:
   - **OAuth Client ID:** `509554651020-o197cnime41ra1pao1h9hfoloekab4b7`
   - **OAuth Client secret:** `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`
4. Click **Close**

## Step 3: Select Gmail API

1. Left side: Find **Gmail API v1**
2. Expand it
3. Check: **☑ https://www.googleapis.com/auth/gmail.readonly**

## Step 4: Authorize

1. Click blue button: **Authorize APIs**
2. Select: `asmayaseen9960@gmail.com`
3. Click **Advanced** → **Go to OAuth Playground (unsafe)**
4. Click **Allow**

## Step 5: Get Tokens

1. You'll be back at playground
2. Click: **Exchange authorization code for tokens**
3. You'll see:
   - Access token
   - Refresh token

## Step 6: Create Token File

Copy the tokens and run in terminal:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Get the tokens from playground, then run:
cat > token.json << 'TOKENEOF'
{
  "token": "PASTE_ACCESS_TOKEN_HERE",
  "refresh_token": "PASTE_REFRESH_TOKEN_HERE",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "509554651020-o197cnime41ra1pao1h9hfoloekab4b7",
  "client_secret": "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",
  "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
}
TOKENEOF
```

## Step 7: Test

```bash
python3 gmail_watcher.py /mnt/d/Ai-Employee/AI_Employee_Vault credentials/credentials.json
```

**Should work immediately!**

---

## If Successful, Move to Gold Tier!

Silver complete! Now focus on Gold requirements.
