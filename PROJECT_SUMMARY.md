# OWASP LLM Security Demo - Project Summary

## Architecture Overview

**Full-stack security demonstration tool** detecting OWASP Top 10 LLM vulnerabilities using hybrid detection approach: pattern matching + perplexity analysis.

### Core Components

**1. Detection Engine (C++)**
- Forked `llama.cpp` with custom security detection logic
- **Hybrid detection**:
  - **Pattern-based** classification for 4 categories (LLM01/02/04/06)
  - **Perplexity-based** classification for LLM03 (Training Data Poisoning)
- Dual-mode operation:
  - `--skip_llm_generation`: Fast pattern matching only (milliseconds)
  - Full inference: Pattern + perplexity detection + LLM response generation
- Runtime configuration via JSON (`config/llm03_baseline.json`)
- Precompiled binaries for production deployment

**Detection Methods**
- **Pattern matching**: Keyword-based rules for prompt injection, insecure output, DoS, excessive agency
- **Perplexity analysis**: Statistical anomaly detection for poisoned/anomalous input text
  - Calculates token-level perplexity using llama.cpp
  - Threshold-based classification (configurable, default: 50.0)
  - Input normalization (removes trailing punctuation)

**2. API Layer (Python/Flask)**
- RESTful endpoints wrapping C++ detection binary
- Request validation and error handling
- Environment-based configuration
- Virtual environment for dependency isolation
- **Version**: 0.10.0

**3. Frontend (Node.js/Express)**
- Web interface for testing prompts
- Sample attack buttons for each OWASP category
- Real-time detection results display
- Responsive UI with dark blue theme
- Perplexity score display for LLM03 detections

**4. Model**
- Qwen 2.5 0.5B (quantized Q4_0, ~409MB)
- Small footprint for fast inference
- Required for LLM03 perplexity calculation
- Optional for pattern-based categories

## Deployment Infrastructure

**Containerization (Docker)**
- Single-stage Debian-based image
- Layer-optimized Dockerfile (dependencies before code)
- Precompiled binaries copied (no build in container)
- Non-root execution (`nobody` user)
- Healthcheck endpoint

**Orchestration**
- Azure Container Instances for cloud deployment
- Cloudflare Tunnel for HTTPS (no Azure costs)
- Entrypoint script manages multi-process startup (Flask + Node.js + Cloudflare)

**CI/CD (GitHub Actions)**
- Automated Docker builds on push
- Layer caching optimization (1min rebuild vs 5min full build)
- Automated deployment to Azure
- Model caching in workflow to avoid re-download

## Detection Implementation

**Pattern-Based Categories (Implemented: 4/10)**
- **LLM01**: Prompt Injection (keywords: ignore, bypass, override)
- **LLM02**: Insecure Output (SQL/XSS injection patterns)
- **LLM04**: Denial of Service (length-based detection, >1000 chars)
- **LLM06**: Excessive Agency (system prompt extraction attempts)

**Perplexity-Based Categories (Implemented: 1/10)**
- **LLM03**: Training Data Poisoning
  - Detection method: Statistical perplexity analysis on input prompts
  - Implementation: `perplexity_utils.cpp` calculates token-level negative log-likelihood
  - Threshold: 50.0 (empirically calibrated)
  - Normalizes input: strips trailing punctuation for consistent tokenization
  - Examples:
    - Nonsense text ("xzqw jumped mflkj") → perplexity 445.24 ✅ Detected
    - Semantic anomaly ("colorless green ideas") → perplexity 154.18 ✅ Detected
    - Logical inconsistency ("cat barked, dog meowed") → perplexity 64.23 ✅ Detected
    - Normal text ("quick brown fox") → perplexity 3.57 ❌ Safe

**Detection Logic**
- Stateless pattern matching in `category.cpp`
- Priority-ordered rules to avoid false positives
- Specific keyword refinement (e.g., "system instructions" vs generic "instructions")
- LLM03 only triggered if pattern-based detection returns "unknown"

