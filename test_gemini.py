import os
from google import genai

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print('? ERROR: GEMINI_API_KEY environment variable set nahi hai!')
    exit(1)

client = genai.Client(api_key=api_key)

try:
    print('? Testing Gemini 2.5 Flash connection for AI Employee Vault...')
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='You are an autonomous AI Employee. In 1 short sentence, confirm you are ready to process business vault tasks.'
    )
    print('? GEMINI CONNECTED SUCCESSFULLY!')
    print('?? Agent Response:', response.text)
except Exception as e:
    print('? Connection Error:', e)
