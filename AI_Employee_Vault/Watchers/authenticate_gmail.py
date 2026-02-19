#!/usr/bin/env python3
"""
Gmail Authentication for WSL
Simple, interactive OAuth flow
"""

import os
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Allow HTTP for localhost (required for WSL/local development)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Run OAuth flow and save token"""

    credentials_path = Path('credentials/credentials.json')
    token_path = Path('token.json')

    print("=" * 70)
    print("Gmail Authentication for WSL")
    print("=" * 70)
    print()

    # Check credentials exist
    if not credentials_path.exists():
        print("❌ Error: credentials.json not found!")
        print(f"Expected location: {credentials_path.absolute()}")
        print()
        print("Please download from Google Cloud Console:")
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop app)")
        print("3. Download JSON")
        print("4. Save as: credentials/credentials.json")
        return False

    print("✅ credentials.json found")
    print()

    # Check if token already exists
    if token_path.exists():
        print("⚠️  token.json already exists!")
        response = input("Do you want to re-authenticate? (y/N): ").strip().lower()
        if response != 'y':
            print("Keeping existing token. Test with: python test_gmail_connection.py")
            return True
        print()

    try:
        print("Starting OAuth flow...")
        print()

        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES,
            redirect_uri='http://localhost:8080/'
        )

        # Get authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='true'
        )

        print("=" * 70)
        print("STEP 1: Authenticate in Browser")
        print("=" * 70)
        print()
        print("Copy and paste this URL into your browser:")
        print()
        print(auth_url)
        print()
        print("-" * 70)
        print()
        print("What will happen:")
        print("  1. Browser opens Google login page")
        print("  2. You'll see: 'Google hasn't verified this app'")
        print("     → Click 'Advanced'")
        print("     → Click 'Go to AI Employee (unsafe)'")
        print("  3. Click 'Allow' to grant Gmail permissions")
        print("  4. Browser redirects to: http://localhost:8080/?code=...")
        print("  5. Page will show 'Unable to connect' (THAT'S NORMAL!)")
        print()
        print("=" * 70)
        print()

        # Get redirect URL from user
        print("STEP 2: Copy the Redirect URL")
        print()
        print("After authorizing, your browser will show an error page.")
        print("Look at the address bar - it will look like:")
        print("  http://localhost:8080/?code=4/0Af...")
        print()
        print("Copy the ENTIRE URL from the address bar and paste it below:")
        print()

        redirect_response = input("Paste redirect URL here: ").strip()

        if not redirect_response:
            print()
            print("❌ No URL provided. Exiting.")
            return False

        if 'code=' not in redirect_response:
            print()
            print("❌ Invalid URL. Must contain '?code='")
            print(f"You provided: {redirect_response[:100]}")
            return False

        print()
        print("Processing authorization...")

        # Exchange code for token
        flow.fetch_token(authorization_response=redirect_response)
        creds = flow.credentials

        # Save credentials
        with open(token_path, 'w') as f:
            f.write(creds.to_json())

        print()
        print("=" * 70)
        print("✅ SUCCESS! Authentication complete!")
        print("=" * 70)
        print()
        print(f"Token saved to: {token_path.absolute()}")
        print()
        print("Next steps:")
        print("  1. Test: python test_gmail_connection.py")
        print("  2. Run:  python gmail_watcher.py ../")
        print()

        return True

    except KeyboardInterrupt:
        print()
        print("❌ Cancelled by user")
        return False

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ Authentication failed")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("  1. Wrong URL pasted (must contain ?code=)")
        print("  2. OAuth consent screen not configured")
        print("  3. Redirect URI mismatch in Google Cloud Console")
        print()
        print("To fix:")
        print("  1. Verify redirect URI is: http://localhost:8080/")
        print("  2. Check OAuth consent screen is in 'Testing' mode")
        print("  3. Try again with: python authenticate_gmail.py")
        print()
        return False

if __name__ == "__main__":
    success = authenticate_gmail()
    sys.exit(0 if success else 1)
