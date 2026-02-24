# OWASP LLM Security Demo - Project Summary

## Architecture Overview

**Full-stack security demonstration tool** detecting OWASP Top 10 LLM vulnerabilities using a hybrid detection approach: pattern matching, perplexity analysis, dual-path scoring, and session-aware multi-detector scoring.

### Core Components

**1. Detection Engine (C++)**
- Forked `llama.cpp` with custom security detection logic
- **Hybrid detection**:
  - **Pattern-based** classification for LLM01/02/04/05/06
  - **Perplexity-based** classification for LLM03 (Training Data Poisoning)
- Dual-mode operation:
  - `--skip_llm_generation`: Fast pattern matching only (milliseconds)
  - Full inference: Pattern + perplexity detection + LLM response generation
- Runtime configuration via JSON (`config/llm03_baseline.json`)
- Precompiled binaries for production deployment

**Detection Methods**
- **Pattern matching**: Keyword-based rules for prompt injection, insecure output, DoS, supply chain, excessive agency
- **Perplexity analysis**: Statistical anomaly detection for poisoned/anomalous input text
  - Calculates token-level perplexity using llama.cpp
  - Threshold-based classification (configurable, default: 50.0)
  - Input normalization (removes trailing punctuation)
- **Dual-path scoring** (LLM09): Combines citation fraud detection and statistical hallucination signals across 5 sub-detectors (fake_citation, authority_claim, precision_abuse, hedging_absence, source_unverifiability)
- **Session-aware scoring** (LLM10): IP-based session store (TTL 10 min) with 3 sub-detectors — extraction_intent (45%), query_similarity (45%), rate_anomaly (10%). Responses blocked at score ≥ 0.85

**2. API Layer (Python/Flask)**
- RESTful endpoints wrapping C++ detection binary
- Request validation and error handling
- Environment-based configuration
- Virtual environment for dependency isolation
- In-memory session store for LLM10 (thread-safe, IP-keyed, TTL 10 min)
- **Version**: 0.13.0

**3. Frontend (Node.js/Express)**
- Web interface for testing prompts
- Sample attack buttons for each OWASP category
- Real-time detection results display
- Responsive UI with dark blue theme
- Perplexity score display for LLM03 detections
- Session-aware detector grid with score bars for LLM10
- **Version**: 0.12.0

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

**Pattern-Based Categories**
- **LLM01**: Prompt Injection (keywords: ignore, bypass, override)
- **LLM02**: Insecure Output (SQL/XSS injection patterns)
- **LLM04**: Denial of Service (length-based detection, >1000 chars)
- **LLM05**: Supply Chain (model swap/load patterns)
- **LLM06**: Excessive Agency (system prompt extraction attempts)

**Perplexity-Based Categories**
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

**Plugin-Based Categories**
- **LLM07**: Insecure Plugin Design
  - Live SQL query execution against Northwind SQLite DB
  - Unsafe mode: no filtering
  - Safe mode: keyword blocklist (intentionally bypassable via UNION injection)

**Python Scoring Categories**
- **LLM09**: Overreliance / Misinformation
  - Dual-path scoring: citation fraud path + hallucination signal path
  - 5 sub-detectors: fake_citation, authority_claim, precision_abuse, hedging_absence, source_unverifiability
  - Verdicts: high (≥0.60), medium (≥0.30), low (<0.30)

- **LLM10**: Model Theft
  - Session-aware scoring via IP-keyed in-memory store (TTL 10 min, thread-safe)
  - 3 sub-detectors: extraction_intent (45%), query_similarity (45%), rate_anomaly (10%)
  - Verdicts: high (≥0.70), medium (≥0.24), low (<0.24)
  - Response blocked at final score ≥ 0.85

**Detection Logic**
- Stateless pattern matching in `category.cpp`
- Priority-ordered rules to avoid false positives
- Specific keyword refinement (e.g., "system instructions" vs generic "instructions")
- LLM03 only triggered if pattern-based detection returns "unknown"
- LLM09/LLM10 handled entirely in Python (Flask routes), independent of C++ binary

