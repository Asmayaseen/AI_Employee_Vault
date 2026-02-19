#!/usr/bin/env python3
"""
Watchdog Process Monitor (Gold Tier - Error Recovery)

Monitors and auto-restarts critical watcher processes.
Implements Section 7.4 of the hackathon architecture.

Usage:
    python watchdog.py                   # Run watchdog monitor
    python watchdog.py --status          # Show process status
    python watchdog.py --restart <name>  # Restart a process
"""

import subprocess
import time
import signal
import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(
                os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'),
                'Logs', 'watchdog.log'
            ),
            mode='a'
        )
    ]
)
logger = logging.getLogger('Watchdog')

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))
WATCHERS_DIR = VAULT_PATH / 'Watchers'
PID_DIR = Path('/tmp/ai_employee')
STATE_FILE = PID_DIR / 'watchdog_state.json'

# Processes to monitor
MANAGED_PROCESSES = {
    'gmail_watcher': {
        'command': f'python3 {WATCHERS_DIR}/gmail_watcher.py',
        'critical': True,
        'max_restarts': 5,
        'restart_window': 300,  # seconds
    },
    'linkedin_watcher': {
        'command': f'python3 {WATCHERS_DIR}/linkedin_watcher.py',
        'critical': False,
        'max_restarts': 3,
        'restart_window': 300,
    },
    'filesystem_watcher': {
        'command': f'python3 {WATCHERS_DIR}/filesystem_watcher.py',
        'critical': True,
        'max_restarts': 10,
        'restart_window': 300,
    },
    'approval_watcher': {
        'command': f'python3 {WATCHERS_DIR}/approval_watcher.py',
        'critical': True,
        'max_restarts': 5,
        'restart_window': 300,
    },
}

CHECK_INTERVAL = 60  # seconds between health checks


class ProcessState:
    """Track state for a managed process."""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.pid: Optional[int] = None
        self.process: Optional[subprocess.Popen] = None
        self.restart_count = 0
        self.restart_times = []
        self.last_started: Optional[str] = None
        self.status = 'stopped'

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'pid': self.pid,
            'status': self.status,
            'restart_count': self.restart_count,
            'last_started': self.last_started,
        }


class Watchdog:
    """Process health monitor and auto-restarter."""

    def __init__(self):
        PID_DIR.mkdir(parents=True, exist_ok=True)
        self.processes: Dict[str, ProcessState] = {}
        self.running = True

        for name, cfg in MANAGED_PROCESSES.items():
            self.processes[name] = ProcessState(name, cfg)

        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Graceful shutdown on signal."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stop_all()

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process is still alive."""
        if pid is None:
            return False
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def _read_pid_file(self, name: str) -> Optional[int]:
        """Read PID from file."""
        pid_file = PID_DIR / f'{name}.pid'
        if pid_file.exists():
            try:
                return int(pid_file.read_text().strip())
            except (ValueError, IOError):
                return None
        return None

    def _write_pid_file(self, name: str, pid: int):
        """Write PID to file."""
        pid_file = PID_DIR / f'{name}.pid'
        pid_file.write_text(str(pid))

    def _can_restart(self, state: ProcessState) -> bool:
        """Check if process can be restarted (within limits)."""
        now = time.time()
        window = state.config['restart_window']

        # Clean old restart times
        state.restart_times = [t for t in state.restart_times if now - t < window]

        if len(state.restart_times) >= state.config['max_restarts']:
            logger.error(
                f"[{state.name}] Max restarts ({state.config['max_restarts']}) "
                f"reached in {window}s window. Backing off."
            )
            return False

        return True

    def start_process(self, name: str) -> bool:
        """Start a managed process."""
        state = self.processes.get(name)
        if not state:
            logger.error(f"Unknown process: {name}")
            return False

        if state.pid and self._is_process_running(state.pid):
            logger.info(f"[{name}] Already running (PID {state.pid})")
            return True

        try:
            cmd = state.config['command'].split()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            state.process = proc
            state.pid = proc.pid
            state.status = 'running'
            state.last_started = datetime.now().isoformat()

            self._write_pid_file(name, proc.pid)
            logger.info(f"[{name}] Started with PID {proc.pid}")
            return True

        except Exception as e:
            state.status = 'error'
            logger.error(f"[{name}] Failed to start: {e}")
            return False

    def stop_process(self, name: str) -> bool:
        """Stop a managed process."""
        state = self.processes.get(name)
        if not state:
            return False

        if state.pid and self._is_process_running(state.pid):
            try:
                os.kill(state.pid, signal.SIGTERM)
                time.sleep(2)
                if self._is_process_running(state.pid):
                    os.kill(state.pid, signal.SIGKILL)
                logger.info(f"[{name}] Stopped (PID {state.pid})")
            except Exception as e:
                logger.error(f"[{name}] Error stopping: {e}")

        state.pid = None
        state.status = 'stopped'

        pid_file = PID_DIR / f'{name}.pid'
        if pid_file.exists():
            pid_file.unlink()

        return True

    def stop_all(self):
        """Stop all managed processes."""
        for name in self.processes:
            self.stop_process(name)

    def check_and_restart(self):
        """Check all processes and restart dead ones."""
        for name, state in self.processes.items():
            # First check if PID was written by external start scripts
            if not state.pid:
                state.pid = self._read_pid_file(name)

            if state.pid and self._is_process_running(state.pid):
                state.status = 'running'
                continue

            # Process is dead
            state.status = 'dead'
            logger.warning(f"[{name}] Not running")

            if self._can_restart(state):
                state.restart_times.append(time.time())
                state.restart_count += 1
                logger.info(f"[{name}] Attempting restart #{state.restart_count}")

                if self.start_process(name):
                    self._notify_restart(name, state.restart_count)
                else:
                    logger.error(f"[{name}] Restart failed")

    def _notify_restart(self, name: str, count: int):
        """Create notification file for process restart."""
        notif_dir = VAULT_PATH / 'Needs_Action'
        notif_dir.mkdir(exist_ok=True)

        # Only create notification for critical processes or repeated restarts
        state = self.processes[name]
        if state.config.get('critical') or count >= 3:
            filepath = notif_dir / f"WATCHDOG_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath.write_text(f"""---
