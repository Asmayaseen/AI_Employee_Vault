# AI Employee Vault

Personal AI Employee system using Claude Code + Obsidian.

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Items requiring AI processing
├── Pending_Approval/   # Items awaiting human approval
├── Approved/           # Human-approved actions
├── Done/               # Completed items
├── Logs/               # Audit logs (JSON)
├── Plans/              # AI-generated action plans
├── Briefings/          # CEO briefings and reports
├── Accounting/         # Financial tracking
├── Watchers/           # Python watcher scripts
├── MCP_Servers/        # MCP server configurations
├── Dashboard.md        # Real-time status overview
├── Company_Handbook.md # Rules of engagement
└── Business_Goals.md   # Targets and metrics
```

## Quick Start

1. Open this folder as an Obsidian vault
2. Copy `.env.example` to `.env` and fill in credentials
3. Start watchers: `python Watchers/orchestrator.py`
4. Run Claude Code from this directory

## Workflow

1. **Watchers** detect new items (email, messages, files)
2. Items are saved to `/Needs_Action/`
3. **Claude Code** processes items and creates plans
4. Sensitive actions go to `/Pending_Approval/`
5. Human moves approved items to `/Approved/`
6. **MCP Servers** execute approved actions
7. Completed items move to `/Done/`

## Security

- Never commit `.env` files
- All payments require human approval
- Audit logs retained for 90 days
- DRY_RUN=true for development

## Tier Progress

- [x] Bronze: Vault setup complete
- [ ] Bronze: First watcher working
- [ ] Silver: Multiple watchers
- [ ] Silver: MCP server integration
- [ ] Gold: Full automation
