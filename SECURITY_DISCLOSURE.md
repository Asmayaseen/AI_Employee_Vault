# Security Disclosure

## How Credentials Are Handled

### Environment Variables
All sensitive credentials are stored in `.env` files which are listed in `.gitignore` and never committed to version control.

**Location**: `AI_Employee_Vault/.env`

```
# API Keys (never committed)
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
ODOO_PASSWORD=...
META_ACCESS_TOKEN=...
TWITTER_API_KEY=...
```

### Credential Categories

| Category | Storage Method | Access Pattern |
|----------|---------------|----------------|
| Gmail OAuth | `credentials.json` + `token.json` (gitignored) | OAuth 2.0 flow |
| Odoo | Environment variables | JSON-RPC auth per session |
| Social Media | Environment variables | Bearer token / OAuth 1.0a |
| WhatsApp | Playwright session directory (gitignored) | Browser automation |
| LinkedIn | Playwright session directory (gitignored) | Browser automation |

### What Is NOT Committed

The following are excluded via `.gitignore`:
- `.env` files
- `credentials.json` / `token.json` (Google OAuth)
- `.linkedin_session/` (Playwright browser session)
- `.whatsapp_session/` (Playwright browser session)
- Any file matching `*secret*`, `*credential*`, `*token*`
- `__pycache__/`, `node_modules/`

## Human-in-the-Loop Safeguards

### Approval Required For:
- **All payments** to new recipients or amounts > $100
- **Invoice posting** above configured threshold ($500 default)
- **Social media posts** (configurable, default: require approval)
- **Email to new contacts** or bulk sends
- **File deletions** or moves outside vault

### Approval NOT Required For:
- Reading vault files
- Creating draft plans
- Fetching data from APIs (read-only)
- Email replies to known contacts (below threshold)
- Scheduled recurring posts (pre-approved templates)

### Approval Mechanism
File-based: Claude writes an approval file to `/Pending_Approval/`. The human reviews it in Obsidian and moves it to `/Approved/` to execute, or `/Rejected/` to deny.

## Safety Features

1. **DRY_RUN mode**: All action scripts support `DRY_RUN=true` which logs intended actions without executing
2. **DEV_MODE**: Development flag prevents real external actions
3. **Rate limiting**: Configurable max actions per hour per service
4. **Graceful degradation**: When services fail, actions are queued locally (except payments, which require fresh approval)
5. **Audit logging**: Every action logged with actor, target, approval status, and result
6. **90-day log retention**: All JSON logs retained for review

## Data Flow

```
User Input -> Watcher -> Vault (local) -> Claude (local) -> MCP (local) -> External API
                                  ^                                |
                                  |-- Approval file required here -|
```

All data stays local until explicitly sent via an approved MCP action. The Obsidian vault never syncs sensitive credential data.

## Reporting Issues

If you discover a security issue in this project, please report it via the repository's issue tracker.
