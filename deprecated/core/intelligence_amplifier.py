"""
Simple Memory Compression - No More "Intelligence Amplification" Bullshit
Just basic memory compression without all the over-engineering.
"""

from typing import Dict, List, Tuple
from ..utils.logger import debug_info

class IntelligentContextCompressor:
    """SIMPLIFIED: Just basic memory compression without the "intelligence" nonsense."""
    
    def __init__(self):
        debug_info("Simple memory compressor initialized")
    
    def compress_memory_context(self, memories: List[Dict], current_query: str, 
                              token_budget: int = 1000) -> Tuple[str, Dict]:
        """COMPRESSION BYPASSED - Return simple memory context without aggressive compression."""
        
        if not memories:
            return "", {"compression_ratio": 0.0, "memories_processed": 0}
        
        debug_info("🚫 Memory compression BYPASSED per user request", {
            "memories_count": len(memories),
            "token_budget": token_budget,
            "note": "Using simple concatenation instead of compression"
        })
        
        # SIMPLIFIED: Just filter out unhelpful memories and concatenate
        helpful_memories = []
        for memory in memories:
            answer = memory.get('answer', '').lower()
            is_unhelpful = any(phrase in answer for phrase in [
                "as an ai, i don't have",
                "i don't have the ability", 
                "each session is independent",
                "don't have any specific memories",
                "no specific memories saved", 
                "don't have memories",
                "no memories saved",
                "as an ai developed by openai",
                "i don't have personal feelings"
            ])
            if not is_unhelpful:
                helpful_memories.append(memory)
        
        # Simple concatenation without compression
        memory_parts = []
        for memory in helpful_memories[:20]:  # Limit to 20 memories max
            question = memory.get('question', '')
            answer = memory.get('answer', '')
            if question and answer:
                memory_parts.append(f"Q: {question}\nA: {answer}")
        
        compressed_context = "\n\n".join(memory_parts)
        
        # Simple stats
        compression_stats = {
            "compression_ratio": 1.0,  # No compression
            "memories_processed": len(memories),
            "memories_included": len(helpful_memories),
            "token_count": len(compressed_context) // 4,  # Rough estimate
            "note": "compression_bypassed"
        }
        
        return compressed_context, compression_stats

# DELETED ALL THE OTHER BULLSHIT:
# - ContextualIntelligenceAmplifier (200+ lines of nonsense)
# - PersonalityEmergenceEngine (150+ lines of over-engineering) 
# - DynamicTokenAllocator (100+ lines of complexity)
# - UserPattern, ContextSignal (unnecessary dataclasses)
