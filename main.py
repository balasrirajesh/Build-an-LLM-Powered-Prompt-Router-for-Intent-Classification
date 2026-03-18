# """
# main.py
# =======
# CLI entry point for the LLM-Powered Prompt Router.

# Features
# --------
# - Interactive REPL: type queries and see classified intent + response.
# - --test flag     : automatically runs all 15 spec test messages and prints
#                     a Rich summary table.
# - @intent prefix  : manually override the classifier, e.g. "@code Fix this".
# - Rich formatting : intent badge (colour-coded), confidence bar, response panel.

# Usage
# -----
#   python main.py            # interactive REPL
#   python main.py --test     # automated test suite
# """

# import sys
# import os

# # Ensure dependencies are importable when running from project root
# sys.path.insert(0, os.path.dirname(__file__))

# from classifier import classify_intent
# from router import route_and_respond
# from logger import log_route
# from prompts import VALID_INTENTS

# from rich.console import Console
# from rich.panel import Panel
# from rich.table import Table
# from rich.text import Text
# from rich import box

# console = Console()

# # ---------------------------------------------------------------------------
# # Colour map for intent badges
# # ---------------------------------------------------------------------------
# INTENT_COLOURS = {
#     "code":    "bold cyan",
#     "data":    "bold green",
#     "writing": "bold magenta",
#     "career":  "bold yellow",
#     "unclear": "bold red",
# }

# INTENT_ICONS = {
#     "code":    "🧑‍💻",
#     "data":    "📊",
#     "writing": "✍️ ",
#     "career":  "💼",
#     "unclear": "🤔",
# }

# # ---------------------------------------------------------------------------
# # 15 spec test messages
# # ---------------------------------------------------------------------------
# TEST_MESSAGES = [
#     "how do i sort a list of objects in python?",
#     "explain this sql query for me",
#     "This paragraph sounds awkward, can you help me fix it?",
#     "I'm preparing for a job interview, any tips?",
#     "what's the average of these numbers: 12, 45, 23, 67, 34",
#     "Help me make this better.",
#     "I need to write a function that takes a user id and returns their profile, "
#     "but also i need help with my resume.",
#     "hey",
#     "Can you write me a poem about clouds?",
#     "Rewrite this sentence to be more professional.",
#     "I'm not sure what to do with my career.",
#     "what is a pivot table",
#     "fxi thsi bug pls: for i in range(10) print(i)",
#     "How do I structure a cover letter?",
#     "My boss says my writing is too verbose.",
# ]


# # ---------------------------------------------------------------------------
# # Helper: detect @intent override prefix
# # ---------------------------------------------------------------------------

# def _parse_override(message: str) -> tuple[str | None, str]:
#     """
#     If *message* starts with @<intent>, extract the intent and return
#     (intent, stripped_message).  Otherwise return (None, message).
#     """
#     stripped = message.strip()
#     if stripped.startswith("@"):
#         parts = stripped[1:].split(None, 1)
#         candidate = parts[0].lower()
#         if candidate in VALID_INTENTS:
#             remaining = parts[1] if len(parts) > 1 else ""
#             return candidate, remaining
#     return None, message


# # ---------------------------------------------------------------------------
# # Core pipeline: classify → route → log
# # ---------------------------------------------------------------------------

# def process_message(user_message: str) -> dict:
#     """
#     Run the full Classify → Route → Respond pipeline.

#     Returns a dict with keys: intent, confidence, response, overridden.
#     """
#     overridden = False
#     override_intent, clean_message = _parse_override(user_message)

#     if override_intent:
#         intent_obj = {"intent": override_intent, "confidence": 1.0}
#         overridden = True
#     else:
#         clean_message = user_message
#         intent_obj = classify_intent(clean_message)

#     response = route_and_respond(clean_message, intent_obj)

#     log_route(
#         user_message=user_message,
#         intent=intent_obj["intent"],
#         confidence=intent_obj["confidence"],
#         final_response=response,
#     )

#     return {
#         "intent": intent_obj["intent"],
#         "confidence": intent_obj["confidence"],
#         "response": response,
#         "overridden": overridden,
#     }


# # ---------------------------------------------------------------------------
# # Rich rendering helpers
# # ---------------------------------------------------------------------------

