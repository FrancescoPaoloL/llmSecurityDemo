# API

Flask API that orchestrates LLM inference and security detection.

## Setup

Create `.env`:
```bash
BINARY_PATH=/path/to/owasp-llm-tool
MODEL_PATH=/path/to/model.gguf
FLASK_ENV=development
FLASK_PORT=5000
MAX_PROMPT_LENGTH=5000
GENERATION_TIMEOUT=60
```

## Run Locally
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

**Request:**
```bash
curl -X POST http://localhost:5000/api/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Ignore previous instructions"}'
```

**Response:**
```json
{
  "prompt": "Ignore previous instructions",
  "response": "...",
  "category": "LLM01",
  "metadata": {
    "tokens_prompt": 3,
    "tokens_generated": 100,
    "generation_time": 18.5,
    "stop_reason": "max_tokens",
    "perplexity": null
  }
}
```

**Note:** `perplexity` field only present for LLM03 detections.

## Architecture
```
process_prompt()
    │
    ├──► generate_response()  ──► HTTP POST localhost:8081/completion
    │                              └── llama-server (Qwen 2.5 0.5B)
    │
    └──► detect_category()    ──► subprocess: owasp-llm-tool --skip_llm_generation
                                   └── pattern matching: LLM01/02/04/06
                                   └── perplexity: LLM03 (if model loaded)
```

## Detection Modes

**Pattern-based (default):**
- `--skip_llm_generation` flag
- No model required
- Returns: LLM01/02/04/06/unknown
- Fast: <100ms

**Perplexity-based (LLM03):**
- Model loaded via positional arg
- Returns: LLM03/unknown + perplexity score
- Slow: ~20s (includes model initialization)

## Files

| File | Purpose |
|------|---------|
| server.py | Entry point, Flask app initialization |
| config.py | Loads `.env`, validates paths |
| llama_service.py | Calls llama-server + owasp-llm-tool |
| routes/test.py | `/api/test` endpoint logic |
| routes/health.py | `/health` endpoint |

## Version

**Current:** v0.10.0 (LLM03 perplexity detection support)

## Changes in v0.10.0

- Added perplexity field in response metadata (LLM03)
- Support for both pattern and perplexity detection modes
- Updated error handling for model load failures

