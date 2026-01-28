# OWASP LLM Security Demo - Docker Image
# Strategy: Single-stage with precompiled binary (fast builds)

FROM debian:12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Cloudflare Tunnel
RUN curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    -o /usr/local/bin/cloudflared && \
    chmod +x /usr/local/bin/cloudflared

# Create app directory structure
WORKDIR /app

# Copy binaries and ALL shared libraries
RUN mkdir -p /app/binary
COPY --chown=nobody:nogroup ./llama.cpp/build/bin/owasp-llm-tool /app/binary/
COPY --chown=nobody:nogroup ./llama.cpp/build/bin/llama-server /app/binary/
COPY --chown=nobody:nogroup ./llama.cpp/build/lib/*.so* /app/binary/

# Set library path for runtime
ENV LD_LIBRARY_PATH=/app/binary:$LD_LIBRARY_PATH

# Copy model (409MB)
RUN mkdir -p /app/models
#COPY --chown=nobody:nogroup ./llama.cpp/models/qwen2.5-0.5b-instruct-q4_0.gguf /app/models/
COPY --chown=nobody:nogroup ./models/qwen2.5-0.5b-instruct-q4_0.gguf /app/models/


# Copy API code
COPY --chown=nobody:nogroup ./api /app/api

# Copy frontend code
COPY --chown=nobody:nogroup ./frontend /app/frontend

# Setup Python virtual environment and install dependencies
RUN cd /app/api && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Install Node dependencies
RUN cd /app/frontend && \
    npm ci --only=production && \
    npm cache clean --force

# Create .env file for container paths
RUN echo "BINARY_PATH=/app/binary/owasp-llm-tool" > /app/api/.env && \
    echo "MODEL_PATH=/app/models/qwen2.5-0.5b-instruct-q4_0.gguf" >> /app/api/.env && \
    echo "FLASK_ENV=production" >> /app/api/.env && \
    echo "FLASK_PORT=5000" >> /app/api/.env && \
    echo "MAX_PROMPT_LENGTH=5000" >> /app/api/.env && \
    echo "GENERATION_TIMEOUT=60" >> /app/api/.env

# Make binary executable
RUN chmod +x /app/binary/owasp-llm-tool

# Copy entrypoint script
COPY --chown=nobody:nogroup ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose frontend port (Node.js)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Run as non-root user
USER nobody

# Start both services
ENTRYPOINT ["/entrypoint.sh"]

