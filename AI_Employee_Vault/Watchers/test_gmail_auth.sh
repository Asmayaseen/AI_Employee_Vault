#!/bin/bash
# Test Gmail Authentication Script
# This script will test Gmail watcher authentication

set -e

echo "========================================"
echo "  Gmail Watcher Authentication Test"
echo "========================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VAULT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 Vault Directory: $VAULT_DIR"
echo "🔑 Credentials Path: $SCRIPT_DIR/credentials/credentials.json"
echo ""

# Check if credentials exist
if [ ! -f "$SCRIPT_DIR/credentials/credentials.json" ]; then
    echo "❌ ERROR: credentials.json not found!"
    echo "Please download from Google Cloud Console and place in:"
    echo "  $SCRIPT_DIR/credentials/"
    exit 1
fi

echo "✅ Credentials file found!"
echo ""

# Check Python dependencies
echo "📦 Checking Python dependencies..."
if python3 -c "import google.oauth2.credentials" 2>/dev/null; then
    echo "✅ Google API libraries installed"
else
    echo "⚠️  Installing Google API libraries..."
    pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
fi

echo ""
echo "🚀 Starting Gmail Watcher..."
echo ""
echo "What will happen:"
echo "1. Browser will open automatically"
echo "2. Select your Google account"
echo "3. You may see 'Google hasn't verified this app' - this is normal"
echo "4. Click 'Advanced' → 'Go to AI Employee (unsafe)'"
echo "5. Click 'Allow' for Gmail permissions"
echo "6. Browser will show 'Authentication complete'"
echo "7. Watcher will start monitoring your Gmail"
echo ""
echo "Press Ctrl+C to stop the watcher after successful authentication."
echo ""

read -p "Press ENTER to start authentication..."

# Run Gmail watcher
cd "$SCRIPT_DIR"
python3 gmail_watcher.py "$VAULT_DIR" "$SCRIPT_DIR/credentials/credentials.json"
