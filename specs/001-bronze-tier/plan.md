# Implementation Plan: Bronze Tier - File System Watcher

**Feature Branch**: `001-bronze-tier`
**Created**: 2026-02-08
**Spec Reference**: `specs/001-bronze-tier/spec.md`
**Status**: Implemented (Retroactive Documentation)

---

## Summary

Bronze Tier implements the foundational "sensing" layer of the AI Employee system through file system monitoring. The system consists of:

1. **BaseWatcher** - Abstract template class establishing the watcher pattern for all future watchers
2. **FileSystemWatcher** - Concrete implementation monitoring the Inbox folder for new files
3. **Vault Structure** - Standardized Obsidian vault folder organization

This tier provides the minimum viable foundation for the AI Employee to detect work (files dropped in Inbox), track processing state (deduplication), and create structured action items for human review.

---

## Technical Context

### Technology Stack
- **Language**: Python 3.10+
- **Core Libraries**:
  - `pathlib` - Cross-platform file path handling
  - `json` - Structured logging format
  - `logging` - Activity tracking
  - `dotenv` - Environment configuration
  - `abc` (Abstract Base Classes) - Design pattern enforcement

### Platform Support
- Windows 10/11 (including WSL)
- macOS 10.15+
- Linux (Ubuntu 20.04+)

### Constraints
- Must work within Obsidian vault (no modification of Obsidian settings)
- No external API dependencies (local file system only)
- Must be lightweight (<100MB memory, <5% CPU)
- Configuration via environment variables (.env)

---

## Constitution Check

Validating against 8 core principles from `.specify/memory/constitution.md`:

| Principle | Status | Implementation |
|-----------|--------|----------------|
| **1. Safety First** | ✅ PASS | Read-only file detection, no destructive operations without tracking |
| **2. Human-in-the-Loop** | ✅ PASS | All files create action items in Needs_Action for human review |
| **3. Auditability** | ✅ PASS | Every action logged to Logs/[date].json with timestamps |
| **4. Modular Engineering** | ✅ PASS | BaseWatcher pattern enables clean extension for future watchers |
| **5. Folder Workflow** | ✅ PASS | Strict folder separation: Inbox → Needs_Action → Processed |
| **6. Transparent State** | ✅ PASS | .processed_files tracking file shows what's been handled |
| **7. Fail Gracefully** | ✅ PASS | Try-except blocks, graceful shutdown on Ctrl+C, error logging |
| **8. Environment Config** | ✅ PASS | .env file for VAULT_PATH, DRY_RUN, CHECK_INTERVAL |

**Result**: ALL 8 PRINCIPLES PASS ✅

---

## Project Structure

```
AI_Employee/
├── .env                                # Environment configuration
├── .gitignore                          # Exclude secrets and temp files
├── requirements.txt                    # Python dependencies
│
├── .specify/                           # SpecKitPlus methodology files
│   ├── memory/
│   │   └── constitution.md            # Core principles
│   ├── templates/                     # Spec/plan/task templates
│   └── scripts/                       # Automation scripts
│
├── specs/                              # Feature specifications
│   └── 001-bronze-tier/
│       ├── spec.md                    # This feature's specification
│       ├── plan.md                    # This file - implementation plan
│       └── tasks.md                   # Task breakdown
│
├── history/                            # Audit trail
│   └── prompts/
│       └── 001-bronze-tier/
│           ├── 001-spec-creation.spec.prompt.md
│           ├── 002-plan-creation.plan.prompt.md
│           └── 003-implementation.green.prompt.md
│
└── AI_Employee_Vault/                  # Obsidian vault (user workspace)
    ├── Inbox/                         # Drop zone for files
    ├── Needs_Action/                  # Action items created by watchers
    ├── Processed/                     # Completed items (future)
    ├── Logs/                          # Daily activity logs (JSON)
    ├── Plans/                         # Generated plans (future)
    ├── Briefings/                     # CEO reports (future)
    ├── Dashboard.md                   # System status overview
    ├── .processed_files               # Deduplication tracking
    │
    └── Watchers/                      # Watcher implementations
        ├── base_watcher.py            # C1: Abstract base class
        ├── filesystem_watcher.py      # C2: File monitoring
        ├── test_filesystem.py         # C3: Unit tests
        └── requirements.txt           # Dependencies
```

---

## Component Design

### C1: BaseWatcher (Abstract Pattern)

**Purpose**: Establish consistent interface and shared behavior for all watchers.

