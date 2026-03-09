# Social Media API Setup Guide

This guide walks through setting up API tokens for the AI Employee social media watchers.

## Prerequisites

- AI Employee `.env` file at `AI_Employee_Vault/.env`
- Social watchers installed (`facebook_watcher.py`, `instagram_watcher.py`, `twitter_watcher.py`)

---

## Facebook / Instagram (Meta Graph API)

Facebook and Instagram share the same Meta Graph API platform.

### Step 1: Create a Meta App

1. Go to https://developers.facebook.com/apps/
2. Click **Create App**
3. Select **Business** type
4. Fill in app name (e.g., "AI Employee Social")
5. Select your Business Account (or create one)

### Step 2: Add Products

In your app dashboard, add these products:
- **Facebook Login**
- **Instagram Graph API**
- **Pages API** (Messenger)

### Step 3: Get Page Access Token

1. Go to **Graph API Explorer**: https://developers.facebook.com/tools/explorer/
2. Select your app from the dropdown
3. Click **Generate Access Token**
4. Grant these permissions (scopes):
   - `pages_messaging` - Read/send Page messages
   - `pages_read_engagement` - Read comments, reactions
   - `pages_manage_posts` - Manage page posts
   - `instagram_basic` - Basic Instagram access
   - `instagram_manage_messages` - Read Instagram DMs
   - `instagram_manage_comments` - Read Instagram comments
5. Copy the generated **User Access Token**

### Step 4: Get Long-Lived Page Token

Short-lived tokens expire in ~1 hour. Convert to long-lived:

1. Go to **Access Token Debugger**: https://developers.facebook.com/tools/debug/accesstoken/
2. Paste your user token and click **Debug**
3. Click **Extend Access Token** to get a 60-day token
4. Then exchange for a **Page Token** (which never expires):

```
GET /me/accounts?access_token={long-lived-user-token}
```

The response includes `access_token` for each page - this is your never-expiring Page Token.

### Step 5: Get Page ID and Instagram Business ID

**Facebook Page ID:**
- Go to your Facebook Page > About > Page transparency
- Or from the Graph API: `GET /me/accounts` returns `id` for each page

**Instagram Business ID:**
- Your Instagram must be a Business or Creator account
- Connect it to your Facebook Page in Instagram Settings > Account > Linked Accounts
- Get the ID: `GET /{page-id}?fields=instagram_business_account` returns `instagram_business_account.id`

### Step 6: Set Environment Variables

Add to `AI_Employee_Vault/.env`:

```bash
META_ACCESS_TOKEN=your_long_lived_user_token
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_PAGE_TOKEN=your_never_expiring_page_token
INSTAGRAM_BUSINESS_ID=your_instagram_business_id
```

### Step 7: Test

```bash
cd AI_Employee_Vault/Watchers
python facebook_watcher.py --test
python instagram_watcher.py --test
```

---

## Twitter / X API v2

### Step 1: Apply for Developer Access

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Sign up for a **Developer Account** (free tier available)
3. For DM access, apply for **Elevated** access (or Pro tier)

### Step 2: Create a Project and App

1. In the Developer Portal, click **Projects & Apps** > **New Project**
2. Name your project (e.g., "AI Employee")
3. Select use case: "Making a bot"
4. Create an **App** within the project

### Step 3: Configure App Permissions

1. Go to your App settings > **User authentication settings**
2. Click **Set up**
3. App permissions: **Read and write and Direct message**
4. Type of App: **Web App, Automated App or Bot**
5. Callback URL: `http://localhost:3000/callback` (or any valid URL)
6. Website URL: your website or `https://example.com`
7. Save

### Step 4: Generate Tokens

Go to **Keys and Tokens** tab:

1. **API Key and Secret** (Consumer Keys):
   - Click **Regenerate** to get new ones
   - Save `API Key` and `API Key Secret`

2. **Access Token and Secret**:
   - Click **Generate** under Access Token and Secret
   - Save `Access Token` and `Access Token Secret`

3. **Bearer Token**:
   - Click **Regenerate** under Bearer Token
   - Save the `Bearer Token`

### Step 5: Set Environment Variables

Add to `AI_Employee_Vault/.env`:

```bash
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token
```

### Step 6: Test

```bash
cd AI_Employee_Vault/Watchers
python twitter_watcher.py --test
```

---

## Verification

After setting up all tokens, verify everything works:

```bash
# Test individual watchers
python facebook_watcher.py --test
python instagram_watcher.py --test
python twitter_watcher.py --test

# Check orchestrator sees all watchers
python orchestrator.py --status

# Full system test
bash ../../start_everything.sh
```

## Troubleshooting

### Facebook/Instagram
- **Error: Invalid access token** - Token may have expired. Regenerate via Graph API Explorer.
- **Error: Page not found** - Check `FACEBOOK_PAGE_ID` is correct.
- **No Instagram data** - Ensure Instagram is connected to the Facebook Page as a Business account.

### Twitter
- **Error: 403 Forbidden** - Check app permissions include DM access. May need Elevated tier.
- **Error: 401 Unauthorized** - Regenerate all tokens and update .env.
- **No DMs returned** - DM access requires Elevated or Pro tier access.

### General
- Always run `source .env` or restart the watcher after changing tokens.
- Check logs: `tail -f /tmp/{facebook,instagram,twitter}_watcher.log`
- Verify with: `python orchestrator.py --status`
