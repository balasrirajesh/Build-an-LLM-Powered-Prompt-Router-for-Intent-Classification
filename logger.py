"""
logger.py
=========
Provides log_route() — appends one JSON Lines entry to route_log.jsonl.

Each entry contains:
  - timestamp       : ISO-8601 UTC timestamp of the request.
  - user_message    : the original user input.
  - intent          : classified intent label.
  - confidence      : classifier confidence score (float).
  - final_response  : the text returned to the user.
"""

import json
import os
from datetime import datetime, timezone

LOG_FILE = os.path.join(os.path.dirname(__file__), "route_log.jsonl")


def log_route(
    user_message: str,
    intent: str,
    confidence: float,
    final_response: str,
) -> None:
    """
    Append a single JSON Lines record to *route_log.jsonl*.

    Parameters
    ----------
    user_message   : raw user input string.
    intent         : classified intent label (e.g. "code").
    confidence     : float 0.0–1.0 classifier confidence.
    final_response : the text that was returned to the user.
    """
    entry = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "user_message": user_message,
        "intent": intent,
        "confidence": round(float(confidence), 4),
        "final_response": final_response,
    }

    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