**Responsibilities**:
- Initialize vault structure (create folders if missing)
- Provide abstract methods: `check_for_updates()`, `create_action_file()`
- Implement shared logging via `log_action()`
- Provide run loop: `run()` for continuous operation, `run_once()` for testing
- Load configuration from environment variables
- Support dry-run mode for safe testing

**Key Methods**:
```python
class BaseWatcher(ABC):
    def __init__(vault_path, check_interval)

    @abstractmethod
    def check_for_updates() -> list

    @abstractmethod
    def create_action_file(item) -> Path

    def log_action(action_type, details)
    def run()  # Continuous loop
    def run_once()  # Single check
```

**Configuration**:
- `VAULT_PATH` - Path to Obsidian vault (default: current directory)
- `DRY_RUN` - Test mode without actual file operations (default: true)
- `CHECK_INTERVAL` - Seconds between checks (configurable per watcher)

**Logging Format** (JSON):
```json
{
  "timestamp": "2026-02-08T10:30:45",
  "watcher": "FileSystemWatcher",
  "action_type": "file_received",
  "dry_run": true,
  "filename": "invoice.pdf",
  "file_type": "document",
  "size": 245678
}
```

---

### C2: FileSystemWatcher (Concrete Implementation)

**Purpose**: Monitor Inbox folder for new files and create action items.

**Responsibilities**:
- Poll Inbox folder every `check_interval` seconds (default: 10s)
- Detect new files (skip hidden files starting with `.`)
- Prevent duplicate processing using `.processed_files` tracking
- Create structured action files in Needs_Action with metadata
- Classify files by type (document, image, data, etc.)
- Provide type-appropriate suggested actions
- Log all activities to daily JSON log

**Detection Logic**:
1. List all files in Inbox
2. Filter out hidden files (`.` prefix)
3. Check against `.processed_files` set
4. Return list of new files

**Action File Format**:
```markdown
---
type: file_drop
source: inbox
original_name: invoice.pdf
file_type: document
size_bytes: 245678
received: 2026-02-08T10:30:45
priority: medium
status: pending
---

# New File: invoice.pdf

## File Details
- **Name:** invoice.pdf
- **Type:** document
- **Size:** 240 KB
- **Received:** 2026-02-08 10:30

## Original Location
`/path/to/AI_Employee_Vault/Inbox/invoice.pdf`

## Suggested Actions
- [ ] Review document content
- [ ] Extract key information
- [ ] File in appropriate folder
- [ ] Share with relevant party if needed

## Notes
> Add any notes about this file here

---
*Created by FileSystemWatcher*
```

**File Type Classification**:
- **Documents**: .pdf, .doc, .docx → Review, extract info, file
- **Spreadsheets**: .xls, .xlsx, .csv → Review data, validate, import
- **Images**: .jpg, .png, .gif → Categorize, OCR if needed
- **Data**: .json, .csv → Parse, validate, import
- **Archives**: .zip, .rar → Extract, review contents
- **Unknown**: Suggest manual review

**Deduplication Strategy**:
- Track processed files by filename in `.processed_files`
- Load tracking file on watcher startup
- Add to set after creating action file
- Persist to disk after each processing

---

### C3: Vault Initialization

**Purpose**: Ensure required folder structure exists before watcher runs.

**Responsibilities**:
- Create standard folders if missing (idempotent)
- Initialize Dashboard.md if not exists
- Create .env.example template
- Verify write permissions

**Standard Folders**:
```
AI_Employee_Vault/
├── Inbox/           # File drop zone
├── Needs_Action/    # Action items for review
├── Processed/       # Completed items (future)
├── Logs/            # Activity logs (auto-created)
├── Plans/           # Generated plans (future)
├── Briefings/       # CEO reports (future)
└── Watchers/        # Watcher scripts
```

**Initialization** (handled automatically by BaseWatcher.__init__):
```python
self.inbox.mkdir(exist_ok=True)
self.needs_action.mkdir(exist_ok=True)
self.logs.mkdir(exist_ok=True)
```

---

## Error Handling Strategy

| Error Scenario | Detection | Recovery | User Impact |
|----------------|-----------|----------|-------------|
| **Inbox folder deleted** | Exception on `iterdir()` | Recreate folder, log warning | Watcher continues |
| **File locked (in use)** | OSError on file operation | Skip file this cycle, retry next | File processed when unlocked |
| **Corrupted tracking file** | JSONDecodeError | Initialize empty set, backup corrupted file | May reprocess files |
| **Disk full** | OSError on write | Log error, stop gracefully | Manual intervention needed |
| **Permission denied** | PermissionError | Log error, skip file | File skipped, logged |
| **Crash/unexpected exit** | - | Graceful shutdown on Ctrl+C | Clean exit, logs saved |
| **Large file (>100MB)** | Check size before processing | Log warning, process anyway | May slow down watcher |

