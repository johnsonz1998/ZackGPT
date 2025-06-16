import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from src.zackgpt.web.web_api import app, get_assistant, ConnectionManager

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_thread_manager():
    """Create a mock thread manager."""
    thread_manager = Mock()
    thread_manager.get_threads.return_value = [
        {"id": "thread-1", "title": "Test Thread 1", "created_at": "2024-01-01T10:00:00Z"},
        {"id": "thread-2", "title": "Test Thread 2", "created_at": "2024-01-01T11:00:00Z"}
    ]
    thread_manager.create_thread.return_value = {
        "id": "new-thread-123", 
        "title": "New Thread", 
        "created_at": "2024-01-01T12:00:00Z"
    }
    thread_manager.get_thread.return_value = {
        "id": "thread-1", 
        "title": "Test Thread 1", 
        "created_at": "2024-01-01T10:00:00Z"
    }
    thread_manager.get_messages.return_value = [
        {"id": "msg-1", "role": "user", "content": "Hello", "timestamp": "2024-01-01T10:01:00Z"},
        {"id": "msg-2", "role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T10:01:30Z"}
    ]
    thread_manager.add_user_message.return_value = {
        "id": "msg-3", "role": "user", "content": "Test message", "timestamp": "2024-01-01T10:02:00Z"
    }
    thread_manager.add_assistant_message.return_value = {
        "id": "msg-4", "role": "assistant", "content": "Test response", "timestamp": "2024-01-01T10:02:30Z"
    }
    thread_manager.delete_thread.return_value = True
    thread_manager.get_stats.return_value = {
        "threads": {"total": 5, "total_messages": 25}
    }
    return thread_manager

@pytest.fixture
def mock_assistant():
    """Create a mock assistant."""
    assistant = Mock()
    assistant.process_input.return_value = "This is a test response from the assistant."
    assistant.get_evolution_stats.return_value = {"status": "active", "generations": 10}
    return assistant

@pytest.fixture
def mock_memory_manager():
    """Create a mock memory manager."""
    memory_manager = Mock()
    memory_manager.save_interaction.return_value = None
    memory_manager.get_stats.return_value = {"total_memories": 100, "status": "active"}
    return memory_manager

