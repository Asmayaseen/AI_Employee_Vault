# ADR-004: Human-in-the-Loop Approval via Filesystem

- **Status:** Accepted
- **Date:** 2026-02-08
- **Feature:** 002-silver-tier
- **Context:** The AI Employee must not take irreversible actions (payments, emails to new contacts, social media posts) without human approval. Need a simple, reliable approval mechanism that works with the existing Obsidian vault architecture and doesn't require additional infrastructure.

## Decision

Implement file-based approval workflow using the vault folder structure:

1. AI creates approval request as a Markdown file in `/Pending_Approval/` with structured frontmatter (action_type, risk_level, parameters, etc.)
2. Human reviews the request in Obsidian (or any file browser)
3. Human moves the file to `/Approved/` to approve or `/Rejected/` to reject
4. `approval_watcher.py` monitors these folders (5-second interval) and detects file movements
5. Approved actions are executed via MCP servers
6. All approvals/rejections are logged with timestamps in audit log

Approval thresholds per Constitution Principle II:
- All payments and financial transactions
- Emails to new contacts or bulk sends
- Social media posts and direct messages
- File deletions outside the vault
- Any action involving >$50 or new recipients

## Consequences

### Positive

- Zero additional infrastructure - uses existing vault folders
- Human-readable approval requests - Markdown files viewable in Obsidian
- Works in Obsidian UI - drag and drop between folders
- Fully auditable - Git tracks all file movements
- Simple to understand - folder structure is self-explanatory
- Crash-resilient - files survive process restarts, state is persistent
- Works offline - no network dependency for approval

### Negative

- Manual file movement required (no one-click approve button in Obsidian)
- No mobile approval support without additional tooling
- No push notification when new approvals arrive (must check manually)
- Race condition possible if multiple humans approve simultaneously
- Latency depends on approval_watcher check interval (5 seconds)

## Alternatives Considered

- **Web dashboard with approve/reject buttons**: Rejected because it requires additional web infrastructure to maintain. Adds complexity to the system. Could be added as a Platinum tier enhancement.
- **Slack/Discord bot for approvals**: Rejected because it requires an always-on bot service and cloud dependency. Violates local-first principle. Adds third-party service dependency.
- **Email-based approval (reply YES/NO)**: Rejected because it adds latency (email delivery), is harder to track state, and creates circular dependency (using email to approve email actions).
- **CLI confirmation prompts**: Rejected because it requires human to be at the terminal. Doesn't work for background/autonomous operations.

## References

- Feature Spec: `/specs/002-silver-tier/spec.md` (User Story 3)
- Implementation: `AI_Employee_Vault/Watchers/approval_watcher.py`
- Constitution: `.specify/memory/constitution.md` (Principle II: Human-in-the-Loop)