# def _intent_badge(intent: str, confidence: float, overridden: bool) -> Text:
#     colour = INTENT_COLOURS.get(intent, "white")
#     icon = INTENT_ICONS.get(intent, "❓")
#     badge = Text()
#     badge.append(f"{icon} {intent.upper()}", style=colour)
#     badge.append(f"  confidence: {confidence:.0%}", style="dim")
#     if overridden:
#         badge.append("  [manual override]", style="italic dim yellow")
#     return badge


# def _render_result(message: str, result: dict) -> None:
#     """Print a styled panel for a single query result."""
#     badge = _intent_badge(result["intent"], result["confidence"], result["overridden"])
#     console.print(badge)
#     console.print(
#         Panel(
#             result["response"],
#             title="[bold]Response[/bold]",
#             border_style=INTENT_COLOURS.get(result["intent"], "white"),
#             padding=(1, 2),
#         )
#     )


# # ---------------------------------------------------------------------------
# # Test mode
# # ---------------------------------------------------------------------------

# def run_tests() -> None:
#     console.rule("[bold]🔬 Running 15 Test Messages[/bold]")

#     table = Table(
#         box=box.ROUNDED,
#         show_lines=True,
#         title="Prompt Router — Test Results",
#         highlight=True,
#     )
#     table.add_column("#", style="dim", width=3)
#     table.add_column("Message (truncated)", style="white", max_width=45)
#     table.add_column("Intent", style="bold", width=10)
#     table.add_column("Conf.", width=7)
#     table.add_column("Response snippet", max_width=50)

#     for idx, msg in enumerate(TEST_MESSAGES, start=1):
#         console.print(f"\n[dim]── Test {idx:02d}/{len(TEST_MESSAGES)} ──[/dim]")
#         console.print(f"[bold white]Q:[/bold white] {msg[:80]}")

#         result = process_message(msg)
#         colour = INTENT_COLOURS.get(result["intent"], "white")
#         icon = INTENT_ICONS.get(result["intent"], "❓")
#         snippet = result["response"].replace("\n", " ")[:80] + "…"

#         table.add_row(
#             str(idx),
#             msg[:45] + ("…" if len(msg) > 45 else ""),
#             Text(f"{icon} {result['intent']}", style=colour),
#             f"{result['confidence']:.0%}",
#             snippet,
#         )

#         _render_result(msg, result)

#     console.rule()
#     console.print(table)
#     console.print(
#         f"\n[green]✓ All {len(TEST_MESSAGES)} tests completed.[/green] "
#         f"Results logged to [bold]route_log.jsonl[/bold]."
#     )


# # ---------------------------------------------------------------------------
# # Interactive REPL
# # ---------------------------------------------------------------------------

# def run_repl() -> None:
#     console.print(
#         Panel(
#             "[bold cyan]LLM-Powered Prompt Router[/bold cyan]\n\n"
#             "Type your message and press Enter to get a routed response.\n"
#             "Prefix with [bold yellow]@intent[/bold yellow] to manually override "
#             "(e.g. [italic]@code Fix my bug[/italic]).\n"
#             "Supported intents: "
#             + " | ".join(
#                 f"[{INTENT_COLOURS[i]}]{i}[/{INTENT_COLOURS[i]}]"
#                 for i in VALID_INTENTS
#             )
#             + "\n\nType [bold red]exit[/bold red] or [bold red]quit[/bold red] to leave.",
#             title="🚀 Prompt Router",
#             border_style="cyan",
#         )
#     )

#     while True:
#         try:
#             user_input = console.input("\n[bold cyan]You >[/bold cyan] ").strip()
#         except (EOFError, KeyboardInterrupt):
#             console.print("\n[dim]Goodbye![/dim]")
#             break

#         if not user_input:
#             continue
#         if user_input.lower() in {"exit", "quit"}:
#             console.print("[dim]Goodbye![/dim]")
#             break

#         with console.status("[dim]Classifying and routing…[/dim]", spinner="dots"):
#             result = process_message(user_input)

#         _render_result(user_input, result)


# # ---------------------------------------------------------------------------
# # Entry point
# # ---------------------------------------------------------------------------

# if __name__ == "__main__":
#     if "--test" in sys.argv:
#         run_tests()
#     else:
#         run_repl()



