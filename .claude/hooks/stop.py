#!/usr/bin/env python3
"""
Ralph Wiggum Stop Hook - Autonomous Task Completion

This hook intercepts Claude Code's exit and keeps it running until tasks are complete.

How it works:
1. Claude processes a task
2. Claude tries to exit
3. Stop hook checks completion status
4. If not complete: Re-inject prompt and continue
5. If complete: Allow exit

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))
STATE_FILE = VAULT_PATH / '.ralph_state.json'
MAX_ITERATIONS = int(os.getenv('RALPH_MAX_ITERATIONS', '10'))
ENABLED = os.getenv('RALPH_ENABLED', 'true').lower() == 'true'

# Completion check strategies
STRATEGY_PROMISE = 'promise'      # Claude outputs <promise>TASK_COMPLETE</promise>
STRATEGY_FILE = 'file_movement'   # Check if task file moved to /Done
STRATEGY_CUSTOM = 'custom'        # Custom check function


class RalphWiggumHook:
    """Stop hook that keeps Claude working until task complete."""

    def __init__(self):
        self.vault_path = VAULT_PATH
        self.state_file = STATE_FILE
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """Load Ralph state from file."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except Exception as e:
                print(f"Warning: Failed to load Ralph state: {e}", file=sys.stderr)
                return {}
        return {}

    def _save_state(self):
        """Save Ralph state to file."""
        try:
            self.state_file.write_text(json.dumps(self.state, indent=2))
        except Exception as e:
            print(f"Warning: Failed to save Ralph state: {e}", file=sys.stderr)

    def _log(self, message: str):
        """Log to Ralph log file."""
        log_file = self.vault_path / 'Logs' / 'ralph.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"

        with log_file.open('a') as f:
            f.write(log_entry)

        print(f"[Ralph] {message}", file=sys.stderr)

    def is_active(self) -> bool:
        """Check if Ralph loop is currently active."""
        if not ENABLED:
            return False

        return self.state.get('active', False)

    def start_loop(self, task_description: str, strategy: str = STRATEGY_FILE,
                   task_file: str = None, max_iterations: int = None):
        """Start a new Ralph loop."""
        self.state = {
            'active': True,
            'task_description': task_description,
            'strategy': strategy,
            'task_file': task_file,
            'max_iterations': max_iterations or MAX_ITERATIONS,
            'current_iteration': 0,
            'started_at': datetime.now().isoformat(),
            'last_output': None
        }
        self._save_state()
        self._log(f"Started Ralph loop: {task_description}")
        self._log(f"Strategy: {strategy}, Max iterations: {self.state['max_iterations']}")

    def stop_loop(self, reason: str = "completed"):
        """Stop the Ralph loop."""
        if self.state.get('active'):
            iterations = self.state.get('current_iteration', 0)
            self._log(f"Stopping Ralph loop: {reason} (after {iterations} iterations)")

        self.state = {'active': False, 'stopped_at': datetime.now().isoformat()}
        self._save_state()

    def check_completion_promise(self, output: str) -> bool:
        """Check if output contains completion promise."""
        return '<promise>TASK_COMPLETE</promise>' in output

    def check_completion_file_movement(self) -> bool:
        """Check if task file has moved to /Done."""
        task_file = self.state.get('task_file')
        if not task_file:
            return False

        # Check if file is in /Done folder
        done_path = self.vault_path / 'Done'
        task_filename = Path(task_file).name

        return (done_path / task_filename).exists()

    def check_completion_custom(self) -> bool:
        """Custom completion check based on task criteria."""
        # Check multiple conditions
        needs_action = self.vault_path / 'Needs_Action'
        pending_approval = self.vault_path / 'Pending_Approval'

        # Count pending items
        needs_action_count = len(list(needs_action.glob('*.md'))) if needs_action.exists() else 0
        pending_approval_count = len(list(pending_approval.glob('*.md'))) if pending_approval.exists() else 0

        # Complete if no pending items
        return needs_action_count == 0 and pending_approval_count == 0

    def is_complete(self, output: str = None) -> bool:
        """Check if task is complete based on strategy."""
        strategy = self.state.get('strategy', STRATEGY_FILE)

        if strategy == STRATEGY_PROMISE:
            if output is None:
                return False
            return self.check_completion_promise(output)

        elif strategy == STRATEGY_FILE:
            return self.check_completion_file_movement()

        elif strategy == STRATEGY_CUSTOM:
            return self.check_completion_custom()

        return False

    def should_continue(self, output: str = None) -> bool:
        """Determine if Claude should continue working."""
        if not self.is_active():
            return False

        # Check max iterations
        current = self.state.get('current_iteration', 0)
        max_iter = self.state.get('max_iterations', MAX_ITERATIONS)

        if current >= max_iter:
            self._log(f"Max iterations ({max_iter}) reached. Stopping.")
            self.stop_loop("max_iterations")
            return False

        # Check completion
        if self.is_complete(output):
            self._log("Task complete! Stopping.")
            self.stop_loop("completed")
            return False

        # Continue
        self.state['current_iteration'] = current + 1
        self.state['last_output'] = output[:500] if output else None  # Store snippet
        self._save_state()

        self._log(f"Task not complete. Continuing (iteration {current + 1}/{max_iter})")
        return True

    def get_continuation_prompt(self) -> str:
        """Generate prompt to continue the task."""
        task_desc = self.state.get('task_description', 'Continue working on the task')
        iteration = self.state.get('current_iteration', 0)

        prompt = f"""Continue working on: {task_desc}

This is iteration {iteration}. Check your progress:
- Review what you've done so far
- Check /Needs_Action for pending items
- Check /Pending_Approval for items needing approval
- Check /Done to see what's complete

If the task is complete, output: <promise>TASK_COMPLETE</promise>
Otherwise, continue working until complete.
"""
        return prompt


def main():
    """Main hook entry point called by Claude Code."""
    hook = RalphWiggumHook()

    # Read output from stdin (Claude's last response)
    output = sys.stdin.read() if not sys.stdin.isatty() else ""

    # Check if should continue
    if hook.should_continue(output):
        # Re-inject prompt to continue
        continuation = hook.get_continuation_prompt()
        print(continuation, file=sys.stdout)

        # Exit with code 1 to signal "don't stop, continue"
        sys.exit(1)
    else:
        # Allow Claude to exit normally
        if hook.is_active():
            hook.stop_loop("completed")
        sys.exit(0)


if __name__ == '__main__':
    main()
