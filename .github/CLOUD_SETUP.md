# Cloud Agent Setup — GitHub Actions

The GitHub Actions workflows act as the 24/7 Cloud Agent.
Two workflows run automatically:

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `cloud-agent.yml` | Every 15 min | Process Needs_Action → Plans → Pending_Approval |
| `health-monitor.yml` | Every 30 min | Check HuggingFace + Odoo, write health logs |

## GitHub Secrets (All Optional)

Go to: **Settings → Secrets and variables → Actions → New repository secret**

> `claude_processor.py` uses template-based plan generation — no AI API key needed.
> The Cloud Agent runs fully without any secrets configured.

| Secret | Required | Value |
|--------|----------|-------|
| `GMAIL_TOKEN_JSON` | Optional | Contents of `token.json` from Gmail OAuth |
| `GMAIL_CREDENTIALS_JSON` | Optional | Contents of `credentials.json` from Google Cloud |
| `ODOO_URL` | Optional | `https://your-odoo-server.com` |
| `ODOO_DB` | Optional | `odoo` |
| `ODOO_USERNAME` | Optional | `admin` |
| `ODOO_PASSWORD` | Optional | Your Odoo admin password |

## Trigger Manual Run

```bash
# Via GitHub CLI
gh workflow run cloud-agent.yml
gh workflow run health-monitor.yml

# Or via GitHub UI:
# Actions → Cloud Agent → Run workflow
```

## Vault Sync via Git

The cloud agent commits any new files it creates (Plans, Pending_Approval, etc.)
back to the repository. Your local machine pulls these changes, maintaining sync:

```bash
# On local machine — pull cloud agent's work
git pull origin hf-deploy
```

## Architecture

```
GitHub Actions (Cloud Agent)
    ├── Every 15 min: gmail check → Needs_Action/email/
    ├── Every 15 min: claude_processor → Plans/ + Pending_Approval/
    ├── Every 15 min: vault sync → git commit + push
    └── Sunday 00:00: CEO briefing → Briefings/

HuggingFace Space (Dashboard)
    └── Flask API: shows vault status, pending approvals

Local Machine
    ├── git pull → get cloud agent's drafts
    ├── Review Pending_Approval/
    ├── Move to Approved/
    └── approval_watcher.py → executes via Email MCP
```
