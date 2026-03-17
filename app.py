"""
AI Employee - Root Entry Point

This file acts as the WSGI/Gunicorn entry point and can also be run directly.
It imports the Flask app from the dashboard module.

Usage:
    python app.py                        # Run locally
    gunicorn app:app --bind 0.0.0.0:7860 # Production WSGI
"""

import os
import sys
import json
from pathlib import Path

# Add Watchers directory to path so dashboard.py imports work
WATCHERS_PATH = Path(__file__).resolve().parent / 'AI_Employee_Vault' / 'Watchers'
sys.path.insert(0, str(WATCHERS_PATH))

# Set vault path env if not already set
if not os.getenv('VAULT_PATH'):
    os.environ['VAULT_PATH'] = str(Path(__file__).resolve().parent / 'AI_Employee_Vault')

# Write Gmail credentials from environment variables (HuggingFace secrets)
_creds_dir = WATCHERS_PATH / 'credentials'
_creds_dir.mkdir(exist_ok=True)

_gmail_token = os.getenv('GMAIL_TOKEN_JSON', '')
if _gmail_token and not (_creds_dir / 'token.json').exists():
    (_creds_dir / 'token.json').write_text(_gmail_token)

_gmail_creds = os.getenv('GMAIL_CREDENTIALS_JSON', '')
if _gmail_creds and not (_creds_dir / 'credentials.json').exists():
    (_creds_dir / 'credentials.json').write_text(_gmail_creds)

# Import the Flask app from dashboard
from dashboard import app  # noqa: E402

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7860))
    print(f"AI Employee Dashboard starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
