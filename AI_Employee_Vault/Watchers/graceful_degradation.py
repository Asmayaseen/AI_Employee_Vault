#!/usr/bin/env python3
"""
Graceful Degradation Manager (Gold Tier - Error Recovery)

Implements Section 7.3: when components fail, the system degrades gracefully.

- Gmail API down: Queue outgoing emails locally
- Banking API timeout: Never retry payments automatically
- Claude Code unavailable: Watchers continue collecting, queue grows
- Obsidian vault locked: Write to temporary folder, sync later

Usage:
    from graceful_degradation import DegradationManager, ServiceStatus

    dm = DegradationManager()
    dm.report_failure('gmail', 'Connection timeout')
    if dm.is_available('gmail'):
        send_email(...)
    else:
        dm.queue_action('gmail', {'action': 'send_email', 'to': '...'})
"""

import json
import logging
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger('GracefulDegradation')

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))
QUEUE_DIR = VAULT_PATH / 'Queued_Actions'
QUEUE_DIR.mkdir(exist_ok=True)


class ServiceStatus(Enum):
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

    def record_failure(self, error: str):
        """Record a failure event."""
        self.failure_count += 1
        self.last_failure = datetime.now().isoformat()
        self.last_error = error

        if self.failure_count >= self.unavailable_threshold:
            self.status = ServiceStatus.UNAVAILABLE
        elif self.failure_count >= self.degraded_threshold:
            self.status = ServiceStatus.DEGRADED

        logger.warning(
            f"[{self.name}] Failure #{self.failure_count}: {error} "
            f"(status: {self.status.value})"
        )

    def record_success(self):
        """Record a successful operation, potentially recovering status."""
        self.last_success = datetime.now().isoformat()

        if self.failure_count > 0:
            self.failure_count = max(0, self.failure_count - 1)

        if self.failure_count == 0:
            self.status = ServiceStatus.HEALTHY
        elif self.failure_count < self.degraded_threshold:
            self.status = ServiceStatus.HEALTHY

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'status': self.status.value,
            'failure_count': self.failure_count,
            'last_failure': self.last_failure,
            'last_success': self.last_success,
            'last_error': self.last_error,
            'queued_actions': self.queued_actions,
        }


# Services that must NEVER auto-retry
NEVER_RETRY_ACTIONS = {
    'payment',
    'bank_transfer',
    'invoice_post',
    'delete_record',
}


