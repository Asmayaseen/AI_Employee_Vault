#!/usr/bin/env python3
"""
Claim-by-Move Protocol for Platinum Tier Multi-Agent Delegation.

Implements the hackathon-required claim-by-move rule:
- First agent to move an item from /Needs_Action/<domain>/ to /In_Progress/<agent>/ owns it
- Other agents must ignore items already claimed
- Atomic rename prevents race conditions
- Supports both flat and domain-subdirectory layouts

Usage:
    from utils.claim_task import TaskClaimer

    claimer = TaskClaimer(vault_path, agent_name='local')
    task = claimer.claim_next(domain='email')
    if task:
        # Process the task
        claimer.complete(task)   # Moves to /Done
    # OR
        claimer.release(task)   # Returns to /Needs_Action (unclaim)
"""

import os
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger('ClaimTask')


class ClaimedTask:
    """Represents a claimed task file."""

    def __init__(self, original_path: Path, claimed_path: Path, agent: str, domain: str):
        self.original_path = original_path
        self.claimed_path = claimed_path
        self.agent = agent
        self.domain = domain
        self.claimed_at = datetime.now()

    @property
    def filename(self) -> str:
        return self.claimed_path.name

    @property
    def content(self) -> str:
        return self.claimed_path.read_text(encoding='utf-8')

    def __repr__(self):
        return f"ClaimedTask({self.filename}, agent={self.agent}, domain={self.domain})"


