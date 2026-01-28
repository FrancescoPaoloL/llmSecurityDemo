#!/bin/bash
set -e

echo "Starting OWASP LLM Security Demo"

# Set OpenMP threads for performance
export OMP_NUM_THREADS=12
export LD_LIBRARY_PATH=/app/binary:$LD_LIBRARY_PATH

# Start llama-server first (for inference)
echo "Starting llama-server on port 8081..."
NPROC=$(nproc)
echo "   Available CPUs: $NPROC"
echo "   OpenMP threads: $OMP_NUM_THREADS"

/app/binary/llama-server \
  -m /app/models/qwen2.5-0.5b-instruct-q4_0.gguf \
 --host 0.0.0.0 \
  --port 8081 \
  -c 512 \
  -n 50 \
  -t $NPROC \
  -tb $NPROC \
  --parallel 1 \
  --log-disable &
LLAMA_PID=$!

echo "Waiting for llama-server..."
for i in {1..30}; do
    if curl -s http://localhost:8081/health > /dev/null 2>&1; then
        echo "llama-server ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "llama-server failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

echo "Starting Flask API on port 5000..."
cd /app/api
. venv/bin/activate
python3 server.py &
FLASK_PID=$!

echo "Waiting for Flask API..."
for i in {1..30}; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "Flask API ready!"
        break
    fi
    sleep 1
done

echo "Starting Node.js frontend on port 3000..."
cd /app/frontend
node main.js &
FRONTEND_PID=$!

sleep 3

echo "Starting Cloudflare Tunnel..."
cloudflared tunnel --url http://localhost:3000 --no-autoupdate > /tmp/tunnel.log 2>&1 &
TUNNEL_PID=$!

# Wait and extract tunnel URL
sleep 5
TUNNEL_URL=$(grep -Eo 'https://[a-z-]+\.trycloudflare\.com' /tmp/tunnel.log | head -1)


if [ -n "$TUNNEL_URL" ]; then
    echo ""
    echo "=========================================="
    echo "HTTPS Tunnel Active!"
    echo "URL: $TUNNEL_URL"
    echo "=========================================="
    echo ""
else
    echo "Warning: Could not detect tunnel URL, check /tmp/tunnel.log"
fi

# Cleanup on exit
trap "kill $LLAMA_PID $FLASK_PID $FRONTEND_PID $TUNNEL_PID 2>/dev/null" EXIT

# Keep container running
wait

