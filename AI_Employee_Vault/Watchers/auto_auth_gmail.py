"""
Auto Gmail Auth - browser khud khulta hai, token auto save hota hai
"""
import os
import sys
from pathlib import Path

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCRIPT_DIR = Path(__file__).resolve().parent
CREDS_FILE = SCRIPT_DIR / 'credentials' / 'credentials.json'
TOKEN_FILE = SCRIPT_DIR / 'credentials' / 'token.json'

if not CREDS_FILE.exists():
    print("ERROR: credentials.json nahi mila:", CREDS_FILE)
    sys.exit(1)

print("credentials.json mila:", CREDS_FILE)
print("Browser khul raha hai... Google account se login karo aur Allow dabao.")
print("(Agar 'App verified nahi' dikhe toh Advanced > Go to app dabao)")
print()

from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
creds = flow.run_local_server(port=8080, open_browser=True, prompt='consent')

TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
TOKEN_FILE.write_text(creds.to_json(), encoding='utf-8')

print()
print("SUCCESS! Token saved:", TOKEN_FILE)
print("Gmail authentication complete!")
