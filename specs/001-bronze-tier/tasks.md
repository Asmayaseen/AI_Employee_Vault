# Task List: Bronze Tier - File System Watcher

**Feature Branch**: `001-bronze-tier`
**Created**: 2026-02-08
**Plan Reference**: `specs/001-bronze-tier/plan.md`
**Status**: Completed (Retroactive Documentation)

---

## Task Organization

Tasks are organized by implementation phases from the plan. Each task includes:
- **ID**: Unique task identifier
- **[P]**: Indicates task can run in parallel with others
- **[Story]**: Maps to user story (US1, US2, US3, US4)
- **Status**: ✅ Done | ⏳ In Progress | ⏸️ Blocked | ❌ Failed

**Dependencies**: Tasks must be completed in phase order, but tasks within a phase marked [P] can be done in parallel.

---

## Phase 1: Foundation (Blocking All Stories)

### Setup & Structure

**[001]** [P] Create project directory structure
- Create `AI_Employee_Vault/Watchers/` directory
- Create `specs/001-bronze-tier/` directory
- Create `history/prompts/001-bronze-tier/` directory
- **Status**: ✅ Done
- **Files**: Directory structure
- **Test**: Verify folders exist

**[002]** [P] Create .gitignore file
- Ignore `.env`, `*.pyc`, `__pycache__/`, `.processed_*`
- Ignore `Logs/*.json`, `token.json`, `credentials.json`
- **Status**: ✅ Done
- **Files**: `.gitignore`
- **Test**: Git status shows no ignored files

**[003]** [P] Create .env.example template
- Document VAULT_PATH (default: current directory)
- Document CHECK_INTERVAL (default: 60)
- Document DRY_RUN (default: true)
- **Status**: ✅ Done
- **Files**: `.env.example`
- **Test**: File contains all required variables

**[004]** [P] Create requirements.txt
- Add `python-dotenv>=1.0.0`
- **Status**: ✅ Done
- **Files**: `requirements.txt`
- **Test**: `pip install -r requirements.txt` succeeds

### BaseWatcher Implementation

**[005]** Implement BaseWatcher.__init__
- Accept `vault_path` and `check_interval` parameters
- Load environment variables via dotenv
- Initialize standard folders (inbox, needs_action, logs)
- Create folders if missing (mkdir with exist_ok=True)
- Set up logging with class name
- **Status**: ✅ Done
- **Files**: `AI_Employee_Vault/Watchers/base_watcher.py`
- **Lines**: ~60
- **Test**: Instantiate test subclass, verify folders created

**[006]** Implement BaseWatcher abstract methods
- Define `check_for_updates()` abstract method
- Define `create_action_file(item)` abstract method
- Add docstrings with type hints
- **Status**: ✅ Done
- **Files**: `base_watcher.py`
- **Lines**: +20
- **Test**: Cannot instantiate BaseWatcher directly (raises TypeError)

**[007]** Implement BaseWatcher.log_action()
- Accept `action_type` and `details` dict
- Create log entry with timestamp, watcher name, action type
- Append to daily JSON file: `Logs/[YYYY-MM-DD].json`
- Handle existing logs (read, append, write)
- Handle corrupted JSON (initialize empty list)
- **Status**: ✅ Done
- **Files**: `base_watcher.py`
- **Lines**: +30
- **Test**: Call log_action(), verify JSON file created with entry

**[008]** Implement BaseWatcher.run() loop
- Infinite while True loop
- Call `check_for_updates()` to get items
- For each item, call `create_action_file()`
- Log success for each item
- Sleep for `check_interval` seconds
- Catch KeyboardInterrupt for graceful shutdown
- Catch general exceptions, log errors, continue
- **Status**: ✅ Done
- **Files**: `base_watcher.py`
- **Lines**: +20
- **Test**: Run with test subclass, verify loop runs, Ctrl+C stops cleanly

**[009]** Implement BaseWatcher.run_once()
- Single execution (no loop)
- Call `check_for_updates()` once
- Process all returned items
- Return immediately
- **Status**: ✅ Done
- **Files**: `base_watcher.py`
- **Lines**: +10
- **Test**: Run once, verify single execution, no loop

---

## Phase 2: File Detection (User Story 1)

