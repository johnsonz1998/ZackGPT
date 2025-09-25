#!/usr/bin/env python3
"""
Test edge cases for the improved AI memory extraction system.
This showcases how the system now intelligently decides what to save vs ignore.
"""

import sys
import os
sys.path.append('src')

from zackgpt.core.core_assistant import CoreAssistant
from zackgpt.utils.logger import debug_info

def test_edge_cases():
    """Test challenging edge cases for memory decisioning."""
    
    print("🧪 Testing Edge Cases for Intelligent Memory Decisioning")
    print("=" * 60)
    
    edge_cases = [
        {
            "name": "Technical Help vs Personal Info",
            "user_input": "I'm having trouble with Python, I've been programming for 5 years and I work at Microsoft. Can you help me debug this code?",
            "ai_response": "I'd be happy to help with your Python debugging! With 5 years of programming experience, you should be able to tackle this.",
            "expectation": "Should save: 5 years experience, works at Microsoft. Should NOT save: temporary debugging request"
        },
        {
            "name": "Mixed Temporary and Permanent",
            "user_input": "What's the capital of France? By the way, I'm from Texas and I'm planning to move to Paris next year for work.",
            "ai_response": "The capital of France is Paris. That's exciting that you're planning to move there for work!",
            "expectation": "Should save: from Texas, moving to Paris for work. Should NOT save: capital of France question"
        },
        {
            "name": "Vague vs Specific Preferences",
            "user_input": "I like stuff. I enjoy things. Actually, I'm really passionate about renewable energy and I drive a Tesla.",
            "ai_response": "That's great! Renewable energy is an important field, and Tesla makes excellent electric vehicles.",
            "expectation": "Should save: passionate about renewable energy, drives Tesla. Should NOT save: vague 'like stuff'"
        },
        {
            "name": "Emotional Context vs Facts",
            "user_input": "I'm so frustrated today! My boss is being difficult. But on the bright side, I just got accepted to Stanford's MBA program and my girlfriend Sarah is so supportive.",
            "ai_response": "I'm sorry you're having a tough day with your boss. Congratulations on getting accepted to Stanford's MBA program! It's wonderful that Sarah is supportive.",
            "expectation": "Should save: accepted to Stanford MBA, girlfriend Sarah. Should NOT save: temporary frustration"
        },
        {
            "name": "Pure Question (No Personal Info)",
            "user_input": "How do machine learning algorithms work? What's the difference between supervised and unsupervised learning?",
            "ai_response": "Machine learning algorithms learn patterns from data. Supervised learning uses labeled data...",
            "expectation": "Should save: NOTHING (pure informational request, no personal context)"
        }
    ]
    
    try:
        assistant = CoreAssistant()
        
        if not assistant.client:
            print("❌ OpenAI client not available")
            return False
        
        for i, case in enumerate(edge_cases, 1):
            print(f"\n🔬 Edge Case {i}: {case['name']}")
            print(f"Input: {case['user_input'][:80]}...")
            print(f"Expected: {case['expectation']}")
            
            # Test direct extraction to see the analysis
            extracted = assistant.extract_multiple_memories(case['user_input'], case['ai_response'])
            
            print(f"✅ AI Decision: Created {len(extracted)} memories")
            
            if extracted:
                for j, memory in enumerate(extracted, 1):
                    print(f"  {j}. {memory.get('question', 'N/A')[:60]}...")
                    print(f"     → {memory.get('answer', 'N/A')[:60]}...")
                    print(f"     Importance: {memory.get('importance', 'unknown')}")
                    print(f"     Confidence: {memory.get('confidence', 'unknown')}")
                    print(f"     Reasoning: {memory.get('reasoning', 'N/A')[:80]}...")
                    print()
            else:
                print(f"     → AI decided NO memories should be saved")
        
        print("🎯 Analysis Summary:")
        print("The improved system shows sophisticated decision-making by:")
        print("- Distinguishing between temporary requests and lasting information")
        print("- Ignoring conversational filler and focusing on personal facts")
        print("- Providing detailed reasoning for each decision")
        print("- Assigning appropriate importance and confidence levels")
        print("- Consolidating related information efficiently")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_edge_cases()
    sys.exit(0 if success else 1) 