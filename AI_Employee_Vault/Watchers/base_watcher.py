"""
Base Watcher - Template for all AI Employee watchers.
All watchers inherit from this class.
"""

import time
import logging
import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """
    Abstract base class for all watchers.

    Watchers are the "senses" of the AI Employee - they monitor
    external sources and create action files for Claude to process.
    """

    def __init__(self, vault_path: str = None, check_interval: int = 60):
        """
        Initialize the watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks
        """
        self.vault_path = Path(vault_path or os.getenv('VAULT_PATH', '.'))
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

        # Standard folders
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs = self.vault_path / 'Logs'

        # Ensure folders exist
        self.inbox.mkdir(exist_ok=True)
        self.needs_action.mkdir(exist_ok=True)
        self.logs.mkdir(exist_ok=True)

        # Development mode
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

        self.logger.info(f"Initialized {self.__class__.__name__}")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Dry run mode: {self.dry_run}")

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.

        Returns:
            List of new items found
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a markdown file in Needs_Action folder.

        Args:
            item: The item to create an action file for

        Returns:
            Path to the created file
        """
        pass

    def log_action(self, action_type: str, details: dict):
        """
        Log an action to the audit log.

        Args:
            action_type: Type of action (e.g., 'email_received')
            details: Dictionary of action details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "watcher": self.__class__.__name__,
            "action_type": action_type,
            "dry_run": self.dry_run,
            **details
        }

        # Log to daily file
        log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        # Read existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except json.JSONDecodeError:
                logs = []

        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

        self.logger.info(f"Logged: {action_type}")

    def run(self):
        """
        Main loop - continuously check for updates.
        """
        self.logger.info(f"Starting {self.__class__.__name__} (interval: {self.check_interval}s)")

        while True:
            try:
                items = self.check_for_updates()

                for item in items:
                    filepath = self.create_action_file(item)
                    self.logger.info(f"Created action file: {filepath}")

            except KeyboardInterrupt:
                self.logger.info("Stopping watcher (keyboard interrupt)")
                break
            except Exception as e:
                self.logger.error(f"Error in watcher loop: {e}")
                self.log_action("error", {"error": str(e)})

            time.sleep(self.check_interval)

    def run_once(self):
        """
        Run a single check (useful for testing).
        """
        self.logger.info(f"Running single check for {self.__class__.__name__}")
        items = self.check_for_updates()

        for item in items:
            filepath = self.create_action_file(item)
            self.logger.info(f"Created action file: {filepath}")

        return items


if __name__ == "__main__":
    print("This is a base class - import and extend it in your watcher.")
