"""
WatcherConfig and WatcherState models.

Used by:
- orchestrator.py (manages watcher lifecycle)
- dashboard.py (displays watcher status)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import subprocess


@dataclass
class WatcherConfig:
    """Configuration for a watcher process."""
    name: str
    script: str
    enabled: bool = True
    check_interval: int = 60
    max_restarts: int = 5
    restart_delay: int = 30
    required_env: List[str] = field(default_factory=list)
    args: List[str] = field(default_factory=list)


@dataclass
class WatcherState:
    """Runtime state of a watcher process."""
    process: Optional[subprocess.Popen] = None
    start_time: Optional[datetime] = None
    restart_count: int = 0
    last_error: Optional[str] = None
    is_healthy: bool = False

    @property
    def uptime_seconds(self) -> float:
        """Get watcher uptime in seconds."""
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def is_running(self) -> bool:
        """Check if watcher process is still running."""
        if not self.process:
            return False
        return self.process.poll() is None

    def to_dict(self) -> dict:
        """Serialize state (excluding process handle)."""
        return {
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'restart_count': self.restart_count,
            'last_error': self.last_error,
            'is_healthy': self.is_healthy,
            'uptime_seconds': self.uptime_seconds,
            'is_running': self.is_running,
        }
