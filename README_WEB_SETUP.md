# ZackGPT Web Interface Setup

ZackGPT now supports both CLI and Web interfaces! The web interface provides a modern chat experience while maintaining the powerful prompt evolution system.

## 🚀 Quick Start

### Option 1: One-Command Launch (Recommended)

```bash
# Starts both backend and frontend together
./zackgpt_web.sh
```

### Option 2: Manual Launch

#### 1. Start the Backend API Server

```bash
# Use the main launcher
./zackgpt.sh
# Choose option 2 (Web Mode) or 3 (Hybrid Mode)

# Or direct Python execution
python -m scripts.startup.main_web
```

#### 2. Start the Frontend (in a separate terminal)

```bash
cd ui/zackgpt-ui
npm install    # First time only
npm start -- --host 0.0.0.0
```

### Access the Application

- **Frontend UI**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Features

### ✅ Fully Implemented
- **Real-time Chat**: WebSocket-based messaging with typing indicators
- **Thread Management**: Create, select, and delete conversation threads
- **Prompt Evolution**: The sophisticated AI learning system works seamlessly
- **Memory System**: Persistent conversation memory across sessions
- **Health Monitoring**: Connection status and system health indicators
- **Error Handling**: Graceful fallbacks and error recovery

### 🔄 Backend API Endpoints

#### REST API
- `GET /health` - Health check and feature status
- `GET /threads` - List all conversation threads
- `POST /threads` - Create a new thread
- `GET /threads/{id}` - Get thread details
- `DELETE /threads/{id}` - Delete a thread
- `GET /threads/{id}/messages` - Get messages in a thread
- `POST /threads/{id}/messages` - Send a message (REST fallback)
- `GET /stats` - System statistics

#### WebSocket API
- `ws://localhost:8000/ws/{client_id}` - Real-time chat connection
  - Send messages with instant responses
  - Typing indicators
  - Live message streaming

## 🛠 Architecture

### Backend Structure
```
app/
├── web_api.py          # FastAPI server with WebSocket support
├── core_assistant.py   # Main AI logic (unchanged)
├── prompt_builder.py   # Prompt evolution system (unchanged)
├── memory_db.py        # MongoDB integration (unchanged)
└── ...

scripts/startup/
├── main.py             # Multi-mode launcher (CLI/Web/Hybrid)
├── main_web.py         # Dedicated web server launcher
├── main_text.py        # CLI mode (unchanged)
└── ...
```

### Frontend Structure
```
ui/zackgpt-ui/src/app/
├── services/
│   └── api.service.ts  # Backend API integration
├── components/
│   ├── dashboard/      # Main chat interface
│   └── threads/        # Thread management sidebar
└── ...
```

## 💡 Key Design Decisions

### 1. **Zero Hardcoded AI Logic in Frontend**
The frontend is a pure display layer. All AI processing, prompt evolution, and memory management happens in the backend Python services.

### 2. **Backward Compatible CLI**
The original CLI interface (`./zackgpt.sh` → option 1) continues to work exactly as before. The prompt evolution system is shared between CLI and web interfaces.

### 3. **Thread-Isolated AI Instances**
Each conversation thread gets its own `CoreAssistant` instance, ensuring conversation context doesn't leak between threads while maintaining memory and learning across the system.

### 4. **WebSocket-First with REST Fallback**
The frontend prioritizes WebSocket connections for real-time chat but gracefully falls back to REST APIs if WebSocket connection fails.

### 5. **Comprehensive Error Handling**
- Connection status monitoring
- Automatic reconnection attempts
- Clear error messages with retry options
- Graceful degradation when backend is unavailable

## 🔧 Development

### Running in Development Mode

1. **Backend Development**:
   ```bash
   # Auto-reload on changes
   python -m scripts.startup.main_web
   ```

2. **Frontend Development**:
   ```bash
   cd ui/zackgpt-ui
   npm start  # Auto-reload enabled
   ```

### Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Create a thread
curl -X POST http://localhost:8000/threads \
  -H "Content-Type: application/json" \
  -d '{"title": "My Test Thread"}'

# List threads
curl http://localhost:8000/threads

# Send a message (REST API)
curl -X POST http://localhost:8000/threads/{thread_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello ZackGPT!", "thread_id": "{thread_id}"}'
```

## 🌟 Advanced Features

### Prompt Evolution Integration
The web interface fully integrates with ZackGPT's prompt evolution system:
- User ratings can be collected through the UI
- The AI learns from conversation patterns
- Evolution statistics are available via `/stats` endpoint
- Component-based prompt enhancement continues to work

### Memory System
- Conversation history is preserved across sessions
- Important facts are automatically extracted and stored
- Cross-thread memory sharing for user preferences
- MongoDB-backed persistence

### Real-time Features
- Typing indicators during AI response generation
- Live message streaming
- Connection status monitoring
- Automatic reconnection handling

## 🚨 Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Verify dependencies
pip install -r requirements.txt

# Check .env file
cat .env | grep OPENAI_API_KEY
```

### Frontend Connection Issues
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check console for WebSocket errors
3. Try refreshing the page
4. Use the "Try to Reconnect" button

### API Key Issues
```bash
# Verify API key is loaded
echo $OPENAI_API_KEY

# Check .env file format
# Should be: OPENAI_API_KEY=sk-...
```

## 📊 Monitoring

### Health Endpoint
```json
{
  "status": "healthy",
  "version": "1.0.0", 
  "backend_connected": true,
  "features": {
    "websocket_chat": true,
    "thread_management": true,
    "memory_persistence": true,
    "prompt_evolution": true
  }
}
```

### System Stats
```json
{
  "total_threads": 5,
  "total_messages": 23,
  "evolution_stats": {
    "total_components": 12,
    "experiments": 45,
    "success_rate": 0.87
  },
  "memory_stats": {
    "status": "available"
  }
}
```

---

🎉 **Congratulations!** You now have a fully functional web interface for ZackGPT that maintains all the power of the original prompt evolution system while providing a modern, real-time chat experience. 