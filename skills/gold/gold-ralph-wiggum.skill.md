# gold-ralph-wiggum

Gold Tier autonomous multi-step task loop with self-healing, loop detection, escalation, and recovery metrics.

## What you do

Implement the Ralph Wiggum autonomous loop pattern at production quality. Claude keeps working on multi-step tasks until completion criteria are met, with built-in safeguards against infinite loops, automatic error recovery, and human escalation when needed.

## When to use

- Multi-step task processing (e.g., clear all items in /Needs_Action)
- Batch operations requiring iteration
- Autonomous workflows that must self-recover from transient failures
- Fire-and-forget task execution with guaranteed completion or escalation

## Prerequisites

- Python 3.10+
- Ralph hook files: `.claude/hooks/stop.py`, `.claude/hooks/ralph_controller.py`
- Vault folder structure: `/Needs_Action`, `/Done`, `/Pending_Approval`, `/Logs`
- Environment: `VAULT_PATH`, `RALPH_ENABLED=true`

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    RALPH WIGGUM GOLD LOOP                        │
│                                                                  │
│   ┌──────────┐     ┌──────────┐     ┌──────────────┐            │
│   │  START    │────▶│ PROCESS  │────▶│ COMPLETION   │            │
│   │  LOOP    │     │  TASK    │     │  CHECK       │            │
│   └──────────┘     └────┬─────┘     └──────┬───────┘            │
│                         │                   │                    │
│                    ┌────▼─────┐        ┌────▼─────┐             │
│                    │  ERROR?  │        │ DONE?    │             │
│                    └────┬─────┘        └────┬─────┘             │
│                    Yes  │  No          Yes  │  No               │
│                 ┌───────▼──┐    ┌──────▼──┐ │                   │
│                 │ RECOVERY │    │  EXIT   │ │                   │
│                 │ STRATEGY │    │  CLEAN  │ │                   │
│                 └────┬─────┘    └─────────┘ │                   │
│                      │                      │                   │
│              ┌───────▼──────┐    ┌──────────▼────┐              │
│              │ RETRY OK?    │    │ MAX ITER?     │              │
│              └──┬────┬──────┘    └──┬────┬───────┘              │
│             Yes │    │ No       No  │    │ Yes                  │
│                 │  ┌─▼────────┐     │  ┌─▼──────────┐          │
│                 │  │ ESCALATE │     │  │ ESCALATE   │          │
│                 │  │ TO HUMAN │     │  │ TO HUMAN   │          │
│                 │  └──────────┘     │  └────────────┘          │
│                 │                   │                           │
│                 └─── LOOP BACK ◀───┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Completion Strategies

### 1. Promise Strategy
Claude outputs `<promise>TASK_COMPLETE</promise>` when done.

```bash
python ralph_controller.py start \
  "Process all items in /Needs_Action" \
  --strategy promise \
  --max-iterations 10
```

### 2. File Movement Strategy (Recommended)
Task complete when target file moves to /Done.

```bash
python ralph_controller.py start \
  "Process email from client" \
  --strategy file_movement \
  --file "/mnt/d/Ai-Employee/AI_Employee_Vault/Needs_Action/EMAIL_client.md"
```

### 3. Folder Empty Strategy
Complete when /Needs_Action has no remaining items.

```bash
python ralph_controller.py start \
  "Clear all pending work" \
  --strategy custom \
  --max-iterations 20
```

## Loop Detection & Self-Healing

### Loop Detection

The controller tracks iteration patterns to detect stuck loops:

```python
# ralph_controller.py loop detection logic
class LoopDetector:
    """Detect when the loop is stuck repeating the same actions."""

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.action_history = []
        self.error_history = []

    def record_action(self, action_hash: str, success: bool):
        """Record an action for pattern analysis."""
        self.action_history.append(action_hash)
        if not success:
            self.error_history.append(action_hash)

    def is_stuck(self) -> bool:
        """Check if recent actions show a repetitive pattern."""
        if len(self.action_history) < self.window_size:
            return False
        recent = self.action_history[-self.window_size:]
        # Stuck = all recent actions are identical
        return len(set(recent)) == 1

    def is_error_spiral(self) -> bool:
        """Check if errors are cascading."""
        if len(self.error_history) < 3:
            return False
        # 3+ consecutive errors = spiral
        recent_errors = self.error_history[-3:]
        return len(recent_errors) == 3
```

