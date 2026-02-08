#!/usr/bin/env python3
"""
LinkedIn Watcher Test Script
Tests LinkedIn monitoring without requiring full browser interaction.
"""

import sys
from pathlib import Path
from linkedin_watcher import LinkedInWatcher, PLAYWRIGHT_AVAILABLE

def main():
    print("=" * 70)
    print("LinkedIn Watcher - Test Suite")
    print("=" * 70)
    print()

    # Check prerequisites
    print("1. Checking Prerequisites...")
    print()

    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not installed")
        print("   Install with: pip install playwright && playwright install chromium")
        return 1
    else:
        print("✅ Playwright is installed")

    print()

    # Initialize watcher
    print("2. Initializing LinkedIn Watcher...")
    print()

    try:
        vault_path = Path(__file__).parent.parent
        watcher = LinkedInWatcher(str(vault_path), check_interval=60)
        print(f"✅ Watcher initialized")
        print(f"   Vault: {watcher.vault_path}")
        print(f"   Session: {watcher.session_path}")
        print(f"   Dry run: {watcher.dry_run}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize watcher: {e}")
        return 1

    # Check session status
    print("3. Checking LinkedIn Session...")
    print()

    session_exists = watcher.session_path.exists() and any(watcher.session_path.iterdir())

    if session_exists:
        print("✅ Session directory exists (may have saved login)")
    else:
        print("⚠️  No saved session found")
        print("   First run will require LinkedIn login in browser")

    print()

    # Show configuration
    print("4. Configuration:")
    print()
    print(f"   Check interval: {watcher.check_interval} seconds")
    print(f"   Lead keywords: {', '.join(watcher.lead_keywords[:5])}...")
    print(f"   Processed file: {watcher.processed_file.name}")
    print()

    # WSL Warning
    print("5. Important Notes for WSL:")
    print()
    print("⚠️  You are running on WSL. LinkedIn watcher requires:")
    print("   - X Server (VcXsrv or WSLg) for browser display")
    print("   - Or use --headless mode (may trigger LinkedIn security)")
    print()
    print("📝 Recommended Setup:")
    print("   1. Install VcXsrv on Windows")
    print("   2. Set DISPLAY environment variable")
    print("   3. Or run on native Linux/macOS")
    print()

    # Manual test option
    print("6. Test Options:")
    print()
    print("A. Full test (opens browser, requires login):")
    print("   python test_linkedin.py --full")
    print()
    print("B. Configuration test (no browser):")
    print("   python test_linkedin.py")
    print()
    print("C. Run watcher continuously:")
    print("   python linkedin_watcher.py ../")
    print()

    # If --full flag provided
    if "--full" in sys.argv:
        print("=" * 70)
        print("Running Full Browser Test")
        print("=" * 70)
        print()
        print("⚠️  Browser will open. You may need to:")
        print("   - Login to LinkedIn")
        print("   - Complete security challenges")
        print("   - Wait for session to be saved")
        print()

        input("Press Enter to continue or Ctrl+C to cancel...")

        try:
            print("\nInitializing browser...")
            watcher._init_browser()
            print("✅ Browser initialized")

            print("\nChecking LinkedIn login status...")
            logged_in = watcher._ensure_logged_in()

            if logged_in:
                print("✅ Successfully logged in to LinkedIn!")
                print("\nRunning single check...")
                items = watcher.check_for_updates()
                print(f"✅ Check complete. Found {len(items)} new items")

                if items:
                    print("\nNew items:")
                    for item in items:
                        print(f"  - {item.get('type', 'unknown')}: {item.get('preview', 'No preview')[:50]}")
                else:
                    print("  (No new messages or notifications)")
            else:
                print("❌ Failed to login to LinkedIn")
                print("   Please check browser and try again")

            # Cleanup
            if watcher._browser:
                watcher._browser.close()
            if watcher._playwright:
                watcher._playwright.stop()

        except KeyboardInterrupt:
            print("\n\n⚠️  Test cancelled by user")
            return 1
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            return 1

    print("=" * 70)
    print("Test Complete")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(main())
