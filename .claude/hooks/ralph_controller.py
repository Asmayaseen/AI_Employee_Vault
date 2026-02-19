#!/usr/bin/env python3
"""
Ralph Wiggum Loop Controller

Helper script to start/stop/status Ralph loops from orchestrator or command line.

Usage:
    python ralph_controller.py start "Process all items in /Needs_Action"
    python ralph_controller.py stop
    python ralph_controller.py status
    python ralph_controller.py reset
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Import the hook class
from stop import RalphWiggumHook, STRATEGY_FILE, STRATEGY_PROMISE, STRATEGY_CUSTOM


class RalphController:
    """Control Ralph loops from orchestrator or CLI."""

    def __init__(self):
        self.hook = RalphWiggumHook()

    def start(self, task_description: str, strategy: str = STRATEGY_FILE,
              task_file: str = None, max_iterations: int = 10):
        """Start a new Ralph loop."""
        if self.hook.is_active():
            print("❌ Ralph loop already active!")
            print(f"   Task: {self.hook.state.get('task_description')}")
            print(f"   Iteration: {self.hook.state.get('current_iteration')}/{self.hook.state.get('max_iterations')}")
            return False

        self.hook.start_loop(task_description, strategy, task_file, max_iterations)
        print(f"✅ Ralph loop started!")
        print(f"   Task: {task_description}")
        print(f"   Strategy: {strategy}")
        print(f"   Max iterations: {max_iterations}")

        if task_file:
            print(f"   Tracking file: {task_file}")

        return True

    def stop(self, reason: str = "manual"):
        """Stop the current Ralph loop."""
        if not self.hook.is_active():
            print("ℹ️  No active Ralph loop")
            return False

        iterations = self.hook.state.get('current_iteration', 0)
        self.hook.stop_loop(reason)

        print(f"✅ Ralph loop stopped: {reason}")
        print(f"   Completed {iterations} iterations")
        return True

    def status(self):
        """Show status of Ralph loop."""
        if not self.hook.is_active():
            print("Status: ⚪ INACTIVE")
            if self.hook.state.get('stopped_at'):
                print(f"Last stopped: {self.hook.state.get('stopped_at')}")
            return

        print("Status: 🟢 ACTIVE")
        print(f"Task: {self.hook.state.get('task_description')}")
        print(f"Strategy: {self.hook.state.get('strategy')}")
        print(f"Iteration: {self.hook.state.get('current_iteration')}/{self.hook.state.get('max_iterations')}")
        print(f"Started: {self.hook.state.get('started_at')}")

        if self.hook.state.get('task_file'):
            print(f"Tracking: {self.hook.state.get('task_file')}")

    def reset(self):
        """Reset Ralph state (emergency use)."""
        self.hook.state = {'active': False}
        self.hook._save_state()
        print("✅ Ralph state reset")

    def check_completion(self):
        """Check if current task is complete."""
        if not self.hook.is_active():
            print("No active Ralph loop")
            return None

        complete = self.hook.is_complete()
        if complete:
            print("✅ Task is COMPLETE")
        else:
            print("⏳ Task still IN PROGRESS")

        return complete


def main():
    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop Controller')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start Ralph loop')
    start_parser.add_argument('task', help='Task description')
    start_parser.add_argument('--strategy', choices=['promise', 'file_movement', 'custom'],
                              default='file_movement', help='Completion detection strategy')
    start_parser.add_argument('--file', help='Task file to track (for file_movement strategy)')
    start_parser.add_argument('--max-iterations', type=int, default=10,
                              help='Maximum iterations')

    # Stop command
    subparsers.add_parser('stop', help='Stop Ralph loop')

    # Status command
    subparsers.add_parser('status', help='Show Ralph loop status')

    # Reset command
    subparsers.add_parser('reset', help='Reset Ralph state')

    # Check command
    subparsers.add_parser('check', help='Check task completion')

    args = parser.parse_args()
    controller = RalphController()

    if args.command == 'start':
        controller.start(
            args.task,
            strategy=args.strategy,
            task_file=args.file,
            max_iterations=args.max_iterations
        )

    elif args.command == 'stop':
        controller.stop()

    elif args.command == 'status':
        controller.status()

    elif args.command == 'reset':
        controller.reset()

    elif args.command == 'check':
        controller.check_completion()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
