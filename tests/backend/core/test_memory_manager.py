"""
Memory Manager Unit Tests
Tests for memory management, persistence, and retrieval functionality
"""

import pytest
import os
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.zackgpt.data.memory_manager import MemoryManager as PersistentMemoryManager

@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    with patch('src.zackgpt.core.database.OpenAI') as mock_openai_class:
        # Mock the OpenAI client and embeddings
        mock_client = Mock()
        mock_embeddings = Mock()
        
        # Create a counter to generate unique embeddings
        call_count = 0
        def create_unique_embedding(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Generate very different embeddings to ensure low similarity
            # Use different patterns for each call
            if call_count % 2 == 1:
                embedding = [1.0] * 768 + [0.0] * 768  # First half 1.0, second half 0.0
            else:
                embedding = [0.0] * 768 + [1.0] * 768  # First half 0.0, second half 1.0
            return Mock(data=[Mock(embedding=embedding)])
        
        mock_embeddings.create.side_effect = create_unique_embedding
        mock_client.embeddings = mock_embeddings
        mock_openai_class.return_value = mock_client
        yield mock_client

@pytest.fixture
def memory_manager(mock_openai):
    """Create a test memory manager instance with mocked OpenAI."""
    import uuid
            # Mock get_database to return a fresh test database
    with patch('src.zackgpt.data.memory_manager.get_database') as mock_get_db:
        from src.zackgpt.data.database import Database as ZackGPTDatabase
        test_db_name = f"test_memory_{uuid.uuid4().hex[:8]}"
        mongo_uri = f"mongodb://localhost:27017/{test_db_name}"
        test_db = ZackGPTDatabase(mongo_uri)
        mock_get_db.return_value = test_db
        yield PersistentMemoryManager()
        # Cleanup
        try:
            test_db.client.drop_database(test_db_name)
        except:
            pass

@pytest.fixture
def sample_memory():
    """Create a sample memory for testing."""
    return {
        "question": "Test question?",
        "answer": "Test answer",
        "agent": "test_agent",
        "importance": "medium",
        "tags": ["test", "sample"]
    }

class TestMemoryManagerBasics:
    """Test basic MemoryManager functionality."""
    
    def test_memory_manager_creation(self, memory_manager):
        """Test MemoryManager instantiation."""
        assert memory_manager is not None
        assert hasattr(memory_manager, 'db')
        assert hasattr(memory_manager, 'save_memory')
        assert hasattr(memory_manager, 'get_memory')
    
    def test_memory_creation(self, memory_manager, sample_memory):
        """Test memory creation."""
        memory_id = memory_manager.save_memory(**sample_memory)
        assert memory_id is not None
        
        # Verify memory was saved
        saved_memory = memory_manager.get_memory(memory_id)
        assert saved_memory is not None
        assert saved_memory['question'] == sample_memory['question']
        assert saved_memory['answer'] == sample_memory['answer']

class TestMemoryOperations:
    """Test memory operations and management."""
    
    def test_save_memory(self, memory_manager, sample_memory):
        """Test saving a memory."""
        memory_id = memory_manager.save_memory(**sample_memory)
        assert memory_id is not None
        
        # Verify memory exists
        saved_memory = memory_manager.get_memory(memory_id)
        assert saved_memory is not None
        assert saved_memory['question'] == sample_memory['question']
    
    def test_get_memory(self, memory_manager, sample_memory):
        """Test retrieving a memory."""
        memory_id = memory_manager.save_memory(**sample_memory)
        retrieved_memory = memory_manager.get_memory(memory_id)
        assert retrieved_memory is not None
        assert retrieved_memory['question'] == sample_memory['question']
    
    def test_update_memory(self, memory_manager, sample_memory):
        """Test updating a memory."""
        memory_id = memory_manager.save_memory(**sample_memory)
        updated_answer = "Updated answer"
        success = memory_manager.update_memory(memory_id, answer=updated_answer)
        assert success
        
        updated_memory = memory_manager.get_memory(memory_id)
        assert updated_memory['answer'] == updated_answer
    
    def test_delete_memory(self, memory_manager, sample_memory):
        """Test deleting a memory."""
        memory_id = memory_manager.save_memory(**sample_memory)
        success = memory_manager.delete_memory(memory_id)
        assert success
        
        # Verify memory is deleted
        deleted_memory = memory_manager.get_memory(memory_id)
        assert deleted_memory is None

class TestMemoryQueries:
    """Test memory querying and filtering."""
    
    def test_query_memories(self, memory_manager):
        """Test querying memories."""
        # Add test memories
        memory1 = {
            "question": "What is Python?",
            "answer": "Python is a programming language",
            "agent": "test_agent",
            "importance": "high",
            "tags": ["programming", "python"]
        }
        memory2 = {
            "question": "What is Java?",
            "answer": "Java is another programming language",
            "agent": "test_agent",
            "importance": "medium",
            "tags": ["programming", "java"]
        }
        
        memory_manager.save_memory(**memory1)
        memory_manager.save_memory(**memory2)
        
        # Query memories
        results = memory_manager.query_memories(
            query="programming language",
            limit=2
        )
        assert len(results) > 0
        assert any("Python" in m['answer'] for m in results)
    
    def test_query_memories_by_agent(self, memory_manager):
        """Test querying memories by agent."""
        # Add test memories with different agents
        memory1 = {
            "question": "Test question 1",
            "answer": "Test answer 1",
            "agent": "agent1",
            "importance": "medium"
        }
        memory2 = {
            "question": "Test question 2",
            "answer": "Test answer 2",
            "agent": "agent2",
            "importance": "medium"
        }
        
        memory_manager.save_memory(**memory1)
        memory_manager.save_memory(**memory2)
        
        # Query memories by agent
        results = memory_manager.query_memories(
            query="test",
            agent="agent1"
        )
        assert len(results) == 1
        assert results[0]['agent'] == "agent1"

class TestMemoryContext:
    """Test memory context and retrieval."""
    
    def test_get_relevant_context(self, memory_manager):
        """Test getting relevant context from memories."""
        # Add test memories
        memory1 = {
            "question": "What is the capital of France?",
            "answer": "Paris is the capital of France",
            "agent": "test_agent",
            "importance": "high"
        }
        memory2 = {
            "question": "What is the population of Paris?",
            "answer": "Paris has about 2.2 million people",
            "agent": "test_agent",
            "importance": "medium"
        }
        
        memory_manager.save_memory(**memory1)
        memory_manager.save_memory(**memory2)
        
        # Get context for a related query
        context = memory_manager.get_relevant_context(
            query="Tell me about Paris",
            max_memories=2
        )
        assert "Paris" in context
        assert "capital" in context
        assert "population" in context
    
    def test_build_memory_context(self, memory_manager):
        """Test building comprehensive memory context."""
        # Add test memories
        memory1 = {
            "question": "What is Python?",
            "answer": "Python is a programming language",
            "agent": "test_agent",
            "importance": "high",
            "tags": ["programming"]
        }
        
        memory_manager.save_memory(**memory1)
        
        # Build context
        context = memory_manager.build_memory_context(
            query="Tell me about programming languages",
            include_metadata=True
        )
        assert "context" in context
        assert "memory_count" in context
        assert "memories" in context
        assert context["memory_count"] > 0

# Test runner for standalone execution
if __name__ == "__main__":
    print("🧪 Running Memory Manager Unit Tests")
    print("=" * 60)
    
    test_classes = [
        TestMemoryManagerBasics,
        TestMemoryOperations,
        TestMemoryQueries,
        TestMemoryContext
    ]
    
    for test_class in test_classes:
        print(f"\n🔧 Running {test_class.__name__}...")
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    print(f"  • {method_name}...")
                    getattr(instance, method_name)()
                except Exception as e:
                    print(f"    ❌ Failed: {e}")
                else:
                    print(f"    ✅ Passed")
    
    print("\n🎉 Memory Manager Unit Tests Complete!") 