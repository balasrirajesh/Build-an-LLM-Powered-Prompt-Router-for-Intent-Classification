"""
router.py
=========
Provides route_and_respond(message, intent_obj)
"""

import os

from openai import OpenAI
from dotenv import load_dotenv

from prompts import EXPERT_PROMPTS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("❌ OPENROUTER_API_KEY not set in .env")

# OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "Prompt Router Project"
    }
)

# ✅ FIXED MODEL (WORKING)
_GENERATION_MODEL = "openai/gpt-3.5-turbo"


# ---------------------------------------------------------------------------
# Main Function
# ---------------------------------------------------------------------------

def route_and_respond(message: str, intent_obj: dict) -> str:
    intent = intent_obj.get("intent", "unclear")

    system_prompt = EXPERT_PROMPTS.get(intent, EXPERT_PROMPTS["unclear"])

    try:
        completion = client.chat.completions.create(
            model=_GENERATION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"[router] Error: {e}")
        return "⚠️ Error generating response. Please try again."