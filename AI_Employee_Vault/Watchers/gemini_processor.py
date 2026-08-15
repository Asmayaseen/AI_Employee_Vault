import os
import json
import logging
from pathlib import Path
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GeminiProcessor")

class GeminiProcessor:
    def __init__(self, api_key=None, model="gemini-flash-latest"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set.")
        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        logger.info(f"Initialized GeminiProcessor with model: {self.model}")

    def process_task(self, task_text: str, context: str = "") -> dict:
        prompt = f"""
You are the autonomous reasoning engine of AI Employee Vault operating for small businesses.
Your role is to analyze tasks, draft responses, generate CRM actions, and flag items requiring human approval.

Context / Business State:
{context}

Task / Event to Process:
{task_text}

Provide output strictly in JSON format with the following keys:
- "summary": A brief one-line summary of the task.
- "action_type": One of ["EMAIL_REPLY", "CRM_UPDATE", "SOCIAL_POST", "INTERNAL_NOTE", "ESCALATE"].
- "suggested_action": The exact response, draft content, or action detail.
- "requires_human_approval": true/false (true for financial, contract, or high-risk actions).
- "reasoning": 1-2 sentence explanation of your decision.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            parsed = json.loads(response.text)
            logger.info("Successfully processed task via Gemini 2.5")
            return parsed
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return {
                "summary": "Processing Error",
                "action_type": "ESCALATE",
                "suggested_action": str(e),
                "requires_human_approval": True,
                "reasoning": "Gemini API call failed"
            }

if __name__ == "__main__":
    processor = GeminiProcessor()
    test_task = "Inbound email from Sarah: Interested in deploying AI Employee Vault for her 10-person agency. Wants pricing and setup timeline."
    result = processor.process_task(test_task, context="Standard Tier: /mo, Enterprise: /mo. Setup takes under 24 hours.")
    print("\n--- GEMINI AUTONOMOUS REASONING OUTPUT ---")
    print(json.dumps(result, indent=2))