## Testing & Validation

**Test Suite**
- `test_owasp.sh`: Bash script, 53 test prompts across 7 categories (binary-based)
- `test_llm10.sh`: Bash script, 18 test prompts via HTTP (Flask-based, session-aware)
- `test_plugin.sh`: HTTP tests for LLM07 SQLite plugin
- **Results: 70/71 passing (98.6% accuracy)**
  - LLM01: 11/12 (1 known false positive: "ignore spam emails")
  - LLM02: 9/9 (100%)
  - LLM03: 6/6 (100%)
  - LLM04: 1/1 (100%)
  - LLM05: 7/7 (100%)
  - LLM06: 9/9 (100%)
  - LLM07: 6/6 (100%)
  - LLM09: 9/9 (100%)
  - LLM10: 18/18 (100%)

**Performance**
- Pattern detection: <100ms in `--skip_llm_generation` mode
- LLM03 detection: ~18-20s (includes model load + inference)
- LLM09/LLM10 detection: <200ms (pure Python, no model required)
- Full demo mode: ~2-3s with response generation

## Technical Stack

**Languages & Frameworks**
- C++17 (detection engine, perplexity calculation)
- Python 3.11 (Flask API, LLM09/LLM10 detectors)
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
- Current: API v0.13.0 / Frontend v0.12.0
- Project tag: `v1.0.0` (all 9 implemented categories complete)

## Documentation

**Structure**
- Architecture diagrams (`docs/architecture.md`)
- OWASP category references (`docs/owasp-references.md`)
- Component-specific READMEs (API, frontend, Docker, llama.cpp)
- Testing methodology (`tests/TESTING.md`)
- Configuration guide (`config/llm03_baseline.json` with inline comments)

## Key Design Decisions

1. **Hybrid detection approach**: Pattern matching for speed + perplexity for statistical anomaly + Python scoring for behavioral/session analysis
2. **Perplexity on input prompts**: Detects poisoned/anomalous text before generation
3. **Runtime JSON config**: Threshold tuning without recompilation
4. **Input normalization**: Removes punctuation to prevent tokenization variance
5. **Precompiled binaries**: Avoid build complexity in Docker, faster deployments
6. **Dual-mode detection**: Flexibility for demo (with LLM) vs production (pattern only)
7. **Session store in-memory**: Simple, zero-dependency, sufficient for demo scope
8. **Response blocking at 0.85**: Conservative threshold to minimize false positives on LLM10
9. **Cloudflare Tunnel**: Free HTTPS without Azure networking costs
10. **Layer-optimized Docker**: Fast iteration during development (dependencies cached)

## Current State (February 2026)

- **9/10 OWASP categories implemented**
  - 5 pattern-based (LLM01/02/04/05/06)
  - 1 perplexity-based (LLM03)
  - 1 plugin-based (LLM07)
  - 1 dual-path scoring (LLM09)
  - 1 session-aware scoring (LLM10)
  - LLM08 skipped (duplicate of LLM06 in OWASP spec)
- **70/71 tests passing (98.6% accuracy)**
- Functional demo deployed on Azure
- CI/CD pipeline operational
- Project tagged `v1.0.0`

## Known Limitations

1. **Pattern detection**: Keyword-based, susceptible to evasion via paraphrasing
2. **LLM03 perplexity**:
   - Requires model load (~20s overhead per test)
   - Sensitive to tokenization (punctuation affects scores)
   - Threshold calibrated for Qwen 2.5 0.5B only
3. **LLM09 dual-path scoring**: Heuristic-based, no external source verification
4. **LLM10 session store**: In-memory only, resets on restart; IP-based attribution is trivially bypassable with proxies
5. **False positives**: 1 known case (LLM01: benign "ignore" usage)
6. **Language**: English only
7. **Scope**: Educational/portfolio project, not production-grade security tool


