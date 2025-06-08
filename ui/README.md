# 🤖 ZackGPT Web UI

A modern, professional web interface for interacting with ZackGPT, featuring chat threads, settings management, and real-time system monitoring.

![ZackGPT UI Screenshot](docs/screenshot.png)

## ✨ Features

### 💬 **Chat Threads**
- **Multiple Conversations**: Organize discussions into separate threads
- **Thread Management**: Create, rename, and delete conversation threads
- **Message History**: Each thread maintains its own conversation history
- **Smart Previews**: See the last message in each thread at a glance
- **Thread Switching**: Seamlessly switch between different conversations

### ⚙️ **Settings Management**
- **Core AI Settings**: Model selection, temperature, max tokens
- **Voice Configuration**: Enable/disable voice features, choose TTS voices
- **Memory Settings**: Configure conversation memory and storage limits
- **Evolution Controls**: Manage prompt evolution system parameters
- **Real-time Updates**: Changes take effect immediately
- **Configuration Validation**: Input validation with helpful error messages

### 📊 **System Dashboard**
- **Real-time Statistics**: Monitor messages, response times, and system uptime
- **Live Logs**: View system logs with color-coded severity levels
- **Evolution Metrics**: Track prompt evolution performance and experiments
- **Connection Status**: Clear indication of backend connectivity

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Professional Styling**: Clean, modern interface with smooth animations
- **Intuitive Navigation**: Easy-to-use sidebar with chat threads and settings
- **Typing Indicators**: Real-time feedback during AI response generation
- **Status Updates**: Clear visual feedback for all user actions

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- ZackGPT backend running (optional for demo mode)

### Installation & Development

1. **Install Dependencies**
   ```bash
   cd ui/zackgpt-ui
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```
   Open [http://localhost:4200](http://localhost:4200) in your browser.

3. **Production Build**
   ```bash
   npm run build
   ```

### Quick Launch Script
Use the convenient launcher from the project root:
```bash
./zackgpt_ui.sh
```

## 🔧 Configuration

### Backend Integration
The UI expects the ZackGPT backend at `http://localhost:8000` by default. Update the API URL in:
- `src/app/services/zackgpt-api.service.ts`

### Demo Mode
The UI includes a fully functional demo mode that works without a backend:
- Sample chat threads with demo conversations
- Simulated AI responses with realistic delays
- Mock settings that can be modified
- Full feature demonstration

## 📚 Architecture

### Technology Stack
- **Framework**: Angular 18+ with standalone components
- **Styling**: SCSS with modern CSS features
- **HTTP Client**: Angular HttpClient for REST API calls
- **WebSockets**: RxJS WebSocket for real-time communication
- **Forms**: Angular Reactive Forms with validation

### Component Structure
```
src/app/
├── components/
│   ├── dashboard/          # Main chat interface
│   ├── settings/           # Configuration management
│   └── threads/           # Thread sidebar and management
├── services/
│   └── zackgpt-api.service.ts  # Backend communication
└── app.component.*        # Main app layout and routing
```

### Key Services

#### **ZackgptApiService**
Handles all backend communication:
- REST API calls for threads, settings, logs
- WebSocket connection for real-time updates
- Automatic reconnection and error handling
- Demo mode fallbacks

## 🔌 API Integration

The UI requires specific backend endpoints. See [BACKEND_API_REQUIREMENTS.md](BACKEND_API_REQUIREMENTS.md) for:
- Required HTTP endpoints
- WebSocket event specifications
- Database schema changes
- Implementation guidelines

### Required Endpoints
- `GET/POST/PATCH/DELETE /api/threads/*` - Thread management
- `GET/PATCH /api/config` - Settings management
- `GET /api/stats` - System statistics
- `GET /api/logs` - System logs
- WebSocket `/ws` - Real-time updates

## 🎯 Usage Guide

### Creating Chat Threads
1. Click "New Thread" in the sidebar
2. Enter a descriptive name
3. Press Enter or click "Create"
4. Start chatting immediately

### Managing Settings
1. Click the ⚙️ "Settings" tab in the sidebar
2. Modify any configuration options
3. Click "Save Changes" to apply
4. Use "Reset to Defaults" to restore original settings

### Chatting with ZackGPT
1. Select a thread from the sidebar
2. Type your message in the input field
3. Press Enter or click "Send"
4. Watch the typing indicator while ZackGPT responds
5. View response times and conversation statistics

## 🔧 Development

### Project Structure
```
ui/zackgpt-ui/
├── src/
│   ├── app/                # Angular application
│   ├── assets/            # Static assets
│   └── styles.scss        # Global styles
├── public/                # Public assets
├── package.json          # Dependencies and scripts
└── angular.json          # Angular configuration
```

### Development Commands
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

### Code Style
- **TypeScript**: Strict mode enabled
- **Linting**: Angular ESLint configuration
- **Formatting**: Prettier with Angular conventions
- **Components**: Standalone components with OnPush change detection
- **Styling**: SCSS with BEM methodology

## 🚧 Development Roadmap

### Completed ✅
- ✅ Chat threads with full CRUD operations
- ✅ Settings management with validation
- ✅ Real-time chat interface with typing indicators
- ✅ Responsive design for all screen sizes
- ✅ Demo mode for testing without backend
- ✅ Professional styling and animations

### In Progress 🔄
- 🔄 Backend API implementation
- 🔄 WebSocket real-time updates
- 🔄 Configuration persistence

### Planned 📋
- 📋 Thread search and filtering
- 📋 Message export functionality
- 📋 Advanced evolution metrics visualization
- 📋 Dark/light theme toggle
- 📋 Keyboard shortcuts
- 📋 Voice input/output integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the code style guidelines
4. Test thoroughly in both demo and connected modes
5. Commit with clear messages: `git commit -m 'Add amazing feature'`
6. Push to your branch: `git push origin feature/amazing-feature`
7. Submit a pull request

## 📝 License

This project is part of ZackGPT and follows the same licensing terms.

## 🆘 Support

### Troubleshooting

**White Screen/Loading Issues**
- Ensure Node.js 18+ is installed
- Clear browser cache and reload
- Check browser console for errors

**Backend Connection Issues**
- Verify backend is running on expected port
- Check API URL configuration in service
- Use demo mode for testing UI features

**Build/Development Issues**
- Delete `node_modules` and run `npm install`
- Update Node.js to latest LTS version
- Check Angular CLI version compatibility

### Getting Help
- Check the [BACKEND_API_REQUIREMENTS.md](BACKEND_API_REQUIREMENTS.md) for integration details
- Review browser console for error messages
- Test in demo mode to isolate UI vs backend issues

---

**Built with ❤️ for the ZackGPT project** 