# ZackGPT UI - Advanced AI Chat with Prompt Evolution

This is the Angular frontend for ZackGPT, an AI assistant that uses an advanced prompt evolution system to continuously improve its responses based on conversation patterns and feedback.

## 🧬 What Makes ZackGPT Special

Unlike traditional AI assistants, ZackGPT features:

- **Prompt Evolution System**: Uses statistical learning and AI enhancement to evolve prompts over time
- **Self-Improving AI**: Learns from conversation patterns to provide better responses
- **Context-Aware Responses**: Adapts to your conversation style and needs
- **Thread-Based Conversations**: Organize chats by topic with persistent memory
- **Real-Time Analytics**: Monitor AI performance and evolution statistics

## 🚀 Quick Start

### 1. Start the ZackGPT Backend (Required)

The UI requires the ZackGPT backend to function. Navigate to the main ZackGPT directory and run:

```bash
cd /home/zack/ZackGPT
./zackgpt.sh
```

This will start the backend server with the prompt evolution system.

### 2. Start the Angular UI

```bash
cd ui/zackgpt-ui
npm start
```

The UI will be available at `http://localhost:4200`

## 📋 Features

### Chat Threads
- Create multiple conversation threads
- Thread-specific message history
- Real-time message sync with backend
- Thread management (create, delete, rename)

### Prompt Evolution Integration
- Connected to backend's AI enhancement system
- No hardcoded responses - all AI-generated
- Uses the `GenerativePromptEvolver` for smart responses
- Incorporates conversation context and learning

### Settings Management
- Configure AI model parameters
- Adjust prompt evolution settings
- Manage API keys
- Control voice and memory features

### Real-Time Analytics
- Monitor prompt evolution statistics
- Track AI performance metrics
- View system logs and debug info
- Evolution experiment tracking

## 🔧 Backend Connection

The UI connects to the ZackGPT backend via:
- **HTTP API**: `http://localhost:8000/api` for REST operations
- **WebSocket**: `ws://localhost:8000/ws` for real-time communication

### Connection Status
- 🟢 **Connected**: Full prompt evolution system active
- 🔴 **Disconnected**: Backend offline, system non-functional

## ⚠️ Important Notes

### No Demo Mode
This UI does **NOT** have a demo mode with hardcoded responses. It requires the full ZackGPT backend to function, which provides:

- AI-generated responses using the prompt evolution system
- Real conversation memory and context
- Adaptive prompt enhancement
- Statistical learning from interactions

### Backend Requirements
Make sure the backend is running with:
- Valid OpenAI API key configured
- Prompt evolution system enabled
- Database connection (MongoDB or file-based memory)
- All required Python dependencies installed

## 🛠️ Development

### Project Structure
```
src/app/
├── components/
│   ├── dashboard/         # Main chat interface
│   ├── threads/           # Thread management
│   └── settings/          # Configuration
├── services/
│   └── zackgpt-api.service.ts  # Backend API integration
└── app.component.ts       # Main app shell
```

### Key Components
- **Dashboard**: Chat interface with real-time messaging
- **Threads**: Thread management and selection
- **Settings**: Configuration for backend settings
- **API Service**: Handles all backend communication

### Backend API Integration
The UI integrates with these backend systems:
- `app/core_assistant.py` - Main AI assistant with prompt evolution
- `app/prompt_builder.py` - Evolutionary prompt system
- `app/prompt_enhancer.py` - AI-powered prompt enhancement
- `config/prompt_evolution/` - Statistical learning data

## 🔍 Troubleshooting

### Backend Not Connected
1. Ensure backend is running: `./zackgpt.sh`
2. Check API endpoint: `http://localhost:8000/api/stats`
3. Verify WebSocket: `ws://localhost:8000/ws`
4. Check backend logs for errors

### No Responses Generated
1. Verify OpenAI API key is configured
2. Check prompt evolution system is enabled
3. Ensure sufficient API credits
4. Review backend debug logs

### Empty Thread List
1. Backend connection required for thread persistence
2. Create first thread using "New Thread" button
3. Threads are stored in backend database/memory

## 📚 Learn More

- **Main ZackGPT Docs**: See `/README.md` in the root directory
- **Backend API**: Check `/BACKEND_API_REQUIREMENTS.md`
- **Prompt Evolution**: Explore `app/prompt_builder.py`
- **Configuration**: Review `config/config.py`

---

**🧬 Experience AI that evolves with every conversation!**
