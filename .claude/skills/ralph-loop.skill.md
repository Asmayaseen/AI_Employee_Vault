# ralph-loop

Autonomous task completion using the Ralph Wiggum pattern. This skill keeps Claude working until a task is complete.

## What you do

You are the Ralph Wiggum autonomous loop manager. You can start, stop, and monitor autonomous task completion loops. When a Ralph loop is active, Claude will continue working on the task until completion criteria are met.

## When to use

- When you need Claude to work autonomously until task is complete
- For multi-step processing tasks (e.g., process all files in /Needs_Action)
- When you want fire-and-forget task execution
- For complex workflows that need iteration

## Prerequisites

- Python 3.10+ installed
- Ralph hook files in place (.claude/hooks/stop.py)
- Vault folder structure ready (/Needs_Action, /Done, etc.)
- Environment variable VAULT_PATH set (optional, defaults to /mnt/d/Ai-Employee/AI_Employee_Vault)

## Completion Strategies

### 1. Promise Strategy (Simple)
Claude outputs `<promise>TASK_COMPLETE</promise>` when done.

```bash
# Start with promise strategy
python /mnt/d/Ai-Employee/.claude/hooks/ralph_controller.py start \
  "Process all items in /Needs_Action" \
  --strategy promise \
  --max-iterations 10
```

### 2. File Movement Strategy (Recommended)
Task is complete when a specific file moves to /Done folder.

```bash
# Start with file tracking
python /mnt/d/Ai-Employee/.claude/hooks/ralph_controller.py start \
  "Process email from client" \
  --strategy file_movement \
  --file "/mnt/d/Ai-Employee/AI_Employee_Vault/Needs_Action/EMAIL_client_inquiry.md"
```

### 3. Custom Strategy (Advanced)
Complete when no pending items in /Needs_Action and /Pending_Approval.

```bash
# Start with custom strategy
python /mnt/d/Ai-Employee/.claude/hooks/ralph_controller.py start \
  "Clear all pending work" \
  --strategy custom \
  --max-iterations 20
```

## Instructions

### Step 1: Check Ralph Status

```bash
cd /mnt/d/Ai-Employee/.claude/hooks
python ralph_controller.py status
```

### Step 2: Start a Ralph Loop

For processing all pending items:
```bash
python ralph_controller.py start "Process all items in /Needs_Action and move completed to /Done" \
  --strategy custom \
  --max-iterations 10
```

For tracking a specific task file:
```bash
python ralph_controller.py start "Handle client email" \
  --strategy file_movement \
  --file "/mnt/d/Ai-Employee/AI_Employee_Vault/Needs_Action/EMAIL_123.md" \
  --max-iterations 5
```

### Step 3: Monitor Progress

Check the Ralph log:
```bash
tail -f /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/ralph.log
```

Check current status:
```bash
python ralph_controller.py status
```

### Step 4: Stop a Ralph Loop

Normal stop:
```bash
python ralph_controller.py stop
```

Emergency reset:
```bash
python ralph_controller.py reset
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│              RALPH WIGGUM LOOP                      │
│                                                     │
│   1. User starts loop with task description         │
│   2. Claude processes task                          │
│   3. Claude tries to exit                           │
│   4. Stop hook intercepts:                          │
│      ├── Check completion criteria                  │
│      ├── If NOT complete:                           │
│      │   ├── Increment iteration                    │
│      │   ├── Re-inject continuation prompt          │
│      │   └── Continue Claude (exit code 1)          │
│      └── If COMPLETE:                               │
│          ├── Log completion                         │
│          └── Allow exit (exit code 0)               │
│   5. Repeat 2-4 until complete or max iterations    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Integration with Orchestrator

The Ralph loop integrates with the orchestrator for automated task processing:

```python
# In orchestrator, when new items arrive in /Needs_Action:
from ralph_controller import RalphController

controller = RalphController()
controller.start(
    "Process all pending items",
    strategy="custom",
    max_iterations=10
)
```

## Example Workflow

### Autonomous Email Processing

1. Gmail watcher detects new email → creates file in /Needs_Action
2. Orchestrator triggers Claude processor
3. Ralph loop starts with file_movement strategy
4. Claude:
   - Reads email content
   - Creates plan in /Plans
   - If approval needed: creates approval request in /Pending_Approval
   - Waits for approval (approval watcher monitors)
   - Executes action via MCP
   - Moves completed file to /Done
5. Ralph hook detects file in /Done → allows exit

### Batch Processing

```bash
# Process all 10 pending emails
python ralph_controller.py start \
  "Process all 10 items in /Needs_Action. For each item: analyze, create plan, execute if safe, or request approval. Move to /Done when complete." \
  --strategy custom \
  --max-iterations 30
```

## Safety Features

- **Max Iterations**: Prevents infinite loops (default: 10)
- **Logging**: All actions logged to ralph.log
- **State Persistence**: State saved to file, survives crashes
- **Emergency Stop**: `ralph_controller.py reset` clears all state
- **Human-in-the-Loop**: Sensitive actions still require approval

## Troubleshooting

### Ralph not starting
1. Check RALPH_ENABLED environment variable
2. Verify state file permissions
3. Check logs: `tail /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/ralph.log`

### Loop not stopping
1. Check completion criteria
2. Verify file paths are correct
3. Use `ralph_controller.py reset` to force stop

### Task not completing
1. Check /Needs_Action and /Done folders
2. Review ralph.log for errors
3. Increase max_iterations if needed

## Related Skills

- orchestrator.skill.md - Master control system
- claude-processor.skill.md - Task processing
- approval-monitor.skill.md - Human approval workflow
