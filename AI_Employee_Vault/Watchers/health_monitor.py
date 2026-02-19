"""
Health Monitor Watcher - Real-time health monitoring with alerting.

Periodically checks the health of all AI Employee services and triggers
alerts when issues are detected. Integrates with the dashboard for
real-time status display.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.alert_manager import send_alert, AlertLevel

logger = logging.getLogger(__name__)

CHECK_INTERVAL = int(os.environ.get("HEALTH_CHECK_INTERVAL", "30"))  # seconds
HEALTH_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "Logs", "health_state.json")
HEALTH_HISTORY_DIR = os.path.join(os.path.dirname(__file__), "..", "Logs", "health")

# Services to monitor
SERVICES = {
    "dashboard": {
        "url": os.environ.get("DASHBOARD_URL", "http://localhost:3000"),
        "name": "Next.js Dashboard",
        "critical": True,
    },
    "api": {
        "url": os.environ.get("API_URL", "http://localhost:9000") + "/api/health",
        "name": "Flask API",
        "critical": True,
    },
    "odoo": {
        "url": os.environ.get("ODOO_URL", "http://localhost:8069") + "/web/login",
        "name": "Odoo ERP",
        "critical": False,
    },
}

# Alert thresholds
CONSECUTIVE_FAILURES_WARN = 2
CONSECUTIVE_FAILURES_CRITICAL = 5


def _ensure_dirs() -> None:
    """Ensure required directories exist."""
    Path(HEALTH_HISTORY_DIR).mkdir(parents=True, exist_ok=True)
    Path(HEALTH_STATE_FILE).parent.mkdir(parents=True, exist_ok=True)


def _load_state() -> dict:
    """Load health monitor state."""
    try:
        with open(HEALTH_STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"services": {}, "last_check": None}


def _save_state(state: dict) -> None:
    """Save health monitor state."""
    _ensure_dirs()
    with open(HEALTH_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _log_health_check(results: dict) -> None:
    """Append health check results to daily log."""
    _ensure_dirs()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = os.path.join(HEALTH_HISTORY_DIR, f"health_{date_str}.jsonl")
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def check_service(service_id: str, config: dict) -> dict:
    """Check health of a single service."""
    result = {
        "service": service_id,
        "name": config["name"],
        "healthy": False,
        "latency_ms": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        start = time.monotonic()
        req = Request(config["url"], method="GET")
        req.add_header("User-Agent", "AI-Employee-HealthMonitor/1.0")
        with urlopen(req, timeout=10) as resp:
            result["healthy"] = resp.status < 500
            result["status_code"] = resp.status
        result["latency_ms"] = round((time.monotonic() - start) * 1000, 1)
    except (URLError, TimeoutError, OSError) as e:
        result["latency_ms"] = round((time.monotonic() - start) * 1000, 1)
        result["error"] = str(e)

    return result


def run_health_check() -> dict:
    """Run health checks on all services."""
    state = _load_state()
    results = {}
    overall_healthy = True

    for service_id, config in SERVICES.items():
        check = check_service(service_id, config)
        results[service_id] = check

        # Track consecutive failures
        svc_state = state.get("services", {}).get(service_id, {"consecutive_failures": 0})

        if check["healthy"]:
            # Service recovered
            if svc_state.get("consecutive_failures", 0) >= CONSECUTIVE_FAILURES_WARN:
                send_alert(
                    f"Service Recovered: {config['name']}",
                    f"Service {config['name']} is healthy again after {svc_state['consecutive_failures']} failures.",
                    AlertLevel.INFO,
                )
            svc_state["consecutive_failures"] = 0
            svc_state["status"] = "healthy"
        else:
            svc_state["consecutive_failures"] = svc_state.get("consecutive_failures", 0) + 1
            svc_state["status"] = "unhealthy"

            if config.get("critical", False):
                overall_healthy = False

            # Send alerts based on failure count
            if svc_state["consecutive_failures"] == CONSECUTIVE_FAILURES_WARN:
                send_alert(
                    f"Service Degraded: {config['name']}",
                    f"Service {config['name']} has failed {svc_state['consecutive_failures']} consecutive health checks.\n"
                    f"URL: {config['url']}\n"
                    f"Error: {check.get('error', 'Unknown')}",
                    AlertLevel.WARNING,
                )
            elif svc_state["consecutive_failures"] == CONSECUTIVE_FAILURES_CRITICAL:
                send_alert(
                    f"Service Down: {config['name']}",
                    f"CRITICAL: Service {config['name']} has been down for {svc_state['consecutive_failures']} consecutive checks.\n"
                    f"URL: {config['url']}\n"
                    f"Error: {check.get('error', 'Unknown')}\n"
                    f"Immediate attention required.",
                    AlertLevel.CRITICAL,
                )

        svc_state["last_check"] = check["timestamp"]
        svc_state["last_latency_ms"] = check["latency_ms"]
        state.setdefault("services", {})[service_id] = svc_state

    state["last_check"] = datetime.now(timezone.utc).isoformat()
    state["overall_healthy"] = overall_healthy
    _save_state(state)
    _log_health_check(results)

    return {
        "overall_healthy": overall_healthy,
        "services": results,
        "timestamp": state["last_check"],
    }


def get_health_summary() -> dict:
    """Get current health summary without running new checks."""
    state = _load_state()
    return {
        "overall_healthy": state.get("overall_healthy", True),
        "last_check": state.get("last_check"),
        "services": {
            sid: {
                "status": svc.get("status", "unknown"),
                "consecutive_failures": svc.get("consecutive_failures", 0),
                "last_check": svc.get("last_check"),
                "last_latency_ms": svc.get("last_latency_ms", 0),
            }
            for sid, svc in state.get("services", {}).items()
        },
    }


def run_monitor_loop() -> None:
    """Main monitoring loop — runs continuously."""
    logger.info("Health Monitor started (interval: %ds)", CHECK_INTERVAL)

    while True:
        try:
            result = run_health_check()
            status = "HEALTHY" if result["overall_healthy"] else "DEGRADED"
            logger.info(
                "Health check complete: %s (%d services)",
                status, len(result["services"]),
            )
        except Exception as e:
            logger.error("Health check error: %s", e)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    run_monitor_loop()
