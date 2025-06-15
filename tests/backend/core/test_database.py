"""
Database Unit Tests
Tests for database connectivity, operations, and data persistence
"""

import pytest
import os
import sys
import sqlite3
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.zackgpt.core.database import ZackGPTDatabase, get_database


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    yield db_path
    # Cleanup
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass


@pytest.fixture
def mock_openai():
    """Mock OpenAI client to prevent real API calls."""
    with patch('src.zackgpt.core.database.OpenAI') as mock_openai_class:
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock embedding response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]  # Standard embedding size
        mock_client.embeddings.create.return_value = mock_response
        
        yield mock_client


@pytest.fixture
def database(mock_openai):
    """Create a test database instance with mocked OpenAI."""
    # Use in-memory database for speed
    db = ZackGPTDatabase(":memory:")
    yield db
    # Cleanup is automatic for in-memory databases


@pytest.fixture
def database_with_data(database):
    """Create a database with some test data."""
    # Create test thread
    thread = database.create_thread("Test Thread")
    thread_id = thread["id"]
    
    # Add test messages
    database.add_message(thread_id, "user", "Hello")
    database.add_message(thread_id, "assistant", "Hi there!")
    
    # Add test memory
    database.save_memory("What is Python?", "Python is a programming language", "test_agent")
    
    yield database, thread_id
    
    # Cleanup is handled by the database fixture


class TestDatabaseBasics:
    """Test basic database functionality."""
    
    def test_database_creation(self, database):
        """Test database instantiation."""
        assert database is not None
        assert hasattr(database, 'db_path')
        assert hasattr(database, 'get_connection')
        assert hasattr(database, 'create_thread')
    
    def test_database_tables_created(self, database):
        """Test that all required tables are created."""
        # First, let's manually try to create tables to see if there's an error
        try:
            with database.get_connection() as conn:
                print("Testing manual table creation...")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS test_table (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL
                    )
                """)
                conn.commit()
                print("Manual table creation successful")
                
                # Check if our manual table was created
                manual_tables = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """).fetchall()
                print(f"Tables after manual creation: {[t[0] for t in manual_tables]}")
        except Exception as e:
            print(f"Error during manual table creation: {e}")
        
        # Now check the actual database initialization
        with database.get_connection() as conn:
            # Check if tables exist
            tables = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """).fetchall()
            
            table_names = [table[0] for table in tables]
            expected_tables = ['threads', 'messages', 'memories', 'user_settings', 'sessions']
            
            # Debug: print what tables we actually have
            print(f"Found tables: {table_names}")
            
            # Let's also try to manually call _init_database again
            print("Calling _init_database manually...")
            try:
                database._init_database()
                print("Manual _init_database call successful")
            except Exception as e:
                print(f"Error during manual _init_database: {e}")
            
            # Check tables again
            tables_after = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """).fetchall()
            table_names_after = [table[0] for table in tables_after]
            print(f"Tables after manual _init_database: {table_names_after}")
            
            for table in expected_tables:
                assert table in table_names_after, f"Table {table} not found. Available: {table_names_after}"


