"""
classifier.py
=============
Provides classify_intent(message) — the first step in the routing pipeline.

The function:
  1. Calls OpenRouter with the short CLASSIFIER_PROMPT to detect intent.
  2. Parses the JSON response.
  3. Applies a confidence threshold (< 0.7 → "unclear").
  4. On ANY error (network, JSON parse, unexpected schema) returns a safe
     fallback: {"intent": "unclear", "confidence": 0.0}
"""

import json
import os
import re

from openai import OpenAI
from dotenv import load_dotenv

from prompts import CLASSIFIER_PROMPT, VALID_INTENTS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

# Initialize the OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", "")
)

_CLASSIFIER_MODEL = "google/gemini-2.0-flash-exp:free"
_CONFIDENCE_THRESHOLD = 0.7   # below this → treat as "unclear"

_FALLBACK = {"intent": "unclear", "confidence": 0.0}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> str:
    """
    Try to extract a JSON object from raw LLM text.
    Handles cases where the model wraps the JSON in markdown code fences
    or adds extra prose before/after.
    """
    # Strip markdown fences if present
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)

    # Try the whole text as-is
    bare = re.search(r"\{.*?\}", text, re.DOTALL)
    if bare:
        return bare.group(0)

    return text   # let json.loads raise if it can't parse


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_intent(message: str) -> dict:
    """
    Classify the user *message* into one of the supported intent labels.

    Returns a dict: {"intent": str, "confidence": float}

    Failures (network error, malformed JSON, missing keys, invalid intent)
    are caught and the function returns _FALLBACK instead of raising.
    """
    try:
        completion = client.chat.completions.create(
            model=_CLASSIFIER_MODEL,
            messages=[
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=0.0,
            max_tokens=64,
        )

        raw = completion.choices[0].message.content.strip()

        # --- Parse JSON ---------------------------------------------------
        json_str = _extract_json(raw)
        parsed = json.loads(json_str)

        # --- Validate schema ----------------------------------------------
        intent = str(parsed.get("intent", "")).lower()
        confidence = float(parsed.get("confidence", 0.0))

        if intent not in VALID_INTENTS:
            print(f"[classifier] Unknown intent '{intent}', defaulting to unclear.")
            return _FALLBACK

        # --- Confidence threshold -----------------------------------------
        if confidence < _CONFIDENCE_THRESHOLD and intent != "unclear":
            print(
                f"[classifier] Low confidence ({confidence:.2f}) for intent "
                f"'{intent}', downgrading to unclear."
            )
            intent = "unclear"
            # Keep original confidence for logging transparency
            return {"intent": "unclear", "confidence": confidence}

        return {"intent": intent, "confidence": confidence}

    except json.JSONDecodeError as exc:
        print(f"[classifier] JSON parse error: {exc}")
        return _FALLBACK
    except KeyError as exc:
        print(f"[classifier] Missing key in LLM response: {exc}")
        return _FALLBACK
    except Exception as exc:  # noqa: BLE001
        print(f"[classifier] Unexpected error: {exc}")
        return _FALLBACK
