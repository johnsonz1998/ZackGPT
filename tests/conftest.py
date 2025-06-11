"""
pytest configuration and global fixtures for ZackGPT test suite
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Test environment configuration
TEST_CONFIG = {
    "OPENAI_API_KEY": "test-key-12345",
    "OPENAI_MODEL": "gpt-4",
    "TEST_DATABASE_URL": "sqlite:///test_memory.db",
    "TEST_MODE": True,
    "DEBUG_MODE": True,
    "LOG_LEVEL": "DEBUG"
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables for each test."""
    original_env = {}
    
    # Store original values
    for key, value in TEST_CONFIG.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = str(value)
    
    yield
    
    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from the AI assistant.",
                    "role": "assistant"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 15,
            "total_tokens": 25
        }
    }

@pytest.fixture
def sample_thread_data():
    """Sample thread data for testing."""
    return {
        "id": "test-thread-123",
        "title": "Test Thread",
        "created_at": "2025-06-11T03:00:00Z",
        "updated_at": "2025-06-11T03:00:00Z",
        "message_count": 0
    }

@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "id": "test-message-456",
        "role": "user",
        "content": "Hello, this is a test message!",
        "timestamp": "2025-06-11T03:00:00Z",
        "thread_id": "test-thread-123"
    }

@pytest.fixture
def websocket_test_client():
    """WebSocket test client configuration."""
    return {
        "url": "ws://localhost:8000/ws/test-client",
        "timeout": 30,
        "max_retries": 3
    }

# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.performance = pytest.mark.performance 