class DegradationManager:
    """
    Central manager for service health and graceful degradation.

    When a service becomes unavailable, actions are queued to disk
    and replayed when the service recovers.
    """

    def __init__(self):
        self.services: Dict[str, ServiceState] = {}
        self._init_default_services()

    def _init_default_services(self):
        """Register default AI Employee services."""
        defaults = {
            'gmail': {'degraded_threshold': 3, 'unavailable_threshold': 5},
            'whatsapp': {'degraded_threshold': 2, 'unavailable_threshold': 4},
            'linkedin': {'degraded_threshold': 3, 'unavailable_threshold': 6},
            'odoo': {'degraded_threshold': 2, 'unavailable_threshold': 4},
            'facebook': {'degraded_threshold': 3, 'unavailable_threshold': 5},
            'instagram': {'degraded_threshold': 3, 'unavailable_threshold': 5},
            'twitter': {'degraded_threshold': 3, 'unavailable_threshold': 5},
            'claude_code': {'degraded_threshold': 1, 'unavailable_threshold': 3},
            'vault': {'degraded_threshold': 1, 'unavailable_threshold': 2},
        }

        for name, thresholds in defaults.items():
            self.services[name] = ServiceState(name, **thresholds)

    def report_failure(self, service: str, error: str):
        """Report a service failure."""
        if service not in self.services:
            self.services[service] = ServiceState(service)
        self.services[service].record_failure(error)

    def report_success(self, service: str):
        """Report a successful service interaction."""
        if service not in self.services:
            self.services[service] = ServiceState(service)
        self.services[service].record_success()

    def is_available(self, service: str) -> bool:
        """Check if a service is available (healthy or degraded)."""
        state = self.services.get(service)
        if not state:
            return True  # Unknown services assumed available
        return state.status != ServiceStatus.UNAVAILABLE

    def get_status(self, service: str) -> ServiceStatus:
        """Get current status of a service."""
        state = self.services.get(service)
        return state.status if state else ServiceStatus.HEALTHY

    def queue_action(self, service: str, action: Dict):
        """
        Queue an action for later execution when service recovers.

        Args:
            service: Service name
            action: Action dict to be replayed later
        """
        # Safety: Never queue payment-related actions
        action_type = action.get('action_type', '')
        if action_type in NEVER_RETRY_ACTIONS:
            logger.warning(
                f"[{service}] Action '{action_type}' cannot be queued (safety rule). "
                "Requires fresh human approval."
            )
            self._create_approval_request(service, action)
            return

        service_queue = QUEUE_DIR / service
        service_queue.mkdir(exist_ok=True)

        ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filepath = service_queue / f"queued_{ts}.json"

        queue_entry = {
            'service': service,
            'action': action,
            'queued_at': datetime.now().isoformat(),
            'status': 'pending',
        }

        filepath.write_text(json.dumps(queue_entry, indent=2, default=str))

        state = self.services.get(service)
        if state:
            state.queued_actions += 1

        logger.info(f"[{service}] Action queued: {filepath.name}")

    def _create_approval_request(self, service: str, action: Dict):
        """Create HITL approval for actions that can't be auto-queued."""
        approval_dir = VAULT_PATH / 'Pending_Approval'
        approval_dir.mkdir(exist_ok=True)

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = approval_dir / f"DEGRADED_{service.upper()}_{ts}.md"

        filepath.write_text(f"""---
type: degradation_approval
service: {service}
action_type: {action.get('action_type', 'unknown')}
created: {datetime.now().isoformat()}
status: pending
---

## Service Degradation - Manual Action Required

**Service**: {service}
**Status**: Unavailable
**Action**: {action.get('action_type', 'unknown')}

This action could not be automatically queued due to safety rules.
Manual intervention is required.

### Action Details
```json
{json.dumps(action, indent=2, default=str)}
```

### To Approve
Move this file to `/Approved` when service is restored.
""")

    def replay_queued(self, service: str, executor_fn) -> Dict:
        """
        Replay queued actions for a service that has recovered.

        Args:
            service: Service name
            executor_fn: Function to execute each action

        Returns:
            Dict with replay results
        """
        service_queue = QUEUE_DIR / service
        if not service_queue.exists():
            return {'replayed': 0, 'failed': 0}

        replayed = 0
        failed = 0

        for filepath in sorted(service_queue.glob('queued_*.json')):
            try:
                entry = json.loads(filepath.read_text())
                if entry.get('status') == 'completed':
                    continue

                action = entry['action']
                executor_fn(action)

                entry['status'] = 'completed'
                entry['completed_at'] = datetime.now().isoformat()
                filepath.write_text(json.dumps(entry, indent=2, default=str))
                replayed += 1

            except Exception as e:
                entry['status'] = 'failed'
                entry['error'] = str(e)
                filepath.write_text(json.dumps(entry, indent=2, default=str))
                failed += 1
                logger.error(f"[{service}] Replay failed for {filepath.name}: {e}")

        state = self.services.get(service)
        if state:
            state.queued_actions = max(0, state.queued_actions - replayed)

        logger.info(f"[{service}] Replayed {replayed}, failed {failed}")
        return {'replayed': replayed, 'failed': failed}

    def get_all_status(self) -> Dict:
        """Get health status of all services."""
        return {
            name: state.to_dict()
            for name, state in self.services.items()
        }

    def get_degradation_report(self) -> str:
        """Generate human-readable degradation report."""
        lines = ["# Service Health Report", f"Generated: {datetime.now().isoformat()}", ""]

        for name, state in self.services.items():
            icon = {
                ServiceStatus.HEALTHY: 'OK',
                ServiceStatus.DEGRADED: 'WARN',
                ServiceStatus.UNAVAILABLE: 'DOWN',
            }.get(state.status, '?')

            lines.append(
                f"- [{icon}] **{name}**: {state.status.value} "
                f"(failures: {state.failure_count}, queued: {state.queued_actions})"
            )

            if state.last_error:
                lines.append(f"  Last error: {state.last_error}")

        return "\n".join(lines)


# Global instance
_manager: Optional[DegradationManager] = None


def get_manager() -> DegradationManager:
    """Get or create the global DegradationManager."""
    global _manager
    if _manager is None:
        _manager = DegradationManager()
    return _manager