### Self-Healing Strategy

When transient errors occur, the loop applies recovery before retrying:

| Error Type | Recovery Action | Max Retries |
|-----------|----------------|-------------|
| Connection timeout | Wait 30s, retry | 3 |
| Auth expired | Re-authenticate | 2 |
| Rate limited | Exponential backoff (60s base) | 5 |
| File locked | Wait 10s, retry | 3 |
| Browser crash | Cleanup + reinit Playwright | 2 |
| Unknown error | Log + skip item + continue | 1 |

```python
RECOVERY_STRATEGIES = {
    'CONNECTION_ERROR': {
        'action': 'wait_retry',
        'wait_seconds': 30,
        'max_retries': 3
    },
    'AUTH_EXPIRED': {
        'action': 'reauthenticate',
        'max_retries': 2
    },
    'RATE_LIMITED': {
        'action': 'exponential_backoff',
        'base_seconds': 60,
        'max_retries': 5
    },
    'BROWSER_CRASH': {
        'action': 'cleanup_reinit',
        'max_retries': 2
    },
    'FILE_LOCKED': {
        'action': 'wait_retry',
        'wait_seconds': 10,
        'max_retries': 3
    }
}
```

## Escalation Triggers

The loop escalates to a human when ANY of these conditions are met:

1. **Max iterations reached** - Default 10, configurable
2. **Loop detected** - Same action repeated 5+ times with no progress
3. **Error spiral** - 3+ consecutive failures on different items
4. **Critical error** - Payment, security, or data-loss scenarios
5. **Approval timeout** - Item stuck in /Pending_Approval > 24 hours
6. **Resource exhaustion** - Disk > 90%, memory > 85%

### Escalation Actions

```python
def escalate(reason: str, context: dict):
    """Escalate to human when loop cannot self-resolve."""
    escalation_file = vault_path / 'Needs_Action' / f'ESCALATION_{timestamp}.md'
    escalation_file.write_text(f'''---
type: escalation
priority: high
source: ralph_loop
created: {datetime.now().isoformat()}
---

# Ralph Loop Escalation

## Reason
{reason}

## Context
- Iteration: {context.get('iteration', '?')} / {context.get('max_iterations', '?')}
- Items processed: {context.get('processed', 0)}
- Items remaining: {context.get('remaining', 0)}
- Last error: {context.get('last_error', 'None')}

## Action Required
Review the situation and either:
1. Fix the issue and restart the loop
2. Process remaining items manually
3. Adjust loop parameters and retry
''')
    # Also send desktop notification if available
    send_notification("Ralph Loop Escalation", reason)
```

## Fallback Behavior

When primary strategies fail, the loop degrades gracefully:

| Level | Condition | Behavior |
|-------|-----------|----------|
| L0 | Normal | Full autonomous processing |
| L1 | Single item error | Skip item, continue with next |
| L2 | Multiple errors (3+) | Switch to conservative mode (longer waits) |
| L3 | Loop detected | Break loop, escalate stuck item |
| L4 | Error spiral | Stop loop, escalate all remaining |
| L5 | Critical failure | Emergency stop, create incident report |

### Conservative Mode (L2)

```python
# When entering conservative mode:
# - Double wait times between operations
# - Add extra validation before each action
# - Log every step at DEBUG level
# - Process one item at a time (no batching)
```

## Recovery Metrics

The loop tracks metrics for observability:

