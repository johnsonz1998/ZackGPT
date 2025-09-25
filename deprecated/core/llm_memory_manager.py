"""
LLM-Based Memory Manager - NO MORE HARDCODED BULLSHIT!
One intelligent function that decides what memories to save using the LLM.
"""

import json
from typing import Dict, List, Optional
from ..utils.logger import debug_info, debug_success, debug_error

class LLMMemoryManager:
    """CLEAN: Let the LLM decide what memories to save and how to save them."""
    
    def __init__(self, openai_client, database):
        self.client = openai_client
        self.db = database
        
    def process_interaction_for_memories(self, user_input: str, ai_response: str) -> List[Dict]:
        """
        SINGLE FUNCTION: Let LLM analyze interaction and return memory objects to save.
        Returns list of memory objects ready for database saving.
        """
        if not self.client:
            debug_error("No OpenAI client available for memory analysis")
            return []
            
        try:
            # Create the LLM prompt for memory analysis
            analysis_prompt = f"""
Analyze this conversation and determine what information should be saved as memories.

CONVERSATION:
User: {user_input}
Assistant: {ai_response}

TASK: Extract any persistent, valuable information about the user that should be remembered for future conversations.

GUIDELINES:
- Save personal facts, preferences, background, relationships, goals
- Save important context that will help in future interactions  
- DON'T save temporary questions, greetings, or generic responses
- Each memory should be a clear question/answer pair

Return ONLY a JSON object in this format:
{{
  "should_save": true/false,
  "memories": [
    {{
      "question": "What is the user's [specific topic]?",
      "answer": "Clear, factual answer",
      "tags": ["relevant", "category", "tags"],
      "importance": "high/medium/low"
    }}
  ]
}}

If nothing should be saved, return: {{"should_save": false, "memories": []}}
"""

            # Get LLM decision
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up response (remove markdown if present)
            if result_text.startswith('```json'):
                result_text = result_text[7:-3]
            elif result_text.startswith('```'):
                result_text = result_text[3:-3]
            
            # Parse JSON response
            result = json.loads(result_text)
            
            if not result.get('should_save', False):
                debug_info("LLM decided not to save any memories", {
                    "user_input": user_input[:50] + "...",
                    "reasoning": "should_save=false"
                })
                return []
            
            memories = result.get('memories', [])
            debug_info(f"LLM extracted {len(memories)} memories to save", {
                "user_input": user_input[:50] + "...",
                "memory_count": len(memories)
            })
            
            return memories
            
        except json.JSONDecodeError as e:
            debug_error(f"Failed to parse LLM memory response: {e}")
            debug_error(f"Raw response: {result_text}")
            return []
        except Exception as e:
            debug_error(f"LLM memory analysis failed: {e}")
            return []
    
    def save_memories(self, memory_objects: List[Dict]) -> List[str]:
        """
        Save memory objects to database and return list of memory IDs.
        """
        saved_ids = []
        
        for memory in memory_objects:
            try:
                memory_id = self.db.save_memory(
                    question=memory.get('question', ''),
                    answer=memory.get('answer', ''),
                    agent='core_assistant',
                    importance=memory.get('importance', 'medium'),
                    tags=memory.get('tags', ['general'])
                )
                
                if memory_id:
                    saved_ids.append(memory_id)
                    debug_success("LLM memory saved", {
                        "memory_id": memory_id,
                        "question": memory.get('question', '')[:50] + "...",
                        "importance": memory.get('importance', 'medium')
                    })
                    
            except Exception as e:
                debug_error(f"Failed to save LLM memory: {e}")
                
        return saved_ids

# Simple function for CoreAssistant to use
def analyze_and_save_memories(user_input: str, ai_response: str, openai_client, database) -> List[str]:
    """
    SIMPLE INTERFACE: Analyze interaction and save memories.
    Returns list of saved memory IDs.
    """
    manager = LLMMemoryManager(openai_client, database)
    memory_objects = manager.process_interaction_for_memories(user_input, ai_response)
    return manager.save_memories(memory_objects)
