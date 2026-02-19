---
command: /sp.tasks
type: task_generator
created: 2026-02-05
status: active
version: 1.0.0
---

# /sp.tasks - Task List Generator

## Purpose
Generate actionable, dependency-ordered task lists from implementation plans, organizing work into executable chunks with clear acceptance criteria and parallel execution opportunities.

---

## Command Usage

```bash
/sp.tasks <feature-name> [--plan-file "path/to/plan.md"]
```

### Examples
```bash
/sp.tasks gmail-watcher
/sp.tasks ceo-briefing --plan-file "/Plans/PLAN_ceo_briefing_implementation.md"
/sp.tasks odoo-integration
```

---

## What This Command Does

### 1. Load Implementation Plan
- Read `/Plans/PLAN_<feature-name>_implementation.md`
- Extract phases and steps
- Identify dependencies
- Note architecture decisions

### 2. Break Down into Tasks
- Convert plan phases into discrete tasks
- Each task = 15-60 minutes of work
- Add file paths and specific actions
- Include acceptance criteria
- Mark parallel execution opportunities

### 3. Organize by Dependencies
- **Setup Phase:** Infrastructure tasks (no dependencies)
- **Foundation Phase:** Core components (blocks everything)
- **Implementation Phases:** Feature tasks (organized by P1/P2/P3)
- **Polish Phase:** Cross-cutting concerns (after all features)

### 4. Identify Parallel Work
- Mark tasks with `[P]` if they can run in parallel
- Group related tasks
- Show dependency chains
- Optimize for team/agent coordination

### 5. Create Task List
- Generate `/Tasks/TASKS_<feature-name>.md`
- Checkbox format for tracking
- Clear file paths and actions
- Dependency graph
- Estimated time per task

---

## Task List Structure Generated

```markdown
# Tasks: <Feature Name>

**Input:** `/Plans/PLAN_<feature-name>_implementation.md`
**Total Estimate:** X hours
**Parallel Opportunities:** Y tasks

## Format: `[ID] [P?] [Phase] Description`
- **[P]:** Can run in parallel
- **[Phase]:** Setup | Foundation | P1 | P2 | P3 | Polish

---

## Phase 1: Setup (X min)
Purpose: Initialize project structure

- [ ] T001 Create project folder structure: `/path/to/module/`
- [ ] T002 [P] Initialize configuration: `config.yaml`
- [ ] T003 [P] Setup logging: `/Logs/ModuleName.log`

---

## Phase 2: Foundation (X hours)
Purpose: Core infrastructure (BLOCKS all implementation)

⚠️ CRITICAL: No feature work until this phase complete

- [ ] T004 Implement BaseClass in `/path/to/base.py`
- [ ] T005 Setup authentication in `/path/to/auth.py`
- [ ] T006 [P] Create utility functions in `/path/to/utils.py`

**Checkpoint:** Foundation ready - implementation can begin

---

## Phase 3: P1 Implementation (X hours)
Purpose: Critical user scenarios

### User Story 1 (P1)
- [ ] T007 [P] Implement function X in `/path/file.py:line`
- [ ] T008 [P] Implement function Y in `/path/file.py:line`
- [ ] T009 Test user story 1 end-to-end

### User Story 2 (P1)
- [ ] T010 Implement feature Z (depends on T009)

---

## Phase 4: P2 Implementation (X hours)
Purpose: Important enhancements

- [ ] T011 [P] Feature A
- [ ] T012 [P] Feature B

---

## Phase 5: Polish (X min)
Purpose: Documentation and refinement

- [ ] T013 [P] Write README.md
- [ ] T014 [P] Update Dashboard.md
- [ ] T015 Add to history_context.md

---

## Dependencies

### Critical Path:
Setup → Foundation → P1 User Story 1 → P1 User Story 2 → Polish

### Parallel Opportunities:
- T002, T003 can run together
- T007, T008 can run together
- T011, T012 can run together

### Blockers:
- Foundation (Phase 2) blocks all implementation
- Each user story blocks dependent stories
- Tests block progression to next story

---

## Execution Order

**Single Developer:**
T001 → T002 → T003 → T004 → T005 → T006 → ...

**Parallel Execution (if multiple agents):**
```
Round 1: T001
Round 2: T002, T003 (parallel)
Round 3: T004
Round 4: T005, T006 (parallel)
Round 5: T007, T008 (parallel)
...
```
```

---

## Input Sources

### Required:
1. **Implementation Plan:** `/Plans/PLAN_<feature-name>_implementation.md`
   - Phases and steps
   - Dependencies
   - Timeline estimates

2. **Feature Spec:** `/Specs/<feature-name>_spec.md`
   - User scenarios (P1/P2/P3)
   - Acceptance criteria

### Context:
3. **Codebase:** Existing file structure
4. **Constitution:** Task size guidelines (15-60 min)
5. **History:** Lessons on task breakdown

---

## Output Files Created

### 1. Task List
**Location:** `/Tasks/TASKS_<feature-name>.md`
**Content:**
- Numbered task list with checkboxes
- File paths and line numbers (where applicable)
- Parallel execution markers `[P]`
- Phase grouping
- Dependency documentation
- Time estimates per task

