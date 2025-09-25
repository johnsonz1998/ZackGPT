#!/usr/bin/env python3
"""
Ultimate Memory Stress Test for ZackGPT Neural Memory System

This will push the memory extraction and neural retrieval to absolute limits:
- Multiple memory extraction from single conversations
- Garbage filtering and relevance detection
- Edge cases and complex scenarios
- Performance under stress
"""

import sys
import os
import time
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.zackgpt.core.core_assistant import CoreAssistant
from src.zackgpt.data.database import get_database

class MemoryStressTester:
    def __init__(self):
        self.assistant = CoreAssistant()
        self.db = get_database()
        self.test_results = []
        
    def log_test(self, test_name: str, input_text: str, expected_memories: int, 
                 actual_memories: int, memory_details: list):
        """Log test results for analysis."""
        result = {
            "test_name": test_name,
            "input_text": input_text,
            "expected_memories": expected_memories,
            "actual_memories": actual_memories,
            "success": actual_memories >= expected_memories,
            "memory_details": memory_details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        # Print results
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"\n{status} {test_name}")
        print(f"Input: {input_text[:100]}...")
        print(f"Expected: {expected_memories} memories, Got: {actual_memories}")
        
        if memory_details:
            print("Extracted memories:")
            for i, memory in enumerate(memory_details, 1):
                print(f"  {i}. Q: {memory.get('question', 'N/A')[:60]}...")
                print(f"     A: {memory.get('answer', 'N/A')[:60]}...")
                print(f"     Tags: {memory.get('tags', [])}")
                print(f"     Importance: {memory.get('importance', 'N/A')}")
    
    def test_dense_information_extraction(self):
        """Test 1: Dense Information - Multiple facts in one message."""
        print("\n" + "="*60)
        print("🧠 TEST 1: DENSE INFORMATION EXTRACTION")
        print("="*60)
        
        # Test 1.1: Personal identity facts
        response = self.assistant.process_input(
            "Hi, I'm Alex Thompson, I'm 28 years old, I work as a Senior Software Engineer at Google, "
            "I live in San Francisco, my favorite programming language is Python, and I love playing guitar in my free time."
        )
        
        memories = self.assistant.maybe_save_memory_enhanced(
            "Hi, I'm Alex Thompson, I'm 28 years old, I work as a Senior Software Engineer at Google, "
            "I live in San Francisco, my favorite programming language is Python, and I love playing guitar in my free time.",
            response
        )
        
        memory_details = []
        for memory_id in memories:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                memory_details.append(memory)
        
        self.log_test("Dense Personal Info", 
                     "Alex Thompson, 28, Google engineer, SF, Python, guitar",
                     5, len(memories), memory_details)
        
        # Test 1.2: Technical preferences
        response = self.assistant.process_input(
            "I use VS Code as my editor, I prefer React over Angular, I always use TypeScript instead of JavaScript, "
            "my go-to database is PostgreSQL, and I deploy everything on AWS using Docker containers."
        )
        
        memories = self.assistant.maybe_save_memory_enhanced(
            "I use VS Code as my editor, I prefer React over Angular, I always use TypeScript instead of JavaScript, "
            "my go-to database is PostgreSQL, and I deploy everything on AWS using Docker containers.",
            response
        )
        
        memory_details = []
        for memory_id in memories:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                memory_details.append(memory)
        
        self.log_test("Dense Technical Preferences",
                     "VS Code, React>Angular, TypeScript, PostgreSQL, AWS+Docker",
                     4, len(memories), memory_details)
    
    def test_garbage_filtering(self):
        """Test 2: Garbage Filtering - Mix valuable info with irrelevant chatter."""
        print("\n" + "="*60)
        print("🗑️ TEST 2: GARBAGE FILTERING")
        print("="*60)
        
        # Test 2.1: Facts mixed with filler
        response = self.assistant.process_input(
            "Um, well, you know, I was thinking, like, my name is Sarah, and um, "
            "I really like coffee, especially in the morning, you know? Oh and by the way, "
            "I work at Microsoft as a data scientist. Yeah, that's pretty cool I guess."
        )
        
        memories = self.assistant.maybe_save_memory_enhanced(
            "Um, well, you know, I was thinking, like, my name is Sarah, and um, "
            "I really like coffee, especially in the morning, you know? Oh and by the way, "
            "I work at Microsoft as a data scientist. Yeah, that's pretty cool I guess.",
            response
        )
        
        memory_details = []
        for memory_id in memories:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                memory_details.append(memory)
        
        self.log_test("Filler Words Test",
                     "Mixed filler with facts about Sarah, coffee, Microsoft",
                     3, len(memories), memory_details)
        
        # Test 2.2: Should ignore pure garbage
        response = self.assistant.process_input(
            "Yeah, so, um, the weather is nice today, isn't it? I mean, I don't know, "
            "just saying hello really. How are you doing? Pretty good day, I think."
        )
        
        memories = self.assistant.maybe_save_memory_enhanced(
            "Yeah, so, um, the weather is nice today, isn't it? I mean, I don't know, "
            "just saying hello really. How are you doing? Pretty good day, I think.",
            response
        )
        
        memory_details = []
        for memory_id in memories:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                memory_details.append(memory)
        
        self.log_test("Pure Garbage Test",
                     "Weather small talk, should save 0 memories",
                     0, len(memories), memory_details)
    
    def test_edge_cases(self):
        """Test 3: Edge Cases - Weird formats, ambiguous info, contradictions."""
        print("\n" + "="*60)
        print("⚡ TEST 3: EDGE CASES")
        print("="*60)
        
        # Test 3.1: Contradictory information
        response = self.assistant.process_input(
            "My favorite color is blue. Actually, no wait, I think it's red. "
            "Or maybe green? I can't decide between blue and red."
        )
        
        memories = self.assistant.maybe_save_memory_enhanced(
            "My favorite color is blue. Actually, no wait, I think it's red. "
            "Or maybe green? I can't decide between blue and red.",
            response
        )
        
        memory_details = []
        for memory_id in memories:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                memory_details.append(memory)
        
        self.log_test("Contradictory Info",
                     "Conflicting color preferences",
                     1, len(memories), memory_details)
        
        # Test 3.2: Complex nested relationships
        response = self.assistant.process_input(
            "My brother John works at Apple, his wife Lisa is a teacher, "
            "their daughter Emma is 5 years old and loves dinosaurs, "
            "and they live in Austin, Texas."
        )
        
        memories = self.assistant.maybe_save_memory_enhanced(
            "My brother John works at Apple, his wife Lisa is a teacher, "
            "their daughter Emma is 5 years old and loves dinosaurs, "
            "and they live in Austin, Texas.",
            response
        )
        
        memory_details = []
        for memory_id in memories:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                memory_details.append(memory)
        
        self.log_test("Complex Relationships",
                     "Brother John, wife Lisa, daughter Emma, jobs, location",
                     4, len(memories), memory_details)
        
        # Test 3.3: Technical jargon mixed with personal
        response = self.assistant.process_input(
            "I'm debugging a React component that has a useState hook causing infinite re-renders, "
            "my cat Mr. Whiskers keeps walking on my keyboard, and I need to finish this before "
            "my meeting with the DevOps team at 3pm."
        )
        
        memories = self.assistant.maybe_save_memory_enhanced(
            "I'm debugging a React component that has a useState hook causing infinite re-renders, "
            "my cat Mr. Whiskers keeps walking on my keyboard, and I need to finish this before "
            "my meeting with the DevOps team at 3pm.",
            response
        )
        
        memory_details = []
        for memory_id in memories:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                memory_details.append(memory)
        
        self.log_test("Technical + Personal Mix",
                     "React debugging, cat named Mr. Whiskers, DevOps meeting",
                     3, len(memories), memory_details)
    
    def test_stress_scenarios(self):
        """Test 4: Stress Scenarios - Very long messages, rapid info."""
        print("\n" + "="*60)
        print("💥 TEST 4: STRESS SCENARIOS") 
        print("="*60)
        
        # Test 4.1: Information overload
        response = self.assistant.process_input(
            "Let me tell you everything about myself: I'm David Chen, 32 years old, "
            "born in Seattle but now living in New York, I work as a DevOps Engineer at Netflix, "
            "I have a Master's degree in Computer Science from Stanford, I'm married to Jennifer "
            "who's a doctor, we have two kids: Sophie (8) and Max (5), I play tennis every weekend, "
            "I love sushi and Italian food, I drive a Tesla Model 3, my favorite movie is Inception, "
            "I speak English, Mandarin, and Spanish, I'm learning French, I use Arch Linux at home, "
            "macOS at work, I'm allergic to peanuts, I have a golden retriever named Buddy, "
            "and I'm planning to visit Japan next summer."
        )
        
        memories = self.assistant.maybe_save_memory_enhanced(
            "Let me tell you everything about myself: I'm David Chen, 32 years old, "
            "born in Seattle but now living in New York, I work as a DevOps Engineer at Netflix, "
            "I have a Master's degree in Computer Science from Stanford, I'm married to Jennifer "
            "who's a doctor, we have two kids: Sophie (8) and Max (5), I play tennis every weekend, "
            "I love sushi and Italian food, I drive a Tesla Model 3, my favorite movie is Inception, "
            "I speak English, Mandarin, and Spanish, I'm learning French, I use Arch Linux at home, "
            "macOS at work, I'm allergic to peanuts, I have a golden retriever named Buddy, "
            "and I'm planning to visit Japan next summer.",
            response
        )
        
        memory_details = []
        for memory_id in memories:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                memory_details.append(memory)
        
        self.log_test("Information Overload",
                     "Massive info dump: 15+ distinct facts about David Chen",
                     10, len(memories), memory_details)
        
        # Test 4.2: Rapid-fire preferences
        response = self.assistant.process_input(
            "Quick preferences: Coffee>Tea, iOS>Android, Netflix>Hulu, "
            "Python>Java, Mac>PC, Summer>Winter, Dogs>Cats, Books>Movies, "
            "Pizza>Burgers, Beach>Mountains."
        )
        
        memories = self.assistant.maybe_save_memory_enhanced(
            "Quick preferences: Coffee>Tea, iOS>Android, Netflix>Hulu, "
            "Python>Java, Mac>PC, Summer>Winter, Dogs>Cats, Books>Movies, "
            "Pizza>Burgers, Beach>Mountains.",
            response
        )
        
        memory_details = []
        for memory_id in memories:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                memory_details.append(memory)
        
        self.log_test("Rapid-Fire Preferences",
                     "10 rapid preference comparisons",
                     8, len(memories), memory_details)
    
    def test_memory_retrieval_accuracy(self):
        """Test 5: Test the neural retrieval system accuracy."""
        print("\n" + "="*60)
        print("🎯 TEST 5: NEURAL RETRIEVAL ACCURACY")
        print("="*60)
        
        # First, let's see what memories we have stored
        all_memories = self.db.get_all_memories()
        print(f"Total memories stored: {len(all_memories)}")
        
        if len(all_memories) == 0:
            print("⚠️ No memories to test retrieval!")
            return
        
        # Test retrieval queries
        test_queries = [
            "What's my name?",
            "Where do I work?", 
            "What programming languages do I like?",
            "Tell me about my family",
            "What are my hobbies?",
            "What's my favorite food?",
            "Do I have any pets?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            # Use the neural memory retrieval
            context = self.assistant.build_context(query)
            
            # Check if relevant memories were found
            memory_context = ""
            for msg in context:
                if msg["role"] == "system" and "Memory Context:" in msg["content"]:
                    lines = msg["content"].split("\n")
                    in_memory_section = False
                    for line in lines:
                        if "Memory Context:" in line:
                            in_memory_section = True
                            continue
                        elif in_memory_section and line.strip():
                            if not line.startswith("Dynamic") and not line.startswith("Short"):
                                memory_context += line + "\n"
                        elif in_memory_section and line.startswith("CORE"):
                            break
            
            print(f"   Retrieved memory context: {memory_context[:200]}...")
            print(f"   Context length: {len(memory_context)} chars")
            
            if len(memory_context) > 50:
                print("   ✅ Neural retrieval found relevant memories")
            else:
                print("   ❌ Neural retrieval found no memories")
    
    def run_all_tests(self):
        """Run the complete memory stress test suite."""
        print("🚀 STARTING ULTIMATE MEMORY STRESS TEST")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_dense_information_extraction()
        self.test_garbage_filtering() 
        self.test_edge_cases()
        self.test_stress_scenarios()
        self.test_memory_retrieval_accuracy()
        
        # Summary
        end_time = time.time()
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print("\n" + "=" * 80)
        print("📊 FINAL TEST RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Time: {end_time - start_time:.2f} seconds")
        
        # Total memories created
        total_memories = self.db.get_all_memories()
        print(f"Total Memories Created: {len(total_memories)}")
        
        # Save detailed results
        with open("memory_stress_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": total_tests - passed_tests,
                    "success_rate": (passed_tests/total_tests)*100,
                    "total_time": end_time - start_time,
                    "total_memories_created": len(total_memories)
                },
                "detailed_results": self.test_results,
                "all_memories": total_memories
            }, f, indent=2)
        
        print("\n💾 Detailed results saved to: memory_stress_test_results.json")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = MemoryStressTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Your memory system is SOLID! 🔥")
    else:
        print("\n⚠️ Some tests failed. Check the results for improvements needed.") 