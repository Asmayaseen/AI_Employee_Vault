---
id: 002
title: Bronze Tier Implementation Plan Creation
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: bronze-tier
branch: 001-bronze-tier
user: asmayaseen
command: /sp.plan bronze-tier
labels: ["implementation-plan", "architecture", "bronze-tier", "base-watcher"]
links:
  spec: specs/001-bronze-tier/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-bronze-tier/plan.md
tests:
  - Validated against Constitution (8 principles)
  - Reviewed component design (C1-C3)
  - Verified implementation phases
---

## Prompt

Create detailed implementation plan for Bronze Tier File System Watcher based on the specification.

**Input**: `specs/001-bronze-tier/spec.md`

**Requirements**:
- Convert user scenarios into concrete technical components
- Define implementation phases with dependencies
- Document architecture decisions with rationale
- Validate against Constitution principles
- Provide error handling strategy
- Define testing approach

**Context**:
- Building foundation for multi-tier system
- BaseWatcher must support future Gmail/LinkedIn watchers
- Must be simple enough for Bronze tier but extensible
- Python 3.10+ target
- Obsidian vault integration

**Deliverables**:
- Component breakdown (C1, C2, C3...)
- Implementation phases with task estimates
- Error handling matrix
- Security considerations
- Dependencies list

## Response snapshot

Generated comprehensive implementation plan with:

### Technical Stack Selected:
- **Language**: Python 3.10+
- **Core Libraries**: pathlib, json, logging, dotenv, abc
- **Pattern**: Abstract Base Class with concrete implementations
- **Platform**: Cross-platform (Windows/WSL, macOS, Linux)

### Constitution Validation (8/8 PASS):
1. ✅ Safety First: Read-only detection, no destructive ops
2. ✅ Human-in-the-Loop: All files → Needs_Action for review
3. ✅ Auditability: Every action logged to JSON
4. ✅ Modular Engineering: BaseWatcher pattern
5. ✅ Folder Workflow: Inbox → Needs_Action → Processed
6. ✅ Transparent State: .processed_files tracking
7. ✅ Fail Gracefully: Try-except, graceful shutdown
8. ✅ Environment Config: .env configuration

### Component Design (3 components):

**C1: BaseWatcher (Abstract Template)**
- Purpose: Establish watcher interface for all future watchers
- Responsibilities:
  - Initialize vault structure
  - Provide abstract methods: `check_for_updates()`, `create_action_file()`
  - Implement shared `log_action()` method
  - Provide run loops: `run()` continuous, `run_once()` single
  - Load environment configuration
- Key Decision: Abstract base class vs. utility functions
- Rationale: 4+ watchers planned - DRY principle critical
- Lines: ~150

**C2: FileSystemWatcher (Concrete Implementation)**
- Purpose: Monitor Inbox folder for new files
- Responsibilities:
  - Poll Inbox every 10 seconds (configurable)
  - Detect new files, skip hidden files
  - Prevent duplicates via `.processed_files`
  - Classify files by type (document, image, data, etc.)
  - Create action files with metadata and suggested actions
  - Log all activities
- Detection Logic: List → Filter hidden → Check processed → Return new
- Deduplication: Filename-based tracking (simple, effective)
- Lines: ~250

**C3: Vault Initialization**
- Purpose: Ensure folder structure exists
- Handled automatically by BaseWatcher.__init__
- Idempotent: Safe to run multiple times
- Folders: Inbox, Needs_Action, Logs (minimum for Bronze)

### Implementation Phases (7 phases):

**Phase 1: Foundation** (Blocking all)
- BaseWatcher abstract class
- Configuration (.env, requirements.txt)
- Logging infrastructure
- Estimated: 150 lines, 4-6 hours

**Phase 2: File Detection** (User Story 1)
- FileSystemWatcher class
- check_for_updates() implementation
- create_action_file() basic structure
- Deduplication tracking
- Estimated: 100 lines, 3-4 hours

**Phase 3: File Classification** (Enhancement)
- Type detection (_get_file_type)
- Suggested actions (_get_suggested_actions)
- File size formatting
- Estimated: 70 lines, 2-3 hours

**Phase 4: Deduplication** (User Story 2)
- .processed_files persistence
- Load/save tracking file
- Handle corruption
- Estimated: 30 lines, 1-2 hours

**Phase 5: Error Handling** (Reliability)
- Try-except blocks
- Graceful shutdown
- Missing folder recovery
- File lock handling
- Estimated: 40 lines, 2-3 hours

