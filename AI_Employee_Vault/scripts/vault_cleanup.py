#!/usr/bin/env python3
"""
Vault Cleanup Script.

Maintenance tasks:
- Archive old Done items (>30 days)
- Clean old log files (>90 days per Constitution Principle III)
- Remove empty/orphaned files
- Generate cleanup report

Usage:
    python scripts/vault_cleanup.py              # Dry run (default)
    python scripts/vault_cleanup.py --execute    # Actually clean
    python scripts/vault_cleanup.py --report     # Report only
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))
LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', '90'))
DONE_ARCHIVE_DAYS = 30


def find_old_logs(logs_dir: Path, retention_days: int) -> list:
    """Find log files older than retention period."""
    cutoff = datetime.now() - timedelta(days=retention_days)
    old_files = []
    for log_file in logs_dir.glob('*.json'):
        try:
            # Parse date from filename (YYYY-MM-DD.json)
            file_date = datetime.strptime(log_file.stem, '%Y-%m-%d')
            if file_date < cutoff:
                old_files.append(log_file)
        except ValueError:
            continue
    return old_files


def find_old_done_items(done_dir: Path, archive_days: int) -> list:
    """Find completed items older than archive period."""
    cutoff = datetime.now() - timedelta(days=archive_days)
    old_files = []
    for item in done_dir.glob('*.md'):
        mtime = datetime.fromtimestamp(item.stat().st_mtime)
        if mtime < cutoff:
            old_files.append(item)
    return old_files


def find_empty_files(vault_path: Path) -> list:
    """Find empty markdown files (likely orphaned)."""
    empty = []
    for md_file in vault_path.rglob('*.md'):
        if md_file.stat().st_size == 0:
            empty.append(md_file)
    return empty


def main():
    parser = argparse.ArgumentParser(description='Vault cleanup')
    parser.add_argument('--execute', action='store_true', help='Actually perform cleanup')
    parser.add_argument('--report', action='store_true', help='Report only, no action')
    args = parser.parse_args()

    dry_run = not args.execute

    print(f"Vault Cleanup - {'DRY RUN' if dry_run else 'EXECUTING'}")
    print(f"Vault: {VAULT_PATH}")
    print(f"Log retention: {LOG_RETENTION_DAYS} days")
    print(f"Done archive: {DONE_ARCHIVE_DAYS} days")
    print()

    # 1. Old logs
    logs_dir = VAULT_PATH / 'Logs'
    old_logs = find_old_logs(logs_dir, LOG_RETENTION_DAYS) if logs_dir.exists() else []
    print(f"Old log files (>{LOG_RETENTION_DAYS} days): {len(old_logs)}")
    for f in old_logs:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")
        if not dry_run and not args.report:
            f.unlink()

    # 2. Old done items
    done_dir = VAULT_PATH / 'Done'
    old_done = find_old_done_items(done_dir, DONE_ARCHIVE_DAYS) if done_dir.exists() else []
    print(f"\nOld done items (>{DONE_ARCHIVE_DAYS} days): {len(old_done)}")
    archive_dir = VAULT_PATH / 'Done' / 'Archive'
    for f in old_done:
        print(f"  - {f.name}")
        if not dry_run and not args.report:
            archive_dir.mkdir(exist_ok=True)
            shutil.move(str(f), str(archive_dir / f.name))

    # 3. Empty files
    empty_files = find_empty_files(VAULT_PATH)
    # Exclude .gitkeep files
    empty_files = [f for f in empty_files if f.name != '.gitkeep']
    print(f"\nEmpty markdown files: {len(empty_files)}")
    for f in empty_files:
        print(f"  - {f.relative_to(VAULT_PATH)}")

    # Summary
    total_cleanable = len(old_logs) + len(old_done) + len(empty_files)
    print(f"\n{'=' * 40}")
    print(f"Total cleanable items: {total_cleanable}")
    if dry_run and total_cleanable > 0:
        print("Run with --execute to perform cleanup")

    return 0


if __name__ == '__main__':
    sys.exit(main())
