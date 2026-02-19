# AI Employee - Corrected Project Structure

**Date:** 2026-02-05
**Status:** ✅ Fixed and Organized

---

## 🎯 Root Directory Structure

```
/mnt/d/Ai-Employee/
├── .claude/                          # Claude Code configuration
│   ├── commands/                     # SP commands (sp.specify, sp.plan, etc.)
│   └── skills/                       # Executable skills (vault-setup, etc.)
│
├── .specify/                         # SpecifyPlus framework
│   ├── memory/
│   │   └── constitution.md           # Master constitution (Version 1.0.0)
│   ├── templates/                    # SpecifyPlus templates
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── adr-template.md
│   │   └── phr-template.prompt.md
│   └── scripts/                      # PowerShell scripts
│
├── specs/                            # Feature specifications (SpecifyPlus)
│   ├── <feature-name>/              # One folder per feature
│   │   ├── spec.md                  # Created by /sp.specify
│   │   ├── plan.md                  # Created by /sp.plan
│   │   ├── tasks.md                 # Created by /sp.tasks
│   │   └── ...
│   └── README.md
│
├── history/                          # Project history
│   ├── prompts/                     # Prompt History Records (PHR)
│   │   ├── constitution/
│   │   ├── general/
│   │   └── <feature-name>/
│   └── adr/                         # Architecture Decision Records
│
├── skills/                           # Tier-based skill documentation
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── platinum/
│
├── AI_Employee_Vault/                # Obsidian operational vault
│   ├── sp.constitution.md           # Vault-specific constitution
│   ├── Dashboard.md                 # Real-time status
│   ├── Company_Handbook.md          # Rules of engagement
│   ├── Business_Goals.md            # Quarterly objectives
│   │
│   ├── Needs_Action/                # Watchers write here
│   ├── Plans/                       # AI creates plans here
│   ├── Pending_Approval/            # Human reviews here
│   ├── Approved/                    # Human approves here
│   ├── Rejected/                    # Human rejects here
│   ├── Done/                        # Completed work
│   ├── Logs/                        # Audit logs (JSON)
│   │
│   ├── Prompts/                     # Vault working memory
│   │   └── history_context.md
│   ├── Specs/                       # Vault working specs
│   │   └── spec_template.md
│   ├── Watchers/                    # Python watcher scripts
│   ├── MCP_Servers/                 # MCP server code
│   ├── Accounting/                  # Financial records
│   ├── Briefings/                   # CEO briefings (Gold+)
│   └── Inbox/                       # File drops
│
├── 0-hackathon.md                   # Architecture blueprint
├── CLAUDE.md                        # Claude Code rules
├── PROJECT_STATUS.md                # Current status report
├── PROJECT_STRUCTURE.md             # This file
└── README.md                        # Project overview
```

---

## 📂 Directory Purposes

### Configuration Directories

