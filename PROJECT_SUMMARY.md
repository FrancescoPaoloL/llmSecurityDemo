# OWASP LLM Security Demo - Project Summary

## Architecture Overview

**Full-stack security demonstration tool** detecting OWASP Top 10 LLM vulnerabilities using hybrid detection approach.

### Core Components

**1. Detection Engine (C++)**
- Forked `llama.cpp` with custom security detection logic
- Pattern-based classification for 4 OWASP categories (LLM01/02/04/06)
- Dual-mode operation:
  - `--detect-only`: Fast pattern matching (milliseconds)
  - Full inference: Pattern detection + LLM response generation (demo mode)
- Precompiled binaries for production deployment

**2. API Layer (Python/Flask)**
- RESTful endpoints wrapping C++ detection binary
- Request validation and error handling
- Environment-based configuration
- Virtual environment for dependency isolation

**3. Frontend (Node.js/Express)**
- Web interface for testing prompts
- Sample attack buttons for each OWASP category
- Real-time detection results display
- Responsive UI with dark blue theme

**4. Model**
- Qwen 2.5 0.5B (quantized Q4_0, ~409MB)
- Small footprint for fast inference
- Suitable for edge deployment

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
- **LLM04**: Denial of Service (length-based detection)
- **LLM06**: Excessive Agency (system prompt extraction attempts)

**Detection Logic**
- Stateless pattern matching in `category.cpp`
- Priority-ordered rules to avoid false positives
- Specific keyword refinement (e.g., "system instructions" vs generic "instructions")

## Testing & Validation

**Test Suite**
- Bash script with 16 test prompts (4 per category)
- JSON output for programmatic validation
- 100% accuracy on implemented categories
- Sample attack prompts for user testing

**Performance**
- Optimized from 89s → 0.3s generation time
- Detection: <100ms in `--detect-only` mode
- Full demo: ~2-3s with response generation

## Version Control & Release

**Semantic Versioning**
- Separate versioning for API and frontend
- Bash script for version bumping (`scripts/bump-version.sh`)
- Git tags: `api-vX.Y.Z` and `frontend-vX.Y.Z`
- Interactive confirmation before commit

## Documentation

**Structure**
- Architecture diagrams (`docs/architecture.md`)
- OWASP category references (`docs/owasp-references.md`)
- Component-specific READMEs (API, frontend, Docker, llama.cpp)
- Testing methodology (`tests/TESTING.md`)

## Key Design Decisions

1. **Pattern matching over ML-based detection**: Fast, deterministic, production-ready for MVP
2. **Precompiled binaries**: Avoid build complexity in Docker, faster deployments
3. **Dual-mode detection**: Flexibility for demo (with LLM) vs production (pattern only)
4. **Cloudflare Tunnel**: Free HTTPS without Azure networking costs
5. **Layer-optimized Docker**: Fast iteration during development (dependencies cached)

## Current State

- 4/10 OWASP categories implemented with pattern detection
- Functional demo deployed on Azure
- CI/CD pipeline operational
- Ready for expansion to remaining categories (LLM03/05/07/08/09/10)

