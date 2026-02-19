---
id: 001
title: Bronze Tier File Watcher Specification
stage: spec
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: bronze-tier
branch: 001-bronze-tier
user: asmayaseen
command: /sp.specify bronze-tier
labels: ["foundation", "file-watcher", "base-watcher", "bronze-tier"]
links:
  spec: specs/001-bronze-tier/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-bronze-tier/spec.md
tests:
  - Manual testing: File detection in Inbox
  - Manual testing: Action file creation
  - Manual testing: Deduplication logic
---

## Prompt

Create a comprehensive specification for Bronze Tier - the foundational layer of the AI Employee system.

**Requirements**:
- Implement file system monitoring for the Obsidian vault
- Detect new files dropped in /Inbox folder
- Create action items in /Needs_Action folder
- Prevent duplicate processing
- Log all activities
- Establish BaseWatcher pattern for future watchers (Gmail, LinkedIn, WhatsApp)

**Context**:
- This is the first tier - must be simple, reliable, and extensible
- No external API dependencies for Bronze tier (local only)
- Must work on Windows (WSL), macOS, and Linux
- Using Obsidian vault as the workspace
- Following SpecKitPlus methodology

**Success Criteria**:
- File detection within check interval (60 seconds)
- Zero duplicate processing
- Clean watcher pattern for Silver/Gold tier reuse
- Complete audit trail in logs

## Response snapshot

Generated comprehensive specification with:

### User Scenarios (4 stories, prioritized P1-P2):
1. **P1 - Automatic File Detection**: Core "sense" functionality - detect files in Inbox
2. **P1 - Process Deduplication**: Prevent duplicate processing via `.processed_files` tracking
3. **P2 - Vault Initialization**: Auto-create folder structure for first-time setup
4. **P2 - Activity Logging**: Audit trail in daily JSON logs

### Functional Requirements (10 total):
- FR-001: Monitor /Inbox every 60 seconds
- FR-002: Maintain tracking file `.processed_files`
- FR-003: Skip already-processed files
- FR-004: Move processed files to /Processed
- FR-005: Log all activities to Logs/[date].json
- FR-006: Create vault folder structure
- FR-007: Graceful shutdown on Ctrl+C
- FR-008: Use BaseWatcher abstract class
- FR-009: Run continuously until stopped
- FR-010: Support dry-run mode for testing

### Success Criteria (6 measurable outcomes):
- SC-001: 95% detection within 60 seconds
- SC-002: 100% deduplication accuracy
- SC-003: >99% uptime over 24 hours
- SC-004: 100% logging coverage
- SC-005: Vault initialization <5 seconds
- SC-006: Stable memory over 7 days

### Technical Context:
- Python 3.10+ with pathlib, json, logging
- BaseWatcher abstract class pattern
- Environment configuration via .env
- JSON structured logging
- No external dependencies (except python-dotenv)

### Architecture Decisions:
- **BaseWatcher Pattern**: Abstract base class for all future watchers
- **Hash-based Tracking**: Content-based deduplication
- **60-second Polling**: Balance between responsiveness and resources
- **JSON Logs**: Structured data for programmatic analysis

### Edge Cases Identified:
- Inbox folder deleted during operation
- Identical filenames with different content
- Files being written (incomplete) when detected
- Corrupted tracking file
- Concurrent file additions

### Out of Scope:
- File content processing (future tiers)
- External API integration (Silver/Gold tiers)
- File format validation
- Content summarization
- Multi-vault support

## Outcome

- ✅ **Impact**: Complete Bronze Tier specification ready for implementation planning
- 🧪 **Tests**: 4 user stories with Given/When/Then acceptance scenarios
- 📁 **Files**: `specs/001-bronze-tier/spec.md` (10,401 bytes)
- 🔁 **Next prompts**: Create implementation plan (`/sp.plan bronze-tier`)
- 🧠 **Reflection**: Spec establishes foundation pattern that Silver/Gold tiers will inherit. BaseWatcher abstraction is key architectural decision enabling multi-source monitoring.

## Evaluation notes (flywheel)

- **Failure modes observed**: None - spec creation successful on first attempt
- **Graders run and results**:
  - ✅ PASS: All mandatory sections completed (User Scenarios, Requirements, Success Criteria)
  - ✅ PASS: P1/P2 prioritization clear and justified
  - ✅ PASS: Independent testability for each user story
  - ✅ PASS: Technical context appropriate for tier
  - ✅ PASS: Out of scope clearly defined
- **Prompt variant**: Standard SpecKitPlus spec generation
- **Next experiment**: Validate BaseWatcher pattern during plan creation - ensure it supports Gmail/LinkedIn extension without modification

**Key Learnings**:
1. Bronze tier must be minimal but extensible - resist feature creep
2. BaseWatcher pattern is critical investment for future tiers
3. Deduplication is P1 (not P2) - prevents wasted API calls in future tiers
4. JSON logging enables future dashboard/analytics without database

**Architectural Significance**:
📋 **Decision**: Use abstract BaseWatcher pattern
- **Options considered**:
  1. Each watcher independent (duplicate code)
  2. Shared utility functions (less structured)
  3. Abstract base class (chosen)
- **Trade-offs**: Slight upfront complexity vs. massive code reuse in Silver/Gold
- **Rationale**: 4+ watchers planned (File, Gmail, LinkedIn, WhatsApp) - DRY principle critical

Should document as ADR if this becomes contentious during implementation.

---

**Status**: ✅ Specification Complete
**Next Step**: Implementation Plan Creation

