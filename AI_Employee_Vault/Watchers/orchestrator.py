"""
Master Orchestrator - Manages all AI Employee watchers.

This is the central coordinator that:
1. Starts and manages multiple watcher processes
2. Handles process lifecycle (start, stop, restart)
3. Implements health checks and auto-recovery
4. Coordinates between watchers
5. Manages graceful shutdown

Usage:
    python orchestrator.py                  # Start all watchers
    python orchestrator.py --watchers gmail filesystem  # Start specific watchers
    python orchestrator.py --health-only    # Just health check
"""

import os
import sys
import time
import signal
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('orchestrator.log')
    ]
)
logger = logging.getLogger('Orchestrator')


@dataclass
class WatcherConfig:
    """Configuration for a watcher process."""
    name: str
    script: str
    enabled: bool = True
    check_interval: int = 60
    max_restarts: int = 5
    restart_delay: int = 30
    required_env: list = field(default_factory=list)
    args: list = field(default_factory=list)


@dataclass
class WatcherState:
    """Runtime state of a watcher process."""
    process: Optional[subprocess.Popen] = None
    start_time: Optional[datetime] = None
    restart_count: int = 0
    last_error: Optional[str] = None
    is_healthy: bool = False


class Orchestrator:
    """
    Master orchestrator for AI Employee watchers.
    Manages lifecycle, health checks, and coordination.
    """

    # Watcher configurations
    WATCHERS = {
        'filesystem': WatcherConfig(
            name='FileSystem Watcher',
            script='filesystem_watcher.py',
            check_interval=10,
            required_env=[]
        ),
        'gmail': WatcherConfig(
            name='Gmail Watcher',
            script='gmail_watcher.py',
            check_interval=120,
            required_env=['GMAIL_CREDENTIALS_PATH'],
            enabled=True  # Will check for credentials
        ),
        'whatsapp': WatcherConfig(
            name='WhatsApp Watcher',
            script='whatsapp_watcher.py',
            check_interval=30,
            required_env=[],
            enabled=True  # Requires manual QR scan
        ),
        'approval': WatcherConfig(
            name='Approval Watcher',
            script='approval_watcher.py',
            check_interval=5,
            required_env=[]
        ),
        'facebook': WatcherConfig(
            name='Facebook Watcher',
            script='facebook_watcher.py',
            check_interval=300,
            required_env=['META_ACCESS_TOKEN']
        ),
        'instagram': WatcherConfig(
            name='Instagram Watcher',
            script='instagram_watcher.py',
            check_interval=300,
            required_env=['INSTAGRAM_BUSINESS_ID']
        ),
        'twitter': WatcherConfig(
            name='Twitter Watcher',
            script='twitter_watcher.py',
            check_interval=300,
            required_env=['TWITTER_BEARER_TOKEN']
        ),
        'linkedin': WatcherConfig(
            name='LinkedIn Watcher',
            script='linkedin_watcher.py',
            check_interval=300,
            required_env=[]
        )
    }

    def __init__(self, vault_path: str = None, watchers_dir: str = None):
        """Initialize the orchestrator."""
        self.vault_path = Path(vault_path or os.getenv(
            'VAULT_PATH',
            '/mnt/d/Ai-Employee/AI_Employee_Vault'
        ))
        self.watchers_dir = Path(watchers_dir or self.vault_path / 'Watchers')
        self.logs_dir = self.vault_path / 'Logs'
        self.logs_dir.mkdir(exist_ok=True)

        # Watcher states
        self.states: Dict[str, WatcherState] = {}

        # Control flags
        self.running = False
        self.shutdown_event = threading.Event()

        # Health check interval
        self.health_check_interval = 30

        # Zone routing (Platinum)
        self._zone_router = None
        try:
            sys.path.insert(0, str(self.vault_path / 'utils'))
            from work_zones import resolve_zone, get_active_zone
            self._resolve_zone = resolve_zone
            self._get_active_zone = get_active_zone
            logger.info(f"Work zones loaded, active zone: {get_active_zone()}")
        except ImportError:
            self._resolve_zone = None
            self._get_active_zone = None
            logger.info("Work zones module not available, zone routing disabled")

        logger.info(f"Orchestrator initialized")
        logger.info(f"Vault path: {self.vault_path}")
        logger.info(f"Watchers directory: {self.watchers_dir}")

    def should_handle_task(self, task_type: str) -> bool:
        """Check if this agent should handle a given task type based on zone routing."""
        if not self._resolve_zone:
            return True  # No zones configured, handle everything

        agent_name = os.getenv('AGENT_NAME', 'local')
        target_zone = self._resolve_zone(task_type)

        if target_zone == agent_name:
            return True
        if target_zone == 'both':
            return True
        # If routing says 'active', check if we are the active zone
        active = self._get_active_zone()
        if target_zone == active and agent_name == active:
            return True

        logger.debug(f"Task '{task_type}' routed to zone '{target_zone}', skipping (we are '{agent_name}')")
        return False

    def _check_watcher_requirements(self, watcher_id: str) -> tuple[bool, str]:
        """Check if a watcher's requirements are met."""
        config = self.WATCHERS.get(watcher_id)
        if not config:
            return False, f"Unknown watcher: {watcher_id}"

        # Check script exists
        script_path = self.watchers_dir / config.script
        if not script_path.exists():
            return False, f"Script not found: {script_path}"

        # Check required environment variables
        for env_var in config.required_env:
            if not os.getenv(env_var):
                return False, f"Missing environment variable: {env_var}"

        # Special checks
        if watcher_id == 'gmail':
            creds_path = os.getenv('GMAIL_CREDENTIALS_PATH',
                                   str(self.watchers_dir / 'credentials.json'))
            if not Path(creds_path).exists():
                return False, f"Gmail credentials not found at {creds_path}"

        return True, "OK"

    def start_watcher(self, watcher_id: str) -> bool:
        """Start a single watcher process."""
        config = self.WATCHERS.get(watcher_id)
        if not config or not config.enabled:
            logger.warning(f"Watcher {watcher_id} is disabled or not found")
            return False

        # Check requirements
        ready, message = self._check_watcher_requirements(watcher_id)
        if not ready:
            logger.warning(f"Cannot start {watcher_id}: {message}")
            return False

        # Check if already running
        state = self.states.get(watcher_id)
        if state and state.process and state.process.poll() is None:
            logger.info(f"{watcher_id} is already running")
            return True

        try:
            script_path = self.watchers_dir / config.script

            # Build command
            cmd = [
                sys.executable,
                str(script_path),
                '--vault', str(self.vault_path),
                '--interval', str(config.check_interval)
            ] + config.args

            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=str(self.watchers_dir),
                env={**os.environ, 'VAULT_PATH': str(self.vault_path)}
            )

            # Update state
            self.states[watcher_id] = WatcherState(
                process=process,
                start_time=datetime.now(),
                is_healthy=True
            )

            logger.info(f"Started {config.name} (PID: {process.pid})")
            self._log_event('watcher_started', {
                'watcher': watcher_id,
                'pid': process.pid
            })

            return True

        except Exception as e:
            logger.error(f"Failed to start {watcher_id}: {e}")
            if watcher_id in self.states:
                self.states[watcher_id].last_error = str(e)
            return False

    def stop_watcher(self, watcher_id: str) -> bool:
        """Stop a single watcher process."""
        state = self.states.get(watcher_id)
        if not state or not state.process:
            return True

        try:
            process = state.process

            # Try graceful termination
            process.terminate()

            # Wait up to 10 seconds
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill
                process.kill()
                process.wait()

            logger.info(f"Stopped {watcher_id}")
            self._log_event('watcher_stopped', {'watcher': watcher_id})

            state.process = None
            state.is_healthy = False
            return True

        except Exception as e:
            logger.error(f"Error stopping {watcher_id}: {e}")
            return False

    def restart_watcher(self, watcher_id: str) -> bool:
        """Restart a watcher process."""
        state = self.states.get(watcher_id, WatcherState())
        config = self.WATCHERS.get(watcher_id)

        if state.restart_count >= config.max_restarts:
            logger.error(f"{watcher_id} exceeded max restarts ({config.max_restarts})")
            self._log_event('watcher_max_restarts', {'watcher': watcher_id})
            return False

        logger.info(f"Restarting {watcher_id} (attempt {state.restart_count + 1})")

        self.stop_watcher(watcher_id)
        time.sleep(config.restart_delay)

        if self.start_watcher(watcher_id):
            self.states[watcher_id].restart_count = state.restart_count + 1
            return True
        return False

    def check_health(self) -> Dict[str, bool]:
        """Check health of all watchers."""
        health = {}

        for watcher_id, state in self.states.items():
            if not state.process:
                health[watcher_id] = False
                continue

            # Check if process is still running
            poll_result = state.process.poll()
            if poll_result is None:
                # Process is running
                health[watcher_id] = True
                state.is_healthy = True
            else:
                # Process has exited
                health[watcher_id] = False
                state.is_healthy = False
                state.last_error = f"Process exited with code {poll_result}"
                logger.warning(f"{watcher_id} has stopped (exit code: {poll_result})")

        return health

    def _health_check_loop(self):
        """Background thread for health checks and auto-recovery."""
        while not self.shutdown_event.is_set():
            try:
                health = self.check_health()

                for watcher_id, is_healthy in health.items():
                    if not is_healthy and self.WATCHERS[watcher_id].enabled:
                        logger.warning(f"{watcher_id} is unhealthy, attempting restart")
                        self.restart_watcher(watcher_id)

                # Log health status periodically
                self._log_event('health_check', health)

            except Exception as e:
                logger.error(f"Health check error: {e}")

            self.shutdown_event.wait(self.health_check_interval)

    def _log_event(self, event_type: str, details: dict):
        """Log an orchestrator event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }

        # Append to daily log
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}_orchestrator.json"
        try:
            import json
            logs = []
            if log_file.exists():
                logs = json.loads(log_file.read_text())
            logs.append(log_entry)
            log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            logger.error(f"Failed to write log: {e}")

    def start_all(self, watcher_ids: list = None):
        """Start all (or specified) watchers."""
        self.running = True

        watchers_to_start = watcher_ids or list(self.WATCHERS.keys())

        logger.info("=" * 50)
        logger.info("Starting AI Employee Orchestrator")
        logger.info("=" * 50)

        for watcher_id in watchers_to_start:
            if self.WATCHERS.get(watcher_id, WatcherConfig('', '')).enabled:
                self.start_watcher(watcher_id)

        # Start health check thread
        self.health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_thread.start()

        logger.info("Orchestrator started")
        self._log_event('orchestrator_started', {'watchers': watchers_to_start})

    def stop_all(self):
        """Stop all watchers and shutdown."""
        logger.info("Shutting down orchestrator...")
        self.running = False
        self.shutdown_event.set()

        for watcher_id in list(self.states.keys()):
            self.stop_watcher(watcher_id)

        self._log_event('orchestrator_stopped', {})
        logger.info("Orchestrator stopped")

    def status(self) -> dict:
        """Get current status of all watchers."""
        status = {}
        for watcher_id, config in self.WATCHERS.items():
            state = self.states.get(watcher_id, WatcherState())
            ready, message = self._check_watcher_requirements(watcher_id)

            status[watcher_id] = {
                'name': config.name,
                'enabled': config.enabled,
                'requirements_met': ready,
                'requirements_message': message,
                'running': state.process is not None and state.process.poll() is None,
                'healthy': state.is_healthy,
                'pid': state.process.pid if state.process else None,
                'start_time': state.start_time.isoformat() if state.start_time else None,
                'restart_count': state.restart_count,
                'last_error': state.last_error
            }
        return status

    def run(self, watcher_ids: list = None):
        """Main run loop."""
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop_all()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        self.start_all(watcher_ids)

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all()


def print_status(orchestrator: Orchestrator):
    """Print formatted status of all watchers."""
    status = orchestrator.status()

    print("\n" + "=" * 60)
    print("AI Employee Watchers Status")
    print("=" * 60)

    for watcher_id, info in status.items():
        running_icon = "🟢" if info['running'] else "🔴"
        enabled_text = "enabled" if info['enabled'] else "disabled"

        print(f"\n{running_icon} {info['name']} ({watcher_id})")
        print(f"   Status: {enabled_text}")
        print(f"   Requirements: {info['requirements_message']}")

        if info['running']:
            print(f"   PID: {info['pid']}")
            print(f"   Started: {info['start_time']}")
            print(f"   Restarts: {info['restart_count']}")

        if info['last_error']:
            print(f"   Last Error: {info['last_error']}")

    print("\n" + "=" * 60)


# Main execution
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--watchers', '-w', nargs='+', help='Specific watchers to run')
    parser.add_argument('--status', '-s', action='store_true', help='Show status and exit')
    parser.add_argument('--health-only', action='store_true', help='Run health check only')

    args = parser.parse_args()

    vault_path = args.vault or os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')

    orchestrator = Orchestrator(vault_path=vault_path)

    if args.status or args.health_only:
        print_status(orchestrator)
    else:
        print(f"\n🤖 AI Employee Orchestrator Starting...")
        print(f"📁 Vault: {vault_path}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        print("Press Ctrl+C to stop")
        print("-" * 50)

        orchestrator.run(args.watchers)