**Error Logging**:
All errors logged to:
1. Console (stderr) via Python logging
2. Daily JSON log file: `Logs/[YYYY-MM-DD].json`

**Graceful Shutdown**:
- Catch KeyboardInterrupt (Ctrl+C)
- Save current state (.processed_files)
- Log shutdown event
- Exit cleanly

---

## Security Considerations

### Credential Management
- **N/A for Bronze Tier** - No external APIs, no credentials needed
- Future tiers: Use .env for API keys, add to .gitignore

### File Access
- Watcher has read access to Inbox
- Watcher has write access to Needs_Action and Logs
- No access to user's broader file system
- Files stay within vault boundary

### Logging Sensitivity
- Do not log file contents (only metadata)
- File paths logged for debugging (safe in private vault)
- No PII captured (filenames may contain PII - user responsibility)

### Vault Security
- .processed_files contains only filenames (no sensitive data)
- Logs contain timestamps, sizes, types (no content)
- All files remain in user-controlled Obsidian vault

---

## Dependencies

### Python Standard Library (No Installation)
- `pathlib` - File path operations
- `json` - Log file format
- `logging` - Activity logging
- `time` - Sleep intervals
- `datetime` - Timestamps
- `abc` - Abstract base class
- `shutil` - File operations (future)

### Third-Party (requirements.txt)
```txt
python-dotenv>=1.0.0    # Environment variable loading
```

**Installation**:
```bash
pip install -r requirements.txt
```

---

## Implementation Order

### Phase 1: Foundation (P1 - Blocking)
**Goal**: Establish base architecture

**Tasks**:
1. Create project structure (folders, .gitignore)
2. Create .env.example template
3. Implement BaseWatcher abstract class
   - `__init__` with vault initialization
   - Abstract methods: `check_for_updates()`, `create_action_file()`
   - Shared method: `log_action()`
   - Run loop: `run()` and `run_once()`
4. Write BaseWatcher unit tests
5. Document BaseWatcher API

**Deliverables**:
- `base_watcher.py` (150 lines)
- `test_base_watcher.py`
- `.env.example`

**Acceptance**:
- BaseWatcher can be instantiated with test subclass
- Folders auto-created on init
- Logging works to JSON file
- Dry-run mode functional

---

### Phase 2: File Detection (P1 - User Story 1)
**Goal**: Implement file monitoring

**Tasks**:
1. Create FileSystemWatcher class inheriting BaseWatcher
2. Implement `check_for_updates()`:
   - List Inbox files
   - Filter hidden files
   - Check against processed set
3. Implement `create_action_file()`:
   - Generate action file with metadata
   - Classify file type
   - Add suggested actions
4. Add `.processed_files` tracking:
   - `_load_processed()` on init
   - `_save_processed()` after processing
5. Test with various file types

**Deliverables**:
- `filesystem_watcher.py` (200 lines)
- `test_filesystem_watcher.py`

**Acceptance**:
- New file in Inbox detected within check interval
- Action file created in Needs_Action
- File added to .processed_files
- Log entry created

---

### Phase 3: File Classification (P2 - Enhancement)
**Goal**: Smart file type handling

**Tasks**:
1. Implement `_get_file_type()` with extension mapping
2. Implement `_get_suggested_actions()` per file type
3. Add file size formatting (`_format_size()`)
4. Test with 10+ different file types

**Deliverables**:
- Enhanced `filesystem_watcher.py` (+50 lines)
- Test files for each type

**Acceptance**:
- PDFs classified as "document" with review actions
- Images classified as "image" with OCR suggestion
- CSVs classified as "data" with import actions
- Unknown files get generic review action

---

### Phase 4: Deduplication (P1 - User Story 2)
**Goal**: Prevent duplicate processing

**Tasks**:
1. Implement set-based tracking in memory
2. Persist to `.processed_files` after each file
3. Load on watcher startup
4. Handle corrupted tracking file (reset to empty)
5. Test with duplicate file drops

**Deliverables**:
- Deduplication logic in `filesystem_watcher.py`
- Test: Drop same file twice

**Acceptance**:
- First file processed normally
- Second file skipped with log entry
- Tracking file persists across watcher restarts

---