#### `.claude/`
**Purpose:** Claude Code agent configuration
- **commands/** - SP command definitions (sp.specify, sp.plan, sp.tasks, sp.implement)
- **skills/** - Executable agent skills (vault-setup, watcher-setup, etc.)

#### `.specify/`
**Purpose:** SpecifyPlus framework (authoritative templates)
- **memory/constitution.md** - Master project constitution
- **templates/** - Authoritative SpecifyPlus templates
- **scripts/** - Automation scripts

### Working Directories

#### `specs/` (Project Root)
**Purpose:** Feature specifications following SpecifyPlus
- Each feature gets own folder: `specs/<feature-name>/`
- Contains: spec.md, plan.md, tasks.md
- Created by: /sp.specify, /sp.plan, /sp.tasks commands
- **NOT in vault** - Project-level documentation

#### `history/` (Project Root)
**Purpose:** Project historical records
- **prompts/** - PHR files organized by feature/constitution/general
- **adr/** - Architecture Decision Records
- **NOT in vault** - Project-level history

#### `skills/` (Project Root)
**Purpose:** Tier-based skill documentation
- Detailed guides for Bronze/Silver/Gold/Platinum features
- Reference documentation, not operational code

### Operational Directory

#### `AI_Employee_Vault/` (Obsidian Vault)
**Purpose:** Day-to-day AI Employee operations
- **Workflow folders:** Needs_Action, Plans, Pending_Approval, etc.
- **Core files:** Dashboard, Handbook, Goals, Constitution (vault copy)
- **Working memory:** Prompts/history_context.md
- **Working specs:** Specs/spec_template.md (for reference)
- **Execution:** Watchers, MCP_Servers folders

---

## 🔄 Workflow: Specs → Vault

### Feature Development Flow

```
1. PROJECT PLANNING (Project Root)
   /sp.specify <feature>
   → Creates: specs/<feature>/spec.md
   
   /sp.plan <feature>
   → Creates: specs/<feature>/plan.md
   
   /sp.tasks <feature>
   → Creates: specs/<feature>/tasks.md

2. OPERATIONAL EXECUTION (Vault)
   /sp.implement <feature>
   → Works in: AI_Employee_Vault/
   → Creates plans in: Plans/
   → Requests approval in: Pending_Approval/
   → Logs in: Logs/
   → Archives in: Done/

3. HISTORY RECORDING (Project Root)
   Auto-creates PHR
   → Saves to: history/prompts/<feature>/
```

### Key Principle
- **Specs folder** = Project-level planning (static docs)
- **Vault** = Operational execution (dynamic workflow)
- **History** = Project-level memory (audit trail)

---

## ❌ What Was Wrong Before

### Issue 1: Specs in Wrong Location
**Wrong:**
```
AI_Employee_Vault/Specs/    ❌ (vault is for operations, not planning docs)
```

**Correct:**
```
specs/                      ✅ (project root, SpecifyPlus standard)
```

### Issue 2: Command Files in Specs
**Wrong:**
```
AI_Employee_Vault/Specs/sp.specify.md    ❌ (commands go in .claude/)
AI_Employee_Vault/Specs/sp.plan.md       ❌
AI_Employee_Vault/Specs/sp.tasks.md      ❌
```

**Correct:**
```
.claude/commands/sp.specify.md           ✅
.claude/commands/sp.plan.md              ✅
.claude/commands/sp.tasks.md             ✅
```

### Issue 3: Mixed Concerns
**Before:** Vault had both operational files AND documentation templates mixed together

**After:** Clear separation:
- **Project root** = Planning, specs, history
- **Vault** = Operations, workflow, real-time data

---

## ✅ Corrected Structure Benefits

### 1. Clear Separation of Concerns
- Project planning ≠ Operational execution
- Static docs ≠ Dynamic workflow
- Templates ≠ Working files

### 2. SpecifyPlus Compliance
- `specs/` at project root (standard)
- `.specify/` for framework (standard)
- Feature folders with spec/plan/tasks (standard)

### 3. Maintainability
- Easy to find specs (project root)
- Easy to find operations (vault)
- Easy to find history (project root)
- No confusion between templates and working files

### 4. Scalability
- Multiple features → Multiple spec folders
- Multiple agents → Shared vault operations
- Multiple sessions → Organized history

---

## 📝 File Location Quick Reference

| File Type | Location | Example |
|-----------|----------|---------|
| SP Commands | `.claude/commands/` | `sp.specify.md` |
| Skills | `.claude/skills/` | `vault-setup.md` |
| Constitution (Master) | `.specify/memory/` | `constitution.md` |
| Templates (Master) | `.specify/templates/` | `spec-template.md` |
| Feature Specs | `specs/<feature>/` | `gmail-watcher/spec.md` |
| PHR Records | `history/prompts/` | `constitution/001-*.md` |
| ADR Records | `history/adr/` | `ADR-001-*.md` |
| Operational Workflow | `AI_Employee_Vault/` | `Needs_Action/`, `Plans/` |
| Dashboard | `AI_Employee_Vault/` | `Dashboard.md` |
| Watcher Code | `AI_Employee_Vault/Watchers/` | `gmail_watcher.py` |

---

## 🚀 Usage Examples

### Create New Feature
```bash
cd /mnt/d/Ai-Employee

# 1. Create specification (creates specs/gmail-watcher/spec.md)
/sp.specify gmail-watcher

# 2. Create plan (creates specs/gmail-watcher/plan.md)
/sp.plan gmail-watcher

# 3. Generate tasks (creates specs/gmail-watcher/tasks.md)
/sp.tasks gmail-watcher

# 4. Implement (works in AI_Employee_Vault/)
/sp.implement gmail-watcher
```

### Check Current Work
```bash
# Operational status
cat AI_Employee_Vault/Dashboard.md

# Pending items
ls AI_Employee_Vault/Needs_Action/

# Current plans
ls AI_Employee_Vault/Plans/

# Project specs
ls specs/
```

---

## 📊 Directory Statistics

```
✅ Corrected Locations:
   - .claude/commands/      → 13 command files
   - .claude/skills/        → 4 skills
   - .specify/memory/       → 1 constitution
   - .specify/templates/    → 7 templates
   - specs/                 → Ready for features
   - history/prompts/       → PHR organized
   - AI_Employee_Vault/     → 20+ folders/files

❌ Removed/Cleaned:
   - AI_Employee_Vault/Specs/sp.* → Moved to .claude/commands/
   - Duplicate spec templates → Kept one reference copy
   - {Prompts,Specs} weird folder → Will be removed
```

---

## ✨ Final Structure Status

**Status:** ✅ CORRECTED
**Complies with:** SpecifyPlus standard
**Ready for:** Feature development
**Clarity:** High (clear separation of concerns)

---

*Structure corrected: 2026-02-05*
*Follows: SpecifyPlus + Hackathon architecture*
*Maintained by: Claude AI Employee Engineer*
