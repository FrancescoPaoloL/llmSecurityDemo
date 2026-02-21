# OWASP LLM Security Demo

[![Docker Build](https://github.com/FrancescoPaoloL/llmSecurityDemo/actions/workflows/docker-build.yml/badge.svg)](https://github.com/FrancescoPaoloL/llmSecurityDemo/actions)
[![Tests](https://img.shields.io/badge/tests-49%2F50%20passing-brightgreen)]()
[![Categories](https://img.shields.io/badge/OWASP%20categories-7%2F10-blue)]()

A detection tool for OWASP Top 10 LLM vulnerabilities using pattern matching and perplexity-based analysis.

## What it does

You enter a prompt, the tool:
1. Analyzes it for OWASP LLM vulnerabilities using **pattern matching** (LLM01/02/04/05/06) and **perplexity analysis** (LLM03)
2. Sends it to a local LLM (Qwen 0.5B) for generation
3. Returns the detected OWASP category and LLM response

The **Plugin Demo (LLM07)** section lets you run SQL queries directly against a SQLite database (Northwind) in unsafe or safe mode, demonstrating how naive keyword-based protection can be bypassed.

**Detection accuracy**: 98% on test suite (49/50 tests passing) — see [tests/TESTING.md](tests/TESTING.md)

**Response quality**: Uses Qwen instruction format with system prompt for coherent, accurate answers.

## Quick Start

### Local (Docker Compose)
```bash
cd docker
docker-compose up -d
# Open browser
http://localhost:3000
```

### Docker Hub
```bash
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
```

See [docs/architecture.md](docs/architecture.md) for details.

## Detected Vulnerabilities

| Category | Name | Detection Method | Status | Accuracy |
|----------|------|------------------|--------|----------|
| LLM01 | Prompt Injection | Pattern matching | ✅ Done | 92% (11/12) |
| LLM02 | Insecure Output Handling | Pattern matching | ✅ Done | 100% (9/9) |
| LLM03 | Training Data Poisoning | Perplexity analysis | ✅ Done | 100% (6/6) |
| LLM04 | Model Denial of Service | Pattern matching | ✅ Done | 100% (1/1) |
| LLM05 | Supply Chain Vulnerabilities | Pattern matching | ✅ Done | 100% (7/7) |
| LLM06 | Excessive Agency | Pattern matching | ✅ Done | 100% (9/9) |
| LLM07 | Insecure Plugin Design | SQLite plugin + HTTP tests | ✅ Done | 100% (6/6) |
| LLM08 | Excessive Agency | - | ❌ Duplicate | - |
| LLM09 | Overreliance | - | 🔜 Future | - |
| LLM10 | Model Theft | - | 🔜 Future | - |

**Overall: 7/10 categories implemented | 49/50 tests passing (98%)**

**Detection Methods:**
- **Pattern matching** (LLM01/02/04/05/06): Keyword-based rules, <100ms
- **Perplexity analysis** (LLM03): Statistical anomaly detection on input prompts
  - High perplexity (>50.0) = anomalous/poisoned text
  - Example: "xzqw jumped mflkj" → perplexity 445.24 ✓ | "quick brown fox" → 3.57 ✗
  - Threshold: configurable via `config/llm03_baseline.json`
- **SQLite plugin** (LLM07): Live query execution against Northwind DB with intentionally bypassable safe mode

See [tests/TESTING.md](tests/TESTING.md) for detailed test results.

## Testing
```bash
./tests/test_owasp.sh           # All categories (pattern + perplexity)
./tests/test_owasp.sh llm03     # Specific category (loads model)
./tests/test_plugin.sh          # Plugin tests - requires Flask running
```

**Note:** LLM03 tests require model loading (~20s per test). Other categories use pattern matching only. Plugin tests require Flask API running on port 5000.

## Project Structure
```
├── api/          # Flask API (v0.11.2)
├── config/       # Runtime configuration (LLM03 threshold)
├── data/         # Northwind SQLite database (LLM07 demo)
├── docker/       # Docker configuration
├── docs/         # Documentation
├── frontend/     # Node.js + EJS UI (v0.10.3)
├── infra/azure/  # Terraform for Azure deployment
├── llama.cpp/    # Pre-built binaries + detection tools
└── tests/        # Test suite (50 test cases)
```

## C++ Source Code

The `owasp-llm-tool` is maintained in a fork of llama.cpp:

https://github.com/FrancescoPaoloL/llama.cpp/tree/feature/owasp-llm-tool/examples/owasp-llm-tool

Features:
- Pattern-based detection for LLM01/02/04/05/06
- Perplexity calculation for LLM03
- JSON config support (nlohmann/json)
- Prompt normalization

## Known Limitations

- **Pattern-based detection** (LLM01/02/04/05/06): keyword matching, not ML-based
- **Perplexity detection** (LLM03): requires model load, sensitive to tokenization
- **Plugin safe mode** (LLM07): intentionally bypassable — demonstrates the vulnerability
- **98% accuracy** with 1 known false positive (LLM01: "ignore spam emails")
- **English only**
- **Basic heuristics** — this is a learning/portfolio project, not production security software

## References

- [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Perplexity Explained](https://huggingface.co/docs/transformers/perplexity)
- [Northwind SQLite](https://github.com/jpwhite3/northwind-SQLite3)

## License

MIT

