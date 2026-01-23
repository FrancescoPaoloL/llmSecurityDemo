# OWASP LLM Security Demo

A demo tool for detecting LLM vulnerabilities based on the OWASP Top 10 for LLMs.

## What it does

You enter a prompt, the tool:
1. Sends it to a local LLM (Qwen 0.5B)
2. Analyzes the prompt for security issues
3. Returns the OWASP category detected

## Quick Start

### Local (Docker)
```bash
cd docker
sudo docker-compose build
sudo docker-compose up -d

# Open browser
http://localhost:3000
```

### Docker Hub
```bash
docker pull francescopaololezza/owasp-llm-demo:v3
docker run -d -p 3000:3000 -p 5000:5000 -p 8081:8081 francescopaololezza/owasp-llm-demo:v3

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

| Category | Name | Status |
|----------|------|--------|
| LLM01 | Prompt Injection | Done |
| LLM02 | Sensitive Data Exposure | Done |
| LLM03 | Training Data Poisoning | TODO |
| LLM04 | Model Denial of Service | TODO |
| LLM05 | Supply Chain Vulnerabilities | TODO |
| LLM06 | Excessive Agency | Done |
| LLM07 | Insecure Plugin Design | TODO |
| LLM08 | Excessive Agency | TODO |
| LLM09 | Overreliance | TODO |
| LLM10 | Model Theft | TODO |

## Project Structure
```
├── api/          # Flask API
├── docker/       # Docker configuration
├── docs/         # Documentation
├── frontend/     # Node.js + EJS UI
└── infra/azure/  # Terraform for Azure deployment
```

## C++ Source Code

The owasp-llm-tool is maintained in a fork of llama.cpp:

https://github.com/FrancescoPaoloL/llama.cpp/tree/feature/owasp-llm-tool/examples/owasp-llm-tool

## References

- [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)

## License

MIT

