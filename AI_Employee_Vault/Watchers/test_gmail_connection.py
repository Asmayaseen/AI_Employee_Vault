#!/usr/bin/env python3
"""
Quick Gmail Connection Test
Tests if Gmail API authentication is working
"""

import os
import sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def test_gmail_connection():
    """Test Gmail API connection"""

    vault_path = Path(__file__).parent.parent
    credentials_path = vault_path / 'Watchers' / 'credentials' / 'credentials.json'
    token_path = vault_path / 'Watchers' / 'token.json'

    print("=" * 60)
    print("Gmail Connection Test")
    print("=" * 60)
    print(f"Vault path: {vault_path}")
    print(f"Credentials: {credentials_path}")
    print(f"Token: {token_path}")
    print()

    # Check files exist
    if not credentials_path.exists():
        print("❌ credentials.json NOT found!")
        print(f"Expected at: {credentials_path}")
        return False
    else:
        print("✅ credentials.json found")

    if not token_path.exists():
        print("⚠️  token.json NOT found (first time setup)")
        print("   OAuth flow will be required")
        return None
    else:
        print("✅ token.json found")

    # Test authentication
    try:
        print("\nTesting authentication...")
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("   Refreshing expired token...")
                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
                print("✅ Token refreshed successfully")
            else:
                print("❌ Token invalid, re-authentication needed")
                return False
        else:
            print("✅ Token valid")

        # Test API call
        print("\nTesting Gmail API connection...")
        service = build('gmail', 'v1', credentials=creds)

        # Get user profile
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')
        total_messages = profile.get('messagesTotal', 0)

        print(f"✅ Connected to Gmail!")
        print(f"   Email: {email}")
        print(f"   Total messages: {total_messages:,}")

        # Try to get unread count
        unread = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=10
        ).execute()

        unread_count = unread.get('resultSizeEstimate', 0)
        print(f"   Unread messages: {unread_count}")

        print("\n" + "=" * 60)
        print("✅ Gmail connection test PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    result = test_gmail_connection()

    if result is True:
        print("\n✅ Gmail watcher is ready to use!")
        sys.exit(0)
    elif result is False:
        print("\n❌ Gmail connection failed. Check credentials.")
        sys.exit(1)
    else:
        print("\n⚠️  First-time setup required. Run gmail_watcher.py")
        sys.exit(2)