### 2. Implementation Trigger (automatic)
**After tasks approved:** Suggest `/sp.implement` to begin execution

---

## Task Breakdown Rules

### Task Size Guidelines:
- **Minimum:** 15 minutes (smaller = merge with related task)
- **Maximum:** 60 minutes (larger = break into subtasks)
- **Sweet spot:** 30 minutes (focused, testable unit of work)

### Task Granularity:
```python
# TOO LARGE (2+ hours):
- [ ] Implement Gmail watcher

# GOOD (30-60 min each):
- [ ] T001 Setup Gmail API authentication
- [ ] T002 Implement email fetching function
- [ ] T003 Implement action file creation
- [ ] T004 Add error handling and logging
- [ ] T005 Test with real Gmail account
```

### When to Split Tasks:
- Multiple file modifications
- Multiple logical steps
- Long estimated time (>60 min)
- Complex testing required
- Multiple technologies involved

### When to Merge Tasks:
- Same file, adjacent lines
- Same logical unit
- Total time <15 minutes
- Trivial changes

---

## Parallel Execution Detection

### Mark as `[P]` if:
✅ No shared files being edited
✅ No dependencies on each other
✅ Can be tested independently
✅ No shared state modifications

### Examples:

**Parallel:**
```markdown
- [ ] T001 [P] Create models/user.py
- [ ] T002 [P] Create models/invoice.py
```
(Different files, no dependencies)

**Sequential:**
```markdown
- [ ] T003 Create database schema
- [ ] T004 Write migration script (depends on T003)
```
(T004 needs T003 complete)

---

## Dependency Management

### Types of Dependencies:

1. **Blocking (Foundation):**
   ```
   Setup → Foundation (BLOCKS EVERYTHING) → Implementation
   ```

2. **Sequential (Within Phase):**
   ```
   T005 → T006 → T007
   ```

3. **Parallel (Independent):**
   ```
        ┌─ T008
   T007 ┤
        └─ T009
   ```

4. **Convergent (Join Point):**
   ```
   T010 ┐
   T011 ┼→ T012
   T013 ┘
   ```

### Dependency Notation:
```markdown
- [ ] T005 Implement feature X
- [ ] T006 Test feature X (depends on T005)
- [ ] T007 [P] Implement feature Y (can run parallel to T005-T006)
```

---

## Acceptance Criteria per Task

Each task includes:

### What Success Looks Like:
```markdown
- [ ] T001 Implement authentication function

**Acceptance Criteria:**
- Function exists in `/src/auth.py`
- Takes username/password parameters
- Returns auth token or error
- Handles invalid credentials gracefully
- Logs all auth attempts
- Unit test passes
```

### Task Checklist Template:
```markdown
- [ ] TXXX [P?] [Phase] Task description

**File:** `/path/to/file.py` (or new file to create)
**Time:** X minutes
**Dependencies:** TYYY (if any)

**What to do:**
1. Specific action 1
2. Specific action 2
3. Specific action 3

**Acceptance:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Testing:**
- [ ] Unit test: `pytest tests/test_module.py::test_function`
```

---

## Example: Gmail Watcher Task List

**Input Plan:** `/Plans/PLAN_gmail_watcher_implementation.md`

**Generated Tasks:**

