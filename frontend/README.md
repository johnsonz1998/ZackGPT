# ZackGPT Frontend

A modern, ChatGPT-like web interface for ZackGPT, built with React and TypeScript.

## Features

- 🎨 **ChatGPT-style UI** - Exact replica of ChatGPT's interface
- 💬 **Real-time Chat** - WebSocket-powered instant messaging
- 🧵 **Thread Management** - Create, switch, and delete conversation threads
- ⚙️ **Settings Panel** - Configure API keys, model settings, and features
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile
- 🌙 **Dark Theme** - Beautiful dark theme matching ChatGPT
- 📝 **Markdown Support** - Full markdown rendering for AI responses
- 🔄 **Auto-reconnect** - Automatic WebSocket reconnection
- 💾 **Persistent Conversations** - All chats are saved and restored

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- ZackGPT backend running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The frontend will start on `http://localhost:3000` and automatically connect to the ZackGPT backend on port 8000.

## Usage

### Starting a Conversation

1. **New Chat**: Click the "New chat" button in the sidebar or start typing in the welcome screen
2. **Send Messages**: Type your message and press Enter or click the send button
3. **Switch Conversations**: Click on any conversation in the sidebar to switch to it

### Features

- **Ctrl/Cmd + Enter**: Send message (alternative to clicking send button)
- **Auto-resize**: Message input automatically resizes as you type
- **Typing Indicators**: See when ZackGPT is thinking/responding
- **Message History**: All conversations are automatically saved
- **Delete Conversations**: Hover over a conversation and click the X button

### Settings

Access the settings panel by clicking the gear icon in the sidebar. Configure:

- **General**: View model configuration and enabled features
- **API Keys**: Set up OpenAI, ElevenLabs, SerpAPI, and Google API keys
- **Web Search**: Configure web search engines and settings

## Technical Details

### Architecture

- **Frontend**: React 18 + TypeScript
- **Styling**: CSS3 with CSS modules
- **Icons**: Lucide React
- **Markdown**: react-markdown with remark-gfm
- **WebSocket**: Native WebSocket API for real-time communication
- **HTTP Client**: Fetch API for REST endpoints

### API Integration

The frontend connects to the ZackGPT backend via:

- **REST API**: Thread management, configuration, message history
- **WebSocket**: Real-time messaging and typing indicators
- **Proxy**: Development proxy configured to route API calls to port 8000

### Key Components

- **App.tsx**: Main application component with chat interface
- **Settings.tsx**: Configuration management modal
- **App.css**: Main styles matching ChatGPT design
- **Settings.css**: Settings modal styles

## Development

### Available Scripts

- `npm start`: Start development server
- `npm build`: Create production build
- `npm test`: Run test suite
- `npm run eject`: Eject from Create React App (not recommended)

### Environment Configuration

The frontend automatically connects to:
- **API**: `http://localhost:8000` (via proxy)
- **WebSocket**: `ws://localhost:8000`

For production deployment, update these URLs in `src/App.tsx`.

## Features in Detail

### Thread Management
- Create new conversations automatically or manually
- Switch between multiple conversations seamlessly
- Delete conversations with confirmation
- Persistent conversation history

### Real-time Chat
- WebSocket-powered instant messaging
- Typing indicators when AI is responding
- Automatic reconnection on connection loss
- Message delivery confirmation

### Settings Management
- View current configuration
- Update API keys securely
- Monitor feature status
- Configure web search options

### Responsive Design
- Mobile-first responsive layout
- Collapsible sidebar on mobile
- Touch-friendly interface
- Optimized for all screen sizes

## Troubleshooting

### Common Issues

1. **Cannot connect to backend**
   - Ensure ZackGPT backend is running on port 8000
   - Check that CORS is properly configured

2. **WebSocket connection fails**
   - Verify WebSocket endpoint is accessible
   - Check browser console for error messages

3. **API key updates not working**
   - Ensure backend has write permissions to .env file
   - Check backend logs for error messages

### Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This frontend is part of the ZackGPT project and follows the same license terms.
