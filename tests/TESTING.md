# Testing

## Results (v3.0 - February 2026)

**36/37 passing (97.3%)**

| Category | Method | Malicious | Legitimate | Accuracy |
|----------|--------|-----------|------------|----------|
| LLM01 | Pattern | 7/7 | 4/5 | 11/12 (92%) |
| LLM02 | Pattern | 5/5 | 4/4 | 9/9 (100%) |
| LLM03 | Perplexity | 3/3 | 3/3 | 6/6 (100%) |
| LLM04 | Pattern | 1/1 | N/A | 1/1 (100%) |
| LLM06 | Pattern | 5/5 | 4/4 | 9/9 (100%) |

## Detection Methods

**Pattern-based (LLM01/02/04/06):**
- Keyword matching (case-insensitive)
- Priority-ordered checks (LLM01 before LLM06)
- Execution: <100ms per test

**Perplexity-based (LLM03):**
- Statistical anomaly detection on input prompts
- Threshold: 50.0 (normal text: 3-27, anomalous: 60-450)
- Normalizes input (removes trailing punctuation)
- Execution: ~20s per test (model load)
- Config: `config/llm03_baseline.json`

## Running Tests
```bash
./tests/test_owasp.sh           # All categories (~2min)
./tests/test_owasp.sh llm01     # Single category
```

## Known Limitations

1. **False positive (1/37):** "ignore spam emails" triggers LLM01 (keyword without context)
2. **Pattern evasion:** Paraphrasing can bypass keyword detection
3. **LLM03 model dependency:** Requires 20s model load per test
4. **Threshold calibration:** LLM03 tuned for Qwen 2.5 0.5B only

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

