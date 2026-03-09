"""
Work Zones - Cloud/Local zone routing with automatic failover.

Manages routing of tasks between local and cloud environments.
Provides automatic failover when a zone becomes unhealthy.
"""

import os
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum
from urllib.request import urlopen, Request
from urllib.error import URLError

logger = logging.getLogger(__name__)

ZONES_CONFIG_FILE = os.environ.get(
    "ZONES_CONFIG",
    os.path.join(os.path.dirname(__file__), "..", "zones.json"),
)
ZONE_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", ".zone_state.json")


class Zone(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


DEFAULT_ZONES_CONFIG = {
    "active_zone": "local",
    "auto_failover": True,
    "failover_threshold": 3,
    "health_check_timeout": 5,
    "zones": {
        "local": {
            "api_url": "http://localhost:9000",
            "dashboard_url": "http://localhost:3000",
            "description": "Local development environment",
        },
        "cloud": {
            "api_url": os.environ.get("CLOUD_API_URL", "https://ai.example.com/api"),
            "dashboard_url": os.environ.get("CLOUD_DASHBOARD_URL", "https://ai.example.com"),
            "description": "Cloud production environment",
        },
    },
    "routing_rules": {
        "email_processing": "active",
        "social_media": "active",
        "approvals": "active",
        "vault_operations": "local",
        "system_monitoring": "both",
    },
}


def _load_config() -> dict:
    """Load zones configuration."""
    try:
        with open(ZONES_CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_ZONES_CONFIG.copy()


def _save_config(config: dict) -> None:
    """Save zones configuration."""
    Path(ZONES_CONFIG_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(ZONES_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def _load_state() -> dict:
    """Load zone state."""
    try:
        with open(ZONE_STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"failures": {"local": 0, "cloud": 0}, "last_check": {}}


def _save_state(state: dict) -> None:
    """Save zone state."""
    with open(ZONE_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check_zone_health(zone: str) -> dict:
    """Check health of a specific zone."""
    config = _load_config()
    zone_config = config["zones"].get(zone, {})
    api_url = zone_config.get("api_url", "")

    result = {
        "zone": zone,
        "healthy": False,
        "latency_ms": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if not api_url:
        result["error"] = "No API URL configured"
        return result

    try:
        start = time.monotonic()
        req = Request(f"{api_url}/api/health", method="GET")
        req.add_header("User-Agent", "AI-Employee-ZoneCheck/1.0")
        with urlopen(req, timeout=config.get("health_check_timeout", 5)) as resp:
            result["healthy"] = resp.status == 200
            result["latency_ms"] = round((time.monotonic() - start) * 1000, 1)
    except (URLError, TimeoutError, OSError) as e:
        result["error"] = str(e)
        result["latency_ms"] = round((time.monotonic() - start) * 1000, 1)

    return result


def get_active_zone() -> str:
    """Get the currently active zone."""
    config = _load_config()
    return config.get("active_zone", "local")


def set_active_zone(zone: str) -> dict:
    """Manually set the active zone."""
    if zone not in ("local", "cloud"):
        raise ValueError(f"Invalid zone: {zone}. Must be 'local' or 'cloud'")

    config = _load_config()
    old_zone = config.get("active_zone", "local")
    config["active_zone"] = zone
    _save_config(config)

    logger.info("Active zone changed: %s -> %s", old_zone, zone)
    return {"old_zone": old_zone, "new_zone": zone}


def get_zone_status() -> dict:
    """Get full status of all zones."""
    config = _load_config()
    state = _load_state()

    return {
        "active_zone": config.get("active_zone", "local"),
        "auto_failover": config.get("auto_failover", True),
        "zones": {
            name: {
                "description": zone_cfg.get("description", ""),
                "api_url": zone_cfg.get("api_url", ""),
                "failures": state.get("failures", {}).get(name, 0),
                "last_check": state.get("last_check", {}).get(name),
            }
            for name, zone_cfg in config.get("zones", {}).items()
        },
        "routing_rules": config.get("routing_rules", {}),
    }


def resolve_zone(task_type: str) -> str:
    """
    Resolve which zone should handle a given task type.

    Returns the zone name ('local' or 'cloud').
    """
    config = _load_config()
    rules = config.get("routing_rules", {})
    active = config.get("active_zone", "local")

    rule = rules.get(task_type, "active")
    if rule == "active":
        return active
    elif rule == "both":
        return active  # primary zone handles it
    elif rule in ("local", "cloud"):
        return rule
    return active


def check_and_failover() -> dict | None:
    """
    Check zone health and failover if needed.

    Returns failover details if a failover occurred, None otherwise.
    """
    config = _load_config()
    if not config.get("auto_failover", True):
        return None

    active = config.get("active_zone", "local")
    state = _load_state()

    health = check_zone_health(active)
    state.setdefault("failures", {"local": 0, "cloud": 0})
    state.setdefault("last_check", {})
    state["last_check"][active] = health["timestamp"]

    if health["healthy"]:
        state["failures"][active] = 0
        _save_state(state)
        return None

    # Increment failure count
    state["failures"][active] = state["failures"].get(active, 0) + 1
    threshold = config.get("failover_threshold", 3)

    if state["failures"][active] >= threshold:
        # Failover to other zone
        target = "cloud" if active == "local" else "local"
        target_health = check_zone_health(target)
        state["last_check"][target] = target_health["timestamp"]

        if target_health["healthy"]:
            config["active_zone"] = target
            _save_config(config)
            state["failures"][active] = 0
            _save_state(state)

            logger.warning(
                "Failover triggered: %s -> %s (after %d failures)",
                active, target, threshold,
            )
            return {
                "from_zone": active,
                "to_zone": target,
                "reason": f"{threshold} consecutive health check failures",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    _save_state(state)
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(get_zone_status(), indent=2))
