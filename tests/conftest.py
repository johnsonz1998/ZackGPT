"""
pytest configuration and global fixtures for ZackGPT test suite
"""

import pytest
import asyncio
import os
import sys
import subprocess
import time
import requests
import signal
import psutil
from pathlib import Path
from typing import Optional
import glob

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Test environment configuration
TEST_CONFIG = {
    "OPENAI_API_KEY": "test-key-12345",
    "OPENAI_MODEL": "gpt-4",
    "TEST_DATABASE_URL": "sqlite:///test_memory.db",
    "TEST_MODE": "True",
    "DEBUG_MODE": "True",
    "LOG_LEVEL": "DEBUG"
}

# Test server configuration
TEST_SERVER_CONFIG = {
    "host": "127.0.0.1",
    "port": 8000,
    "startup_timeout": 30,
    "shutdown_timeout": 10
}

class TestServerManager:
    """Manages the test backend server lifecycle."""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.server_url = f"http://{TEST_SERVER_CONFIG['host']}:{TEST_SERVER_CONFIG['port']}"
    
    def is_server_running(self) -> bool:
        """Check if the server is running and healthy."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200 and response.json().get('status') == 'healthy'
        except:
            return False
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use."""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                return True
        return False
    
    def kill_process_on_port(self, port: int):
        """Kill any process using the specified port."""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                try:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                    process.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    if psutil.pid_exists(conn.pid):
                        psutil.Process(conn.pid).kill()
    
    def start_server(self) -> bool:
        """Start the test backend server."""
        if self.is_server_running():
            print("✅ Backend server already running")
            return True
        
        # Kill any existing process on the port
        if self.is_port_in_use(TEST_SERVER_CONFIG['port']):
            print(f"🧹 Cleaning up existing process on port {TEST_SERVER_CONFIG['port']}")
            self.kill_process_on_port(TEST_SERVER_CONFIG['port'])
            time.sleep(2)
        
        print("🚀 Starting test backend server...")
        
        # Start the server process
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.zackgpt.web.web_api:app",
            "--host", TEST_SERVER_CONFIG['host'],
            "--port", str(TEST_SERVER_CONFIG['port']),
            "--log-level", "warning"  # Reduce log noise during tests
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_root,
                env={**os.environ, **TEST_CONFIG}
            )
            
            # Wait for server to be ready
            start_time = time.time()
            while time.time() - start_time < TEST_SERVER_CONFIG['startup_timeout']:
                if self.is_server_running():
                    print("✅ Test backend server started successfully")
                    return True
                time.sleep(1)
            
            print("❌ Test backend server failed to start within timeout")
            self.stop_server()
            return False
            
        except Exception as e:
            print(f"❌ Failed to start test backend server: {e}")
            return False
    
    def stop_server(self):
        """Stop the test backend server."""
        if self.process:
            try:
                # Try graceful shutdown first
                self.process.terminate()
                self.process.wait(timeout=TEST_SERVER_CONFIG['shutdown_timeout'])
                print("✅ Test backend server stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                self.process.kill()
                self.process.wait()
                print("⚠️ Test backend server force killed")
            finally:
                self.process = None

# Global test server manager
_test_server_manager = TestServerManager()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def test_server():
    """Start and stop the test backend server for the entire test session."""
    # Only start server for integration tests
    if any(marker in sys.argv for marker in ['integration', 'e2e', '--all']):
        if not _test_server_manager.start_server():
            pytest.exit("Failed to start test backend server")
    
    yield _test_server_manager
    
    # Cleanup
    _test_server_manager.stop_server()

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
def backend_url():
    """Provide the backend server URL for tests."""
    return _test_server_manager.server_url

@pytest.fixture
def backend_health_check():
    """Check if backend is healthy before running integration tests."""
    if not _test_server_manager.is_server_running():
        pytest.skip("Backend server not running")
    return True

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
        "url": f"ws://{TEST_SERVER_CONFIG['host']}:{TEST_SERVER_CONFIG['port']}/ws/test-client",
        "timeout": 30,
        "max_retries": 3
    }

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test."""
    yield
    
    # Cleanup any test database files
    test_db_files = glob.glob("test_*.db") + glob.glob("**/test_*.db", recursive=True)
    for db_file in test_db_files:
        try:
            if os.path.exists(db_file):
                os.remove(db_file)
        except:
            pass

@pytest.fixture
def clean_database():
    """Provide a clean in-memory database for testing."""
    from unittest.mock import patch, Mock
    
    # Mock OpenAI to prevent real API calls
    with patch('src.zackgpt.core.database.OpenAI') as mock_openai_class:
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock embedding response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        
        from src.zackgpt.core.database import ZackGPTDatabase
        db = ZackGPTDatabase(":memory:")
        yield db
        # Cleanup is automatic for in-memory databases

# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.performance = pytest.mark.performance 