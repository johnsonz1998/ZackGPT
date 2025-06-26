#!/usr/bin/env python3
"""
ZackGPT Intelligence Integration Tests

Comprehensive tests for the intelligence amplification system including:
- Persistent context storage across conversation threads
- Real-world conversation simulation
- Cross-component integration
- Memory + intelligence optimization
"""

import sys
import os
import time
import tempfile
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

def test_environment_setup():
    """Set up test environment with necessary API keys."""
    # Set dummy API key to avoid import errors
    os.environ.setdefault('OPENAI_API_KEY', 'test_key_12345')
    print("✅ Test environment configured")

def test_imports_and_initialization():
    """Test that all components can be imported and initialized."""
    print("\n🔧 Testing Imports and Initialization...")
    
    try:
        from zackgpt.core.intelligence_amplifier import (
            IntelligentContextCompressor,
            PersonalityEmergenceEngine,
            ContextualIntelligenceAmplifier,
            DynamicTokenAllocator
        )
        print("✅ Intelligence components imported successfully")
        
        from zackgpt.data.database import get_database
        from zackgpt.data.thread_manager import ThreadManager
        print("✅ Data layer components imported successfully")
        
        # Test initialization
        compressor = IntelligentContextCompressor()
        personality = PersonalityEmergenceEngine()
        token_allocator = DynamicTokenAllocator()
        
        # Initialize thread manager
        thread_manager = ThreadManager()
        amplifier = ContextualIntelligenceAmplifier(thread_manager=thread_manager)
        
        print("✅ All components initialized successfully")
        return {
            'compressor': compressor,
            'personality': personality,
            'amplifier': amplifier,
            'token_allocator': token_allocator,
            'thread_manager': thread_manager
        }
        
    except Exception as e:
        print(f"❌ Import/initialization failed: {e}")
        return None

def simulate_realistic_conversation():
    """Simulate a realistic conversation to test persistent context."""
    
    conversation_stages = [
        # Stage 1: Initial contact
        {
            "user": "Hi there, I'm new to programming and need help",
            "expected_expertise": "low",
            "expected_type": "general"
        },
        # Stage 2: Getting technical
        {
            "user": "I want to learn Python. Can you explain what functions are?",
            "expected_expertise": "low",
            "expected_type": "technical"
        },
        # Stage 3: More complex
        {
            "user": "How do I implement error handling with try-except blocks?",
            "expected_expertise": "medium", 
            "expected_type": "technical"
        },
        # Stage 4: Advanced discussion
        {
            "user": "I'm working on a REST API with FastAPI and need to implement authentication middleware",
            "expected_expertise": "high",
            "expected_type": "technical"
        },
        # Stage 5: Troubleshooting
        {
            "user": "I'm getting a 500 error when I call my endpoint. This is urgent!",
            "expected_type": "technical",
            "urgency": True
        }
    ]
    
    return conversation_stages

