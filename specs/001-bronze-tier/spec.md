# Feature Specification: Bronze Tier - File System Watcher

**Feature Branch**: `001-bronze-tier`
**Created**: 2026-02-08
**Status**: Implemented (Retroactive Spec)
**Tier**: Bronze - Foundation Layer

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic File Detection (Priority: P1)

As a user, I want the AI Employee to automatically detect new files in the Inbox folder so I can have them processed without manual intervention.

**Why this priority**: This is the foundational "sense" of the AI Employee. Without automatic file detection, the entire system cannot function autonomously.

**Independent Test**: Can be fully tested by placing a file in `/Inbox/` and verifying it gets detected and processed within the check interval. Delivers immediate value by making the AI Employee aware of new work.

**Acceptance Scenarios**:

1. **Given** AI Employee is running, **When** a `.md` file is placed in `/Inbox/`, **Then** the file is detected within check interval
2. **Given** a file has been detected, **When** the file is processed, **Then** it is moved to `/Processed/` folder
3. **Given** multiple files are added simultaneously, **When** watcher runs, **Then** all files are detected and queued

---

### User Story 2 - Process Deduplication (Priority: P1)

As a user, I want the system to prevent duplicate processing of the same file so I don't get redundant outputs.

**Why this priority**: Critical for system reliability. Duplicate processing wastes API credits and creates confusion with multiple outputs for the same input.

**Independent Test**: Can be tested by placing the same file twice and verifying only one processing action is taken. Prevents waste and maintains data integrity.

**Acceptance Scenarios**:

1. **Given** a file has been processed once, **When** the same file appears again, **Then** it is skipped with a log entry
2. **Given** tracking file `.processed_files` exists, **When** watcher starts, **Then** previous processing history is loaded
3. **Given** a file is being processed, **When** watcher checks again before completion, **Then** file is not re-queued

---

### User Story 3 - Vault Initialization (Priority: P2)

As a user, I want the Obsidian vault to be automatically initialized with the required folder structure so I can start using the system immediately.

**Why this priority**: Important for first-time setup but not needed for ongoing operations. Enables quick onboarding.

**Independent Test**: Can be tested by running initialization script and verifying all required folders exist. Delivers complete working environment.

**Acceptance Scenarios**:

1. **Given** vault path is provided, **When** initialization runs, **Then** all standard folders are created (Inbox, Needs_Action, Processed, Logs, Plans, Briefings, Dashboard.md)
2. **Given** folders already exist, **When** initialization runs, **Then** existing content is preserved (idempotent)
3. **Given** initialization completes, **When** watcher starts, **Then** all required paths are accessible

---

### User Story 4 - Activity Logging (Priority: P2)

As a user, I want all file processing activities logged so I can audit what the AI Employee has done.

**Why this priority**: Important for transparency and debugging but system works without it. Enables trust and troubleshooting.

**Independent Test**: Can be tested by processing files and reviewing daily log files. Provides audit trail.

**Acceptance Scenarios**:

1. **Given** a file is processed, **When** action completes, **Then** entry is written to `Logs/[date].json`
2. **Given** an error occurs, **When** exception is caught, **Then** error details are logged with timestamp
3. **Given** logs exist for 30+ days, **When** cleanup runs, **Then** old logs are archived

---

### Edge Cases

- What happens when Inbox folder is deleted while watcher is running?
- How does system handle files with identical names but different content?
- What if a file is being written to (incomplete) when watcher detects it?
- How does system recover if `.processed_files` tracking file is corrupted?
- What happens during concurrent file additions?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST monitor `/Inbox/` folder for new `.md` files every 60 seconds
- **FR-002**: System MUST maintain a tracking file `.processed_files` with hash of processed items
- **FR-003**: System MUST skip files already in `.processed_files` to prevent duplicate processing
- **FR-004**: System MUST move processed files from `/Inbox/` to `/Processed/` folder
- **FR-005**: System MUST log all activities (file detected, processed, errors) to `Logs/[date].json`
- **FR-006**: System MUST create required folder structure if missing (Inbox, Needs_Action, Processed, Logs, Plans, Briefings)
- **FR-007**: System MUST handle graceful shutdown on Ctrl+C without data loss
- **FR-008**: System MUST use BaseWatcher abstract class for consistent watcher pattern
- **FR-009**: System MUST run continuously until stopped by user
- **FR-010**: System MUST support dry-run mode for testing without file modifications

### Non-Functional Requirements

- **NFR-001**: Check interval must be configurable (default: 60 seconds)
- **NFR-002**: Memory usage must remain under 100MB during continuous operation
- **NFR-003**: System must handle 100+ files in inbox without performance degradation
- **NFR-004**: Log files must use structured JSON format for parsing
- **NFR-005**: System must work on Windows (WSL), macOS, and Linux

