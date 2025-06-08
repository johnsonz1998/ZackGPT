# Backend API Requirements for ZackGPT UI

## Overview
The enhanced ZackGPT UI requires several new backend endpoints to support chat threads and settings management. This document outlines the required API changes.

## 🔌 Required HTTP Endpoints

### Chat Threads Management

#### `GET /api/threads`
Get all chat threads for the user.

**Response:**
```json
[
  {
    "id": "thread-123",
    "name": "General Discussion", 
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T14:20:00Z",
    "message_count": 15,
    "preview": "How does the prompt evolution system work?"
  }
]
```

#### `POST /api/threads`
Create a new chat thread.

**Request:**
```json
{
  "name": "Development Help"
}
```

**Response:**
```json
{
  "id": "thread-456",
  "name": "Development Help",
  "created_at": "2024-01-15T15:00:00Z", 
  "updated_at": "2024-01-15T15:00:00Z",
  "message_count": 0,
  "preview": null
}
```

#### `GET /api/threads/{thread_id}/messages`
Get messages for a specific thread.

**Response:**
```json
[
  {
    "id": "msg-1",
    "timestamp": "2024-01-15T10:30:00Z",
    "user_message": "Hello!",
    "assistant_response": "Hi there! How can I help you?",
    "response_time": 1.2
  }
]
```

#### `PATCH /api/threads/{thread_id}`
Update thread properties (name, etc).

**Request:**
```json
{
  "name": "Updated Thread Name"
}
```

#### `DELETE /api/threads/{thread_id}`
Delete a chat thread and all its messages.

**Response:** `204 No Content`

---

### Settings Management

#### `GET /api/config`
Get current ZackGPT configuration.

**Response:**
```json
{
  "model_name": "gpt-4",
  "max_tokens": 2000,
  "temperature": 0.7,
  "voice_enabled": false,
  "voice_model": "whisper-1", 
  "tts_voice": "alloy",
  "memory_enabled": true,
  "max_memory_entries": 1000,
  "evolution_enabled": true,
  "evolution_frequency": 10,
  "openai_api_key_masked": "sk-...***",
  "elevenlabs_api_key_masked": "***masked***",
  "debug_mode": false,
  "log_level": "INFO"
}
```

#### `PATCH /api/config`
Update configuration settings.

**Request:**
```json
{
  "temperature": 0.8,
  "max_tokens": 3000,
  "voice_enabled": true
}
```

**Response:** Updated config object (same format as GET)

#### `POST /api/config/reset`
Reset configuration to default values.

**Response:** Default config object

---

### Existing Endpoints (Enhanced)

#### `POST /api/conversation` or WebSocket `user_message`
Send a message - now requires thread_id.

**WebSocket Message:**
```json
{
  "type": "user_message",
  "data": {
    "message": "Hello ZackGPT!",
    "thread_id": "thread-123"
  }
}
```

#### Enhanced WebSocket Events
The UI expects these WebSocket event types:

- `new_message` - New AI response in a thread
- `stats_update` - Updated system statistics  
- `logs_update` - New log entries
- `typing` - AI is processing (typing indicator)
- `thread_updated` - Thread metadata changed

---

## 🗄️ Database Schema Changes

### Threads Table
```sql
CREATE TABLE threads (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    message_count INT DEFAULT 0,
    preview TEXT
);
```

### Messages Table (Enhanced)
```sql
ALTER TABLE messages ADD COLUMN thread_id VARCHAR(50);
ALTER TABLE messages ADD FOREIGN KEY (thread_id) REFERENCES threads(id);
```

---

## 🔧 Implementation Notes

### Config.py Integration
The `/api/config` endpoints should:

1. **Read from config.py** - Load current settings from the Python config file
2. **Update config.py** - Write changes back to the config file  
3. **Reload modules** - Ensure changes take effect without restart
4. **Mask API keys** - Never send full API keys to frontend

Example config.py structure expected:
```python
# ZackGPT Configuration
MODEL_NAME = "gpt-4"
MAX_TOKENS = 2000
TEMPERATURE = 0.7
VOICE_ENABLED = False
MEMORY_ENABLED = True
EVOLUTION_ENABLED = True
# ... etc
```

### Thread Management
- Each thread maintains its own conversation context
- Message count should auto-update when messages are added
- Preview should be the last user message in the thread
- Thread deletion should cascade to remove all messages

### WebSocket Enhancements
- Include `thread_id` in all message-related WebSocket events
- Send `thread_updated` events when thread metadata changes
- Clients should join thread-specific rooms for targeted updates

---

## 🚀 Implementation Priority

1. **High Priority**
   - Chat threads CRUD operations
   - Thread-specific message retrieval
   - Basic config GET/PATCH endpoints

2. **Medium Priority** 
   - Config reset functionality
   - WebSocket thread-specific events
   - Database schema migration

3. **Low Priority**
   - Advanced thread features (search, tags, etc.)
   - Config validation and error handling
   - Thread archiving/soft delete

---

## 🧪 Testing

The UI includes demo mode that works without a backend. To test:

1. Run `npm start` in `ui/zackgpt-ui/`
2. Navigate to `http://localhost:4200`
3. Create threads, send messages, modify settings
4. All features work with mock data

Once backend endpoints are implemented, disable demo mode by setting API responses to succeed. 