## Testing & Validation

**Test Suite**
- Bash script with 37 test prompts across 5 categories
- JSON output for programmatic validation
- **Results: 36/37 passing (97.3% accuracy)**
  - LLM01: 13/14 (1 false positive: "ignore spam emails")
  - LLM02: 9/9 (100%)
  - LLM03: 6/6 (100%)
  - LLM04: 1/1 (100%)
  - LLM06: 9/9 (100%)
- Test execution:
  - Pattern categories: <100ms (no model required)
  - LLM03: ~20s per test (model loading + perplexity calculation)

**Performance**
- Pattern detection: <100ms in `--skip_llm_generation` mode
- LLM03 detection: ~18-20s (includes model load + inference)
- Full demo mode: ~2-3s with response generation

## Technical Stack

**Languages & Frameworks**
- C++17 (detection engine, perplexity calculation)
- Python 3.11 (Flask API)
- Node.js 20 (frontend)
- Bash (testing, deployment scripts)

**Libraries**
- llama.cpp (LLM inference)
- nlohmann/json (C++ JSON parsing)
- Flask (Python web framework)
- Express + EJS (Node.js templating)

**Infrastructure**
- Docker (containerization)
- Azure Container Instances (cloud hosting)
- Cloudflare Tunnel (HTTPS)
- GitHub Actions (CI/CD)

## Version Control & Release

**Semantic Versioning**
- Separate versioning for API and frontend
- Bash script for version bumping (`scripts/bump-version.sh`)
- Git tags: `api-vX.Y.Z` and `frontend-vX.Y.Z`
- Interactive confirmation before commit
- Current: API v0.10.0 (LLM03 release)

## Documentation

**Structure**
- Architecture diagrams (`docs/architecture.md`)
- OWASP category references (`docs/owasp-references.md`)
- Component-specific READMEs (API, frontend, Docker, llama.cpp)
- Testing methodology (`tests/TESTING.md`)
- Configuration guide (`config/llm03_baseline.json` with inline comments)

## Key Design Decisions

1. **Hybrid detection approach**: Pattern matching for speed + perplexity for statistical anomaly detection
2. **Perplexity on input prompts**: Detects poisoned/anomalous text before generation
3. **Runtime JSON config**: Threshold tuning without recompilation
4. **Input normalization**: Removes punctuation to prevent tokenization variance
5. **Precompiled binaries**: Avoid build complexity in Docker, faster deployments
6. **Dual-mode detection**: Flexibility for demo (with LLM) vs production (pattern only)
7. **Cloudflare Tunnel**: Free HTTPS without Azure networking costs
8. **Layer-optimized Docker**: Fast iteration during development (dependencies cached)

## Current State (February 2026)

- **5/10 OWASP categories implemented**
  - 4 pattern-based (LLM01/02/04/06)
  - 1 perplexity-based (LLM03)
- **36/37 tests passing (97.3% accuracy)**
- Functional demo deployed on Azure
- CI/CD pipeline operational
- **Next targets**: LLM05 (Supply Chain), LLM07 (Insecure Plugin)
- **Timeline**: 7/10 categories by March 2026

## Known Limitations

1. **Pattern detection**: Keyword-based, susceptible to evasion via paraphrasing
2. **LLM03 perplexity**:
   - Requires model load (~20s overhead per test)
   - Sensitive to tokenization (punctuation affects scores)
   - Threshold calibrated for Qwen 2.5 0.5B only
3. **False positives**: 1 known case (LLM01: benign "ignore" usage)
4. **Language**: English only
5. **Scope**: Educational/portfolio project, not production-grade security tool

## Lessons Learned

1. **Perplexity calculation**: Token-level analysis more robust than sentence-level
2. **Threshold calibration**: Requires empirical testing with diverse examples
3. **Preprocessing matters**: Punctuation normalization critical for consistency
4. **Testing isolation**: LLM03 tests must load model individually (no batch)
5. **JSON config**: Runtime configuration beats hardcoded thresholds for demos

