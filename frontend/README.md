# Frontend

Node.js + Express server with EJS templates.

## Setup

```bash
cd frontend
npm install
npm start
```

Opens at http://localhost:3000

## Structure

| File | Purpose |
|------|---------|
| app.js | Express server, proxies to Flask API |
| views/index.ejs | HTML template |
| public/css/style.css | Styles |
| public/js/form-handler.js | Form logic, API calls |

## Flow

```
User → form-handler.js → app.js → Flask API :5000
```

## API Proxies

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/test` | POST | Main vulnerability detection (LLM01–LLM06, LLM09, LLM02:2025, LLM06:2025) |
| `/api/plugin/query` | POST | SQLite plugin demo (LLM07) |
| `/api/llm10` | POST | Model Theft detection (LLM10, session-aware) |
| `/api/version` | GET | API version info |

## LLM10 Fields

`POST /api/llm10` accepts:

```json
{
  "prompt": "string",
  "max_tokens": 50,
  "embedding_requested": false,
  "logprobs_requested": false
}
```

Response includes `verdict` (low/medium/high), `score`, per-detector breakdown, session info, and `response` (null if blocked at score ≥ 0.85).

