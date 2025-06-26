import sys
sys.path.insert(0, 'src')

import asyncio
from zackgpt.data.thread_manager import ThreadManager
from zackgpt.data.memory_manager import MemoryManager
from zackgpt.core.core_assistant import CoreAssistant

async def test_endpoint_logic():
    print("Testing web endpoint logic...")
    
    # Initialize components like the web API does
    thread_manager = ThreadManager()
    memory_manager = MemoryManager()
    
    # Use an existing thread or create one
    threads = thread_manager.get_all_threads()
    if threads:
        thread_id = threads[0]["id"]
        print(f"Using existing thread: {thread_id}")
    else:
        thread_id = thread_manager.create_thread("Test Thread")
        print(f"Created new thread: {thread_id}")
    
    if not thread_id:
        print("❌ Failed to get/create thread")
        return
    
    print("✅ Thread ready")
    
    # Test adding user message
    print("Adding user message...")
    user_message = thread_manager.add_user_message(thread_id, "Hello test message")
    print(f"User message: {user_message}")
    
    # Test getting AI response  
    print("Getting AI response...")
    assistant = CoreAssistant()
    ai_response = assistant.process_input("Hello test message")
    print(f"AI response: {ai_response[:100]}...")
    
    # Test adding assistant message
    print("Adding assistant message...")
    assistant_message = thread_manager.add_assistant_message(thread_id, ai_response)
    print(f"Assistant message: {assistant_message}")
    
    # Test saving to memory
    print("Saving interaction to memory...")
    memory_notification = memory_manager.save_interaction_with_notification(
        "Hello test message", ai_response, agent="core_assistant", thread_id=thread_id
    )
    print(f"Memory notification: {memory_notification}")
    
    print("✅ All endpoint logic working!")

if __name__ == "__main__":
    asyncio.run(test_endpoint_logic())
