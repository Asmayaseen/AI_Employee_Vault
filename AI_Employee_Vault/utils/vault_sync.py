"""
Vault Sync - Git-based vault synchronization between local and cloud.

Provides bidirectional sync with conflict resolution (local always wins).
Runs on a configurable schedule (default: every 5 minutes).
"""

import os
import subprocess
import logging
import json
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

VAULT_DIR = os.environ.get("VAULT_DIR", os.path.join(os.path.dirname(__file__), ".."))
SYNC_REMOTE = os.environ.get("VAULT_SYNC_REMOTE", "origin")
SYNC_BRANCH = os.environ.get("VAULT_SYNC_BRANCH", "main")
SYNC_INTERVAL = int(os.environ.get("VAULT_SYNC_INTERVAL", "300"))  # seconds
SYNC_STATE_FILE = os.path.join(VAULT_DIR, ".vault_sync_state.json")


class VaultSyncError(Exception):
    """Raised when vault sync encounters an error."""
    pass


def _run_git(args: list[str], cwd: str | None = None) -> str:
    """Run a git command and return stdout."""
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        cwd=cwd or VAULT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise VaultSyncError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def get_sync_status() -> dict:
    """Get current sync status."""
    state = _load_state()
    try:
        local_head = _run_git(["rev-parse", "HEAD"])
        dirty = bool(_run_git(["status", "--porcelain"]))
    except VaultSyncError:
        local_head = "unknown"
        dirty = False

    return {
        "last_sync": state.get("last_sync"),
        "last_status": state.get("last_status", "never"),
        "local_head": local_head,
        "dirty": dirty,
        "remote": SYNC_REMOTE,
        "branch": SYNC_BRANCH,
        "interval_seconds": SYNC_INTERVAL,
    }


def _load_state() -> dict:
    """Load sync state from disk."""
    try:
        with open(SYNC_STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_state(status: str, details: str = "") -> None:
    """Save sync state to disk."""
    state = {
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "last_status": status,
        "details": details,
    }
    with open(SYNC_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def sync_vault(force: bool = False) -> dict:
    """
    Perform a vault sync operation.

    Strategy:
    1. Stage and commit any local changes
    2. Fetch remote
    3. Rebase local on top of remote (local wins conflicts)
    4. Push to remote

    Args:
        force: If True, force push on conflict (use with caution)

    Returns:
        dict with sync result details
    """
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "success",
        "details": "",
        "changes_pushed": 0,
        "changes_pulled": 0,
    }

    try:
        # Step 1: Commit local changes
        status_output = _run_git(["status", "--porcelain"])
        if status_output:
            _run_git(["add", "-A"])
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            _run_git(["commit", "-m", f"vault-sync: auto-commit {timestamp}"])
            result["changes_pushed"] += len(status_output.splitlines())
            logger.info("Committed %d local changes", result["changes_pushed"])

        # Step 2: Fetch remote
        try:
            _run_git(["fetch", SYNC_REMOTE, SYNC_BRANCH])
        except VaultSyncError as e:
            if "Could not resolve" in str(e) or "Could not read" in str(e):
                result["details"] = "Remote not reachable, local-only commit done"
                _save_state("partial", result["details"])
                return result
            raise

        # Step 3: Check for remote changes
        try:
            behind = _run_git(["rev-list", "--count", f"HEAD..{SYNC_REMOTE}/{SYNC_BRANCH}"])
            result["changes_pulled"] = int(behind)
        except VaultSyncError:
            result["changes_pulled"] = 0

        # Step 4: Rebase (local wins conflicts)
        if result["changes_pulled"] > 0:
            try:
                _run_git(["rebase", f"{SYNC_REMOTE}/{SYNC_BRANCH}"])
            except VaultSyncError:
                # Conflict: abort rebase and force local version
                logger.warning("Rebase conflict detected, resolving with local-wins strategy")
                _run_git(["rebase", "--abort"])
                if force:
                    _run_git(["push", SYNC_REMOTE, SYNC_BRANCH, "--force-with-lease"])
                    result["details"] = "Force pushed (local wins)"
                else:
                    _run_git(["merge", f"{SYNC_REMOTE}/{SYNC_BRANCH}", "-X", "ours"])
                    result["details"] = "Merged with local-wins strategy"

        # Step 5: Push
        try:
            _run_git(["push", SYNC_REMOTE, SYNC_BRANCH])
        except VaultSyncError as e:
            if "non-fast-forward" in str(e):
                result["details"] = "Push rejected, will retry next cycle"
                result["status"] = "pending"
            else:
                raise

        _save_state(result["status"], result["details"])
        logger.info("Vault sync complete: %s", result["status"])

    except VaultSyncError as e:
        result["status"] = "error"
        result["details"] = str(e)
        _save_state("error", str(e))
        logger.error("Vault sync failed: %s", e)

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(sync_vault(), indent=2))
