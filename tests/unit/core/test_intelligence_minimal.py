"""
Minimal tests for ZackGPT Intelligence Amplification System

Tests the core intelligence components without complex dependencies.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Mock the problematic dependencies before importing our modules
mock_logger = Mock()
mock_logger.debug_log = Mock()
mock_logger.debug_info = Mock()
mock_logger.debug_success = Mock()
mock_logger.debug_error = Mock()

mock_database = Mock()
mock_get_database = Mock(return_value=mock_database)

# Patch the modules before importing
sys.modules['zackgpt.core.logger'] = mock_logger
sys.modules['zackgpt.data.database'] = Mock(get_database=mock_get_database)

# Mock config to avoid complex import chain
mock_config = Mock()
mock_config.PROMPT_EVOLUTION_ENABLED = True
mock_config.PROMPT_ENHANCER_DEBUG = False
sys.modules['config'] = mock_config

def test_intelligence_imports():
    """Test that intelligence components can be imported."""
    try:
        from zackgpt.core.intelligence_amplifier import (
            DynamicTokenAllocator,
            PersonalityEmergenceEngine,
            ContextualIntelligenceAmplifier,
            IntelligentContextCompressor
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import intelligence components: {e}")

def test_token_allocator():
    """Test the DynamicTokenAllocator functionality."""
    from zackgpt.core.intelligence_amplifier import DynamicTokenAllocator
    
    allocator = DynamicTokenAllocator()
    
    # Test basic allocation
    allocation = allocator.calculate_optimal_allocation("Simple query", 4000)
    
    # Check required components
    required_components = ["memory_context", "conversation_history", "system_prompt", "response_buffer"]
    for component in required_components:
        assert component in allocation
        assert allocation[component] > 0
    
    # Check budget constraint
    total = sum(allocation.values())
    assert total <= 4000
    
    # Test complex query gets different allocation
    complex_allocation = allocator.calculate_optimal_allocation(
        "Help me design and implement a complex distributed system", 4000
    )
    
    # Complex queries should allocate more to memory context
    assert complex_allocation["memory_context"] >= allocation["memory_context"]

def test_personality_engine():
    """Test the PersonalityEmergenceEngine functionality."""
    from zackgpt.core.intelligence_amplifier import PersonalityEmergenceEngine
    
    engine = PersonalityEmergenceEngine()
    
    # Test polite interaction analysis
    signal = engine.analyze_user_interaction(
        "Please help me with this task, thank you",
        "I'd be happy to help you!"
    )
    
    assert signal.signal_type == "interaction_analysis"
    assert len(signal.evidence) > 0
    assert "polite_communication" in signal.evidence
    
    # Test personality trait learning
    assert engine.personality_traits["formality"] > 0
    assert engine.personality_traits["warmth"] > 0
    
    # Test adaptation generation
    adaptation = engine.generate_personality_adaptation()
    assert isinstance(adaptation, str)
    assert len(adaptation) > 0

def test_context_amplifier():
    """Test the ContextualIntelligenceAmplifier functionality.""" 
    from zackgpt.core.intelligence_amplifier import ContextualIntelligenceAmplifier
    
    amplifier = ContextualIntelligenceAmplifier()
    
    # Test conversation context analysis
    conversation = [
        {"content": "How do I implement a REST API?", "role": "user"},
        {"content": "You can use FastAPI", "role": "assistant"}
    ]
    
    context = amplifier.analyze_conversation_context(
        conversation, "What about database integration?"
    )
    
    assert "conversation_type" in context
    assert "user_expertise" in context
    assert "task_complexity" in context
    
    # Test context awareness generation
    awareness = amplifier.generate_context_awareness(context)
    assert isinstance(awareness, str)
    assert len(awareness) > 0

def test_memory_compressor():
    """Test the IntelligentContextCompressor functionality."""
    from zackgpt.core.intelligence_amplifier import IntelligentContextCompressor
    
    compressor = IntelligentContextCompressor()
    
    # Test with empty memories
    compressed, stats = compressor.compress_memory_context([], "test query")
    assert compressed == ""
    assert stats["compression_ratio"] == 0.0
    assert stats["memories_processed"] == 0
    
    # Test with sample memories
    sample_memories = [
        {
            "question": "What is Python?",
            "answer": "Python is a programming language",
            "created_at": datetime.now().isoformat(),
            "importance_score": 0.8,
            "tags": ["programming"]
        }
    ]
    
    compressed, stats = compressor.compress_memory_context(
        sample_memories, "Tell me about Python", token_budget=500
    )
    
    assert isinstance(compressed, str)
    assert stats["memories_processed"] == 1
    assert stats["token_count"] <= 500
    assert stats["compression_ratio"] >= 0.0

def test_intelligence_integration():
    """Test integration between intelligence components."""
    from zackgpt.core.intelligence_amplifier import (
        DynamicTokenAllocator,
        PersonalityEmergenceEngine,
        ContextualIntelligenceAmplifier
    )
    
    # Create components
    allocator = DynamicTokenAllocator()
    personality = PersonalityEmergenceEngine()
    amplifier = ContextualIntelligenceAmplifier()
    
    # Simulate a conversation flow
    user_input = "Please help me with Python programming"
    ai_response = "I'd be happy to help you with Python!"
    
    # Analyze interaction
    signal = personality.analyze_user_interaction(user_input, ai_response)
    
    # Analyze context
    conversation = [
        {"content": user_input, "role": "user"},
        {"content": ai_response, "role": "assistant"}
    ]
    context = amplifier.analyze_conversation_context(conversation, "How do I use functions?")
    
    # Calculate token allocation with context
    allocation = allocator.calculate_optimal_allocation("How do I use functions?", 4000, context)
    
    # All should work together
    assert len(signal.evidence) > 0
    assert context["conversation_type"] in ["general", "technical"]
    assert sum(allocation.values()) <= 4000
    
    # Personality should learn and adapt
    adaptation = personality.generate_personality_adaptation()
    awareness = amplifier.generate_context_awareness(context)
    
    assert len(adaptation) > 0
    assert len(awareness) > 0

def test_data_structures():
    """Test the intelligence system data structures."""
    from zackgpt.core.intelligence_amplifier import UserPattern, ContextSignal
    
    # Test UserPattern
    pattern = UserPattern(
        pattern_type="communication_style",
        pattern_value="formal",
        confidence=0.8,
        evidence_count=5,
        last_observed=datetime.now().isoformat(),
        context_tags=["professional", "technical"]
    )
    
    assert pattern.pattern_type == "communication_style"
    assert pattern.confidence == 0.8
    assert len(pattern.context_tags) == 2
    
    # Test ContextSignal
    signal = ContextSignal(
        signal_type="urgency",
        strength=0.7,
        evidence=["asap", "urgent", "quickly"],
        timestamp=datetime.now().isoformat()
    )
    
    assert signal.signal_type == "urgency"
    assert signal.strength == 0.7
    assert len(signal.evidence) == 3

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 