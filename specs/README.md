# Specs Directory

This directory contains feature specifications following SpecifyPlus methodology.

## Structure

```
specs/
├── <feature-name>/
│   ├── spec.md          # Feature specification (created by /sp.specify)
│   ├── plan.md          # Implementation plan (created by /sp.plan)
│   ├── tasks.md         # Task breakdown (created by /sp.tasks)
│   ├── research.md      # Research notes (optional)
│   ├── data-model.md    # Data models (optional)
│   └── contracts/       # API contracts (optional)
└── README.md            # This file
```

## Workflow

1. **Specify:** `/sp.specify <feature>` → Creates `specs/<feature>/spec.md`
2. **Plan:** `/sp.plan <feature>` → Creates `specs/<feature>/plan.md`
3. **Tasks:** `/sp.tasks <feature>` → Creates `specs/<feature>/tasks.md`
4. **Implement:** `/sp.implement <feature>` → Executes tasks

## Example

```bash
# Step 1: Create specification
/sp.specify gmail-watcher

# Result: specs/gmail-watcher/spec.md created

# Step 2: Create implementation plan
/sp.plan gmail-watcher

# Result: specs/gmail-watcher/plan.md created

# Step 3: Generate tasks
/sp.tasks gmail-watcher

# Result: specs/gmail-watcher/tasks.md created

# Step 4: Implement
/sp.implement gmail-watcher
```

## Guidelines

- Each feature gets its own folder
- Follow SpecifyPlus templates from `.specify/templates/`
- Keep specs updated as features evolve
- Link specs to constitution principles

---

**Location:** Project root `/specs/`
**Purpose:** Feature documentation and planning
**Framework:** SpecifyPlus
