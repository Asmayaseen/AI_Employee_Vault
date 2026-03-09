"""
ServiceState model for graceful degradation tracking.

Used by:
- graceful_degradation.py (tracks service health)
- orchestrator.py (monitors component health)
- dashboard.py (displays service status)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ServiceStatus(Enum):
    """Service health status levels."""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    UNAVAILABLE = 'unavailable'


@dataclass
class ServiceState:
    """State tracker for a single service/component."""
    name: str
    status: ServiceStatus = ServiceStatus.HEALTHY
    failure_count: int = 0
    last_failure: Optional[str] = None
    last_success: Optional[str] = None
    last_error: Optional[str] = None
    queued_actions: int = 0

    # Thresholds
    degraded_threshold: int = 2
    unavailable_threshold: int = 5
    recovery_window: int = 300  # seconds before resetting failure count

    def record_failure(self, error: str) -> None:
        """Record a service failure and update status."""
        self.failure_count += 1
        self.last_failure = datetime.now().isoformat()
        self.last_error = error

        if self.failure_count >= self.unavailable_threshold:
            self.status = ServiceStatus.UNAVAILABLE
        elif self.failure_count >= self.degraded_threshold:
            self.status = ServiceStatus.DEGRADED

    def record_success(self) -> None:
        """Record a successful operation and potentially recover status."""
        self.last_success = datetime.now().isoformat()
        self.failure_count = max(0, self.failure_count - 1)

        if self.failure_count < self.degraded_threshold:
            self.status = ServiceStatus.HEALTHY
        elif self.failure_count < self.unavailable_threshold:
            self.status = ServiceStatus.DEGRADED

    @property
    def is_available(self) -> bool:
        """Check if service is available for operations."""
        return self.status != ServiceStatus.UNAVAILABLE

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'status': self.status.value,
            'failure_count': self.failure_count,
            'last_failure': self.last_failure,
            'last_success': self.last_success,
            'last_error': self.last_error,
            'queued_actions': self.queued_actions,
        }
