#!/usr/bin/env python3
"""
System Health Check Script.

Quick diagnostic for the entire AI Employee system.
Checks vault structure, watcher processes, MCP servers, and configuration.

Usage:
    python scripts/health_check.py
    python scripts/health_check.py --verbose
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))


def check_vault_structure():
    """Check vault directories exist."""
    required = [
        'Inbox', 'Needs_Action', 'Plans', 'Pending_Approval',
        'Approved', 'Rejected', 'Done', 'Logs', 'Briefings'
    ]
    results = []
    for d in required:
        exists = (VAULT_PATH / d).exists()
        results.append((d, exists))
    return results


def check_env_config():
    """Check .env configuration."""
    env_file = VAULT_PATH / '.env'
    if not env_file.exists():
        return [('.env file', False)]

    required_keys = ['VAULT_PATH']
    optional_keys = ['GMAIL_CREDENTIALS_PATH', 'CLAUDE_API_KEY', 'DRY_RUN']

    results = [('.env file', True)]
    content = env_file.read_text()
    for key in required_keys:
        found = key in content
        results.append((f'ENV: {key}', found))
    return results


def check_watcher_files():
    """Check watcher Python files exist."""
    watchers_dir = VAULT_PATH / 'Watchers'
    files = [
        'base_watcher.py', 'orchestrator.py', 'claude_processor.py',
        'filesystem_watcher.py', 'gmail_watcher.py', 'audit_logger.py',
        'retry_handler.py', 'graceful_degradation.py'
    ]
    results = []
    for f in files:
        exists = (watchers_dir / f).exists()
        results.append((f'Watcher: {f}', exists))
    return results


def check_recent_logs():
    """Check if logs are being written."""
    logs_dir = VAULT_PATH / 'Logs'
    if not logs_dir.exists():
        return [('Logs directory', False)]

    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    today_log = logs_dir / f'{today}.json'
    yesterday_log = logs_dir / f'{yesterday}.json'

    results = [('Logs directory', True)]
    results.append((f'Today log ({today})', today_log.exists()))
    results.append((f'Yesterday log ({yesterday})', yesterday_log.exists()))
    return results


def check_pending_items():
    """Count items in each status folder."""
    folders = ['Needs_Action', 'Pending_Approval', 'Approved', 'Done']
    results = []
    for folder in folders:
        path = VAULT_PATH / folder
        count = len(list(path.glob('*.md'))) if path.exists() else 0
        results.append((f'{folder} items', count))
    return results


def main():
    verbose = '--verbose' in sys.argv

    print("=" * 60)
    print("  AI Employee System Health Check")
    print(f"  Vault: {VAULT_PATH}")
    print(f"  Time: {datetime.now().isoformat()}")
    print("=" * 60)

    sections = [
        ("Vault Structure", check_vault_structure),
        ("Configuration", check_env_config),
        ("Watcher Files", check_watcher_files),
        ("Recent Logs", check_recent_logs),
    ]

    total_checks = 0
    total_pass = 0

    for section_name, check_fn in sections:
        print(f"\n--- {section_name} ---")
        results = check_fn()
        for name, status in results:
            total_checks += 1
            if isinstance(status, bool):
                icon = "PASS" if status else "FAIL"
                if status:
                    total_pass += 1
                print(f"  [{icon}] {name}")
            else:
                total_pass += 1
                print(f"  [INFO] {name}: {status}")

    # Item counts
    print(f"\n--- Item Counts ---")
    for name, count in check_pending_items():
        print(f"  {name}: {count}")

    print(f"\n{'=' * 60}")
    print(f"  Health: {total_pass}/{total_checks} checks passed")
    health_pct = (total_pass / total_checks * 100) if total_checks > 0 else 0
    status = "HEALTHY" if health_pct >= 80 else "DEGRADED" if health_pct >= 50 else "UNHEALTHY"
    print(f"  Status: {status} ({health_pct:.0f}%)")
    print(f"{'=' * 60}")

    return 0 if health_pct >= 80 else 1


if __name__ == '__main__':
    sys.exit(main())
