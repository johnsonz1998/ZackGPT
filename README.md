# 🧠 ZackGPT

**ZackGPT is Zack's personal AI assistant with advanced prompt evolution, memory systems, and multi-interface support.**

## 🚀 Quick Start

### One-Command Launch
```bash
# Launch web interface (recommended)
./scripts/launcher/zackgpt_web.sh

# Launch CLI interface  
./scripts/launcher/zackgpt_text.sh
```

### Access Points
- **Web Interface**: http://localhost:4200 (Modern chat UI)
- **CLI Interface**: Direct terminal interaction
- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## ✨ Features

### 🧠 **Advanced AI Capabilities**
- **Prompt Evolution System**: AI continuously learns and adapts its responses
- **Memory System**: Persistent conversation memory across sessions  
- **Quality Assessment**: Real-time response quality monitoring
- **Component Learning**: Dynamic prompt component optimization

### 🌐 **Multi-Interface Support**
- **Web Interface**: Modern React-based chat experience
- **CLI Interface**: Terminal-based interaction
- **REST API**: Full programmatic access
- **WebSocket API**: Real-time communication

### 🔍 **Web Search Integration**
- **Real-time Information**: Access current news, weather, prices
- **Multiple Search Engines**: SerpAPI, Google Custom Search, DuckDuckGo
- **Smart Detection**: Automatically knows when to search
- **Content Extraction**: Reads and analyzes web pages

### 🧪 **Enterprise-Grade Testing**
- **42 Comprehensive Tests**: 93% pass rate
- **Professional Test Runner**: Colored output, smart categorization
- **Performance Benchmarking**: Response times, memory monitoring
- **CI/CD Ready**: Complete coverage reporting

## 📁 Project Structure

```
ZackGPT/
├── app/                    # Core AI application
│   ├── core_assistant.py   # Main AI logic
│   ├── prompt_builder.py   # Prompt evolution system
│   ├── database.py         # Unified MongoDB database
│   └── web_api.py          # FastAPI server
├── frontend/               # React web interface
│   ├── src/components/     # UI components
│   └── src/services/       # API integration
├── tests/                  # Comprehensive test suite
│   ├── backend/            # Backend API tests
│   ├── frontend/           # Frontend component tests
│   └── integration/        # End-to-end tests
├── scripts/                # Organized shell scripts
│   ├── launcher/           # Application launchers
│   ├── setup/              # Installation scripts
│   └── tools/              # Development utilities
├── config/                 # Configuration management
└── docs/                   # Documentation
```

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (for memory persistence)

### 1. Clone & Install
```bash
git clone https://github.com/your-repo/ZackGPT.git
cd ZackGPT
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your API keys:
OPENAI_API_KEY=your_openai_key_here
WEB_SEARCH_ENABLED=true
SERPAPI_KEY=your_serpapi_key_here  # Optional but recommended
```

### 3. Frontend Setup (for web interface)
```bash
cd frontend
npm install
cd ..
```

### 4. Run Tests (optional but recommended)
```bash
python tests/run_tests.py --all
```

## 🔧 Usage

### Web Interface
```bash
./scripts/launcher/zackgpt_web.sh
# Opens http://localhost:4200
```

### CLI Interface  
```bash
./scripts/launcher/zackgpt_text.sh
# Direct terminal chat
```

### API Access
```bash
# Health check
curl http://localhost:8000/health

# Send message via REST
curl -X POST http://localhost:8000/threads/123/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello ZackGPT!"}'
```

### WebSocket Chat
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/client-123');
ws.send(JSON.stringify({
  type: 'message',
  content: 'Hello via WebSocket!'
}));
```

## 🔍 Web Search Setup

ZackGPT includes powerful web search capabilities for real-time information.

### Configuration
Add to your `.env` file:
```bash
WEB_SEARCH_ENABLED=true
WEB_SEARCH_MAX_RESULTS=5

# Choose one or more search engines:
SERPAPI_KEY=your_serpapi_key_here           # Recommended
GOOGLE_API_KEY=your_google_api_key_here     # Alternative  
GOOGLE_CSE_ID=your_custom_search_id_here    # Required with Google
```

### Search Engine Setup

**SerpAPI (Recommended)**
1. Sign up at [serpapi.com](https://serpapi.com)
2. Get your API key
3. Free tier: 100 searches/month

**Google Custom Search**
1. Enable API at [Google Cloud Console](https://console.cloud.google.com)
2. Create Custom Search Engine at [cse.google.com](https://cse.google.com)
3. Free tier: 100 searches/day

**DuckDuckGo**
- Always available as fallback
- No API key required

### Usage Examples
```
❯ What's the latest news about AI?
❯ Search for Python tutorials
❯ What's the weather in New York?
❯ Current Bitcoin price
❯ Tell me about recent quantum computing developments
```

## 🧪 Testing

### Run Test Suite
```bash
python tests/run_tests.py --all --coverage  # Full test suite with coverage
python tests/run_tests.py --backend         # Backend tests only
python tests/run_tests.py --integration     # Integration tests
python tests/run_tests.py --performance     # Performance benchmarks
```

### Test Categories
- **42 Total Tests**: Comprehensive coverage
- **Backend API Tests**: REST + WebSocket validation  
- **Core Assistant Tests**: AI processing verification
- **OpenAI Integration Tests**: API connectivity
- **Performance Tests**: Response time benchmarks

## 🏗 Architecture

### Backend Components
- **FastAPI Server**: REST API + WebSocket support
- **CoreAssistant**: Main AI processing engine
- **Prompt Builder**: Dynamic prompt evolution system
- **Memory Database**: MongoDB-backed conversation persistence
- **Web Search**: Multi-engine search integration

### Frontend Components
- **React Dashboard**: Modern chat interface
- **Thread Management**: Conversation organization
- **API Service**: Backend integration layer
- **Real-time Chat**: WebSocket-based messaging

### Key Design Principles
1. **Zero AI Logic in Frontend**: Pure display layer
2. **Backward Compatible CLI**: Original interface preserved
3. **Thread-Isolated AI**: Separate instances per conversation
4. **WebSocket-First**: Real-time with REST fallback
5. **Comprehensive Error Handling**: Graceful degradation

## 🚨 Troubleshooting

### Backend Issues
```bash
# Check if port 8000 is in use
lsof -i :8000

# Verify dependencies
pip install -r requirements.txt

# Check environment variables
echo $OPENAI_API_KEY
```

### Frontend Issues
```bash
# Verify backend is running
curl http://localhost:8000/health

# Restart frontend
cd frontend && npm start
```

### API Key Issues
```bash
# Test OpenAI connection
python -c "import openai; print('OpenAI available')"

# Check web search setup
python -c "from app.web_search import WebSearcher; print('Search enabled')"
```

## 📊 Monitoring

### Health Endpoints
- `GET /health` - System health check
- `GET /stats` - Performance statistics
- `GET /threads` - Active conversations

### Quality Metrics
- Response quality scoring
- Prompt evolution tracking
- Memory utilization stats
- Search usage analytics

## 🔐 Security

- API keys stored in environment variables
- No hardcoded credentials
- Secure WebSocket connections
- Request validation and sanitization
- Rate limiting on API endpoints

## 🚀 Development

### Local Development
```bash
# Backend with auto-reload
python -m scripts.startup.main_web

# Frontend with hot reload
cd frontend && npm start
```

### Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `python tests/run_tests.py --all`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push branch: `git push origin feature/amazing-feature`
6. Open Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- FastAPI for the excellent web framework
- React community for frontend tools
- MongoDB for reliable data persistence

---

**Built with ❤️ for efficient AI assistance** 