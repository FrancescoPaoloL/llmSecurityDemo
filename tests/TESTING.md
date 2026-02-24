# Testing

## Results (v4.0 - February 2026)

**70/71 passing (98.6%)**

| Category | Method | Malicious | Legitimate | Accuracy |
|----------|--------|-----------|------------|----------|
| LLM01 | Pattern | 7/7 | 4/5 | 11/12 (92%) |
| LLM02 | Pattern | 5/5 | 4/4 | 9/9 (100%) |
| LLM03 | Perplexity | 3/3 | 3/3 | 6/6 (100%) |
| LLM04 | Pattern | 1/1 | N/A | 1/1 (100%) |
| LLM05 | Pattern | 5/5 | 2/2 | 7/7 (100%) |
| LLM06 | Pattern | 5/5 | 4/4 | 9/9 (100%) |
| LLM07 | Plugin | 3/3 | 3/3 | 6/6 (100%) |
| LLM09 | Dual-path | 5/5 | 4/4 | 9/9 (100%) |
| LLM10 | Session-aware | 9/9 | 9/9 | 18/18 (100%) |

**Overall: 70/71 (98.6%) — 1 known false positive (LLM01)**

## Detection Methods

**Pattern-based (LLM01/02/04/05/06):**
- Keyword matching (case-insensitive)
- Priority-ordered checks (LLM01 before LLM06)
- Execution: <100ms per test

**Perplexity-based (LLM03):**
- Statistical anomaly detection on input prompts
- Threshold: 50.0 (normal text: 3-27, anomalous: 60-450)
- Normalizes input (removes trailing punctuation)
- Execution: ~20s per test (model load)
- Config: `config/llm03_baseline.json`

**Plugin-based (LLM07):**
- Live SQL execution against Northwind SQLite DB
- Tests both unsafe mode (no filtering) and safe mode (keyword blocklist)
- Safe mode intentionally bypassable via UNION injection — demonstrates the vulnerability
- Requires Flask running on port 5000

**Dual-path scoring (LLM09):**
- Citation fraud path + hallucination signal path
- 5 sub-detectors: fake_citation, authority_claim, precision_abuse, hedging_absence, source_unverifiability
- Verdicts: high (≥0.60), medium (≥0.30), low (<0.30)
- Execution: <200ms per test (pure Python, no model)
- Requires Flask running on port 5000

**Session-aware scoring (LLM10):**
- IP-based session store (TTL 10 min, thread-safe)
- 3 sub-detectors: extraction_intent (45%), query_similarity (45%), rate_anomaly (10%)
- Verdicts: high (≥0.70), medium (≥0.24), low (<0.24)
- Response blocked at score ≥ 0.85
- Test runner uses `X-Forwarded-For` to isolate malicious/legitimate sessions
- Execution: <200ms per test (pure Python, no model)
- Requires Flask running on port 5000

## Running Tests

```bash
./tests/test_owasp.sh           # All categories (pattern + perplexity) — ~2min
./tests/test_owasp.sh llm01     # Single category
./tests/test_owasp.sh llm09     # Overreliance / misinformation
./tests/test_plugin.sh          # LLM07 plugin — requires Flask running
./tests/test_llm10.sh           # LLM10 model theft — requires Flask running
```

## Known Limitations

1. **False positive (1/71):** "ignore spam emails" triggers LLM01 (keyword without context)
2. **Pattern evasion:** Paraphrasing can bypass keyword detection
3. **LLM03 model dependency:** Requires 20s model load per test
4. **LLM03 threshold calibration:** Tuned for Qwen 2.5 0.5B only
5. **LLM09 heuristic-based:** No external source verification
6. **LLM10 session store:** In-memory only, resets on restart; IP attribution bypassable with proxies

## Configuration

Adjust LLM03 threshold without rebuild:

```json
// config/llm03_baseline.json
{
  "models": {
    "default": {
      "threshold": 50.0  // Increase = fewer detections
    }
  }
}
```