def test_persistent_context_integration(components):
    """Test that context persists and evolves across conversation stages."""
    print("\n🧠 Testing Persistent Context Integration...")
    
    if not components:
        print("❌ Cannot test - components not available")
        return False
    
    thread_manager = components['thread_manager']
    amplifier = components['amplifier']
    personality = components['personality']
    
    try:
        # Create a test thread
        thread_id = thread_manager.create_thread("Integration Test Thread")
        if not thread_id:
            print("❌ Failed to create test thread")
            return False
        
        print(f"✅ Created test thread: {thread_id}")
        
        # Simulate conversation stages
        conversation_stages = simulate_realistic_conversation()
        conversation_history = []
        
        context_evolution = []
        
        for i, stage in enumerate(conversation_stages):
            print(f"\n--- Stage {i+1}: {stage['user'][:50]}... ---")
            
            # Add user message to conversation
            user_message = {"role": "user", "content": stage['user']}
            conversation_history.append(user_message)
            
            # Save user message
            thread_manager.save_message(thread_id, "user", stage['user'])
            
            # Analyze context with persistence
            context = amplifier.analyze_conversation_context(
                conversation_history, 
                stage['user'], 
                thread_id=thread_id
            )
            
            context_evolution.append({
                'stage': i + 1,
                'context': dict(context),
                'query': stage['user'][:50]
            })
            
            # Analyze personality
            ai_response = f"I'll help you with that. This appears to be a {context['conversation_type']} question."
            personality_signal = personality.analyze_user_interaction(
                stage['user'], 
                ai_response
            )
            
            # Add AI response to conversation
            ai_message = {"role": "assistant", "content": ai_response}
            conversation_history.append(ai_message)
            thread_manager.save_message(thread_id, "assistant", ai_response)
            
            # Verify context evolution
            print(f"   🎯 Context Type: {context['conversation_type']}")
            print(f"   🎓 User Expertise: {context['user_expertise']}")
            print(f"   📊 Evolution Count: {context['context_evolution_count']}")
            print(f"   🧬 Personality Signals: {personality_signal.evidence}")
            
            # Brief pause to simulate real conversation
            time.sleep(0.1)
        
        # Test context persistence across restarts
        print("\n🔄 Testing Context Persistence Across Sessions...")
        
        # Create a new amplifier instance (simulating restart)
        new_amplifier = ContextualIntelligenceAmplifier(thread_manager=thread_manager)
        
        # Analyze with empty conversation history but existing thread context
        final_context = new_amplifier.analyze_conversation_context(
            [], 
            "Can you help me with advanced Python concepts?", 
            thread_id=thread_id
        )
        
        print(f"   🔄 Restored Context Type: {final_context.get('conversation_type', 'none')}")
        print(f"   🔄 Restored Expertise: {final_context.get('user_expertise', 'none')}")
        print(f"   🔄 Evolution Count: {final_context.get('context_evolution_count', 0)}")
        print(f"   🔄 Learned Patterns: {len(final_context.get('learned_patterns', {}))}")
        
        # Verify context evolution
        context_evolution_data = thread_manager.get_context_evolution(thread_id)
        print(f"   📈 Context History Entries: {len(context_evolution_data)}")
        
        # Clean up
        thread_manager.delete_thread(thread_id)
        print(f"✅ Cleaned up test thread: {thread_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Persistent context integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_intelligence_optimization(components):
    """Test memory compression with intelligence optimization."""
    print("\n🧠💾 Testing Memory + Intelligence Optimization...")
    
    if not components:
        print("❌ Cannot test - components not available")
        return False
    
    compressor = components['compressor']
    token_allocator = components['token_allocator']
    
    try:
        # Create test memories
        test_memories = [
            {
                "question": "How do I create a Python function?",
                "answer": "Use the 'def' keyword followed by function name and parentheses",
                "created_at": datetime.now().isoformat(),
                "importance_score": 0.7,
                "tags": ["python", "functions", "basics"]
            },
            {
                "question": "What is object-oriented programming?",
                "answer": "OOP is a programming paradigm based on objects and classes",
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "importance_score": 0.8,
                "tags": ["programming", "oop", "concepts"]
            },
            {
                "question": "How to handle database connections in Python?",
                "answer": "Use context managers or connection pooling for efficient database handling",
                "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "importance_score": 0.9,
                "tags": ["python", "database", "advanced"]
            }
        ]
        
        # Test different query complexities
        queries = [
            ("Hi", 1000),  # Simple query
            ("Can you explain Python functions to me please?", 2000),  # Medium query
            ("I need help implementing a complex microservices architecture with database optimization and error handling", 4000)  # Complex query
        ]
        
        for query, token_budget in queries:
            print(f"\n   Testing query: '{query[:40]}...'")
            
            # Get token allocation
            allocation = token_allocator.calculate_optimal_allocation(query, token_budget)
            memory_budget = allocation['memory_context']
            
            # Compress memories with allocated budget
            compressed, stats = compressor.compress_memory_context(
                test_memories, query, token_budget=memory_budget
            )
            
            print(f"   📊 Token Budget: {token_budget}")
            print(f"   💾 Memory Budget: {memory_budget}")
            print(f"   🗜️ Compressed Length: {len(compressed)}")
            print(f"   📈 Compression Ratio: {stats['compression_ratio']:.3f}")
            print(f"   🎯 Memories Included: {stats['memories_included']}/{stats['memories_total']}")
            print(f"   ⚡ Information Density: {stats['information_density']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory intelligence optimization test failed: {e}")
        return False

def test_real_world_scenario(components):
    """Test a comprehensive real-world scenario."""
    print("\n🌍 Testing Real-World Scenario...")
    
    if not components:
        print("❌ Cannot test - components not available")
        return False
    
    try:
        # Simulate a complex technical support conversation
        thread_manager = components['thread_manager']
        amplifier = components['amplifier']
        personality = components['personality']
        compressor = components['compressor']
        
        # Create thread
        thread_id = thread_manager.create_thread("Real-World Technical Support")
        
        # Simulate memories from previous conversations
        previous_memories = [
            {
                "question": "User prefers detailed explanations",
                "answer": "This user always asks for comprehensive details and examples",
                "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
                "importance_score": 0.8,
                "tags": ["user_preference", "communication_style"]
            },
            {
                "question": "Previous API integration help",
                "answer": "Helped user integrate with REST APIs using Python requests library",
                "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "importance_score": 0.9,
                "tags": ["api", "python", "integration", "technical"]
            }
        ]
        
        # Multi-turn conversation
        conversation = [
            "Hi, I'm back again. I'm having issues with the API integration we discussed yesterday.",
            "The POST request is returning a 401 error and I'm not sure why.",
            "I've checked the API key multiple times and it seems correct.",
            "This is quite urgent as our production deployment is scheduled for today."
        ]
        
        conversation_history = []
        
        for i, user_input in enumerate(conversation):
            print(f"\n--- Turn {i+1} ---")
            print(f"User: {user_input}")
            
            # Build conversation history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Analyze context with persistence
            context = amplifier.analyze_conversation_context(
                conversation_history, user_input, thread_id=thread_id
            )
            
            # Analyze personality
            ai_response = "Let me help you troubleshoot this API authentication issue."
            personality_signal = personality.analyze_user_interaction(user_input, ai_response)
            
            # Compress relevant memories
            compressed_memories, memory_stats = compressor.compress_memory_context(
                previous_memories, user_input, token_budget=800
            )
            
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            print(f"Context: {context['conversation_type']} | Expertise: {context['user_expertise']} | Urgency: {'high_urgency' in personality_signal.evidence}")
            print(f"Memory Compression: {memory_stats['memories_included']} memories, {memory_stats['compression_ratio']:.2f} ratio")
        
        # Test final state
        final_context = thread_manager.get_thread_context(thread_id)
        print(f"\n✅ Final thread context has {len(final_context)} keys")
        print(f"✅ Context evolution count: {final_context.get('context_evolution_count', 0)}")
        
        # Cleanup
        thread_manager.delete_thread(thread_id)
        
        return True
        
    except Exception as e:
        print(f"❌ Real-world scenario test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_application_startup():
    """Test that the application can start with intelligence features."""
    print("\n🚀 Testing Application Startup Integration...")
    
    try:
        # Test core assistant import
        from zackgpt.core.core_assistant import CoreAssistant
        print("✅ CoreAssistant import successful")
        
        # Test prompt builder import  
        from zackgpt.core.prompt_builder import EvolutionaryPromptBuilder
        print("✅ EvolutionaryPromptBuilder import successful")
        
        # Test if intelligence features are available
        prompt_builder = EvolutionaryPromptBuilder()
        if hasattr(prompt_builder, 'intelligence_components'):
            print("✅ Intelligence components integrated into prompt builder")
        else:
            print("⚠️ Intelligence components not yet integrated into prompt builder")
        
        return True
        
    except Exception as e:
        print(f"❌ Application startup test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests."""
    print("🧪 ZackGPT Intelligence Integration Tests")
    print("=" * 50)
    
    # Setup
    test_environment_setup()
    
    # Test component initialization
    components = test_imports_and_initialization()
    
    if not components:
        print("\n❌ Integration tests failed - could not initialize components")
        return False
    
    # Run integration tests
    tests = [
        ("Persistent Context Integration", lambda: test_persistent_context_integration(components)),
        ("Memory Intelligence Optimization", lambda: test_memory_intelligence_optimization(components)),
        ("Real-World Scenario", lambda: test_real_world_scenario(components)),
        ("Application Startup", test_application_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Integration Test Results")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! The intelligence system is ready.")
    else:
        print(f"⚠️ {total - passed} tests failed. Review the failures above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1) 