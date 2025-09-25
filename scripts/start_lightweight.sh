#!/bin/bash

# ZackGPT Lightweight Mode Startup Script
# For resource-constrained servers

set -e

echo "🚀 ZackGPT Lightweight Mode Startup"
echo "===================================="

# Navigate to project directory
cd "$(dirname "$0")/.."

echo "📍 Working directory: $(pwd)"

# Kill any existing ZackGPT processes
echo "🔧 Cleaning up existing processes..."
pkill -f "uvicorn.*zackgpt" 2>/dev/null || true
pkill -f "python.*zackgpt" 2>/dev/null || true
sleep 2

# Wait for port to be free
echo "⏳ Waiting for port 8000 to be free..."
while lsof -i:8000 >/dev/null 2>&1; do
    echo "   Port 8000 still in use, waiting..."
    sleep 1
done

# Set lightweight mode environment variables
echo "⚡ Enabling lightweight mode..."
export ZACKGPT_LIGHTWEIGHT=true
export ZACKGPT_MODE=lightweight
export MAX_CONVERSATION_HISTORY=3
export MAX_MEMORY_RETRIEVAL=5
export MAX_TOKENS=1000
export THREAD_POOL_SIZE=1

# Disable all non-essential features
export ENABLE_PERIODIC_CLEANUP=false
export ENABLE_MEMORY_ANALYTICS=false
export ENABLE_AUTO_BACKUP=false
export ENABLE_DEBUG_ANALYTICS=false
export ENABLE_MONGODB_LOGGING=false
export ENABLE_DETAILED_METRICS=false
export ENABLE_MEMORY_CACHING=false
export ENABLE_CONVERSATION_CACHING=false
export ENABLE_THREAD_PRELOADING=false
export ENABLE_WEBSOCKET_KEEPALIVE=false
export ENABLE_EXTERNAL_SEARCH=false
export ENABLE_PERPLEXITY_INTEGRATION=false
export ENABLE_AI_MEMORY_EXTRACTION=false
export ENABLE_PROMPT_EVOLUTION=false
export ENABLE_RESPONSE_QUALITY_ASSESSMENT=false
export ENABLE_HOT_RELOAD=false
export ENABLE_DEBUG_ENDPOINTS=false

echo "📊 Lightweight settings applied:"
echo "  🚫 All background tasks disabled"
echo "  🚫 Web search disabled"
echo "  🚫 AI features simplified"
echo "  ⚡ Single thread pool"
echo "  💾 Reduced memory limits"

# Start the server with minimal settings
echo ""
echo "🚀 Starting ZackGPT in lightweight mode..."
echo "   Server will be available at: http://localhost:8000"
echo "   Frontend should connect to: http://localhost:3000"
echo ""
echo "💡 To stop: Press Ctrl+C"
echo "💡 For normal mode: Use 'python3 -m uvicorn src.zackgpt.web.web_api:app --host 0.0.0.0 --port 8000'"
echo ""

# Start server (single worker, no reload for minimum resource usage)
exec python3 -m uvicorn src.zackgpt.web.web_api:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level warning \
    --no-access-log 