### FileSystemWatcher Core

**[010]** [US1] Create FileSystemWatcher class structure
- Inherit from BaseWatcher
- Override `__init__` with default check_interval=10
- Call `super().__init__()`
- Initialize empty set: `self.processed_files`
- **Status**: ✅ Done
- **Files**: `AI_Employee_Vault/Watchers/filesystem_watcher.py`
- **Lines**: ~20
- **Test**: Instantiate FileSystemWatcher, verify inheritance

**[011]** [US1] Implement _load_processed()
- Check if `.processed_files` exists in vault root
- If exists, read lines into set
- If not exists, initialize empty set
- Call from `__init__`
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +10
- **Test**: Create .processed_files with test data, verify loaded into set

**[012]** [US1] Implement _save_processed()
- Write `self.processed_files` set to `.processed_files`
- One filename per line
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +5
- **Test**: Modify set, call _save_processed(), verify file written

**[013]** [US1] Implement check_for_updates()
- List all files in `self.inbox` using `iterdir()`
- Filter: only files (not directories)
- Filter: skip hidden files (name starts with `.`)
- Filter: skip if filename in `self.processed_files`
- Return list of Path objects
- Log found files
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +15
- **Test**: Drop 3 files in Inbox (1 hidden, 1 processed), verify 1 returned

**[014]** [US1] Implement create_action_file() - Basic structure
- Generate timestamp: `YYYYMMDD_HHMMSS`
- Create action filename: `FILE_{timestamp}_{original_stem}.md`
- Build frontmatter with metadata (type, source, name, received)
- Build markdown body with file details
- Write to `Needs_Action/` folder
- Return Path to action file
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +40
- **Test**: Process test file, verify action file created with correct format

**[015]** [US1] Add file to processed set after action file creation
- After creating action file, add `file_path.name` to `self.processed_files`
- Call `_save_processed()`
- Call `self.log_action()` with file details
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +5
- **Test**: Process file, verify added to .processed_files

---

## Phase 3: File Classification (Enhancement)

### Type Detection

**[016]** [P] Implement _get_file_type()
- Create extension-to-type mapping dict
- Documents: .pdf, .doc, .docx
- Spreadsheets: .xls, .xlsx, .csv
- Images: .jpg, .jpeg, .png, .gif
- Data: .json, .csv
- Archives: .zip, .rar
- Text: .txt, .md
- Audio: .mp3, .wav
- Video: .mp4, .mov
- Default: 'unknown'
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +20
- **Test**: Test each extension, verify correct type returned

**[017]** [P] Implement _get_suggested_actions()
- Create type-to-actions mapping dict
- Documents: Review, extract info, file, share
- Spreadsheets: Review data, validate, import, summarize
- Images: Review, categorize, OCR if needed
- Data: Parse, validate, import, backup
- Archives: Extract, review contents
- Unknown: Manual review needed
- Format as markdown checklist
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +50
- **Test**: Test each type, verify appropriate actions returned

**[018]** [P] Implement _format_size() helper
- Convert bytes to human-readable (KB, MB, GB)
- Use 1024 as divisor
- Return string with unit
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +10
- **Test**: Test various sizes (100, 1024, 1048576), verify formatting

**[019]** Integrate classification into create_action_file()
- Call `_get_file_type(file_path.suffix)`
- Call `_get_suggested_actions(file_type)`
- Call `_format_size(file_path.stat().st_size)`
- Include in action file frontmatter and body
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +10
- **Test**: Process PDF, verify correct type and actions in action file

---

## Phase 4: Deduplication (User Story 2)

### Duplicate Prevention

**[020]** [US2] Test duplicate detection logic
- Drop file named "test.txt" in Inbox
- Verify action file created
- Drop same "test.txt" again
- Verify NO new action file created
- Verify log entry shows "skipped duplicate"
- **Status**: ✅ Done
- **Files**: Test script
- **Test**: Manual test with duplicate file

**[021]** [US2] Handle tracking file corruption
- Add try-except in `_load_processed()`
- If read fails or invalid format, log warning
- Initialize empty set
- Backup corrupted file to `.processed_files.backup`
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +10
- **Test**: Create invalid .processed_files, verify recovery