```json
{
  "loop_id": "ralph_20260216_143000",
  "started": "2026-02-16T14:30:00",
  "completed": "2026-02-16T14:45:23",
  "status": "completed",
  "iterations": 7,
  "max_iterations": 10,
  "items_processed": 12,
  "items_skipped": 1,
  "items_escalated": 0,
  "errors": {
    "total": 2,
    "recovered": 2,
    "fatal": 0
  },
  "recovery_actions": [
    {"type": "wait_retry", "iteration": 3, "success": true},
    {"type": "cleanup_reinit", "iteration": 5, "success": true}
  ],
  "timing": {
    "total_seconds": 923,
    "avg_item_seconds": 71,
    "longest_item_seconds": 180
  },
  "degradation_level": "L0"
}
```

Metrics are saved to: `Logs/ralph_metrics_{date}.json`

### Health Dashboard Integration

The orchestrator reads Ralph metrics for the dashboard:

```python
# In orchestrator health check:
ralph_metrics = load_ralph_metrics()
dashboard_data['ralph'] = {
    'status': ralph_metrics.get('status', 'idle'),
    'last_run': ralph_metrics.get('completed'),
    'success_rate': calculate_success_rate(ralph_metrics),
    'avg_processing_time': ralph_metrics.get('timing', {}).get('avg_item_seconds', 0)
}
```

## Usage

### Start a Gold-tier Ralph loop

```bash
cd /mnt/d/Ai-Employee/.claude/hooks

# Process all pending items with self-healing
python ralph_controller.py start \
  "Process all items in /Needs_Action" \
  --strategy custom \
  --max-iterations 15 \
  --recovery-enabled \
  --metrics-enabled

# Track a specific file with escalation
python ralph_controller.py start \
  "Handle urgent client email" \
  --strategy file_movement \
  --file "/mnt/d/Ai-Employee/AI_Employee_Vault/Needs_Action/EMAIL_urgent.md" \
  --max-iterations 5 \
  --escalate-on-timeout 3600
```

### Monitor

```bash
# Real-time status
python ralph_controller.py status

# View metrics
cat /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/ralph_metrics_$(date +%Y-%m-%d).json | python -m json.tool

# View recovery log
tail -f /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/ralph.log
```

### Stop

```bash
# Graceful stop (finish current item)
python ralph_controller.py stop

# Emergency reset (immediate)
python ralph_controller.py reset
```

## Safety Features

- **Max Iterations**: Hard limit prevents infinite loops (default: 10)
- **Loop Detection**: Detects stuck patterns within 5 iterations
- **Error Spiral Detection**: Stops after 3 consecutive failures
- **State Persistence**: State file survives crashes, enables resume
- **HITL Preserved**: Sensitive actions always route through /Pending_Approval
- **Audit Trail**: Every action logged with timestamps and outcomes
- **Resource Guards**: Checks disk/memory before each iteration
- **Graceful Degradation**: 6-level fallback strategy (L0-L5)

## Integration

### With Orchestrator

```python
from ralph_controller import RalphController

controller = RalphController()
controller.start(
    task="Process all pending items",
    strategy="custom",
    max_iterations=15,
    recovery_enabled=True,
    metrics_enabled=True
)
```

### With Scheduler

```python
# In scheduler.py - periodic Ralph loop for batch processing
async def task_ralph_batch():
    """Run Ralph loop for any accumulated items."""
    needs_action = vault_path / 'Needs_Action'
    items = list(needs_action.glob('*.md'))
    if len(items) >= 3:  # Only batch if 3+ items
        controller = RalphController()
        controller.start(
            task=f"Batch process {len(items)} items",
            strategy="custom",
            max_iterations=len(items) * 2
        )
```

## Related Skills

- ralph-loop.skill.md - Base Silver tier Ralph loop
- gold-error-recovery.skill.md - Error handling patterns
- gold-ceo-briefing.skill.md - Reports on Ralph metrics

---

*Skill: gold-ralph-wiggum*
*Tier: Gold*
*Dependencies: ralph-loop (Silver), error-recovery (Gold)*
