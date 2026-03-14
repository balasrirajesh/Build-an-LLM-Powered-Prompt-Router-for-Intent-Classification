# LLM-Powered Prompt Router

A complete, runnable Python application that acts as an intelligent router for user intents. It leverages OpenRouter (`google/gemini-2.0-flash-exp:free`) to classify user requests into predefined intents and subsequently queries a specialized expert prompt to generate a highly aligned, high-quality response.

## Features
- **Intent Classification**: Two-stage routing pipeline. The first LLM call classifies user input.
- **Expert Personas**: Depending on the classified intent (`code`, `data`, `writing`, `career`, `unclear`), the prompt is routed to a specialized expert prompt for generation in a second LLM call.
- **Clarification Loop**: If the intent is unclear or confidence is low (< 0.7), the router asks for clarification.
- **Interactive REPL**: A rich CLI interface to interact with the router.
- **Comprehensive Logging**: Saves every route and response to `route_log.jsonl`.
- **Automated Tests**: A built-in 15-message test suite `--test` to verify routing behaviours.

## Important Note
This project uses **OpenRouter** to access models like `google/gemini-2.0-flash-exp:free`. You must provide a valid `OPENROUTER_API_KEY` to run the application.

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Or Python 3.11+ (if running locally)
- An OpenRouter API Key.

### 1. Environment Configuration
Copy the sample environment file and insert your API key:
```bash
cp .env.example .env
```
Inside `.env`, set:
```env
OPENROUTER_API_KEY=your_actual_openrouter_api_key
```

### 2. Running with Docker Compose
To run the interactive REPL in a containerized environment:
```bash
# Build and run the image, attaching to the container's standard input
docker-compose run --rm router
```

To run the automated test suite within Docker:
```bash
docker-compose run --rm router python main.py --test
```

### 3. Running Locally (Without Docker)
```bash
# Optional: Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Run interactive REPL
python main.py

# Run test suite
python main.py --test
```

## Architecture and Design
1. **Classifier `classifier.py`**: Interrogates the user message with a low-cost, low-temperature LLM call restricted to JSON output. It enforces a strict schema (`intent`, `confidence`) and applies a `0.7` confidence threshold to fallback to `unclear`.
2. **Router & Generator `router.py`**: Uses the extracted intent to select an `EXPERT_PROMPT` (from `prompts.py`). It passes the user message to the OpenRouter API with the expert system instruction, yielding high-quality, persona-specific completions.
3. **Logger `logger.py`**: Intercepts the response and securely writes the user's message, evaluated intent, confidence, and output to `route_log.jsonl`.
4. **CLI `main.py`**: Glues the components together using `rich` for elegant formatting. Supports manual overrides using `@intent` (e.g. `@code How do I sorting array in python`).

## Artifacts
All tests results from automated runs are logged locally to `route_log.jsonl`.
