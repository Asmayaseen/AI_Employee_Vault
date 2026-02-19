#!/bin/bash
# Simple Gmail Authentication Helper for WSL

echo "================================================"
echo "Gmail Authentication Setup for WSL"
echo "================================================"
echo ""
echo "This will authenticate your Gmail account."
echo "Since we're in WSL, we'll use a manual process."
echo ""

cd "$(dirname "$0")"

echo "Starting authentication..."
echo ""

# Run Python script and capture the OAuth URL
python3 - << 'PYTHON_SCRIPT'
import os
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

vault_path = Path(__file__).parent if hasattr(Path, 'parent') else Path.cwd().parent
credentials_path = Path('credentials/credentials.json')
token_path = Path('token.json')

if not credentials_path.exists():
    print("❌ Error: credentials.json not found!")
    print(f"Please place it in: {credentials_path.absolute()}")
    sys.exit(1)

print("✅ credentials.json found")
print("")
print("Starting OAuth flow...")
print("")

try:
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        SCOPES,
        redirect_uri='http://localhost:8080/'
    )

    # Get the authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )

    print("=" * 70)
    print("STEP 1: Open this URL in your Windows browser:")
    print("=" * 70)
    print("")
    print(auth_url)
    print("")
    print("=" * 70)
    print("")
    print("STEP 2: After you authorize:")
    print("  - You'll be redirected to http://localhost:8080/?code=...")
    print("  - The page will NOT load (that's normal)")
    print("  - Copy the FULL URL from your browser's address bar")
    print("")
    print("=" * 70)
    print("")

    # Get the redirect URL from user
    redirect_response = input("Paste the full redirect URL here: ").strip()

    if not redirect_response:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)

    print("")
    print("Processing authorization...")

    # Fetch the token
    flow.fetch_token(authorization_response=redirect_response)
    creds = flow.credentials

    # Save the token
    with open(token_path, 'w') as f:
        f.write(creds.to_json())

    print("")
    print("=" * 70)
    print("✅ Authentication successful!")
    print("=" * 70)
    print(f"Token saved to: {token_path.absolute()}")
    print("")
    print("You can now run: python gmail_watcher.py ../")
    print("")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    sys.exit(1)

PYTHON_SCRIPT

echo ""
echo "Done!"