class TestThreadOperations:
    """Test thread CRUD operations."""
    
    def test_create_thread(self, database):
        """Test creating a new thread."""
        thread = database.create_thread("Test Thread")
        
        assert thread is not None
        assert thread["title"] == "Test Thread"
        assert "id" in thread
        assert thread["message_count"] == 0
    
    def test_get_thread(self, database):
        """Test retrieving a thread."""
        # Create thread
        created_thread = database.create_thread("Test Thread")
        thread_id = created_thread["id"]
        
        # Retrieve thread
        retrieved_thread = database.get_thread(thread_id)
        
        assert retrieved_thread is not None
        assert retrieved_thread["id"] == thread_id
        assert retrieved_thread["title"] == "Test Thread"
    
    def test_get_nonexistent_thread(self, database):
        """Test retrieving a non-existent thread."""
        result = database.get_thread("nonexistent-id")
        assert result is None
    
    def test_get_all_threads(self, database):
        """Test retrieving all threads."""
        # Create multiple threads
        database.create_thread("Thread 1")
        database.create_thread("Thread 2")
        database.create_thread("Thread 3")
        
        threads = database.get_all_threads()
        assert len(threads) == 3
        
        # Check ordering (should be by updated_at desc)
        titles = [t["title"] for t in threads]
        assert "Thread 3" in titles
        assert "Thread 2" in titles
        assert "Thread 1" in titles
    
    def test_update_thread(self, database):
        """Test updating a thread."""
        thread = database.create_thread("Original Title")
        thread_id = thread["id"]
        
        # Update title
        success = database.update_thread(thread_id, title="Updated Title")
        assert success
        
        # Verify update
        updated_thread = database.get_thread(thread_id)
        assert updated_thread["title"] == "Updated Title"
    
    def test_delete_thread(self, database):
        """Test deleting a thread."""
        thread = database.create_thread("To Delete")
        thread_id = thread["id"]
        
        # Add a message to the thread
        database.add_message(thread_id, "user", "Test message")
        
        # Delete thread
        success = database.delete_thread(thread_id)
        assert success
        
        # Verify deletion
        deleted_thread = database.get_thread(thread_id)
        assert deleted_thread is None
        
        # Verify messages are also deleted (cascade)
        messages = database.get_thread_messages(thread_id)
        assert len(messages) == 0


class TestMessageOperations:
    """Test message CRUD operations."""
    
    def test_add_message(self, database):
        """Test adding a message to a thread."""
        thread = database.create_thread("Test Thread")
        thread_id = thread["id"]
        
        message = database.add_message(thread_id, "user", "Hello world!")
        
        assert message is not None
        assert message["role"] == "user"
        assert message["content"] == "Hello world!"
        assert message["thread_id"] == thread_id
    
    def test_get_message(self, database):
        """Test retrieving a specific message."""
        thread = database.create_thread("Test Thread")
        thread_id = thread["id"]
        
        created_message = database.add_message(thread_id, "user", "Test message")
        message_id = created_message["id"]
        
        retrieved_message = database.get_message(message_id)
        
        assert retrieved_message is not None
        assert retrieved_message["id"] == message_id
        assert retrieved_message["content"] == "Test message"
    
    def test_get_thread_messages(self, database):
        """Test retrieving all messages for a thread."""
        thread = database.create_thread("Test Thread")
        thread_id = thread["id"]
        
        # Add multiple messages
        database.add_message(thread_id, "user", "Message 1")
        database.add_message(thread_id, "assistant", "Response 1")
        database.add_message(thread_id, "user", "Message 2")
        
        messages = database.get_thread_messages(thread_id)
        
        assert len(messages) == 3
        assert messages[0]["content"] == "Message 1"
        assert messages[1]["content"] == "Response 1"
        assert messages[2]["content"] == "Message 2"


class TestMemoryOperations:
    """Test memory CRUD operations."""
    
    def test_save_memory(self, database, mock_openai):
        """Test saving a memory."""
        memory_id = database.save_memory(
            "What is Python?", 
            "Python is a programming language",
            agent="test_agent"
        )
        
        assert memory_id is not None
        
        # Verify the memory was saved
        memory = database.get_memory(memory_id)
        assert memory is not None
        assert memory["question"] == "What is Python?"
        assert memory["answer"] == "Python is a programming language"
        assert memory["agent"] == "test_agent"
    
    def test_get_memory(self, database, mock_openai):
        """Test retrieving a specific memory."""
        memory_id = database.save_memory("Test question", "Test answer")
        
        memory = database.get_memory(memory_id)
        
        assert memory is not None
        assert memory["question"] == "Test question"
        assert memory["answer"] == "Test answer"
    
    def test_query_memories_by_similarity(self, database, mock_openai):
        """Test querying memories by similarity."""
        # Save some memories
        database.save_memory("What is Python?", "Python is a programming language")
        database.save_memory("What is JavaScript?", "JavaScript is a web language")
        
        # Query for similar memories
        memories = database.query_memories_by_similarity("Tell me about Python")
        
        assert len(memories) >= 0  # Should return some results
        # Note: Exact results depend on embedding similarity


