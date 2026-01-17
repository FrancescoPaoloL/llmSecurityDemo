# API

Flask API that orchestrates LLM inference and security detection.

## Setup

Before running, create a `.env` file like this:
```
BINARY_PATH=/path/to/owasp-llm-tool
MODEL_PATH=/path/to/model.gguf
FLASK_ENV=development
FLASK_PORT=5000
MAX_PROMPT_LENGTH=5000
GENERATION_TIMEOUT=60
```

## Run locally
```bash
cd api
python -m venv api__venv
source api__venv/bin/activate
pip install -r requirements.txt
python server.py
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/test | Process prompt and detect OWASP category |
| GET | /health | Health check |

## Example
```bash
curl -X POST http://localhost:5000/api/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'
```

Response:
```json
{
  "prompt": "Hello",
  "response": "...",
  "category": "unknown",
  "metadata": {
    "tokens_prompt": 1,
    "tokens_generated": 25,
    "generation_time": 0.3,
    "stop_reason": "limit"
  }
}
```

## Files

| File | Purpose |
|------|---------|
| server.py | Entry point |
| config.py | Loads .env, validates paths |
| llama_service.py | Calls llama-server + owasp-llm-tool |
| routes/test.py | /api/test endpoint |
| routes/health.py | /health endpoint |



**Visual:**
```
process_prompt()
    │
    ├──► generate_response()  ──► HTTP POST localhost:8081/completion
    │                              └── returns: content, tokens, time
    │
    └──► detect_category()    ──► subprocess: owasp-llm-tool --detect-only
                                   └── returns: LLM01/02/06/unknown
