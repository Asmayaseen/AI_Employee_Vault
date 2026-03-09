"""
Vault helper utilities.

Functions for interacting with the Obsidian vault structure.
Used by all watchers and processors.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


# Standard vault directories per Constitution Principle IX
VAULT_DIRS = [
    'Inbox',
    'Needs_Action',
    'Plans',
    'Pending_Approval',
    'Approved',
    'Rejected',
    'Done',
    'Logs',
    'Briefings',
    'Accounting',
    'Queued_Actions',
    'Reports',
]


def get_vault_path() -> Path:
    """
    Get the vault path from environment or default.

    Returns:
        Path to the Obsidian vault root.
    """
    return Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))


def ensure_vault_dirs(vault_path: Path = None) -> Dict[str, Path]:
    """
    Ensure all required vault directories exist.

    Args:
        vault_path: Optional override for vault root.

    Returns:
        Dictionary mapping directory names to their Path objects.
    """
    vault = vault_path or get_vault_path()
    dirs = {}
    for dir_name in VAULT_DIRS:
        dir_path = vault / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        dirs[dir_name.lower()] = dir_path
    return dirs


def read_frontmatter(filepath: Path) -> Dict[str, Any]:
    """
    Read YAML frontmatter from a Markdown file.

    Args:
        filepath: Path to the Markdown file.

    Returns:
        Dictionary of frontmatter key-value pairs.
    """
    content = filepath.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return {}

    end_idx = content.find('---', 3)
    if end_idx < 0:
        return {}

    frontmatter = content[3:end_idx].strip()
    metadata = {}
    for line in frontmatter.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, value = line.partition(':')
            metadata[key.strip()] = value.strip()
    return metadata


def get_body_content(filepath: Path) -> str:
    """
    Get the body content of a Markdown file (after frontmatter).

    Args:
        filepath: Path to the Markdown file.

    Returns:
        Body content string.
    """
    content = filepath.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return content

    end_idx = content.find('---', 3)
    if end_idx < 0:
        return content

    return content[end_idx + 3:].strip()


def count_items_by_status(vault_path: Path = None) -> Dict[str, int]:
    """
    Count items in each vault status folder.

    Returns:
        Dictionary mapping folder names to item counts.
    """
    vault = vault_path or get_vault_path()
    counts = {}
    for dir_name in VAULT_DIRS:
        dir_path = vault / dir_name
        if dir_path.exists():
            counts[dir_name] = len(list(dir_path.glob('*.md')))
        else:
            counts[dir_name] = 0
    return counts
