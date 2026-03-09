"""
Alert Manager - Email/SMS alert system for AI Employee.

Sends notifications when health checks fail, zones failover,
or other critical events occur.
"""

import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Configuration from environment
SMTP_HOST = os.environ.get("ALERT_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("ALERT_SMTP_PORT", "587"))
SMTP_USER = os.environ.get("ALERT_SMTP_USER", "")
SMTP_PASS = os.environ.get("ALERT_SMTP_PASS", "")
ALERT_FROM = os.environ.get("ALERT_FROM_EMAIL", SMTP_USER)
ALERT_TO = os.environ.get("ALERT_TO_EMAIL", "")
ALERTS_ENABLED = os.environ.get("ALERTS_ENABLED", "false").lower() == "true"

ALERT_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "Logs", "alerts")


class AlertLevel:
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


def _ensure_log_dir() -> None:
    """Ensure alert log directory exists."""
    Path(ALERT_LOG_DIR).mkdir(parents=True, exist_ok=True)


def _log_alert(alert: dict) -> None:
    """Log alert to file."""
    _ensure_log_dir()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = os.path.join(ALERT_LOG_DIR, f"alerts_{date_str}.jsonl")
    with open(log_file, "a") as f:
        f.write(json.dumps(alert) + "\n")


def send_email_alert(
    subject: str,
    body: str,
    level: str = AlertLevel.WARNING,
) -> dict:
    """
    Send an email alert.

    Returns dict with send status.
    """
    result = {
        "type": "email",
        "level": level,
        "subject": subject,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sent": False,
    }

    if not ALERTS_ENABLED:
        result["reason"] = "Alerts disabled (set ALERTS_ENABLED=true)"
        _log_alert(result)
        return result

    if not all([SMTP_USER, SMTP_PASS, ALERT_TO]):
        result["reason"] = "Email credentials not configured"
        _log_alert(result)
        return result

    try:
        msg = MIMEMultipart()
        msg["From"] = ALERT_FROM
        msg["To"] = ALERT_TO
        msg["Subject"] = f"[AI Employee {level.upper()}] {subject}"

        html_body = f"""
        <html>
        <body style="font-family: sans-serif; padding: 20px;">
            <div style="border-left: 4px solid {'#FF2D55' if level == 'critical' else '#FF6B00' if level == 'warning' else '#0097A7'}; padding-left: 16px;">
                <h2 style="margin: 0 0 8px 0;">AI Employee Alert</h2>
                <p style="color: #555; margin: 0 0 16px 0;">Level: <strong>{level.upper()}</strong></p>
                <div style="background: #f5f5f5; padding: 16px; border-radius: 8px;">
                    <pre style="margin: 0; white-space: pre-wrap;">{body}</pre>
                </div>
                <p style="color: #888; margin: 16px 0 0 0; font-size: 12px;">
                    Sent at {result['timestamp']} by AI Employee Alert Manager
                </p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        result["sent"] = True
        logger.info("Alert email sent: %s", subject)

    except Exception as e:
        result["reason"] = str(e)
        logger.error("Failed to send alert email: %s", e)

    _log_alert(result)
    return result


def send_alert(
    title: str,
    message: str,
    level: str = AlertLevel.WARNING,
    channels: list[str] | None = None,
) -> list[dict]:
    """
    Send alert through configured channels.

    Args:
        title: Alert title/subject
        message: Alert body
        level: Alert severity level
        channels: List of channels to use (default: ["email"])

    Returns:
        List of send results per channel
    """
    if channels is None:
        channels = ["email"]

    results = []
    for channel in channels:
        if channel == "email":
            results.append(send_email_alert(title, message, level))
        else:
            results.append({
                "type": channel,
                "level": level,
                "sent": False,
                "reason": f"Channel '{channel}' not implemented",
            })

    return results


def get_recent_alerts(limit: int = 50) -> list[dict]:
    """Get recent alerts from log files."""
    _ensure_log_dir()
    alerts = []

    log_files = sorted(Path(ALERT_LOG_DIR).glob("alerts_*.jsonl"), reverse=True)
    for log_file in log_files[:7]:  # Last 7 days
        try:
            with open(log_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        alerts.append(json.loads(line))
        except (json.JSONDecodeError, IOError):
            continue
        if len(alerts) >= limit:
            break

    return sorted(alerts, key=lambda a: a.get("timestamp", ""), reverse=True)[:limit]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = send_alert(
        "Test Alert",
        "This is a test alert from the AI Employee Alert Manager.",
        AlertLevel.INFO,
    )
    print(json.dumps(result, indent=2))