```markdown
# Tasks: Gmail Watcher

**Total Estimate:** 10 hours
**Parallel Opportunities:** 5 tasks

---

## Phase 1: Setup (30 min)

- [ ] T001 Create folder structure
  - `/AI_Employee_Code/watchers/gmail/`
  - `__init__.py`, `gmail_watcher.py`, `config.py`

- [ ] T002 [P] Create credentials folder
  - `/AI_Employee_Code/credentials/`
  - Add to `.gitignore`

- [ ] T003 [P] Install dependencies
  - `pip install google-auth-oauthlib google-api-python-client`

---

## Phase 2: Foundation (2 hours)

⚠️ BLOCKS all implementation

- [ ] T004 Setup Gmail API in Google Cloud Console
  - Enable Gmail API
  - Create OAuth 2.0 credentials
  - Download credentials.json
  - **Time:** 30 min

- [ ] T005 Implement authentication function
  - **File:** `/watchers/gmail/gmail_watcher.py`
  - OAuth flow with token persistence
  - **Time:** 60 min

- [ ] T006 Test authentication
  - Browser OAuth consent working
  - Token saved to token.json
  - **Time:** 30 min

**Checkpoint:** Authentication working ✅

---

## Phase 3: P1 Implementation - Email Detection (4 hours)

### Core Watcher Logic

- [ ] T007 [P] Create GmailWatcher class
  - **File:** `/watchers/gmail/gmail_watcher.py`
  - Inherit from BaseWatcher
  - Initialize Gmail API service
  - **Time:** 45 min

- [ ] T008 [P] Implement check_for_updates()
  - Query for "is:unread is:important"
  - Filter already processed IDs
  - Return list of new emails
  - **Time:** 60 min

- [ ] T009 Implement create_action_file()
  - Extract email metadata (from, subject, body)
  - Create structured markdown with YAML frontmatter
  - Save to `/Needs_Action/EMAIL_*.md`
  - **Time:** 60 min
  - **Depends on:** T007, T008

- [ ] T010 Add logging
  - Log all API calls
  - Log file creations
  - Error logging
  - **Time:** 30 min

### Testing

- [ ] T011 Test with real Gmail account
  - Send test email marked important
  - Verify detection within 2 minutes
  - Check action file created correctly
  - **Time:** 45 min
  - **Depends on:** T009

---

## Phase 4: P2 Implementation - Reliability (2 hours)

- [ ] T012 [P] Implement duplicate prevention
  - Track processed message IDs
  - Persist to file or memory
  - **Time:** 30 min

- [ ] T013 [P] Add error handling
  - API rate limit handling
  - Network error retry (exponential backoff)
  - Token expiry handling
  - **Time:** 45 min

- [ ] T014 Add health check logging
  - Log every check cycle
  - Log success/failure counts
  - **Time:** 15 min

---

## Phase 5: Deployment (1.5 hours)

- [ ] T015 Create PM2 configuration
  - **File:** `ecosystem.config.js`
  - Configure restart policy
  - **Time:** 30 min

- [ ] T016 Test PM2 supervision
  - Start watcher with PM2
  - Verify auto-restart on crash
  - Check logs via `pm2 logs`
  - **Time:** 30 min

- [ ] T017 Integration test
  - Full end-to-end test
  - Multiple emails
  - Verify no duplicates
  - **Time:** 30 min

---

## Phase 6: Polish (1 hour)

- [ ] T018 [P] Write README.md
  - Setup instructions
  - Configuration guide
  - **Time:** 20 min

- [ ] T019 [P] Update Dashboard.md
  - Add Gmail watcher status
  - **Time:** 10 min

- [ ] T020 [P] Update history_context.md
  - Document implementation
  - Note lessons learned
  - **Time:** 20 min

- [ ] T021 Create usage documentation
  - How to configure important filters
  - How to monitor logs
  - **Time:** 10 min

---

## Dependencies

**Critical Path:**
T001 → T004 → T005 → T006 → T007 → T008 → T009 → T011 → T015 → T016 → T017

**Parallel Opportunities:**
- Round 1: T002, T003 (with T001)
- Round 2: T007, T008 (after T006)
- Round 3: T012, T013 (after T011)
- Round 4: T018, T019, T020 (final polish)

**Blockers:**
- T006 (auth test) blocks all implementation
- T011 (integration test) blocks deployment
- T017 (final test) blocks polish

---

## Execution Order

**Solo Implementation:**
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020 → T021

**Time Savings with Parallel:**
- Sequential: 10 hours
- With parallel: ~8.5 hours (15% faster)
```

---

## Workflow Integration

```
/sp.specify → /sp.plan → /sp.tasks → /sp.implement
                              ↓
                        Task list created
                              ↓
                        Human reviews
                              ↓
                   ┌──────────┴──────────┐
                   ↓                     ↓
              Approved            Need changes?
                   ↓                     ↓
            /sp.implement          Revise tasks
```

---

## Best Practices

### Do's ✅
- Keep tasks 15-60 minutes each
- Include specific file paths
- Add clear acceptance criteria
- Mark parallel opportunities
- Document dependencies
- Estimate conservatively
- Include testing tasks
- Add documentation tasks

### Don'ts ❌
- Don't create tasks >60 minutes
- Don't skip file path specification
- Don't forget testing steps
- Don't ignore parallel opportunities
- Don't omit documentation tasks
- Don't create tasks <15 minutes (merge them)

---

## Skill Growth Notes

### What This Command Teaches AI:
- How to break plans into tasks
- How to identify dependencies
- How to estimate task duration
- How to find parallel execution opportunities
- How to write clear acceptance criteria

### Improvements Over Time:
- More accurate time estimates
- Better task granularity
- Improved dependency detection
- Cleaner parallel grouping
- Better acceptance criteria

---

## Metrics to Track

| Metric | Target | Current |
|--------|--------|---------|
| Task lists created per week | 2-4 | TBD |
| Average tasks per feature | 15-25 | TBD |
| Task completion rate | >90% | TBD |
| Time estimate accuracy | ±20% | TBD |
| Parallel execution utilization | >30% | TBD |

---

## Version History

- **v1.0.0** (2026-02-05) - Initial command specification
  - Core task generation logic
  - Dependency management
  - Parallel execution detection
  - Acceptance criteria framework

---

## Related Documentation

- **Input:** `/Plans/PLAN_<feature>_implementation.md`
- **Output:** `/Tasks/TASKS_<feature>.md`
- **Next Step:** `/Specs/sp.implement.md`
- **Templates:** `.specify/templates/tasks-template.md`

---

**Status:** ✅ Active
**Required for:** All features before implementation
**Tier:** All tiers

---

*This command follows SpecKitPlus methodology for structured task generation*
