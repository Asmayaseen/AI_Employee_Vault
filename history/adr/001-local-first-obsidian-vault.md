# ADR-001: Local-First Architecture with Obsidian Vault

- **Status:** Accepted
- **Date:** 2026-02-05
- **Feature:** 001-bronze-tier
- **Context:** The AI Employee system needs persistent storage for state, actions, plans, and audit trails. The system handles sensitive data (banking, personal emails, credentials) and must prioritize privacy. Storage must be debuggable, survive process crashes, and enable human oversight.

## Decision

Use Obsidian (local Markdown vault) as the single source of truth for all system state. Implement a file-based state machine with folders representing workflow stages:

- `/Inbox/` - Raw incoming items
- `/Needs_Action/` - Items requiring AI processing
- `/Plans/` - Generated action plans
- `/Pending_Approval/` - Actions awaiting human review
- `/Approved/` - Human-approved actions
- `/Rejected/` - Human-rejected actions
- `/Done/` - Completed and archived tasks
- `/Logs/` - JSON audit logs
- `/Briefings/` - CEO briefing reports

All data stored as Markdown files with YAML frontmatter for structured metadata. File movement between folders represents state transitions.

## Consequences

### Positive

- Complete data sovereignty - all sensitive data remains on user's machine
- Human-readable state - anyone can inspect system status by opening files
- Git-versioned - full history of all state changes
- Crash-resilient - file-based state survives process crashes and restarts
- No cloud dependency - works offline, no vendor lock-in
- Easy debugging - standard text files, no database queries needed
- Obsidian provides rich linking, search, and visualization for free

### Negative

- No concurrent write safety - single-user system only
- Limited query capabilities compared to a database
- Manual backup responsibility falls on user
- No real-time collaboration features
- File system performance degrades with very large file counts (>10k)
- No built-in schema validation for frontmatter

## Alternatives Considered

- **SQLite**: Rejected because it's harder to inspect and debug manually. Users can't browse state via a folder structure. Doesn't integrate with Obsidian's visualization.
- **PostgreSQL**: Rejected as over-engineered for a single-user local system. Adds cloud dependency for hosting. Operational overhead for maintenance.
- **Firebase/Cloud DB**: Rejected because it directly violates the local-first principle. Sensitive financial and personal data would leave the user's machine.
- **Plain filesystem without Obsidian**: Rejected because it loses Obsidian's rich linking, graph view, search, and plugin ecosystem that provides the "dashboard" experience.

## References

- Feature Spec: `/specs/001-bronze-tier/spec.md`
- Implementation Plan: `/specs/001-bronze-tier/plan.md`
- Constitution: `.specify/memory/constitution.md` (Principle I: Local-First Architecture)