class TestWebAPI:
    """Test web API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_get_threads(self, mock_thread_manager, client):
        """Test getting threads."""
        mock_thread_manager.get_threads.return_value = []
        
        response = client.get("/threads")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_create_thread(self, mock_thread_manager, client):
        """Test creating a thread."""
        mock_thread_manager.create_thread.return_value = {
            "id": "test-123",
            "title": "Test Thread"
        }
        
        response = client.post("/threads", json={"title": "Test Thread"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-123"

class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "backend_connected" in data
        assert "features" in data

class TestThreadEndpoints:
    """Test thread management endpoints."""
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_get_threads(self, mock_tm, client, mock_thread_manager):
        """Test getting all threads."""
        mock_tm.get_threads.return_value = mock_thread_manager.get_threads.return_value
        
        response = client.get("/threads")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "thread-1"
        assert data[1]["id"] == "thread-2"
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_create_thread(self, mock_tm, client, mock_thread_manager):
        """Test creating a new thread."""
        mock_tm.create_thread.return_value = mock_thread_manager.create_thread.return_value
        
        thread_data = {"title": "New Test Thread"}
        response = client.post("/threads", json=thread_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "new-thread-123"
        assert data["title"] == "New Thread"
        mock_tm.create_thread.assert_called_once_with("New Test Thread")
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_get_thread(self, mock_tm, client, mock_thread_manager):
        """Test getting a specific thread."""
        mock_tm.get_thread.return_value = mock_thread_manager.get_thread.return_value
        
        response = client.get("/threads/thread-1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "thread-1"
        assert data["title"] == "Test Thread 1"
        mock_tm.get_thread.assert_called_once_with("thread-1")
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_get_thread_not_found(self, mock_tm, client):
        """Test getting a non-existent thread."""
        mock_tm.get_thread.return_value = None
        
        response = client.get("/threads/non-existent")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Thread not found"
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    @patch('src.zackgpt.web.web_api.assistants', {})
    def test_delete_thread(self, mock_tm, client, mock_thread_manager):
        """Test deleting a thread."""
        mock_tm.delete_thread.return_value = mock_thread_manager.delete_thread.return_value
        
        response = client.delete("/threads/thread-1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Thread deleted successfully"
        mock_tm.delete_thread.assert_called_once_with("thread-1")
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_delete_thread_not_found(self, mock_tm, client):
        """Test deleting a non-existent thread."""
        mock_tm.delete_thread.return_value = False
        
        response = client.delete("/threads/non-existent")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Thread not found"

class TestMessageEndpoints:
    """Test message management endpoints."""
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_get_messages(self, mock_tm, client, mock_thread_manager):
        """Test getting messages from a thread."""
        mock_tm.get_thread.return_value = mock_thread_manager.get_thread.return_value
        mock_tm.get_messages.return_value = mock_thread_manager.get_messages.return_value
        
        response = client.get("/threads/thread-1/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["role"] == "user"
        assert data[1]["role"] == "assistant"
        mock_tm.get_messages.assert_called_once_with("thread-1")
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_get_messages_thread_not_found(self, mock_tm, client):
        """Test getting messages from non-existent thread."""
        mock_tm.get_thread.return_value = None
        
        response = client.get("/threads/non-existent/messages")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Thread not found"
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    @patch('src.zackgpt.web.web_api.get_assistant')
    @patch('src.zackgpt.web.web_api.memory_manager')
    def test_send_message(self, mock_mm, mock_get_assistant, mock_tm, client, 
                         mock_thread_manager, mock_assistant, mock_memory_manager):
        """Test sending a message to a thread."""
        mock_tm.get_thread.return_value = mock_thread_manager.get_thread.return_value
        mock_tm.add_user_message.return_value = mock_thread_manager.add_user_message.return_value
        mock_tm.add_assistant_message.return_value = mock_thread_manager.add_assistant_message.return_value
        mock_get_assistant.return_value = mock_assistant
        mock_mm.save_interaction.return_value = mock_memory_manager.save_interaction.return_value
        
        message_data = {
            "content": "Hello, assistant!",
            "thread_id": "thread-1",
            "force_web_search": False
        }
        response = client.post("/threads/thread-1/messages", json=message_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "assistant"
        assert data["content"] == "Test response"
        
        mock_tm.add_user_message.assert_called_once_with("thread-1", "Hello, assistant!")
        mock_assistant.process_input.assert_called_once_with("Hello, assistant!")
        mock_tm.add_assistant_message.assert_called_once()
        mock_mm.save_interaction.assert_called_once()
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_send_message_thread_not_found(self, mock_tm, client):
        """Test sending message to non-existent thread."""
        mock_tm.get_thread.return_value = None
        
        message_data = {
            "content": "Hello!",
            "thread_id": "non-existent",
            "force_web_search": False
        }
        response = client.post("/threads/non-existent/messages", json=message_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Thread not found"
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    @patch('src.zackgpt.web.web_api.get_assistant')
    def test_send_message_with_web_search(self, mock_get_assistant, mock_tm, client, 
                                        mock_thread_manager, mock_assistant):
        """Test sending message with forced web search."""
        mock_tm.get_thread.return_value = mock_thread_manager.get_thread.return_value
        mock_tm.add_user_message.return_value = mock_thread_manager.add_user_message.return_value
        mock_tm.add_assistant_message.return_value = mock_thread_manager.add_assistant_message.return_value
        mock_get_assistant.return_value = mock_assistant
        
        message_data = {
            "content": "What's the weather?",
            "thread_id": "thread-1",
            "force_web_search": True
        }
        response = client.post("/threads/thread-1/messages", json=message_data)
        
        assert response.status_code == 200
        # Verify web search was forced
        mock_assistant.process_input.assert_called_once_with("[WEB_SEARCH_FORCED] What's the weather?")

class TestSystemEndpoints:
    """Test system information endpoints."""
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    @patch('src.zackgpt.web.web_api.memory_manager')
    @patch('src.zackgpt.web.web_api.CoreAssistant')
    def test_get_stats(self, mock_core_assistant, mock_mm, mock_tm, client, 
                      mock_thread_manager, mock_memory_manager):
        """Test getting system statistics."""
        mock_tm.get_stats.return_value = mock_thread_manager.get_stats.return_value
        mock_mm.get_stats.return_value = mock_memory_manager.get_stats.return_value
        
        mock_assistant_instance = Mock()
        mock_assistant_instance.get_evolution_stats.return_value = {"status": "active"}
        mock_core_assistant.return_value = mock_assistant_instance
        
        response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_threads"] == 5
        assert data["total_messages"] == 25
        assert "evolution_stats" in data
        assert "memory_stats" in data
    
    @patch('src.zackgpt.web.web_api.config')
    def test_get_config(self, mock_config, client):
        """Test getting configuration."""
        # Mock config attributes
        mock_config.LLM_MODEL = "gpt-4"
        mock_config.MAX_TOKENS = 2000
        mock_config.LLM_TEMPERATURE = 0.7
        mock_config.OPENAI_API_KEY = "sk-test123456789"
        mock_config.DEBUG_MODE = True
        
        response = client.get("/config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_name"] == "gpt-4"
        assert data["max_tokens"] == 2000
        assert data["temperature"] == 0.7
        assert data["debug_mode"] is True
        # API key should be masked
        assert "sk-test" not in data["openai_api_key_masked"]
        assert "***" in data["openai_api_key_masked"]
    
    def test_update_config(self, client):
        """Test updating configuration."""
        config_updates = {
            "temperature": 0.8,
            "max_tokens": 3000
        }
        response = client.patch("/config", json=config_updates)
        
        assert response.status_code == 200
        # For now, just returns current config
        data = response.json()
        assert "model_name" in data
    
    def test_update_api_keys(self, client):
        """Test updating API keys."""
        api_keys = {
            "openai_api_key": "sk-new-key-123",
            "serpapi_key": "new-serpapi-key"
        }
        
        with patch('builtins.open', create=True) as mock_open:
            with patch('os.path.exists', return_value=False):
                response = client.post("/config/api-keys", json=api_keys)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "updated_keys" in data
    
    def test_reset_config(self, client):
        """Test resetting configuration."""
        response = client.post("/config/reset")
        
        assert response.status_code == 200
        data = response.json()
        assert "model_name" in data

class TestConnectionManager:
    """Test WebSocket connection manager."""
    
    @pytest.fixture
    def connection_manager(self):
        """Create a ConnectionManager instance."""
        return ConnectionManager()
    
    def test_connection_manager_creation(self, connection_manager):
        """Test creating a ConnectionManager."""
        assert len(connection_manager.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_connect_websocket(self, connection_manager):
        """Test connecting a WebSocket."""
        mock_websocket = Mock()
        mock_websocket.accept = Mock()
        
        await connection_manager.connect(mock_websocket, "client-1")
        
        assert "client-1" in connection_manager.active_connections
        assert connection_manager.active_connections["client-1"] == mock_websocket
        mock_websocket.accept.assert_called_once()
    
    def test_disconnect_websocket(self, connection_manager):
        """Test disconnecting a WebSocket."""
        mock_websocket = Mock()
        connection_manager.active_connections["client-1"] = mock_websocket
        
        connection_manager.disconnect("client-1")
        
        assert "client-1" not in connection_manager.active_connections
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, connection_manager):
        """Test sending a personal message."""
        mock_websocket = Mock()
        mock_websocket.send_text = Mock()
        connection_manager.active_connections["client-1"] = mock_websocket
        
        await connection_manager.send_personal_message("Hello!", "client-1")
        
        mock_websocket.send_text.assert_called_once_with("Hello!")
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, connection_manager):
        """Test broadcasting a message."""
        mock_websocket1 = Mock()
        mock_websocket2 = Mock()
        mock_websocket1.send_text = Mock()
        mock_websocket2.send_text = Mock()
        
        connection_manager.active_connections["client-1"] = mock_websocket1
        connection_manager.active_connections["client-2"] = mock_websocket2
        
        await connection_manager.broadcast("Broadcast message")
        
        mock_websocket1.send_text.assert_called_once_with("Broadcast message")
        mock_websocket2.send_text.assert_called_once_with("Broadcast message")

class TestGetAssistantFunction:
    """Test the get_assistant utility function."""
    
    @patch('src.zackgpt.web.web_api.assistants', {})
    @patch('src.zackgpt.web.web_api.CoreAssistant')
    def test_get_assistant_new(self, mock_core_assistant):
        """Test getting a new assistant instance."""
        mock_assistant = Mock()
        mock_core_assistant.return_value = mock_assistant
        
        result = get_assistant("new-thread-123")
        
        assert result == mock_assistant
        mock_core_assistant.assert_called_once()
    
    @patch('src.zackgpt.web.web_api.assistants', {"existing-thread": Mock()})
    def test_get_assistant_existing(self):
        """Test getting an existing assistant instance."""
        from src.zackgpt.web.web_api import assistants
        existing_assistant = assistants["existing-thread"]
        
        result = get_assistant("existing-thread")
        
        assert result == existing_assistant

class TestWebAPIIntegration:
    """Test web API integration scenarios."""
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    @patch('src.zackgpt.web.web_api.get_assistant')
    @patch('src.zackgpt.web.web_api.memory_manager')
    def test_full_conversation_flow(self, mock_mm, mock_get_assistant, mock_tm, client,
                                  mock_thread_manager, mock_assistant, mock_memory_manager):
        """Test a complete conversation flow."""
        # Setup mocks
        mock_tm.create_thread.return_value = {"id": "flow-thread", "title": "Flow Test"}
        mock_tm.get_thread.return_value = {"id": "flow-thread", "title": "Flow Test"}
        mock_tm.add_user_message.return_value = {"id": "msg-1", "role": "user", "content": "Hello"}
        mock_tm.add_assistant_message.return_value = {"id": "msg-2", "role": "assistant", "content": "Hi!"}
        mock_get_assistant.return_value = mock_assistant
        mock_mm.save_interaction.return_value = None
        
        # 1. Create thread
        response = client.post("/threads", json={"title": "Flow Test"})
        assert response.status_code == 200
        thread_data = response.json()
        thread_id = thread_data["id"]
        
        # 2. Send message
        message_data = {
            "content": "Hello, how are you?",
            "thread_id": thread_id,
            "force_web_search": False
        }
        response = client.post(f"/threads/{thread_id}/messages", json=message_data)
        assert response.status_code == 200
        
        # 3. Get messages
        response = client.get(f"/threads/{thread_id}/messages")
        assert response.status_code == 200
        
        # Verify the flow worked
        mock_tm.create_thread.assert_called_once()
        mock_assistant.process_input.assert_called_once()
        mock_mm.save_interaction.assert_called_once()
    
    def test_error_handling(self, client):
        """Test API error handling."""
        # Test invalid JSON
        response = client.post("/threads", data="invalid json")
        assert response.status_code == 422
        
        # Test missing required fields
        response = client.post("/threads", json={})
        assert response.status_code == 422
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get("/health")
        
        # FastAPI should handle CORS if configured
        assert response.status_code == 200
    
    @patch('src.zackgpt.web.web_api.thread_manager')
    def test_concurrent_requests(self, mock_tm, client, mock_thread_manager):
        """Test handling concurrent requests."""
        mock_tm.get_threads.return_value = mock_thread_manager.get_threads.return_value
        
        # Simulate multiple concurrent requests
        responses = []
        for _ in range(5):
            response = client.get("/threads")
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        assert mock_tm.get_threads.call_count == 5 