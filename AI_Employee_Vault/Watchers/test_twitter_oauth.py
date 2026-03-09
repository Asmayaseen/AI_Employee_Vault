#!/usr/bin/env python3
"""
Twitter OAuth 1.0a — End-to-End Test
Tests auth, posts a tweet, deletes it, and prints a clear PASS/FAIL result.

Run from: AI_Employee_Vault/Watchers/
  python test_twitter_oauth.py          # post + auto-delete
  python test_twitter_oauth.py --keep   # post + keep tweet live

If your app still shows 403:
  developer.twitter.com → App → User authentication settings
  → App permissions: "Read and Write" → Save
  → Keys and tokens → Access Token and Secret → Regenerate
  → Paste new values into .env
"""

import os, sys, asyncio, hashlib, hmac, base64, time, urllib.parse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

BEARER_TOKEN  = os.getenv('TWITTER_BEARER_TOKEN', '').strip()
API_KEY       = os.getenv('TWITTER_API_KEY', '').strip()
API_SECRET    = os.getenv('TWITTER_API_SECRET', '').strip()
ACCESS_TOKEN  = os.getenv('TWITTER_ACCESS_TOKEN', '').strip()
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '').strip()

BASE  = 'https://api.twitter.com/2'
SEP   = '─' * 60
BOLD  = lambda s: f"\033[1m{s}\033[0m"
GREEN = lambda s: f"\033[92m{s}\033[0m"
RED   = lambda s: f"\033[91m{s}\033[0m"
YEL   = lambda s: f"\033[93m{s}\033[0m"

# ── OAuth 1.0a header ──────────────────────────────────────────────────────────

