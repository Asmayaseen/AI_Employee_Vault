#!/usr/bin/env python3
"""
Structured Audit Logger (Gold Tier)

Implements Section 6.3 Audit Logging schema:
{
    "timestamp": "",
    "action_type": "",
    "actor": "",
    "domain": "",
    "target": "",
    "parameters": {},
    "approval_status": "",
    "approved_by": "",
    "result": "",
    "error": ""
}

Features:
- JSON structured logs in /Vault/Logs/YYYY-MM-DD.json
- 90-day retention policy with automatic cleanup
- Log rotation (one file per day)
- Thread-safe writing
- Query/filter capabilities

Usage:
    from audit_logger import AuditLogger

    logger = AuditLogger()
    logger.log_action(
        action_type='email_send',
        actor='claude_code',
        domain='gmail',
        target='client@example.com',
        parameters={'subject': 'Invoice'},
        approval_status='approved',
        approved_by='human',
        result='success'
    )
"""

import json
import os
import logging
import threading
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger('AuditLogger')

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))
LOGS_DIR = VAULT_PATH / 'Logs'
RETENTION_DAYS = 90


class AuditLogger:
    """
    Centralized audit logger for all AI Employee actions.

    Each day gets its own JSON file: YYYY-MM-DD.json
    Each file contains an array of log entries.
    """

    def __init__(self, logs_dir: Path = None, retention_days: int = RETENTION_DAYS):
        self.logs_dir = logs_dir or LOGS_DIR
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self._lock = threading.Lock()

    def _get_log_file(self, dt: date = None) -> Path:
        """Get log file path for a given date."""
        dt = dt or date.today()
        return self.logs_dir / f"{dt.isoformat()}.json"

    def _read_log_file(self, filepath: Path) -> List[Dict]:
        """Read existing log entries from file."""
        if not filepath.exists():
            return []
        try:
            content = filepath.read_text(encoding='utf-8').strip()
            if not content:
                return []
            data = json.loads(content)
            return data if isinstance(data, list) else [data]
        except (json.JSONDecodeError, IOError):
            return []

    def _write_log_file(self, filepath: Path, entries: List[Dict]):
        """Write log entries to file."""
        filepath.write_text(
            json.dumps(entries, indent=2, default=str, ensure_ascii=False),
            encoding='utf-8'
        )

    def log_action(
        self,
        action_type: str,
        actor: str = 'claude_code',
        domain: str = '',
        target: str = '',
        parameters: Dict = None,
        approval_status: str = 'not_required',
        approved_by: str = '',
        result: str = 'success',
        error: str = '',
        metadata: Dict = None,
    ) -> Dict:
        """
        Log a structured action entry.

        Args:
            action_type: Type of action (email_send, invoice_create, social_post, etc.)
            actor: Who performed the action (claude_code, watcher, human, etc.)
            domain: Domain/service (gmail, odoo, facebook, etc.)
            target: Target of the action (email address, customer name, etc.)
            parameters: Action parameters (dict)
            approval_status: approved, rejected, not_required, pending
            approved_by: Who approved (human, auto, etc.)
            result: success, failure, partial, queued
            error: Error message if failed
            metadata: Additional metadata

        Returns:
            The created log entry
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': actor,
            'domain': domain,
            'target': target,
            'parameters': parameters or {},
            'approval_status': approval_status,
            'approved_by': approved_by,
            'result': result,
            'error': error,
        }

        if metadata:
            entry['metadata'] = metadata

        with self._lock:
            filepath = self._get_log_file()
            entries = self._read_log_file(filepath)
            entries.append(entry)
            self._write_log_file(filepath, entries)

        if result == 'failure':
            logger.warning(f"AUDIT [{action_type}] {domain} -> {target}: FAILED - {error}")
        else:
            logger.info(f"AUDIT [{action_type}] {domain} -> {target}: {result}")

        return entry

    def query_logs(
        self,
        start_date: date = None,
        end_date: date = None,
        action_type: str = None,
        domain: str = None,
        actor: str = None,
        result: str = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Query log entries with filters.

        Args:
            start_date: Start of date range (default: today)
            end_date: End of date range (default: today)
            action_type: Filter by action type
            domain: Filter by domain
            actor: Filter by actor
            result: Filter by result
            limit: Max entries to return

        Returns:
            List of matching log entries (newest first)
        """
        start = start_date or date.today()
        end = end_date or date.today()

        all_entries = []
        current = end

        while current >= start:
            filepath = self._get_log_file(current)
            entries = self._read_log_file(filepath)
            all_entries.extend(entries)
            current -= timedelta(days=1)

        # Apply filters
        filtered = all_entries
        if action_type:
            filtered = [e for e in filtered if e.get('action_type') == action_type]
        if domain:
            filtered = [e for e in filtered if e.get('domain') == domain]
        if actor:
            filtered = [e for e in filtered if e.get('actor') == actor]
        if result:
            filtered = [e for e in filtered if e.get('result') == result]

        # Sort newest first
        filtered.sort(key=lambda e: e.get('timestamp', ''), reverse=True)

        return filtered[:limit]

    def get_daily_summary(self, dt: date = None) -> Dict:
        """
        Get summary statistics for a day.

        Returns:
            Dict with counts by action_type, domain, result
        """
        dt = dt or date.today()
        entries = self._read_log_file(self._get_log_file(dt))

        summary = {
            'date': dt.isoformat(),
            'total_actions': len(entries),
            'by_result': {},
            'by_domain': {},
            'by_action_type': {},
            'failures': [],
        }

        for entry in entries:
            # Count by result
            r = entry.get('result', 'unknown')
            summary['by_result'][r] = summary['by_result'].get(r, 0) + 1

            # Count by domain
            d = entry.get('domain', 'unknown')
            summary['by_domain'][d] = summary['by_domain'].get(d, 0) + 1

            # Count by action type
            a = entry.get('action_type', 'unknown')
            summary['by_action_type'][a] = summary['by_action_type'].get(a, 0) + 1

            # Collect failures
            if r == 'failure':
                summary['failures'].append({
                    'action': a,
                    'domain': d,
                    'error': entry.get('error', ''),
                    'timestamp': entry.get('timestamp'),
                })

        return summary

    def enforce_retention(self) -> int:
        """
        Delete log files older than retention period.

        Returns:
            Number of files deleted
        """
        cutoff = date.today() - timedelta(days=self.retention_days)
        deleted = 0

        for filepath in self.logs_dir.glob('*.json'):
            try:
                # Extract date from filename
                file_date = date.fromisoformat(filepath.stem)
                if file_date < cutoff:
                    filepath.unlink()
                    deleted += 1
                    logger.info(f"Retention cleanup: deleted {filepath.name}")
            except (ValueError, OSError):
                continue

        return deleted

    def get_retention_info(self) -> Dict:
        """Get retention policy info."""
        files = list(self.logs_dir.glob('*.json'))
        dates = []
        for f in files:
            try:
                dates.append(date.fromisoformat(f.stem))
            except ValueError:
                continue

        return {
            'retention_days': self.retention_days,
            'log_file_count': len(dates),
            'oldest_log': min(dates).isoformat() if dates else None,
            'newest_log': max(dates).isoformat() if dates else None,
            'cutoff_date': (date.today() - timedelta(days=self.retention_days)).isoformat(),
        }


# Global instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create the global AuditLogger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
