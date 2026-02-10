#!/usr/bin/env python3
"""
Ralph Wiggum Integration Module

This module provides seamless integration between the orchestrator and Ralph loops.
It allows the orchestrator to automatically start Ralph loops when work is detected.

Features:
- Automatic Ralph loop triggering when items arrive in /Needs_Action
- Claude processor integration
- Status reporting and monitoring
- Emergency stop capabilities
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from stop import RalphWiggumHook, STRATEGY_FILE, STRATEGY_PROMISE, STRATEGY_CUSTOM
from ralph_controller import RalphController


class RalphIntegration:
    """Integration layer between orchestrator and Ralph loops."""

    def __init__(self, vault_path: str = None):
        """Initialize Ralph integration."""
        self.vault_path = Path(vault_path or os.getenv(
            'VAULT_PATH',
            '/mnt/d/Ai-Employee/AI_Employee_Vault'
        ))
        self.controller = RalphController()
        self.hooks_dir = Path(__file__).parent
        self.logs_dir = self.vault_path / 'Logs'
        self.logs_dir.mkdir(exist_ok=True)

    def _log(self, message: str):
        """Log integration events."""
        log_file = self.logs_dir / 'ralph_integration.log'
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"

        with log_file.open('a') as f:
            f.write(log_entry)

    def get_pending_count(self) -> Dict[str, int]:
        """Count pending items in various folders."""
        folders = {
            'needs_action': self.vault_path / 'Needs_Action',
            'pending_approval': self.vault_path / 'Pending_Approval',
            'plans': self.vault_path / 'Plans',
            'done': self.vault_path / 'Done'
        }

        counts = {}
        for name, folder in folders.items():
            if folder.exists():
                counts[name] = len(list(folder.glob('*.md')))
            else:
                counts[name] = 0

        return counts

    def should_start_ralph(self) -> tuple[bool, str]:
        """Determine if Ralph loop should be started."""
        # Don't start if already active
        if self.controller.hook.is_active():
            return False, "Ralph loop already active"

        counts = self.get_pending_count()

        # Start if there are pending items
        if counts['needs_action'] > 0:
            return True, f"{counts['needs_action']} items in /Needs_Action"

        return False, "No pending work"

    def start_automatic_processing(self, max_iterations: int = 10) -> bool:
        """Start automatic processing of pending items."""
        should_start, reason = self.should_start_ralph()

        if not should_start:
            self._log(f"Not starting Ralph: {reason}")
            return False

        counts = self.get_pending_count()
        task_description = f"Process {counts['needs_action']} items in /Needs_Action. For each item: analyze content, create plan, execute if safe, or request approval. Move to /Done when complete."

        success = self.controller.start(
            task_description,
            strategy=STRATEGY_CUSTOM,
            max_iterations=max_iterations
        )

        if success:
            self._log(f"Started automatic processing: {reason}")
        else:
            self._log(f"Failed to start processing")

        return success

    def start_file_processing(self, file_path: str, max_iterations: int = 5) -> bool:
        """Start processing a specific file."""
        file_path = Path(file_path)

        if not file_path.exists():
            self._log(f"File not found: {file_path}")
            return False

        task_description = f"Process {file_path.name}: analyze content, create plan, execute actions, and move to /Done when complete."

        success = self.controller.start(
            task_description,
            strategy=STRATEGY_FILE,
            task_file=str(file_path),
            max_iterations=max_iterations
        )

        if success:
            self._log(f"Started file processing: {file_path.name}")
        else:
            self._log(f"Failed to start file processing")

        return success

    def trigger_claude_processor(self) -> bool:
        """Trigger Claude to process pending items."""
        try:
            # Check if there's work to do
            counts = self.get_pending_count()
            if counts['needs_action'] == 0:
                self._log("No items to process")
                return False

            # Start Ralph loop first
            self.start_automatic_processing()

            # The actual Claude invocation happens through the cron/orchestrator
            # This just sets up the state for when Claude runs

            self._log(f"Triggered processing for {counts['needs_action']} items")
            return True

        except Exception as e:
            self._log(f"Error triggering processor: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Ralph status."""
        status = {
            'ralph_active': self.controller.hook.is_active(),
            'pending_counts': self.get_pending_count(),
            'state': self.controller.hook.state.copy(),
            'timestamp': datetime.now().isoformat()
        }

        if status['ralph_active']:
            status['progress'] = {
                'current_iteration': self.controller.hook.state.get('current_iteration', 0),
                'max_iterations': self.controller.hook.state.get('max_iterations', 10),
                'task': self.controller.hook.state.get('task_description', 'Unknown'),
                'strategy': self.controller.hook.state.get('strategy', 'Unknown')
            }

        return status

    def emergency_stop(self) -> bool:
        """Emergency stop all Ralph operations."""
        self._log("EMERGENCY STOP triggered")
        self.controller.reset()
        return True

    def check_and_auto_process(self) -> bool:
        """
        Check for pending work and auto-start processing if needed.

        This is designed to be called periodically by the orchestrator.
        """
        status = self.get_status()

        # If Ralph is already running, check progress
        if status['ralph_active']:
            progress = status.get('progress', {})
            current = progress.get('current_iteration', 0)
            max_iter = progress.get('max_iterations', 10)
            self._log(f"Ralph active: iteration {current}/{max_iter}")
            return True

        # Check if there's work to do
        counts = status['pending_counts']
        if counts['needs_action'] > 0:
            self._log(f"Auto-processing: {counts['needs_action']} pending items")
            return self.start_automatic_processing()

        return False


# CLI interface for testing
def main():
    """CLI for Ralph integration testing."""
    import argparse

    parser = argparse.ArgumentParser(description='Ralph Integration Manager')
    subparsers = parser.add_subparsers(dest='command')

    # Status
    subparsers.add_parser('status', help='Show integration status')

    # Auto-process
    subparsers.add_parser('auto', help='Auto-process pending items')

    # Process file
    file_parser = subparsers.add_parser('process', help='Process specific file')
    file_parser.add_argument('file', help='File to process')

    # Trigger
    subparsers.add_parser('trigger', help='Trigger Claude processor')

    # Stop
    subparsers.add_parser('stop', help='Emergency stop')

    args = parser.parse_args()
    integration = RalphIntegration()

    if args.command == 'status':
        status = integration.get_status()
        print(json.dumps(status, indent=2, default=str))

    elif args.command == 'auto':
        result = integration.start_automatic_processing()
        print(f"Auto-processing: {'Started' if result else 'Not started'}")

    elif args.command == 'process':
        result = integration.start_file_processing(args.file)
        print(f"File processing: {'Started' if result else 'Failed'}")

    elif args.command == 'trigger':
        result = integration.trigger_claude_processor()
        print(f"Trigger: {'Success' if result else 'Failed'}")

    elif args.command == 'stop':
        integration.emergency_stop()
        print("Emergency stop executed")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