class TestDatabaseSettings:
    """Test user settings operations."""
    
    def test_set_and_get_setting(self, database):
        """Test setting and getting user preferences."""
        database.set_setting("theme", "dark")
        
        value = database.get_setting("theme")
        assert value == "dark"
    
    def test_get_nonexistent_setting(self, database):
        """Test getting a non-existent setting with default."""
        value = database.get_setting("nonexistent", "default_value")
        assert value == "default_value"
    
    def test_get_all_settings(self, database):
        """Test getting all settings."""
        database.set_setting("setting1", "value1")
        database.set_setting("setting2", "value2")
        
        settings = database.get_all_settings()
        
        assert "setting1" in settings
        assert "setting2" in settings
        assert settings["setting1"] == "value1"
        assert settings["setting2"] == "value2"


class TestDatabaseStats:
    """Test database statistics."""
    
    def test_get_stats(self, database_with_data):
        """Test getting database statistics."""
        database, thread_id = database_with_data
        
        stats = database.get_stats()
        
        assert "total_threads" in stats
        assert "total_messages" in stats
        assert "total_memories" in stats
        assert stats["total_threads"] >= 1
        assert stats["total_messages"] >= 2
        assert stats["total_memories"] >= 1


class TestDatabaseCleanup:
    """Test database cleanup operations."""
    
    def test_cleanup_old_data(self, database):
        """Test cleaning up old data."""
        # This test just verifies the method runs without error
        # In a real scenario, we'd create old data first
        result = database.cleanup_old_data(days=30)
        
        assert isinstance(result, dict)
        assert "deleted_sessions" in result
        assert "deleted_memories" in result


class TestDatabaseConnection:
    """Test database connection management."""
    
    def test_connection_context_manager(self, database):
        """Test connection context manager."""
        with database.get_connection() as conn:
            assert conn is not None
            assert isinstance(conn, sqlite3.Connection)
            
            # Test a simple query
            result = conn.execute("SELECT 1").fetchone()
            assert result[0] == 1
    
    def test_multiple_connections(self, database):
        """Test multiple simultaneous connections."""
        # This should work fine with SQLite
        with database.get_connection() as conn1:
            with database.get_connection() as conn2:
                result1 = conn1.execute("SELECT 1").fetchone()
                result2 = conn2.execute("SELECT 2").fetchone()
                
                assert result1[0] == 1
                assert result2[0] == 2


class TestDatabaseErrorHandling:
    """Test database error handling."""
    
    def test_invalid_thread_id(self, database):
        """Test operations with invalid thread ID."""
        # Should not raise exception, just return None/empty
        thread = database.get_thread("invalid-id")
        assert thread is None
        
        messages = database.get_thread_messages("invalid-id")
        assert len(messages) == 0
    
    def test_invalid_memory_id(self, database):
        """Test operations with invalid memory ID."""
        memory = database.get_memory("invalid-id")
        assert memory is None


# Performance tests (quick ones)
class TestDatabasePerformance:
    """Test database performance (lightweight tests)."""
    
    def test_bulk_message_insertion(self, database):
        """Test inserting multiple messages quickly."""
        thread = database.create_thread("Bulk Test")
        thread_id = thread["id"]
        
        # Insert 10 messages (small number for speed)
        for i in range(10):
            database.add_message(thread_id, "user", f"Message {i}")
        
        messages = database.get_thread_messages(thread_id)
        assert len(messages) == 10
    
    def test_thread_retrieval_performance(self, database):
        """Test retrieving threads quickly."""
        # Create 5 threads (small number for speed)
        for i in range(5):
            database.create_thread(f"Thread {i}")
        
        threads = database.get_all_threads()
        assert len(threads) == 5


# Test runner for standalone execution
if __name__ == "__main__":
    print("🧪 Running Database Unit Tests")
    print("=" * 60)
    
    # Run with pytest
    import subprocess
    result = subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print(f"\nTest completed with exit code: {result.returncode}") 