### Phase 5: Error Handling (P2 - Reliability)
**Goal**: Graceful error recovery

**Tasks**:
1. Add try-except blocks in run loop
2. Implement graceful shutdown (Ctrl+C)
3. Handle missing Inbox folder
4. Handle file lock errors
5. Log all errors to JSON

**Deliverables**:
- Error handling in `filesystem_watcher.py` (+30 lines)
- Error test scenarios

**Acceptance**:
- Watcher survives Inbox deletion (recreates)
- Locked files skipped, logged, retried next cycle
- Ctrl+C shuts down cleanly
- All errors logged

---

### Phase 6: Configuration (P2 - Flexibility)
**Goal**: Environment-based config

**Tasks**:
1. Create `.env.example` with all options
2. Load config via `python-dotenv`
3. Support VAULT_PATH, CHECK_INTERVAL, DRY_RUN
4. Document configuration options

**Deliverables**:
- `.env.example`
- Configuration documentation in README

**Acceptance**:
- Watcher reads .env on startup
- CHECK_INTERVAL changes polling speed
- DRY_RUN prevents file modifications
- Missing .env uses defaults

---

### Phase 7: Documentation & Testing (P3 - Polish)
**Goal**: Complete package ready for use

**Tasks**:
1. Write comprehensive README.md
2. Create usage examples
3. Write troubleshooting guide
4. Run full test suite
5. Document API for future watchers
6. Create quickstart script

**Deliverables**:
- README.md with usage guide
- `examples/` folder with sample code
- Test coverage report
- Quickstart shell script

**Acceptance**:
- New user can set up in <5 minutes
- All tests pass
- Documentation covers common issues
- Examples run successfully

---

## Complexity Tracking

| Principle | Decision | Justification |
|-----------|----------|---------------|
| **KISS** | Use file system polling instead of OS event watching | Polling is simpler, cross-platform, adequate for 10s interval |
| **YAGNI** | No file content analysis in Bronze tier | Content processing is future tier - Bronze only detects |
| **DRY** | BaseWatcher extracts shared logic | Avoid duplication when adding Gmail/LinkedIn watchers |
| **Single Responsibility** | FileSystemWatcher only monitors files | No processing, no decision-making - just detection |

**Why Not Use watchdog Library?**
- Adds external dependency
- More complex (event-driven)
- Polling is sufficient for 10s check interval
- Easier to understand and debug

**Why JSON Logs Instead of Database?**
- Lightweight (no DB setup)
- Human-readable
- Easy to parse programmatically later
- Adequate for <10,000 actions/day

---

## Artifacts Generated

### Code Files
- [ ] `base_watcher.py` (150 lines)
- [ ] `filesystem_watcher.py` (250 lines)
- [ ] `test_base_watcher.py` (100 lines)
- [ ] `test_filesystem_watcher.py` (150 lines)
- [ ] `requirements.txt` (1 line)

### Documentation
- [ ] `README.md` - Usage guide
- [ ] `.env.example` - Configuration template
- [ ] `specs/001-bronze-tier/spec.md` - Feature specification
- [ ] `specs/001-bronze-tier/plan.md` - This implementation plan
- [ ] `specs/001-bronze-tier/tasks.md` - Task breakdown

### Generated Files (Runtime)
- [ ] `.processed_files` - Tracking file
- [ ] `Logs/[YYYY-MM-DD].json` - Daily activity logs
- [ ] `Needs_Action/FILE_*.md` - Action items

### History (Audit Trail)
- [ ] `history/prompts/001-bronze-tier/001-spec-creation.spec.prompt.md`
- [ ] `history/prompts/001-bronze-tier/002-plan-creation.plan.prompt.md`
- [ ] `history/prompts/001-bronze-tier/003-task-generation.tasks.prompt.md`
- [ ] `history/prompts/001-bronze-tier/004-implementation.green.prompt.md`

---

## Next Steps

1. **Review this plan** - Ensure technical approach is sound
2. **Generate tasks** - Run `/sp.tasks bronze-tier` to create detailed task list
3. **Begin implementation** - Follow phases 1-7 in order
4. **Test incrementally** - Validate each phase before moving to next
5. **Document learnings** - Create PHRs for each major decision
6. **Prepare for Silver Tier** - Gmail watcher will reuse BaseWatcher pattern

---

**Status**: ✅ Implemented (Retroactive Documentation)
**Implementation Date**: 2026-02-05 to 2026-02-07
**Next Spec**: `specs/002-silver-tier/spec.md` (Gmail, WhatsApp, LinkedIn watchers)

