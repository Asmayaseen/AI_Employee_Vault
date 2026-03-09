"""
File operation helpers.

Safe file writing, atomic moves, and filename generation.
Used across all watchers and processors.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


def safe_write(filepath: Path, content: str, encoding: str = 'utf-8') -> Path:
    """
    Safely write content to a file, creating parent dirs if needed.

    Args:
        filepath: Target file path.
        content: Content to write.
        encoding: File encoding (default utf-8).

    Returns:
        Path to the written file.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding=encoding)
    return filepath


def atomic_move(source: Path, dest_dir: Path) -> Path:
    """
    Atomically move a file to a destination directory.

    If a file with the same name exists in dest, appends a counter.

    Args:
        source: Source file path.
        dest_dir: Destination directory.

    Returns:
        Path to the moved file.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / source.name

    # Handle name collision
    counter = 1
    while dest.exists():
        stem = source.stem
        suffix = source.suffix
        dest = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    shutil.move(str(source), str(dest))
    return dest


def generate_filename(
    prefix: str,
    timestamp: datetime = None,
    title: str = "",
    extension: str = ".md"
) -> str:
    """
    Generate a standardized filename.

    Format: PREFIX_YYYYMMDD_HHMMSS_title_slug.ext

    Args:
        prefix: File prefix (e.g., EMAIL, FILE, PLAN, APPROVAL).
        timestamp: Optional timestamp (defaults to now).
        title: Optional title to slugify.
        extension: File extension (default .md).

    Returns:
        Generated filename string.
    """
    ts = timestamp or datetime.now()
    ts_str = ts.strftime('%Y%m%d_%H%M%S')

    if title:
        # Slugify title: lowercase, replace non-alphanum with underscore, truncate
        slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
        slug = slug[:50]  # Truncate long titles
        return f"{prefix}_{ts_str}_{slug}{extension}"
    else:
        return f"{prefix}_{ts_str}{extension}"


def get_file_age_hours(filepath: Path) -> float:
    """
    Get file age in hours.

    Args:
        filepath: Path to file.

    Returns:
        Age in hours.
    """
    if not filepath.exists():
        return 0.0
    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
    return (datetime.now() - mtime).total_seconds() / 3600