### Key Entities

- **File Entry**: Represents a markdown file with attributes (path, filename, hash, processed_timestamp)
- **Processing Log**: JSON record of each action taken (timestamp, watcher, action_type, file_path, status)
- **Tracking Record**: Persisted list of processed file hashes to prevent duplication

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: File detection happens within 60 seconds of file being added to Inbox (95% of time)
- **SC-002**: Zero duplicate processing of same file content (100% accuracy)
- **SC-003**: Watcher uptime >99% over 24-hour period without crashes
- **SC-004**: All file operations logged with timestamps (100% coverage)
- **SC-005**: System successfully initializes vault structure in under 5 seconds
- **SC-006**: Memory footprint remains stable over 7-day continuous operation

## Technical Context

### Technology Stack
- **Language**: Python 3.10+
- **Dependencies**: pathlib, json, hashlib, time, logging, dotenv
- **Design Pattern**: Abstract BaseWatcher class with concrete FileWatcher implementation
- **Process Management**: Can be run via systemd, PM2, or nohup

### Integration Points
- **Obsidian Vault**: Monitors and modifies folders within Obsidian vault structure
- **Environment Variables**: Reads configuration from `.env` (VAULT_PATH, DRY_RUN, CHECK_INTERVAL)
- **File System**: Direct file operations (read, move, delete)

### Architecture Decisions
- **Why abstract BaseWatcher**: Establishes pattern for future watchers (Gmail, LinkedIn, Slack)
- **Why hash-based tracking**: Content-based deduplication even if filename changes
- **Why 60-second interval**: Balance between responsiveness and system resource usage
- **Why JSON logs**: Structured data enables programmatic analysis and dashboards

## Risks & Constraints

### Technical Risks
- **File locking**: If Obsidian has file open, move operation may fail
- **Large files**: Very large markdown files could slow down hash computation
- **Tracking file corruption**: If `.processed_files` corrupted, may reprocess all files

### Mitigation Strategies
- Retry logic with exponential backoff for file operations
- Stream-based hashing for large files
- Backup tracking file daily

### Constraints
- Must work within Obsidian vault structure (cannot modify vault settings)
- No external API dependencies for Bronze tier (local only)
- Must preserve existing vault content (cannot delete user files)

## Out of Scope

### Explicitly Excluded
- Processing file content (Bronze tier only detects, not processes)
- Email monitoring (that's Silver tier)
- Slack/LinkedIn monitoring (that's Gold tier)
- Automatic responses to file content
- File format validation beyond `.md` extension
- Content summarization or analysis
- Multi-vault support (single vault only)

### Future Enhancements (Later Tiers)
- Silver Tier: Gmail watcher integration
- Gold Tier: LinkedIn and Slack watchers
- Platinum Tier: Multi-source aggregation
- Diamond Tier: Autonomous actions based on file content

## Implementation Notes

### Files Created
- `base_watcher.py` - Abstract base class for all watchers
- `file_watcher.py` - Concrete implementation for file system monitoring
- `init_vault.py` - Vault structure initialization
- `.processed_files` - Tracking file (auto-generated)
- `Logs/[date].json` - Daily activity logs (auto-generated)

### Configuration
```bash
# .env file
VAULT_PATH=/path/to/AI_Employee_Vault
CHECK_INTERVAL=60
DRY_RUN=true  # Set to false for production
```

### Usage
```bash
# Initialize vault (one-time)
python init_vault.py

# Run file watcher
cd Watchers/
python file_watcher.py ../

# Background mode
nohup python file_watcher.py ../ > file_watcher.log 2>&1 &
```

## Testing Strategy

### Unit Tests
- Test hash generation consistency
- Test duplicate detection logic
- Test folder creation (idempotent)
- Test log entry formatting

### Integration Tests
- Test full file detection → move → log workflow
- Test recovery from missing folders
- Test handling of file locked by another process
- Test graceful shutdown

### Acceptance Tests
- Place 10 files in Inbox → Verify all detected and moved
- Place same file twice → Verify second is skipped
- Delete Inbox folder while running → Verify recreation
- Run for 24 hours → Verify no memory leaks

## Definition of Done

- [ ] BaseWatcher abstract class implemented
- [ ] FileWatcher concrete class implemented
- [ ] Vault initialization script working
- [ ] All P1 acceptance scenarios pass
- [ ] Logging to JSON functional
- [ ] Tracking file prevents duplicates
- [ ] Documentation written (README, this spec)
- [ ] Tested on WSL and Windows
- [ ] Code committed to version control
- [ ] PHR created for implementation

---

**Status**: ✅ Implemented (Retroactively documented)
**Next Step**: Create spec for Silver Tier (Gmail Watcher)

