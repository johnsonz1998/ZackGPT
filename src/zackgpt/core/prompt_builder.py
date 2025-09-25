"""
Simple Prompt Builder - No Evolution Bullshit
Just build prompts without all the statistical learning nonsense.
"""

import os
from pathlib import Path
from typing import Dict
from ..utils.logger import debug_info

class PromptBuilder:
    """SIMPLIFIED: Just build prompts without evolutionary complexity."""
    
    def __init__(self):
        self.base_prompt = self._load_base_prompt()
        debug_info("Simple prompt builder initialized")
    
    def _load_base_prompt(self) -> str:
        """Load the base system prompt from file."""
        try:
            prompt_path = Path(__file__).parent.parent / "prompts" / "core_assistant.txt"
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception as e:
            debug_info(f"Could not load base prompt: {e}")
        
        # Fallback prompt
        return """You are a personal AI assistant. Your mission is to be useful and effective through continuous learning and adaptation.

You have access to conversation context and memories:

Dynamic Adaptation:
Observe user communication patterns and adapt accordingly.
Maintain general contextual awareness and adapt as needed.
NEVER make up information or guess. If unsure, say so. Consider the flow and context of the current conversation."""
    
    def build_system_prompt(self, short_term: str, memory_context: str, 
                          conversation_context: Dict = None) -> str:
        """Build a system prompt with memory context."""
        
        # Start with base prompt
        prompt_parts = [self.base_prompt]
        
        # Add memory context if available
        if memory_context and memory_context.strip():
            prompt_parts.append("\nYou have access to conversation context and memories:")
            prompt_parts.append(memory_context)
        
        # Add short term context if available  
        if short_term and short_term.strip():
            prompt_parts.append("\nShort term:")
            prompt_parts.append(short_term)
        
        # Add memory context section
        prompt_parts.append("\nMemory Context:")
        if memory_context:
            prompt_parts.append(memory_context)
        else:
            prompt_parts.append("No specific memories for this conversation yet.")
        
        return "\n\n".join(prompt_parts)

# DELETED ALL THE EVOLUTIONARY BULLSHIT:
# - GenerativePromptEvolver (300+ lines of statistical learning)
# - EvolutionaryPromptBuilder (200+ lines of complexity)  
# - PromptComponent evolution system (100+ lines)
# - AI-powered enhancement (150+ lines of OpenAI calls)
