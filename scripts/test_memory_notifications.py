#!/usr/bin/env python3
"""
Test script for memory notification system
"""
import sys
import os

# Add both the source directory and the root directory to the path
root_dir = os.path.join(os.path.dirname(__file__), '..')
src_dir = os.path.join(root_dir, 'src')
sys.path.insert(0, root_dir)
sys.path.insert(0, src_dir)

try:
    from src.zackgpt.core.memory_manager import PersistentMemoryManager
    from src.zackgpt.core.logger import debug_success, debug_info, debug_error
except ImportError:
    # Fallback to direct imports
    from zackgpt.core.memory_manager import PersistentMemoryManager
    from zackgpt.core.logger import debug_success, debug_info, debug_error

def test_memory_notifications():
    """Test the memory notification system"""
    
    print("🧠 Testing Memory Notification System")
    print("=" * 50)
    
    try:
        # Initialize memory manager
        memory_manager = PersistentMemoryManager()
        debug_success("Memory manager initialized")
        
        # Test scenarios
        test_cases = [
            {
                "question": "My name is John Smith",
                "answer": "Nice to meet you, John! I'll remember your name.",
                "expected_notification": True,
                "expected_tags": ["identity"]
            },
            {
                "question": "My favorite color is blue",
                "answer": "I'll remember that your favorite color is blue.",
                "expected_notification": True,
                "expected_tags": ["preferences"]
            },
            {
                "question": "Hi there",
                "answer": "Hello! How can I help you today?",
                "expected_notification": False,
                "expected_tags": []
            },
            {
                "question": "Remember that I work at Google as a software engineer",
                "answer": "I'll remember that you work at Google as a software engineer.",
                "expected_notification": True,
                "expected_tags": ["work", "memory"]
            }
        ]
        
        print("\n🧪 Running test cases...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['question'][:30]}...")
            
            # Test the notification system
            notification = memory_manager.save_interaction_with_notification(
                question=test_case["question"],
                answer=test_case["answer"],
                thread_id=f"test_thread_{i}"
            )
            
            # Check if notification was created as expected
            if test_case["expected_notification"]:
                if notification:
                    debug_success(f"✅ Notification created: {notification['message']}")
                    debug_info(f"   Tags: {notification['tags']}")
                    debug_info(f"   Memory ID: {notification['memory_id']}")
                    
                    # Check tags
                    expected_tags = set(test_case["expected_tags"])
                    actual_tags = set(notification['tags'])
                    
                    if expected_tags.issubset(actual_tags):
                        debug_success(f"   ✅ Tags match expectation")
                    else:
                        debug_error(f"   ❌ Tag mismatch. Expected: {expected_tags}, Got: {actual_tags}")
                else:
                    debug_error(f"❌ Expected notification but none was created")
            else:
                if notification:
                    debug_error(f"❌ Unexpected notification created: {notification}")
                else:
                    debug_success(f"✅ No notification created (as expected)")
        
        print("\n📊 Memory Statistics:")
        stats = memory_manager.get_stats()
        if isinstance(stats, dict):
            debug_info(f"Total memories: {stats.get('total', 0)}")
        else:
            debug_info(f"Total memories: {stats}")
        
        print("\n🎉 Memory notification system test completed!")
        return True
        
    except Exception as e:
        debug_error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_memory_notifications()
    sys.exit(0 if success else 1) 