def _oauth_header(method: str, url: str) -> str:
    params = {
        'oauth_consumer_key':     API_KEY,
        'oauth_token':            ACCESS_TOKEN,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp':        str(int(time.time())),
        'oauth_nonce':            hashlib.md5(f"{time.time()}".encode()).hexdigest(),
        'oauth_version':          '1.0',
    }
    sorted_p = sorted(params.items())
    param_str = '&'.join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
        for k, v in sorted_p
    )
    base_str = (f"{method}&{urllib.parse.quote(url, safe='')}"
                f"&{urllib.parse.quote(param_str, safe='')}")
    sign_key = (f"{urllib.parse.quote(API_SECRET, safe='')}"
                f"&{urllib.parse.quote(ACCESS_SECRET, safe='')}")
    sig = base64.b64encode(
        hmac.new(sign_key.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()
    params['oauth_signature'] = sig
    return 'OAuth ' + ', '.join(
        f'{k}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(params.items())
    )

# ── Steps ──────────────────────────────────────────────────────────────────────

def step_credentials() -> bool:
    print(f"\n{SEP}\n  STEP 1 — Credential Check\n{SEP}")
    creds = {
        'TWITTER_BEARER_TOKEN':  BEARER_TOKEN,
        'TWITTER_API_KEY':       API_KEY,
        'TWITTER_API_SECRET':    API_SECRET,
        'TWITTER_ACCESS_TOKEN':  ACCESS_TOKEN,
        'TWITTER_ACCESS_SECRET': ACCESS_SECRET,
    }
    ok = True
    for name, val in creds.items():
        if val:
            print(f"  {GREEN('✅')} {name}: ****{val[-6:]}")
        else:
            print(f"  {RED('❌')} {name}: NOT SET")
            ok = False
    if not ok:
        print(f"\n  {RED('FAIL')} — Add missing credentials to .env and retry.")
    else:
        print(f"\n  {GREEN('✅ All 5 credentials present.')}")
    return ok


async def step_auth() -> dict | None:
    import aiohttp
    print(f"\n{SEP}\n  STEP 2 — OAuth 1.0a Auth  (GET /2/users/me)\n{SEP}")
    url = f'{BASE}/users/me'
    headers = {'Authorization': _oauth_header('GET', url),
               'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers) as r:
            data = await r.json()

    if 'data' in data:
        u = data['data']
        print(f"  {GREEN('✅')} Authenticated as: @{u.get('username')}  (ID: {u.get('id')})")
        return u
    else:
        err = data.get('errors', [{}])[0] if data.get('errors') else data
        print(f"  {RED('❌')} Auth failed: {err}")
        if '32' in str(err) or '401' in str(data):
            print(YEL("\n  FIX: Regenerate Access Token at:"))
            print(YEL("  developer.twitter.com → App → Keys and tokens → Regenerate"))
        return None


async def step_post_tweet() -> str | None:
    import aiohttp
    print(f"\n{SEP}\n  STEP 3 — Post Test Tweet  (POST /2/tweets)\n{SEP}")
    url  = f'{BASE}/tweets'
    text = f"[AI Employee] Twitter OAuth 1.0a ✅ — {time.strftime('%Y-%m-%d %H:%M:%S')} #AIEmployee #Test"
    headers = {'Authorization': _oauth_header('POST', url),
               'Content-Type': 'application/json'}
    print(f"  Posting: \"{text}\"")
    async with aiohttp.ClientSession() as s:
        async with s.post(url, headers=headers, json={'text': text}) as r:
            status = r.status
            data   = await r.json()

    if 'data' in data and 'id' in data['data']:
        tid = data['data']['id']
        print(f"  {GREEN('✅')} Tweet posted!  ID: {tid}")
        print(f"  {GREEN('🔗')} https://x.com/i/web/status/{tid}")
        return tid
    else:
        print(f"  {RED('❌')} POST failed  (HTTP {status})")
        print(f"  Response: {data}")
        detail = str(data.get('detail', '')) + str(data.get('title', ''))
        if status == 403 and 'oauth1' in detail.lower():
            print(YEL("\n  ┌─ FIX: App still in Read-Only mode ─────────────────────┐"))
            print(YEL("  │  1. developer.twitter.com → Projects & Apps              │"))
            print(YEL("  │  2. Click your App name                                  │"))
            print(YEL("  │  3. Settings tab → User authentication settings → Edit   │"))
            print(YEL("  │  4. App permissions → ● Read and Write → Save            │"))
            print(YEL("  │  5. Keys and tokens → Access Token and Secret            │"))
            print(YEL("  │     → Regenerate → copy BOTH new values                  │"))
            print(YEL("  │  6. Update .env:                                         │"))
            print(YEL("  │     TWITTER_ACCESS_TOKEN=<new token>                     │"))
            print(YEL("  │     TWITTER_ACCESS_SECRET=<new secret>                   │"))
            print(YEL("  │  7. Run: python test_twitter_oauth.py                    │"))
            print(YEL("  └──────────────────────────────────────────────────────────┘"))
        elif status == 401:
            print(YEL("\n  FIX: Regenerate tokens (old tokens invalid after permission change)"))
        elif status == 429:
            print(YEL("\n  FIX: Rate limited. Wait 15 min and retry."))
        return None


async def step_delete_tweet(tweet_id: str) -> bool:
    import aiohttp
    print(f"\n{SEP}\n  STEP 4 — Delete Test Tweet  (cleanup)\n{SEP}")
    url = f'{BASE}/tweets/{tweet_id}'
    headers = {'Authorization': _oauth_header('DELETE', url),
               'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as s:
        async with s.delete(url, headers=headers) as r:
            data = await r.json()

    if data.get('data', {}).get('deleted'):
        print(f"  {GREEN('✅')} Test tweet deleted (ID: {tweet_id})")
        return True
    else:
        print(f"  {YEL('⚠️')}  Could not auto-delete: {data}")
        print(f"  Manually delete: https://x.com/i/web/status/{tweet_id}")
        return False

# ── Main ───────────────────────────────────────────────────────────────────────

async def main():
    keep = '--keep' in sys.argv
    results = {'credentials': False, 'auth': False, 'tweet': False, 'cleanup': None}

    print(f"\n{'═'*60}")
    print(f"  {BOLD('Twitter OAuth 1.0a — End-to-End Test')}")
    print(f"{'═'*60}")

    # Step 1
    results['credentials'] = step_credentials()
    if not results['credentials']:
        _print_final(results, None)
        sys.exit(1)

    # Step 2
    user = await step_auth()
    results['auth'] = user is not None
    if not results['auth']:
        _print_final(results, None)
        sys.exit(1)

    # Step 3
    tweet_id = await step_post_tweet()
    results['tweet'] = tweet_id is not None
    if not results['tweet']:
        _print_final(results, user)
        sys.exit(1)

    # Step 4
    if keep:
        print(f"\n{SEP}\n  STEP 4 — Cleanup skipped (--keep flag)\n{SEP}")
        print(f"  {YEL('⚠️')}  Tweet is live: https://x.com/i/web/status/{tweet_id}")
        results['cleanup'] = 'skipped'
    else:
        ok = await step_delete_tweet(tweet_id)
        results['cleanup'] = 'ok' if ok else 'manual'

    _print_final(results, user)


def _print_final(results: dict, user: dict | None):
    all_ok = results['credentials'] and results['auth'] and results['tweet']
    print(f"\n{'═'*60}")
    if all_ok:
        uname = f"@{user.get('username')}" if user else ''
        print(f"  {GREEN(BOLD('RESULT: ✅ PASS — Twitter OAuth 1.0a FULLY WORKING'))}")
        print(f"  Account  : {GREEN(uname)}")
        print(f"  Auth     : {GREEN('✅ OAuth 1.0a verified')}")
        print(f"  Posting  : {GREEN('✅ Tweet posted successfully')}")
        cleanup = results.get('cleanup')
        if cleanup == 'ok':
            print(f"  Cleanup  : {GREEN('✅ Test tweet deleted')}")
        elif cleanup == 'skipped':
            print(f"  Cleanup  : {YEL('⚠️  Tweet kept (--keep flag)')}")
        else:
            print(f"  Cleanup  : {YEL('⚠️  Manual delete needed')}")
        print(f"\n  {GREEN('Gold Tier Gap 2: RESOLVED ✅')}")
    else:
        print(f"  {RED(BOLD('RESULT: ❌ FAIL — Twitter not fully working'))}")
        print(f"  Credentials : {GREEN('✅') if results['credentials'] else RED('❌')}")
        print(f"  Auth        : {GREEN('✅') if results['auth'] else RED('❌')}")
        print(f"  Tweet POST  : {GREEN('✅') if results['tweet'] else RED('❌ — Fix permissions first')}")
        print(f"\n  {RED('Fix the issues above, then re-run this script.')}")
    print(f"{'═'*60}\n")


if __name__ == '__main__':
    asyncio.run(main())