class TaskClaimer:
    """
    Atomic claim-by-move protocol for multi-agent task delegation.

    The first agent to successfully rename (move) a file from
    /Needs_Action/ to /In_Progress/<agent>/ owns it.
    os.rename() is atomic on the same filesystem (POSIX guarantee).
    """

    def __init__(self, vault_path: str = None, agent_name: str = None):
        self.vault_path = Path(vault_path or os.getenv(
            'VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'
        ))
        self.agent_name = agent_name or os.getenv('AGENT_NAME', 'local')

        # Directories
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress' / self.agent_name
        self.done = self.vault_path / 'Done'

        # Ensure directories exist
        self.in_progress.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(exist_ok=True)

        # Claim log
        self.claim_log = self.vault_path / 'Logs' / 'claims.jsonl'
        self.claim_log.parent.mkdir(exist_ok=True)

    def _log_claim(self, action: str, filename: str, domain: str, details: dict = None):
        """Append a claim event to the JSONL log."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.agent_name,
            'action': action,
            'filename': filename,
            'domain': domain,
        }
        if details:
            entry.update(details)
        try:
            with open(self.claim_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.warning(f"Failed to write claim log: {e}")

    def list_available(self, domain: str = None) -> List[Path]:
        """List unclaimed tasks in /Needs_Action/, optionally filtered by domain."""
        available = []

        if domain:
            search_dir = self.needs_action / domain
            if search_dir.exists():
                available.extend(sorted(search_dir.glob('*.md'), key=lambda p: p.stat().st_mtime))
        else:
            # Search flat files first, then domain subdirectories
            available.extend(sorted(self.needs_action.glob('*.md'), key=lambda p: p.stat().st_mtime))
            for subdir in sorted(self.needs_action.iterdir()):
                if subdir.is_dir() and subdir.name != '.gitkeep':
                    available.extend(sorted(subdir.glob('*.md'), key=lambda p: p.stat().st_mtime))

        return available

    def is_claimed(self, filepath: Path) -> bool:
        """Check if a task is already claimed by any agent."""
        # Check all agent In_Progress directories
        in_progress_root = self.vault_path / 'In_Progress'
        if in_progress_root.exists():
            for agent_dir in in_progress_root.iterdir():
                if agent_dir.is_dir():
                    if (agent_dir / filepath.name).exists():
                        return True
        return False

    def claim(self, filepath: Path, domain: str = 'general') -> Optional[ClaimedTask]:
        """
        Atomically claim a task by moving it to /In_Progress/<agent>/.

        Returns ClaimedTask on success, None if already claimed by another agent.
        Uses os.rename() which is atomic on POSIX filesystems.
        """
        if not filepath.exists():
            logger.debug(f"File no longer exists (already claimed?): {filepath}")
            return None

        target = self.in_progress / filepath.name

        try:
            # Atomic rename - fails if source doesn't exist (another agent got it first)
            os.rename(str(filepath), str(target))
            logger.info(f"Claimed: {filepath.name} -> In_Progress/{self.agent_name}/")

            task = ClaimedTask(
                original_path=filepath,
                claimed_path=target,
                agent=self.agent_name,
                domain=domain
            )
            self._log_claim('claimed', filepath.name, domain)
            return task

        except FileNotFoundError:
            # Another agent moved it first - this is expected in multi-agent scenarios
            logger.debug(f"Claim race lost for: {filepath.name}")
            return None
        except OSError as e:
            logger.error(f"Claim failed for {filepath.name}: {e}")
            return None

    def claim_next(self, domain: str = None) -> Optional[ClaimedTask]:
        """Claim the oldest available task, optionally from a specific domain."""
        available = self.list_available(domain)

        for filepath in available:
            # Determine domain from path
            task_domain = domain or 'general'
            if filepath.parent != self.needs_action:
                task_domain = filepath.parent.name

            task = self.claim(filepath, domain=task_domain)
            if task:
                return task

        return None

    def complete(self, task: ClaimedTask) -> bool:
        """Move a claimed task to /Done/ (task completed successfully)."""
        if not task.claimed_path.exists():
            logger.warning(f"Task file not found: {task.claimed_path}")
            return False

        done_path = self.done / f"completed_{task.filename}"
        try:
            os.rename(str(task.claimed_path), str(done_path))
            logger.info(f"Completed: {task.filename} -> Done/")
            self._log_claim('completed', task.filename, task.domain)
            return True
        except OSError as e:
            logger.error(f"Complete failed for {task.filename}: {e}")
            return False

    def release(self, task: ClaimedTask) -> bool:
        """Release a claimed task back to /Needs_Action/ (unclaim)."""
        if not task.claimed_path.exists():
            logger.warning(f"Task file not found: {task.claimed_path}")
            return False

        # Return to original location or flat Needs_Action
        target = task.original_path
        if not target.parent.exists():
            target = self.needs_action / task.filename

        try:
            os.rename(str(task.claimed_path), str(target))
            logger.info(f"Released: {task.filename} -> Needs_Action/")
            self._log_claim('released', task.filename, task.domain)
            return True
        except OSError as e:
            logger.error(f"Release failed for {task.filename}: {e}")
            return False

    def get_my_claims(self) -> List[Path]:
        """Get all tasks currently claimed by this agent."""
        if self.in_progress.exists():
            return sorted(self.in_progress.glob('*.md'))
        return []

    def get_all_claims(self) -> Dict[str, List[str]]:
        """Get all claimed tasks across all agents."""
        claims = {}
        in_progress_root = self.vault_path / 'In_Progress'
        if in_progress_root.exists():
            for agent_dir in in_progress_root.iterdir():
                if agent_dir.is_dir() and agent_dir.name not in ('.gitkeep',):
                    files = [f.name for f in agent_dir.glob('*.md')]
                    if files:
                        claims[agent_dir.name] = files
        return claims

    def cleanup_stale(self, max_age_hours: int = 24) -> int:
        """Release tasks claimed more than max_age_hours ago."""
        released = 0
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)

        for filepath in self.get_my_claims():
            if filepath.stat().st_mtime < cutoff:
                task = ClaimedTask(
                    original_path=self.needs_action / filepath.name,
                    claimed_path=filepath,
                    agent=self.agent_name,
                    domain='general'
                )
                if self.release(task):
                    released += 1

        if released:
            logger.info(f"Released {released} stale claims (>{max_age_hours}h)")
        return released