**[022]** [US2] Test persistence across restarts
- Start watcher, process file
- Stop watcher (Ctrl+C)
- Restart watcher
- Drop same file again
- Verify file skipped (loaded from .processed_files)
- **Status**: ✅ Done
- **Files**: Test script
- **Test**: Manual restart test

---

## Phase 5: Error Handling (Reliability)

### Graceful Failures

**[023]** [P] Add graceful shutdown
- Catch KeyboardInterrupt in run() loop
- Log "Stopping watcher" message
- Save current state (_save_processed())
- Exit cleanly with break
- **Status**: ✅ Done
- **Files**: `base_watcher.py`
- **Lines**: Already implemented in [008]
- **Test**: Start watcher, press Ctrl+C, verify clean exit

**[024]** [P] Handle missing Inbox folder
- Add try-except around `self.inbox.iterdir()` in check_for_updates()
- If folder deleted, log warning
- Recreate folder via BaseWatcher init logic
- Continue operation
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +5
- **Test**: Delete Inbox while running, verify recreated

**[025]** [P] Handle file lock errors
- Add try-except around file operations
- Catch PermissionError, OSError
- Log warning with filename
- Skip file this cycle (will retry next cycle)
- Continue processing other files
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`
- **Lines**: +10
- **Test**: Lock file (open in editor), verify skipped and logged

**[026]** [P] Handle disk full scenario
- Catch OSError when writing action file or log
- Log critical error
- Attempt to write to stderr
- Continue (don't crash)
- **Status**: ✅ Done
- **Files**: `filesystem_watcher.py`, `base_watcher.py`
- **Lines**: +10
- **Test**: Simulate with write permission removal

**[027]** Log all errors to JSON
- All exceptions logged via `self.log_action("error", {...})`
- Include error type, message, filename if applicable
- **Status**: ✅ Done
- **Files**: Implemented across all handlers
- **Test**: Trigger error, verify logged to JSON

---

## Phase 6: Configuration (Flexibility)

### Environment Config

**[028]** [P] Document all config options in .env.example
- VAULT_PATH with description and example
- CHECK_INTERVAL with description and default (60)
- DRY_RUN with description and default (true)
- Add comments explaining each option
- **Status**: ✅ Done
- **Files**: `.env.example`
- **Test**: File is clear and complete

**[029]** [P] Load config in BaseWatcher
- Use `os.getenv()` with defaults
- vault_path: default to current directory '.'
- dry_run: default to 'true', parse as boolean
- **Status**: ✅ Done
- **Files**: `base_watcher.py`
- **Lines**: Already implemented in [005]
- **Test**: Run without .env, verify defaults used

**[030]** [P] Test config override
- Create .env with custom values
- Run watcher
- Verify values loaded correctly
- **Status**: ✅ Done
- **Files**: Test script
- **Test**: Set CHECK_INTERVAL=5, verify 5-second waits

**[031]** [P] Implement DRY_RUN mode
- Check `self.dry_run` flag before file operations
- If true, log what WOULD happen but don't do it
- Skip file moves, action file creation
- Still log to demonstrate functionality
- **Status**: ✅ Done
- **Files**: `base_watcher.py`
- **Lines**: +5
- **Test**: Set DRY_RUN=true, verify no files created

---

## Phase 7: Documentation & Testing (Polish)

### User Docs

**[032]** [P] [US3] Write README.md
- Installation instructions
- Configuration guide
- Usage examples (run, run_once)
- File type classification table
- Action file format example
- Troubleshooting section
- **Status**: ✅ Done
- **Files**: `README.md` (in Watchers/)
- **Test**: Follow README, verify works for new user

**[033]** [P] Create quickstart script
- Shell script to automate setup
- Check Python installed
- Install requirements
- Create .env from example
- Initialize vault folders
- Run test
- **Status**: ⏳ Pending
- **Files**: `quickstart.sh`
- **Test**: Run on fresh system, verify complete setup

**[034]** [P] Create usage examples
- Example 1: Run watcher continuously
- Example 2: Run single check
- Example 3: Test with sample files
- Example 4: Check logs
- **Status**: ✅ Done (in README)
- **Files**: `README.md`, `examples/` folder
- **Test**: Each example runs successfully

### Testing

**[035]** Write unit tests for BaseWatcher
- Test initialization creates folders
- Test log_action writes JSON
- Test run_once executes once
- Test graceful shutdown
- **Status**: ⏳ Pending
- **Files**: `test_base_watcher.py`
- **Test**: pytest passes all tests

**[036]** Write unit tests for FileSystemWatcher
- Test file detection
- Test file classification
- Test deduplication
- Test action file creation
- Test error handling
- **Status**: ⏳ Pending
- **Files**: `test_filesystem_watcher.py`
- **Test**: pytest passes all tests

**[037]** Create integration test suite
- Test end-to-end: drop file → action created
- Test multiple file types
- Test duplicate handling
- Test error scenarios
- **Status**: ⏳ Pending
- **Files**: `test_integration.py`
- **Test**: All integration tests pass

**[038]** Run full test coverage
- Execute all unit + integration tests
- Verify >80% code coverage
- Fix any failing tests
- **Status**: ⏳ Pending
- **Test**: `pytest --cov` shows >80%

### Documentation

**[039]** [P] Document BaseWatcher API
- Class docstring with usage example
- Method docstrings with parameters and returns
- Configuration options
- Extension guide for future watchers
- **Status**: ✅ Done
- **Files**: `base_watcher.py` docstrings
- **Test**: Docstrings are clear and complete

**[040]** [P] Write troubleshooting guide
- Common errors and solutions
- FAQ section
- How to check logs
- How to reset processed files
- **Status**: ⏳ Pending
- **Files**: `TROUBLESHOOTING.md`
- **Test**: Guide covers common issues

**[041]** [P] Create CHANGELOG.md
- Document v1.0.0 (Bronze Tier)
- List all features
- Note breaking changes (none for v1.0)
- **Status**: ⏳ Pending
- **Files**: `CHANGELOG.md`
- **Test**: Changelog is accurate

---

## Phase 8: History & Audit Trail

### PHR Creation

**[042]** Create spec creation PHR
- File: `history/prompts/001-bronze-tier/001-spec-creation.spec.prompt.md`
- Document original user request for Bronze Tier
- Capture generated spec.md
- Document assumptions and clarifications
- **Status**: ⏳ Pending
- **Files**: PHR file
- **Test**: PHR matches template format

**[043]** Create plan creation PHR
- File: `history/prompts/001-bronze-tier/002-plan-creation.plan.prompt.md`
- Document plan generation from spec
- Capture architectural decisions
- Document component design choices
- **Status**: ⏳ Pending
- **Files**: PHR file
- **Test**: PHR captures key decisions

**[044]** Create task generation PHR
- File: `history/prompts/001-bronze-tier/003-task-generation.tasks.prompt.md`
- Document task breakdown from plan
- Capture dependency analysis
- Document phase organization
- **Status**: ⏳ Pending
- **Files**: PHR file
- **Test**: PHR explains task structure

**[045]** Create implementation PHR
- File: `history/prompts/001-bronze-tier/004-implementation.green.prompt.md`
- Document actual implementation work
- Capture code written
- Document tests run
- Note any deviations from plan
- **Status**: ⏳ Pending
- **Files**: PHR file
- **Test**: PHR provides complete record

---

## Summary

**Total Tasks**: 45
**Completed**: 31 ✅
**Pending**: 14 ⏳
**Blocked**: 0 ⏸️
**Failed**: 0 ❌

### Completion by Phase:
- **Phase 1** (Foundation): 9/9 tasks ✅
- **Phase 2** (File Detection): 6/6 tasks ✅
- **Phase 3** (Classification): 4/4 tasks ✅
- **Phase 4** (Deduplication): 3/3 tasks ✅
- **Phase 5** (Error Handling): 5/5 tasks ✅
- **Phase 6** (Configuration): 4/4 tasks ✅
- **Phase 7** (Documentation): 4/10 tasks ⏳
- **Phase 8** (History): 0/4 tasks ⏳

### Remaining Work:
Focus on Phase 7 (testing, docs) and Phase 8 (PHRs) to complete Bronze Tier retroactive documentation.

---

**Status**: ✅ Core Implementation Complete, Documentation Pending
**Next**: Create PHRs for audit trail, then move to Silver Tier specs

