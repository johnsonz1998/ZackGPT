"""
ZackGPT Memory Manager - Database-backed persistent memory management
"""
from typing import List, Dict, Optional, Any
from datetime import datetime

from .database import get_database
from .logger import debug_success, debug_error, debug_info, debug_warning


class PersistentMemoryManager:
    """Database-backed memory manager for ZackGPT."""
    
    def __init__(self):
        self.db = get_database()
        debug_success("Memory manager initialized with database persistence")
    
    # =============================
    #        MEMORY OPERATIONS
    # =============================
    
    def save_memory(self, question: str, answer: str, agent: str = "core_assistant",
                   importance: str = "medium", tags: List[str] = None,
                   similarity_threshold: float = 0.95) -> Optional[str]:
        """Save a memory with automatic deduplication."""
        return self.db.save_memory(
            question=question,
            answer=answer,
            agent=agent,
            importance=importance,
            tags=tags,
            similarity_threshold=similarity_threshold
        )
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID."""
        return self.db.get_memory(memory_id)
    
    def query_memories(self, query: str, limit: int = 5, agent: str = None,
                      importance: str = None, tags: List[str] = None,
                      similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Query memories by semantic similarity."""
        return self.db.query_memories_by_similarity(
            query=query,
            limit=limit,
            agent=agent,
            importance=importance,
            tags=tags,
            similarity_threshold=similarity_threshold
        )
    
    def update_memory(self, memory_id: str, **updates) -> bool:
        """Update an existing memory."""
        return self.db.update_memory(memory_id, **updates)
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        return self.db.delete_memory(memory_id)
    
    # =============================
    #        CONTEXT BUILDING
    # =============================
    
    def get_relevant_context(self, query: str, max_memories: int = 5,
                            similarity_threshold: float = 0.4) -> str:
        """Get formatted context from relevant memories."""
        memories = self.query_memories(
            query=query,
            limit=max_memories,
            similarity_threshold=similarity_threshold
        )
        
        if not memories:
            return ""
        
        context_parts = []
        for memory in memories:
            context_parts.append(
                f"Q: {memory['question']}\n"
                f"A: {memory['answer']}"
            )
            
            # Add tags if present
            if memory.get('tags'):
                context_parts[-1] += f"\nTags: {', '.join(memory['tags'])}"
            
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def build_memory_context(self, query: str, include_metadata: bool = False) -> Dict[str, Any]:
        """Build comprehensive memory context for prompt injection."""
        memories = self.query_memories(query, limit=5)
        
        if not memories:
            return {
                "context": "",
                "memory_count": 0,
                "memories": []
            }
        
        # Format for prompt
        context_lines = ["Relevant memories:"]
        for memory in memories:
            context_lines.append(
                f"Q: {memory['question']}\n"
                f"A: {memory['answer']}"
            )
            
            if memory.get('tags'):
                context_lines.append(f"Tags: {', '.join(memory['tags'])}")
            
            context_lines.append("---")
        
        result = {
            "context": "\n".join(context_lines),
            "memory_count": len(memories),
            "memories": memories if include_metadata else [
                {
                    "id": m["id"],
                    "question": m["question"],
                    "answer": m["answer"],
                    "similarity": m.get("similarity", 0)
                } for m in memories
            ]
        }
        
        return result
    
    # =============================
    #        MEMORY EVALUATION
    # =============================
    
    def should_save_memory(self, question: str, answer: str) -> bool:
        """Determine if an interaction should be saved as memory."""
        # Skip very short interactions
        if len(question.strip()) < 5 or len(answer.strip()) < 10:
            return False
        
        # Skip simple greetings
        simple_greetings = ["hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye"]
        if question.lower().strip() in simple_greetings:
            return False
        
        # Skip if answer indicates uncertainty or lack of knowledge
        uncertainty_phrases = [
            "i don't know", "i'm not sure", "i can't", 
            "i don't have", "i'm not aware", "i don't recall"
        ]
        if any(phrase in answer.lower() for phrase in uncertainty_phrases):
            return False
        
        # Check for "remember" keyword - explicit memory request
        if "remember" in question.lower():
            return True
        
        # Check for factual content (questions with question words)
        question_words = ["what", "who", "when", "where", "why", "how", "which"]
        if any(word in question.lower() for word in question_words):
            return True
        
        # Check for personal information sharing
        personal_indicators = ["my", "i am", "i'm", "my name", "i like", "i have"]
        if any(indicator in question.lower() for indicator in personal_indicators):
            return True
        
        return False
    
    def extract_tags(self, question: str, answer: str) -> List[str]:
        """Extract relevant tags from question and answer."""
        tags = []
        
        # Content-based tags
        if any(word in question.lower() for word in ["favorite", "like", "love", "prefer"]):
            tags.append("preferences")
        
        if any(word in question.lower() for word in ["name", "called", "am i", "who am"]):
            tags.append("identity")
        
        if any(word in question.lower() for word in ["family", "mother", "father", "sister", "brother", "grandma", "grandpa"]):
            tags.append("family")
        
        if any(word in question.lower() for word in ["work", "job", "career", "profession"]):
            tags.append("work")
        
        if any(word in question.lower() for word in ["remember", "recall", "memory"]):
            tags.append("memory")
        
        return tags
    
    def extract_fact(self, question: str) -> Optional[str]:
        """Extract a structured fact from the question if possible."""
        # Simple fact extraction - could be enhanced with NLP
        question_lower = question.lower()
        
        # Personal facts
        if "my name is" in question_lower:
            name = question.split("my name is")[-1].strip().rstrip(".,!?")
            return f"Name: {name}"
        
        if "my favorite" in question_lower:
            favorite = question.split("my favorite")[-1].strip().rstrip(".,!?")
            return f"Favorite: {favorite}"
        
        if "i am" in question_lower and any(word in question_lower for word in ["years old", "from", "live in"]):
            fact = question.split("i am")[-1].strip().rstrip(".,!?")
            return f"Personal: {fact}"
        
        return None
    
    # =============================
    #        CONVENIENCE METHODS
    # =============================
    
    def save_interaction(self, question: str, answer: str, agent: str = "core_assistant") -> Optional[str]:
        """Evaluate and save an interaction if appropriate."""
        if not self.should_save_memory(question, answer):
            debug_info("Skipping memory save - interaction doesn't meet criteria", {
                "question": question[:50] + "..." if len(question) > 50 else question
            })
            return None
        
        tags = self.extract_tags(question, answer)
        fact = self.extract_fact(question)
        
        # Determine importance
        importance = "medium"
        if "remember" in question.lower() or fact:
            importance = "high"
        elif any(tag in ["identity", "family"] for tag in tags):
            importance = "high"
        
        debug_info("Saving interaction as memory", {
            "question": question[:50] + "..." if len(question) > 50 else question,
            "tags": tags,
            "fact": fact,
            "importance": importance
        })
        
        return self.save_memory(
            question=question,
            answer=answer,
            agent=agent,
            importance=importance,
            tags=tags
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return self.db.get_stats()["memories"]
    
    def search_memories(self, query: str, **filters) -> List[Dict[str, Any]]:
        """Search memories with various filters."""
        return self.query_memories(query, **filters)
    
    def get_recent_memories(self, limit: int = 10, agent: str = None) -> List[Dict[str, Any]]:
        """Get most recent memories."""
        # Use empty query with low threshold to get recent memories by timestamp
        return self.query_memories(
            query="",  # Empty query
            limit=limit,
            agent=agent,
            similarity_threshold=0.0  # No similarity filtering
        ) 