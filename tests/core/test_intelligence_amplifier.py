"""
Tests for the Intelligence Amplification System - BASIC VERSION

These tests verify that the super-intelligent components work correctly.
"""

import pytest
from datetime import datetime, timedelta

# Simple tests without complex dependencies first
def test_basic_imports():
    """Test that we can import our intelligence components."""
    try:
        from src.zackgpt.core.intelligence_amplifier import (
            IntelligentContextCompressor,
            PersonalityEmergenceEngine, 
            ContextualIntelligenceAmplifier,
            DynamicTokenAllocator
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import intelligence components: {e}")

def test_memory_compressor_initialization():
    """Test that IntelligentContextCompressor can be initialized."""
    from src.zackgpt.core.intelligence_amplifier import IntelligentContextCompressor
    
    compressor = IntelligentContextCompressor()
    assert compressor is not None
    assert hasattr(compressor, 'compress_memory_context')

def test_personality_engine_initialization():
    """Test that PersonalityEmergenceEngine can be initialized."""
    from src.zackgpt.core.intelligence_amplifier import PersonalityEmergenceEngine
    
    engine = PersonalityEmergenceEngine()
    assert engine is not None
    assert hasattr(engine, 'analyze_user_interaction')

def test_context_amplifier_initialization():
    """Test that ContextualIntelligenceAmplifier can be initialized.""" 
    from src.zackgpt.core.intelligence_amplifier import ContextualIntelligenceAmplifier
    
    amplifier = ContextualIntelligenceAmplifier()
    assert amplifier is not None
    assert hasattr(amplifier, 'analyze_conversation_context')

def test_token_allocator_initialization():
    """Test that DynamicTokenAllocator can be initialized."""
    from src.zackgpt.core.intelligence_amplifier import DynamicTokenAllocator
    
    allocator = DynamicTokenAllocator()
    assert allocator is not None
    assert hasattr(allocator, 'calculate_optimal_allocation')

def test_memory_compression_empty():
    """Test memory compression with empty input."""
    from src.zackgpt.core.intelligence_amplifier import IntelligentContextCompressor
    
    compressor = IntelligentContextCompressor()
    compressed, stats = compressor.compress_memory_context([], "test query")
    
    assert compressed == ""
    assert stats["compression_ratio"] == 0.0

def test_token_allocation_basic():
    """Test basic token allocation."""
    from src.zackgpt.core.intelligence_amplifier import DynamicTokenAllocator
    
    allocator = DynamicTokenAllocator()
    allocation = allocator.calculate_optimal_allocation("Simple query", 4000)
    
    # Should return allocation dict with all required components
    required_components = ["memory_context", "conversation_history", "system_prompt", "response_buffer"]
    for component in required_components:
        assert component in allocation
        assert allocation[component] > 0
    
    # Total shouldn't exceed available tokens
    total = sum(allocation.values())
    assert total <= 4000

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
