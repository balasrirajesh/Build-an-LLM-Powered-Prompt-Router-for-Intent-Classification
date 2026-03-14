"""
router.py
=========
Provides route_and_respond(message, intent_obj) — the second step in the
routing pipeline.

The function looks up the appropriate expert system prompt using the intent
label from the classifier, then makes a second (generation) LLM call to
produce the final, high-quality response.

Special case: intent == "unclear" → the unclear expert prompt asks the user
for clarification instead of attempting to answer.
"""

import os

import google.generativeai as genai
from dotenv import load_dotenv

from prompts import EXPERT_PROMPTS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

_GENERATION_MODEL = "gemini-2.0-flash"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def route_and_respond(message: str, intent_obj: dict) -> str:
    """
    Select the expert system prompt matching *intent_obj["intent"]* and call
    the generation LLM to produce the final answer.

    Parameters
    ----------
    message     : the original user message.
    intent_obj  : dict returned by classify_intent, e.g.
                  {"intent": "code", "confidence": 0.92}

    Returns
    -------
    str — the generated response text.
    """
    intent = intent_obj.get("intent", "unclear")

    # Safety net: if intent is somehow not in our map, fall back to "unclear"
    system_prompt = EXPERT_PROMPTS.get(intent, EXPERT_PROMPTS["unclear"])

    model = genai.GenerativeModel(
        model_name=_GENERATION_MODEL,
        system_instruction=system_prompt,
    )

    response = model.generate_content(
        message,
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            max_output_tokens=1024,
        ),
    )

    return response.text.strip()
