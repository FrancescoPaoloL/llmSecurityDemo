# OWASP LLM Security Demo

[![Docker Build](https://github.com/FrancescoPaoloL/llmSecurityDemo/actions/workflows/docker-build.yml/badge.svg)](https://github.com/FrancescoPaoloL/llmSecurityDemo/actions)
![Tests](https://img.shields.io/badge/tests-70%2F71%20passing-brightgreen)
![Categories](https://img.shields.io/badge/OWASP%20categories-9%2F10-blue)

A detection tool for OWASP Top 10 LLM vulnerabilities using pattern matching, perplexity-based analysis, and session-aware scoring.

> **Learning/portfolio project — not production security software.** Detection is heuristic-based (keyword patterns, perplexity thresholds, in-memory session store), all known limitations are listed below.

## What it does

You enter a prompt, the tool:

1. Analyzes it for OWASP LLM vulnerabilities using **pattern matching** (LLM01/02/04/05/06), **perplexity analysis** (LLM03), **dual-path scoring** (LLM09), and **session-aware multi-detector scoring** (LLM10)
2. Sends it to a local LLM (Qwen 0.5B) for generation
3. Returns the detected OWASP category and LLM response

The **Plugin Demo (LLM07)** section lets you run SQL queries directly against a SQLite database (Northwind) in unsafe or safe mode, demonstrating how naive keyword-based protection can be bypassed.

The **Model Theft Demo (LLM10)** section detects extraction attempts through session-aware analysis across three sub-detectors. Responses are blocked when the confidence score reaches ≥ 0.85.

**Test results on internal suite**: 70/71 passing (98.6%) — note that the test suite is authored alongside the detection rules, so this measures internal consistency, not generalization. See [tests/TESTING.md](tests/TESTING.md).

**Generation**: uses Qwen 0.5B via llama-server with the Qwen instruction format and a system prompt.

## Quick Start

### Local (Docker Compose)

```
cd docker
docker-compose up -d
# Open browser
http://localhost:3000
```

### Docker Hub

```
docker pull francescopaololezza/owasp-llm-demo:main
docker run -d -p 3000:3000 francescopaololezza/owasp-llm-demo:main
# Open browser
http://localhost:3000
```

### Azure

See [infra/azure/README.md](infra/azure/README.md) for Terraform deployment.

## Architecture

```
Browser (:3000) → Node.js → Flask API (:5000) → llama-server (:8081)
                                             → owasp-llm-tool (detection)
                                             → SQLite plugin (LLM07)
                                             → session store (LLM10)
```

See [docs/architecture.md](docs/architecture.md) for details.

## Detected Vulnerabilities

| Category | Name | Detection Method | Status | Tests passing |
| --- | --- | --- | --- | --- |
| LLM01 | Prompt Injection | Pattern matching | ✅ Done | 11/12 |
| LLM02 | Insecure Output Handling | Pattern matching | ✅ Done | 9/9 |
| LLM03 | Training Data Poisoning | Perplexity analysis | ✅ Done | 6/6 |
| LLM04 | Model Denial of Service | Pattern matching | ✅ Done | 1/1 |
| LLM05 | Supply Chain Vulnerabilities | Pattern matching | ✅ Done | 7/7 |
| LLM06 | Excessive Agency | Pattern matching | ✅ Done | 9/9 |
| LLM07 | Insecure Plugin Design | SQLite plugin + HTTP tests | ✅ Done | 6/6 |
| LLM08 | Excessive Agency | - | ❌ Duplicate | - |
| LLM09 | Overreliance / Misinformation | Dual-path scoring (5 sub-detectors) | ✅ Done | 9/9 |
| LLM10 | Model Theft | Session-aware scoring (3 sub-detectors) | ✅ Done | 18/18 |

**Overall: 9/10 categories implemented | 70/71 internal tests passing**

**Detection Methods:**

* **Pattern matching** (LLM01/02/04/05/06): keyword-based rules, <100ms
* **Perplexity analysis** (LLM03): statistical anomaly detection on input prompts
  + High perplexity (>50.0) = anomalous/poisoned text
  + Example: "xzqw jumped mflkj" → perplexity 445.24 ✓ | "quick brown fox" → 3.57 ✗
  + Threshold: configurable via `config/llm03_baseline.json`
* **SQLite plugin** (LLM07): live query execution against Northwind DB with intentionally bypassable safe mode
* **Dual-path scoring** (LLM09): combines citation fraud detection and statistical hallucination signals across 5 sub-detectors (fake_citation, authority_claim, precision_abuse, hedging_absence, source_unverifiability)
* **Session-aware scoring** (LLM10): IP-based session store (TTL 10 min) with 3 sub-detectors — extraction_intent (45%), query_similarity (45%), rate_anomaly (10%). Responses blocked at score ≥ 0.85

See [tests/TESTING.md](tests/TESTING.md) for detailed test results.

## Testing

```
./tests/test_owasp.sh           # All categories (pattern + perplexity) — 52/53
./tests/test_owasp.sh llm03     # Specific category (loads model)
./tests/test_owasp.sh llm09     # Overreliance / misinformation
./tests/test_llm10.sh           # Model theft — requires Flask running — 18/18
./tests/test_plugin.sh          # Plugin tests — requires Flask running
```

**Note:** LLM03 tests require model loading (~20s per test). Other categories use pattern matching only. `test_llm10.sh` and `test_plugin.sh` require Flask API running on port 5000.

## Project Structure

```
├── api/          # Flask API (v0.13.0)
├── config/       # Runtime configuration (LLM03 threshold)
├── data/         # Northwind SQLite database (LLM07 demo)
├── docker/       # Docker configuration
├── docs/         # Documentation
├── frontend/     # Node.js + EJS UI (v0.12.0)
├── infra/azure/  # Terraform for Azure deployment
├── llama.cpp/    # Pre-built binaries + detection tools
└── tests/        # Test suite (71 test cases)
```

## C++ Source Code

The `owasp-llm-tool` is maintained in a fork of llama.cpp:

<https://github.com/FrancescoPaoloL/llama.cpp/tree/feature/owasp-llm-tool/examples/owasp-llm-tool>

Features:

* Pattern-based detection for LLM01/02/04/05/06
* Perplexity calculation for LLM03
* JSON config support (nlohmann/json)
* Prompt normalization

## Known Limitations

* **Pattern-based detection** (LLM01/02/04/05/06): keyword matching, not ML-based
* **Perplexity detection** (LLM03): requires model load, sensitive to tokenization
* **Plugin safe mode** (LLM07): intentionally bypassable — demonstrates the vulnerability
* **LLM09 dual-path scoring**: heuristic-based, no external source verification
* **LLM10 session store**: in-memory only, resets on restart; IP-based attribution is trivially bypassable with proxies
* **Test suite is internal**: 70/71 passing measures consistency against rules I wrote myself, not generalization to unseen attacks. 1 known false positive (LLM01: "ignore spam emails").
* **English only**
* **CI/CD pipeline does not run tests automatically**: the `owasp-llm-tool` binary is cross-compiled locally from the llama.cpp fork and committed pre-built. Tests must be run manually before pushing (`./tests/test_owasp.sh`).

## References

* [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
* [llama.cpp](https://github.com/ggerganov/llama.cpp)
* [Perplexity Explained](https://huggingface.co/docs/transformers/perplexity)
* [Northwind SQLite](https://github.com/jpwhite3/northwind-SQLite3)

## License

MIT


## Connect with me

[LinkedIn](https://www.linkedin.com/in/francescopl/) · [Kaggle](https://www.kaggle.com/francescopaolol)


