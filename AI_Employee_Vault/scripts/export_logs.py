#!/usr/bin/env python3
"""
Log Export Script.

Export audit logs to CSV or filtered JSON for analysis.

Usage:
    python scripts/export_logs.py --format csv --output report.csv
    python scripts/export_logs.py --format json --days 7
    python scripts/export_logs.py --filter action_type=email_send --days 30
"""

import os
import sys
import csv
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))
LOGS_DIR = VAULT_PATH / 'Logs'


def load_logs(days: int = 7) -> list:
    """Load log entries from the last N days."""
    entries = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        log_file = LOGS_DIR / f"{date.strftime('%Y-%m-%d')}.json"
        if log_file.exists():
            try:
                data = json.loads(log_file.read_text())
                if isinstance(data, list):
                    entries.extend(data)
            except json.JSONDecodeError:
                continue
    return entries


def filter_logs(entries: list, filters: dict) -> list:
    """Filter log entries by key=value pairs."""
    filtered = entries
    for key, value in filters.items():
        filtered = [e for e in filtered if str(e.get(key, '')) == value]
    return filtered


def export_csv(entries: list, output: str):
    """Export entries to CSV."""
    if not entries:
        print("No entries to export")
        return

    # Collect all keys
    all_keys = set()
    for entry in entries:
        all_keys.update(entry.keys())
    fields = sorted(all_keys)

    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(entries)

    print(f"Exported {len(entries)} entries to {output}")


def export_json(entries: list, output: str):
    """Export entries to JSON."""
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2)
    print(f"Exported {len(entries)} entries to {output}")


def main():
    parser = argparse.ArgumentParser(description='Export audit logs')
    parser.add_argument('--format', choices=['csv', 'json'], default='json')
    parser.add_argument('--output', default=None, help='Output file path')
    parser.add_argument('--days', type=int, default=7, help='Number of days to export')
    parser.add_argument('--filter', action='append', help='Filter as key=value')
    args = parser.parse_args()

    entries = load_logs(args.days)
    print(f"Loaded {len(entries)} log entries from last {args.days} days")

    # Apply filters
    if args.filter:
        filters = {}
        for f in args.filter:
            key, _, value = f.partition('=')
            filters[key] = value
        entries = filter_logs(entries, filters)
        print(f"After filtering: {len(entries)} entries")

    # Default output filename
    output = args.output or f"logs_export_{datetime.now().strftime('%Y%m%d')}.{args.format}"

    if args.format == 'csv':
        export_csv(entries, output)
    else:
        export_json(entries, output)

    return 0


if __name__ == '__main__':
    sys.exit(main())
