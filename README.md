# OWASP LLM Security Demo

[![Docker Build](https://github.com/FrancescoPaoloL/llmSecurityDemo/actions/workflows/docker-build.yml/badge.svg)](https://github.com/FrancescoPaoloL/llmSecurityDemo/actions)

A demo tool for detecting LLM vulnerabilities based on the OWASP Top 10 for LLMs.

## What it does

You enter a prompt, the tool:
1. Analyzes it for OWASP LLM vulnerabilities using pattern matching
2. Sends it to a local LLM (Qwen 0.5B)
3. Returns the OWASP category detected and LLM response

**Detection accuracy**: 84% on test suite (see [tests/TESTING.md](tests/TESTING.md))

**Response quality**: Uses Qwen instruction format with system prompt for coherent, accurate answers. Examples: "What is 2+2?" returns "2 + 2 equals 4", security prompts receive safe, appropriate responses.

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
```

See [docs/architecture.md](docs/architecture.md) for details.

## Detected Vulnerabilities

| Category | Name | Status | Accuracy |
|----------|------|--------|----------|
| LLM01 | Prompt Injection | Done | 75% |
| LLM02 | Insecure Output Handling | Done | 89% |
| LLM03 | Training Data Poisoning | TODO | - |
| LLM04 | Model Denial of Service | Done | 100% |
| LLM05 | Supply Chain Vulnerabilities | TODO | - |
| LLM06 | Excessive Agency | Done | 100% |
| LLM07 | Insecure Plugin Design | TODO | - |
| LLM08 | Excessive Agency | TODO | - |
| LLM09 | Overreliance | TODO | - |
| LLM10 | Model Theft | TODO | - |

Overall: 4/10 categories, 84% average accuracy. See [tests/TESTING.md](tests/TESTING.md) for details.

## Testing
```bash
./tests/test_owasp.sh           # All categories
./tests/test_owasp.sh llm01     # Specific category
```

## Project Structure
```
├── api/          # Flask API
├── docker/       # Docker configuration
├── docs/         # Documentation
├── frontend/     # Node.js + EJS UI
├── infra/azure/  # Terraform for Azure deployment
├── llama.cpp/    # Pre-built binaries
└── tests/        # Test suite
```

## C++ Source Code

The owasp-llm-tool is maintained in a fork of llama.cpp:

https://github.com/FrancescoPaoloL/llama.cpp/tree/feature/owasp-llm-tool/examples/owasp-llm-tool

## Known Limitations

- Pattern-based detection (keyword matching, not ML)
- 84% accuracy with known false positives/negatives
- English only
- Basic heuristics

This is a learning project, not production security software.

## References

- [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)

## License

MIT
