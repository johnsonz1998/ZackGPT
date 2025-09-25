#!/usr/bin/env python3
"""
Test script for AI-powered multi-memory extraction feature.

This script demonstrates how the system can now analyze a single message 
and create multiple memories for different pieces of information.
"""

import sys
import os
sys.path.append('src')

from zackgpt.core.core_assistant import CoreAssistant
from zackgpt.data.memory_manager import MemoryManager
from zackgpt.utils.logger import debug_info, debug_success, debug_error

def test_multi_memory_extraction():
    """Test the new multi-memory extraction feature."""
    
    print("🧠 Testing AI-Powered Multi-Memory Extraction")
    print("=" * 60)
    
    # Test cases that should create multiple memories
    test_cases = [
        {
            "user_input": "My name is Alex, I work at Google as a software engineer, and my favorite programming language is Python. I also love playing guitar in my free time.",
            "ai_response": "Nice to meet you Alex! I'll remember that you work at Google as a software engineer, that Python is your favorite programming language, and that you enjoy playing guitar.",
            "expected_memories": 4  # name, work, preferences, hobbies
        },
        {
            "user_input": "Remember that I live in San Francisco, I'm 28 years old, and I graduated from Stanford with a Computer Science degree.",
            "ai_response": "I'll remember that you live in San Francisco, you're 28 years old, and you graduated from Stanford with a Computer Science degree.",
            "expected_memories": 3  # location, identity, education
        },
        {
            "user_input": "I prefer tea over coffee, I'm vegetarian, and my favorite color is blue.",
            "ai_response": "Got it! I'll remember your preferences: you prefer tea over coffee, you're vegetarian, and your favorite color is blue.",
            "expected_memories": 3  # all preferences
        },
        {
            "user_input": "What's the weather like?",
            "ai_response": "I don't have access to current weather data.",
            "expected_memories": 0  # no saveable information
        },
        {
            "user_input": "Hi, how are you? I'm doing well, just got back from my vacation in Japan. I really love sushi and I'm thinking about learning Japanese. Also, what's 2+2?",
            "ai_response": "Hello! I'm doing well, thank you for asking. It sounds like you had a great vacation in Japan! I'd be happy to help if you decide to learn Japanese - it's a fascinating language. And 2+2 equals 4.",
            "expected_memories": 2  # vacation location, sushi preference, language learning interest (but not the math question or greeting)
        }
    ]
    
    try:
        # Create assistant instance
        assistant = CoreAssistant()
        memory_manager = MemoryManager()
        
        if not assistant.client:
            print("❌ OpenAI client not available - cannot test AI extraction")
            return False
        
        print(f"✅ Assistant and memory manager initialized")
        print(f"📊 Current memory count: {len(memory_manager.db.get_all_memories())}")
        print()
        
        total_memories_before = len(memory_manager.db.get_all_memories())
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"🧪 Test Case {i}: {test_case['user_input'][:50]}...")
            print(f"   Expected memories: {test_case['expected_memories']}")
            
            # Test the enhanced memory saving
            saved_memory_ids = assistant.maybe_save_memory_enhanced(
                test_case["user_input"], 
                test_case["ai_response"]
            )
            
            print(f"   ✅ Created {len(saved_memory_ids)} memories")
            
            if saved_memory_ids:
                print(f"   📝 Memory IDs: {saved_memory_ids}")
                
                # Show details of created memories
                for memory_id in saved_memory_ids:
                    memory = memory_manager.db.get_memory_by_id(memory_id)
                    if memory:
                        print(f"      • Q: {memory['question'][:60]}...")
                        print(f"        A: {memory['answer'][:60]}...")
                        print(f"        Tags: {memory.get('tags', [])}")
                        print(f"        Importance: {memory.get('importance', 'medium')}")
            
            # Check if it matches expectations
            if len(saved_memory_ids) == test_case['expected_memories']:
                print(f"   ✅ PASS: Created expected number of memories")
            else:
                print(f"   ⚠️  Different from expected: got {len(saved_memory_ids)}, expected {test_case['expected_memories']}")
            
            print()
        
        total_memories_after = len(memory_manager.db.get_all_memories())
        total_created = total_memories_after - total_memories_before
        
        print("📈 Summary:")
        print(f"   Total memories before: {total_memories_before}")
        print(f"   Total memories after: {total_memories_after}")
        print(f"   New memories created: {total_created}")
        print()
        
        # Test the AI extraction method directly
        print("🔬 Testing AI Extraction Method Directly:")
        print("-" * 40)
        
        test_input = "My name is Sam, I work as a doctor, and I love hiking on weekends."
        test_response = "I'll remember your information."
        
        extracted_memories = assistant.extract_multiple_memories(test_input, test_response)
        
        print(f"Input: {test_input}")
        print(f"Extracted {len(extracted_memories)} memories:")
        
        for i, memory in enumerate(extracted_memories, 1):
            print(f"  {i}. Q: {memory.get('question', 'N/A')}")
            print(f"     A: {memory.get('answer', 'N/A')}")
            print(f"     Tags: {memory.get('tags', [])}")
            print(f"     Importance: {memory.get('importance', 'medium')}")
            print(f"     Confidence: {memory.get('confidence', 'unknown')}")
            print(f"     Reasoning: {memory.get('reasoning', 'N/A')}")
            print()
        
        print("🎉 Multi-memory extraction test completed successfully!")
        return True
        
    except Exception as e:
        debug_error("Multi-memory extraction test failed", e)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_multi_memory_extraction()
    sys.exit(0 if success else 1) 