**Phase 6: Configuration** (Flexibility)
- .env template
- Configuration docs
- DRY_RUN mode
- Estimated: 20 lines, 1-2 hours

**Phase 7: Documentation** (Polish)
- README with usage guide
- API documentation
- Troubleshooting guide
- Examples
- Estimated: 0 lines code, 4-6 hours docs

### Error Handling Matrix:
Defined 7 error scenarios with detection, recovery, and user impact:
- Inbox folder deleted → Recreate, continue
- File locked → Skip, retry next cycle
- Corrupted tracking → Reset, backup original
- Disk full → Log critical, stop gracefully
- Permission denied → Log, skip file
- Crash → Graceful shutdown via Ctrl+C
- Large file → Process anyway, log warning

### Architecture Decisions Documented:

**Why polling instead of OS events?**
- Polling simpler, cross-platform
- 10s interval adequate for use case
- Avoids watchdog library dependency
- Decision: KISS principle

**Why filename-based deduplication?**
- Simple and effective
- No hash computation overhead
- Good enough for Bronze tier
- Can enhance to content-based in future if needed

**Why JSON logs instead of database?**
- Lightweight (no DB setup)
- Human-readable
- Easy to parse later
- Adequate for <10k actions/day

### Project Structure Defined:
Complete file tree showing:
- .specify/ methodology files
- specs/ feature documentation
- history/prompts/ audit trail
- AI_Employee_Vault/ workspace
- Watchers/ implementations

### Dependencies:
Minimal dependencies (1 external):
- `python-dotenv>=1.0.0` (environment config)
- All other: Python standard library

## Outcome

- ✅ **Impact**: Complete technical blueprint ready for task generation
- 🧪 **Tests**: Error handling strategy covers 7 failure modes
- 📁 **Files**: `specs/001-bronze-tier/plan.md` (15,234 bytes)
- 🔁 **Next prompts**: Generate task breakdown (`/sp.tasks bronze-tier`)
- 🧠 **Reflection**: Component design is minimal but complete. BaseWatcher abstraction validated as good investment - will save significant code in Silver/Gold tiers. Polling approach simpler than initially considered event-driven architecture.

## Evaluation notes (flywheel)

- **Failure modes observed**: None - plan generation successful
- **Graders run and results**:
  - ✅ PASS: All 8 Constitution principles validated
  - ✅ PASS: Component responsibilities clearly defined
  - ✅ PASS: Error handling comprehensive
  - ✅ PASS: Implementation phases have clear dependencies
  - ✅ PASS: Complexity tracking justifies simplicity choices
  - ✅ PASS: Security considerations addressed
- **Prompt variant**: Standard SpecKitPlus plan generation
- **Next experiment**: During task generation, ensure phases can be parallelized where possible

**Key Technical Decisions**:

1. **Polling vs. Event-Driven**
   - Considered: watchdog library for file system events
   - Chose: Simple polling every 10s
   - Rationale: KISS - polling adequate for use case, avoids dependency

2. **Filename vs. Content-Hash Tracking**
   - Considered: Content hashing for true deduplication
   - Chose: Filename tracking (simpler)
   - Rationale: Good enough for Bronze, can enhance later if needed

3. **JSON Logs vs. Database**
   - Considered: SQLite for structured logging
   - Chose: Daily JSON files
   - Rationale: Lightweight, human-readable, no setup overhead

4. **Abstract Base Class vs. Utility Functions**
   - Considered: Shared utilities without inheritance
   - Chose: Abstract base class pattern
   - Rationale: Enforces interface contract for 4+ future watchers

**Risks Identified & Mitigated**:
- **Risk**: BaseWatcher too rigid for future watchers
  - **Mitigation**: Keep interface minimal - only `check_for_updates()` and `create_action_file()`
- **Risk**: Filename tracking breaks if file renamed
  - **Mitigation**: Acceptable for Bronze tier, document in limitations
- **Risk**: JSON logs grow unbounded
  - **Mitigation**: Daily files enable easy cleanup, add log rotation in future

**Complexity Justifications**:
Every simplicity choice justified:
- KISS: Polling over events
- YAGNI: No content analysis in Bronze
- DRY: BaseWatcher for code reuse
- Single Responsibility: FileSystemWatcher only detects

**Security Notes**:
- No credentials needed (Bronze tier local only)
- File paths logged (safe in private vault)
- No file content logged
- Vault access controlled by OS permissions

---

**Status**: ✅ Implementation Plan Complete
**Next Step**: Task Generation for phased execution
**Estimated Total Effort**: 20-25 hours implementation + 6-8 hours documentation

