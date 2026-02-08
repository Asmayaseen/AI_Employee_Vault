#!/usr/bin/env python3
"""
LinkedIn Session Setup - One-time manual login
Run this once to save LinkedIn session, then watcher can run headless
"""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

print("=" * 70)
print("LinkedIn Session Setup - Manual Login")
print("=" * 70)
print()

# Paths
vault_path = Path(__file__).parent.parent
session_path = vault_path / 'Watchers' / '.linkedin_session'
session_path.mkdir(parents=True, exist_ok=True)

print(f"Vault: {vault_path}")
print(f"Session: {session_path}")
print()

# Check if session already exists
if session_path.exists() and any(session_path.iterdir()):
    print("⚠️  Session directory already exists")
    response = input("Delete and create new session? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)

    # Clear old session
    import shutil
    shutil.rmtree(session_path)
    session_path.mkdir(parents=True, exist_ok=True)
    print("✅ Old session cleared")
    print()

print("=" * 70)
print("IMPORTANT: Browser will open in NON-HEADLESS mode")
print("=" * 70)
print()
print("Steps:")
print("1. Browser window will open")
print("2. Login to LinkedIn manually")
print("3. Complete any security challenges")
print("4. Wait on LinkedIn homepage for 10 seconds")
print("5. Browser will close automatically")
print("6. Session will be saved for future use")
print()
print("After this setup, watcher can run in headless mode!")
print("=" * 70)
print()

input("Press Enter to open browser...")

try:
    with sync_playwright() as p:
        print("\nLaunching browser (NON-HEADLESS)...")

        # Force non-headless for login
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False,  # Must see browser for login
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ],
            viewport={'width': 1280, 'height': 800}
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        print("✅ Browser opened")
        print("\nNavigating to LinkedIn...")

        page.goto('https://www.linkedin.com/feed/', timeout=60000)

        print()
        print("=" * 70)
        print("PLEASE LOGIN TO LINKEDIN IN THE BROWSER NOW")
        print("=" * 70)
        print()
        print("After logging in successfully:")
        print("- You should see your LinkedIn feed")
        print("- Wait on the page for 10 seconds")
        print("- Browser will close automatically")
        print()

        # Wait for user to login (5 minutes max)
        print("Waiting for login (timeout: 5 minutes)...")

        try:
            # Wait for feed to load (indicates successful login)
            page.wait_for_selector(
                '[data-control-name="nav.homepage"], .feed-identity-module, .scaffold-layout__main',
                timeout=300000  # 5 minutes
            )

            print()
            print("✅ Login detected!")
            print("\nWaiting 10 seconds to ensure session is saved...")
            time.sleep(10)

            print("✅ Session saved!")

        except Exception as e:
            print(f"\n⚠️  Did not detect successful login: {e}")
            print("\nIf you logged in successfully, session may still be saved.")
            print("Waiting 5 more seconds...")
            time.sleep(5)

        print("\nClosing browser...")
        browser.close()

        print()
        print("=" * 70)
        print("✅ SETUP COMPLETE!")
        print("=" * 70)
        print()
        print(f"Session saved to: {session_path}")
        print()
        print("Now you can run LinkedIn watcher in headless mode:")
        print()
        print("  export LINKEDIN_HEADLESS=true")
        print("  python linkedin_watcher.py ../")
        print()
        print("Or test it:")
        print("  python test_linkedin.py --full")
        print()

except KeyboardInterrupt:
    print("\n\n⚠️  Setup cancelled by user")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Error during setup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
