#!/usr/bin/env python3
"""
Quick test script to verify ZackGPT database persistence works correctly.
"""
import sys
import os
sys.path.append('src')

from src.zackgpt.core.database import get_database
from src.zackgpt.core.thread_manager import PersistentThreadManager
from src.zackgpt.core.memory_manager import PersistentMemoryManager

def test_database_setup():
    """Test basic database setup and connectivity."""
    print("🔧 Testing database setup...")
    
    db = get_database()
    stats = db.get_stats()
    
    print(f"✅ Database initialized successfully")
    print(f"   Path: {db.db_path}")
    print(f"   Threads: {stats['threads']['total']}")
    print(f"   Memories: {stats['memories']['total']}")
    print(f"   Database size: {stats['database']['size_mb']} MB")
    
    # Proper pytest assertions
    assert db is not None
    assert db.db_path is not None
    assert stats['threads']['total'] >= 0
    assert stats['memories']['total'] >= 0
    assert stats['database']['size_mb'] > 0

def test_thread_operations():
    """Test thread and message operations."""
    print("\n💬 Testing thread operations...")
    
    thread_manager = PersistentThreadManager()
    
    # Create a test thread
    thread = thread_manager.create_thread("Test Thread - Database Check")
    print(f"✅ Created thread: {thread.id}")
    
    # Add some messages
    user_msg = thread_manager.add_user_message(thread.id, "Hello, this is a test message!")
    assistant_msg = thread_manager.add_assistant_message(thread.id, "Hello! I can see your message in the database.")
    
    print(f"✅ Added user message: {user_msg.id}")
    print(f"✅ Added assistant message: {assistant_msg.id}")
    
    # Retrieve messages
    messages = thread_manager.get_messages(thread.id)
    print(f"✅ Retrieved {len(messages)} messages from database")
    
    # Get conversation history
    history = thread_manager.get_conversation_history(thread.id)
    print(f"✅ Conversation history has {len(history)} entries")
    
    # Get all threads
    all_threads = thread_manager.get_all_threads()
    print(f"✅ Total threads in database: {len(all_threads)}")
    
    # Proper pytest assertions
    assert thread is not None
    assert thread.id is not None
    assert user_msg.id is not None
    assert assistant_msg.id is not None
    assert len(messages) == 2
    assert len(history) == 2
    assert len(all_threads) >= 1

def test_memory_operations():
    """Test memory operations."""
    print("\n🧠 Testing memory operations...")
    
    memory_manager = PersistentMemoryManager()
    
    # Test memory saving
    memory_id = memory_manager.save_memory(
        question="What is my favorite food?",
        answer="Your favorite food is pizza. You've mentioned it several times!",
        agent="test_assistant",
        importance="high",
        tags=["preferences", "food"]
    )
    
    if memory_id:
        print(f"✅ Saved memory: {memory_id}")
    else:
        print("ℹ️  Memory not saved (likely due to deduplication)")
    
    # Test memory querying
    memories = memory_manager.query_memories("favorite food", limit=3)
    print(f"✅ Found {len(memories)} relevant memories")
    
    for memory in memories[:2]:  # Show first 2
        print(f"   📝 {memory['question'][:50]}... (similarity: {memory.get('similarity', 0):.3f})")
    
    # Test context building
    context = memory_manager.build_memory_context("what do you remember about me?")
    print(f"✅ Built memory context: {len(context['context'])} chars, {context['memory_count']} memories")
    
    # Test interaction saving
    interaction_id = memory_manager.save_interaction(
        "My name is Zack and I love coding",
        "Nice to meet you, Zack! I'll remember that you love coding.",
        agent="test_assistant"
    )
    
    if interaction_id:
        print(f"✅ Saved interaction as memory: {interaction_id}")
    else:
        print("ℹ️  Interaction not saved (didn't meet criteria)")
    
    # Proper pytest assertions 
    assert memory_manager is not None
    assert isinstance(memories, list)
    assert isinstance(context, dict)
    assert 'context' in context
    assert 'memory_count' in context

def test_integration():
    """Test integration between components."""
    print("\n🔗 Testing component integration...")
    
    # Test that the managers can work together
    thread_manager = PersistentThreadManager()
    memory_manager = PersistentMemoryManager()
    
    # Create a thread and save some interactions
    thread = thread_manager.create_thread("Integration Test Thread")
    
    # Simulate a conversation
    user_msg = thread_manager.add_user_message(thread.id, "Hello! My favorite color is blue.")
    assistant_msg = thread_manager.add_assistant_message(thread.id, "Hello! I'll remember that your favorite color is blue.")
    
    # Save the interaction to memory
    memory_id = memory_manager.save_interaction(user_msg.content, assistant_msg.content)
    
    # Query for related memories
    related_memories = memory_manager.query_memories("favorite color")
    
    print(f"✅ Integration test complete:")
    print(f"   Thread: {thread.id}")
    print(f"   Messages: {user_msg.id}, {assistant_msg.id}")
    print(f"   Memory: {memory_id}")
    print(f"   Related memories found: {len(related_memories)}")
    
    # Proper pytest assertions
    assert thread_manager is not None
    assert memory_manager is not None
    assert thread.id is not None
    assert user_msg.id is not None
    assert assistant_msg.id is not None
    assert isinstance(related_memories, list)

def cleanup_test_data(thread_id):
    """Clean up test data."""
    print(f"\n🧹 Cleaning up test data...")
    
    thread_manager = PersistentThreadManager()
    
    # Delete the test thread
    success = thread_manager.delete_thread(thread_id)
    if success:
        print(f"✅ Deleted test thread: {thread_id}")
    else:
        print(f"❌ Failed to delete test thread: {thread_id}")

def main():
    """Run all tests."""
    print("🎯 ZackGPT Database System Test")
    print("=" * 50)
    
    try:
        # Test basic setup
        test_database_setup()
        
        # Test thread operations
        thread_id = test_thread_operations()
        
        # Test memory operations
        test_memory_operations()
        
        # Test integration
        test_integration()
        
        # Cleanup
        cleanup_test_data(thread_id)
        
        print("\n🎉 All tests passed! Database system is working correctly.")
        print("\n📋 Summary:")
        print("   ✅ Database setup and connectivity")
        print("   ✅ Thread and message persistence")
        print("   ✅ Memory storage and retrieval")
        print("   ✅ Component integration")
        print("   ✅ Data cleanup")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 