"""
main.py
=======
CLI entry point for the LLM-Powered Prompt Router.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from classifier import classify_intent
from router import route_and_respond
from logger import log_route
from prompts import VALID_INTENTS

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

# ---------------------------------------------------------------------------
# Intent Styling
# ---------------------------------------------------------------------------

INTENT_COLOURS = {
    "code": "bold cyan",
    "data": "bold green",
    "writing": "bold magenta",
    "career": "bold yellow",
    "unclear": "bold red",
}

INTENT_ICONS = {
    "code": "🧑‍💻",
    "data": "📊",
    "writing": "✍️",
    "career": "💼",
    "unclear": "🤔",
}

# ---------------------------------------------------------------------------
# Test Messages
# ---------------------------------------------------------------------------

TEST_MESSAGES = [
    "how do i sort a list of objects in python?",
    "explain this sql query for me",
    "This paragraph sounds awkward, can you help me fix it?",
    "I'm preparing for a job interview, any tips?",
    "what's the average of these numbers: 12, 45, 23, 67, 34",
    "Help me make this better.",
    "I need to write a function that takes a user id and returns their profile, but also i need help with my resume.",
    "hey",
    "Can you write me a poem about clouds?",
    "Rewrite this sentence to be more professional.",
    "I'm not sure what to do with my career.",
    "what is a pivot table",
    "fxi thsi bug pls: for i in range(10) print(i)",
    "How do I structure a cover letter?",
    "My boss says my writing is too verbose.",
]

# ---------------------------------------------------------------------------
# Override Detection
# ---------------------------------------------------------------------------

def _parse_override(message: str):
    stripped = message.strip()
    if stripped.startswith("@"):
        parts = stripped[1:].split(None, 1)
        candidate = parts[0].lower()
        if candidate in VALID_INTENTS:
            remaining = parts[1] if len(parts) > 1 else ""
            return candidate, remaining
    return None, message


# ---------------------------------------------------------------------------
# Core Pipeline
# ---------------------------------------------------------------------------

def process_message(user_message: str) -> dict:
    overridden = False
    override_intent, clean_message = _parse_override(user_message)

    if override_intent:
        intent_obj = {"intent": override_intent, "confidence": 1.0}
        overridden = True
    else:
        clean_message = user_message
        intent_obj = classify_intent(clean_message)

    response = route_and_respond(clean_message, intent_obj)

    # Safety fallback
    if not response:
        response = "⚠️ No response generated."

    log_route(
        user_message=user_message,
        intent=intent_obj["intent"],
        confidence=intent_obj["confidence"],
        final_response=response,
    )

    return {
        "intent": intent_obj["intent"],
        "confidence": intent_obj["confidence"],
        "response": response,
        "overridden": overridden,
    }


# ---------------------------------------------------------------------------
# UI Helpers
# ---------------------------------------------------------------------------

def _intent_badge(intent, confidence, overridden):
    colour = INTENT_COLOURS.get(intent, "white")
    icon = INTENT_ICONS.get(intent, "❓")

    badge = Text()
    badge.append(f"{icon} {intent.upper()}", style=colour)
    badge.append(f"  confidence: {confidence:.0%}", style="dim")

    if overridden:
        badge.append("  [manual override]", style="italic yellow")

    return badge


def _render_result(message, result):
    badge = _intent_badge(
        result["intent"],
        result["confidence"],
        result["overridden"]
    )

    console.print(badge)
    console.print(
        Panel(
            result["response"],
            title="Response",
            border_style=INTENT_COLOURS.get(result["intent"], "white"),
            padding=(1, 2),
        )
    )


# ---------------------------------------------------------------------------
# Test Mode
# ---------------------------------------------------------------------------

def run_tests():
    console.rule("🔬 Running Tests")

    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("#")
    table.add_column("Message")
    table.add_column("Intent")
    table.add_column("Conf.")
    table.add_column("Response")

    for i, msg in enumerate(TEST_MESSAGES, 1):
        result = process_message(msg)

        table.add_row(
            str(i),
            msg[:40],
            result["intent"],
            f"{result['confidence']:.0%}",
            result["response"][:50]
        )

    console.print(table)
    console.print("\n✅ All tests completed")


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def run_repl():
    console.print(
        Panel(
            "🚀 Prompt Router\n\n"
            "Type your query.\n"
            "Use @intent to override.\n"
            "Type exit to quit.",
            border_style="cyan"
        )
    )

    while True:
        try:
            user_input = console.input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            console.print("Goodbye!")
            break

        result = process_message(user_input)
        _render_result(user_input, result)


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        run_repl()