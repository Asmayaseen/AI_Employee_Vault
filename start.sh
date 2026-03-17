#!/bin/bash
# Startup script — write Gmail credentials from env vars before launching supervisord

CREDS_DIR="/app/AI_Employee_Vault/Watchers/credentials"
mkdir -p "$CREDS_DIR"

# Write Gmail token from HuggingFace secret
if [ -n "$GMAIL_TOKEN_JSON" ]; then
    echo "$GMAIL_TOKEN_JSON" > "$CREDS_DIR/token.json"
    echo "✅ Gmail token.json written"
fi

# Write Gmail credentials from HuggingFace secret
if [ -n "$GMAIL_CREDENTIALS_JSON" ]; then
    echo "$GMAIL_CREDENTIALS_JSON" > "$CREDS_DIR/credentials.json"
    echo "✅ Gmail credentials.json written"
fi

# Start supervisord
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/ai-employee.conf