type: system_alert
source: watchdog
process: {name}
restart_count: {count}
timestamp: {datetime.now().isoformat()}
priority: {'high' if count >= 3 else 'normal'}
---

## Process Restart Alert

**Process**: {name}
**Restart Count**: {count}
**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'WARNING: Multiple restarts detected. Manual investigation recommended.' if count >= 3 else 'Process was automatically restarted.'}
""")

    def save_state(self):
        """Save current state to file."""
        state = {
            'timestamp': datetime.now().isoformat(),
            'processes': {
                name: ps.to_dict()
                for name, ps in self.processes.items()
            }
        }
        STATE_FILE.write_text(json.dumps(state, indent=2))

    def get_status(self) -> Dict:
        """Get status of all processes."""
        status = {}
        for name, state in self.processes.items():
            if not state.pid:
                state.pid = self._read_pid_file(name)

            running = self._is_process_running(state.pid) if state.pid else False
            status[name] = {
                'pid': state.pid,
                'running': running,
                'restart_count': state.restart_count,
                'last_started': state.last_started,
                'critical': state.config.get('critical', False),
            }
        return status

    def run(self):
        """Main watchdog loop."""
        logger.info("Watchdog started - monitoring processes")
        logger.info(f"Managed processes: {list(self.processes.keys())}")

        while self.running:
            try:
                self.check_and_restart()
                self.save_state()
            except Exception as e:
                logger.error(f"Watchdog error: {e}")

            time.sleep(CHECK_INTERVAL)

        logger.info("Watchdog stopped")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='AI Employee Watchdog')
    parser.add_argument('--status', action='store_true', help='Show process status')
    parser.add_argument('--restart', type=str, help='Restart a specific process')
    parser.add_argument('--start-all', action='store_true', help='Start all processes')
    args = parser.parse_args()

    wd = Watchdog()

    if args.status:
        status = wd.get_status()
        print(json.dumps(status, indent=2))
    elif args.restart:
        wd.stop_process(args.restart)
        wd.start_process(args.restart)
    elif args.start_all:
        for name in MANAGED_PROCESSES:
            wd.start_process(name)
        print("All processes started")
    else:
        wd.run()


if __name__ == '__main__':
    main()
