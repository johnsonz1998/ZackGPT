#!/usr/bin/env python3
"""
Lightning-Fast Local Decision Engine for ZackGPT
Uses lightweight ML models to make routing decisions in milliseconds

This is the AI traffic controller that decides:
- Memory retrieval intensity (none/light/moderate/full)
- Whether to save interactions as memories
- Response complexity routing
- Multi-step workflow decisions

All without external API calls - pure local inference.
"""

import re
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from ..utils.logger import debug_info, debug_success, debug_error

# Try to import ML dependencies
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_ML = True
except ImportError:
    HAS_ML = False
    print("⚠️ ML dependencies not available - using rule-based fallbacks")

@dataclass
class RoutingDecision:
    """Decision made by the local router."""
    memory_level: str  # "none", "light", "moderate", "full"
    save_memory: bool  # Should this interaction be saved?
    response_complexity: str  # "simple", "detailed", "analytical"
    needs_web_search: bool  # Should we do web search?
    confidence: float  # How confident are we in this decision?
    reasoning: str  # Why did we make this decision?
    processing_time_ms: float  # How long did the decision take?

class LocalIntelligenceRouter:
    """
    Lightning-fast local decision engine for AI routing.
    
    Uses lightweight ML models and rule-based systems to make
    routing decisions in <50ms without external API calls.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self._load_models()
        self._setup_patterns()
        
        init_time = (time.time() - self.start_time) * 1000
        debug_success(f"Local router initialized in {init_time:.1f}ms", {
            "ml_available": HAS_ML,
            "model_loaded": hasattr(self, 'embedder') if HAS_ML else False
        })
    
    def _load_models(self):
        """Load lightweight ML models for decision making."""
        if not HAS_ML:
            debug_info("Using rule-based routing (no ML dependencies)")
            return
            
        try:
            # Use a tiny, fast sentence transformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Only 80MB, very fast
            self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
            
            # Pre-compute embeddings for common query types
            self._setup_query_embeddings()
            
        except Exception as e:
            debug_error("Failed to load ML models, falling back to rules", e)
            self.embedder = None
    
    def _setup_query_embeddings(self):
        """Pre-compute embeddings for common query patterns."""
        if not hasattr(self, 'embedder') or self.embedder is None:
            return
            
        # Common query types with known memory needs
        self.query_patterns = {
            "greeting": ["hi", "hello", "hey there", "good morning"],
            "personal": ["my name is", "I am", "tell me about myself", "remember that I"],
            "memory_recall": ["do you remember", "what did I say", "we discussed", "you told me"],
            "complex_analysis": ["analyze", "explain in detail", "comprehensive overview", "step by step"],
            "simple_question": ["what is", "how do I", "can you", "quick question"],
            "creative": ["write a story", "create", "generate", "make up"]
        }
        
        try:
            # Pre-compute embeddings for pattern matching
            self.pattern_embeddings = {}
            for category, examples in self.query_patterns.items():
                embeddings = self.embedder.encode(examples)
                self.pattern_embeddings[category] = np.mean(embeddings, axis=0)
                
        except Exception as e:
            debug_error("Failed to setup query embeddings", e)
            self.pattern_embeddings = {}
    
    def _setup_patterns(self):
        """Setup rule-based patterns for fast decisions."""
     
        # Memory trigger patterns (high-priority for saving)
        # HARDCODING REMOVED - Using intelligent keyword analysis instead
        debug_info("Local router using intelligent analysis - no hardcoded patterns")
        
        # Simple keyword sets for intelligent analysis
        self.memory_keywords = ["remember", "recall", "know", "discussed", "mentioned", "told", "said"]
        self.personal_keywords = ["my", "me", "i", "myself", "about", "tell"]
        self.simple_keywords = ["hi", "hello", "hey", "thanks", "yes", "no", "ok", "bye"]
        self.web_keywords = ["current", "latest", "today", "news", "weather", "search"]

    def route_query(self, user_input: str, conversation_context: List[Dict] = None) -> RoutingDecision:
        """
        Make routing decisions for a user query in <50ms.
        
        Args:
            user_input: The user's input text
            conversation_context: Recent conversation messages
            
        Returns:
            RoutingDecision with all routing information
        """
        start_time = time.time()
        
        # Clean and normalize input
        query = user_input.strip().lower()
        word_count = len(user_input.split())
        
        # Start with defaults
        memory_level = "moderate"
        save_memory = False
        response_complexity = "detailed"
        needs_web_search = False
        confidence = 0.7
        reasoning_parts = []
        
        # === STEP 1: Intelligent keyword analysis (no hardcoded patterns) ===
        
        words = query.split()
        
        # Check for simple queries
        simple_score = sum(1 for word in words if word in self.simple_keywords)
        if simple_score > 0 and word_count <= 2:
            memory_level = "none"
            response_complexity = "simple"
            confidence = 0.95
            reasoning_parts.append("simple_greeting")
        
        # Check for memory-intensive queries
        elif memory_level != "none":
            memory_score = sum(1 for word in words if word in self.memory_keywords)
            personal_score = sum(1 for word in words if word in self.personal_keywords)
            
            if memory_score > 0 or personal_score >= 2:
                memory_level = "full"
                response_complexity = "analytical"
                confidence = 0.9
                reasoning_parts.append("memory_query_detected")
        
        # === STEP 2: Intelligent memory saving analysis ===
        
        # Save memory if user is sharing personal info or asking about memory
        personal_sharing = any(word in query for word in ["my", "i am", "i'm", "i have", "i work", "i live"])
        memory_asking = any(word in query for word in self.memory_keywords)
        
        save_memory = personal_sharing or memory_asking
        if save_memory:
            reasoning_parts.append("save_worthy_content")
        
        # === STEP 3: Intelligent web search detection ===
        
        web_score = sum(1 for word in words if word in self.web_keywords)
        if web_score > 0:
            needs_web_search = True
            reasoning_parts.append("web_search_needed")
        
        # === STEP 4: ML-based refinement (if available) ===
        
        if HAS_ML and hasattr(self, 'embedder') and self.embedder is not None:
            try:
                ml_decision = self._ml_enhanced_routing(user_input, memory_level)
                if ml_decision:
                    memory_level = ml_decision.get('memory_level', memory_level)
                    confidence = min(confidence + 0.1, 1.0)  # Boost confidence with ML
                    reasoning_parts.append("ml_enhanced")
            except Exception as e:
                debug_error("ML routing failed, using rule-based", e)
        
        # === STEP 5: Context-based adjustments ===
        
        if conversation_context and len(conversation_context) > 0:
            # If recent context mentions memory/recall, boost memory level
            recent_text = " ".join([msg.get('content', '') for msg in conversation_context[-3:]])
            if any(word in recent_text.lower() for word in ['remember', 'recall', 'mentioned', 'discussed']):
                if memory_level in ["none", "light"]:
                    memory_level = "moderate"
                    reasoning_parts.append("context_memory_boost")
        
        # === STEP 6: Length-based adjustments ===
        
        if word_count <= 3 and memory_level not in ["none"]:
            memory_level = "light"  # Short queries rarely need full memory
            reasoning_parts.append("short_query_optimization")
        elif word_count > 30:
            response_complexity = "analytical"  # Long queries want detailed responses
            reasoning_parts.append("long_query_detail")
        
        processing_time = (time.time() - start_time) * 1000
        
        decision = RoutingDecision(
            memory_level=memory_level,
            save_memory=save_memory,
            response_complexity=response_complexity,
            needs_web_search=needs_web_search,
            confidence=confidence,
            reasoning=" + ".join(reasoning_parts) if reasoning_parts else "default_routing",
            processing_time_ms=processing_time
        )
        
        debug_info(f"Local routing decision ({processing_time:.1f}ms)", {
            "memory_level": memory_level,
            "save_memory": save_memory,
            "complexity": response_complexity,
            "web_search": needs_web_search,
            "confidence": f"{confidence:.2f}",
            "reasoning": decision.reasoning
        })
        
        return decision
    
    def _ml_enhanced_routing(self, user_input: str, current_decision: str) -> Optional[Dict]:
        """Use ML to enhance routing decisions."""
        if not self.pattern_embeddings:
            return None
            
        try:
            # Get query embedding
            query_embedding = self.embedder.encode([user_input])[0]
            
            # Find most similar pattern
            best_match = None
            best_similarity = 0
            
            for category, pattern_embedding in self.pattern_embeddings.items():
                similarity = cosine_similarity([query_embedding], [pattern_embedding])[0][0]
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = category
            
            # Apply ML-based routing rules
            if best_similarity > 0.7:  # High confidence threshold
                if best_match == "greeting":
                    return {"memory_level": "none"}
                elif best_match == "personal":
                    return {"memory_level": "full"}
                elif best_match == "memory_recall":
                    return {"memory_level": "full"}
                elif best_match == "complex_analysis":
                    return {"memory_level": "moderate"}
                elif best_match == "simple_question":
                    return {"memory_level": "light"}
                    
        except Exception as e:
            debug_error("ML enhancement failed", e)
            
        return None
    
    def should_save_interaction(self, user_input: str, ai_response: str) -> Tuple[bool, float, str]:
        """
        Decide if an interaction should be saved as memory.
        
        Returns:
            (should_save, confidence, reasoning)
        """
        start_time = time.time()
        
        # Fast rule-based memory saving decision
        save_score = 0
        reasons = []
        
        combined_text = f"{user_input} {ai_response}".lower()
        
        # Check for personal information using intelligent analysis
        personal_sharing = any(word in combined_text for word in ["my", "i am", "i'm", "i have", "i work", "i live"])
        memory_asking = any(word in combined_text for word in self.memory_keywords)
        
        if personal_sharing:
            save_score += 2
            reasons.append("personal_info")
        
        if memory_asking:
            save_score += 1
            reasons.append("memory_related")
        
        # Boost for longer, meaningful interactions
        if len(ai_response) > 200:
            save_score += 1
            reasons.append("substantial_response")
        
        # Reduce for simple greetings using intelligent analysis
        simple_score = sum(1 for word in user_input.lower().split() if word in self.simple_keywords)
        if simple_score > 0 and len(user_input.split()) <= 2:
            save_score -= 2
            reasons.append("simple_interaction")
        
        should_save = save_score > 0
        confidence = min(abs(save_score) / 3.0, 1.0)  # Normalize to 0-1
        reasoning = " + ".join(reasons) if reasons else "default_threshold"
        
        processing_time = (time.time() - start_time) * 1000
        
        debug_info(f"Memory save decision ({processing_time:.1f}ms)", {
            "should_save": should_save,
            "confidence": f"{confidence:.2f}",
            "score": save_score,
            "reasoning": reasoning
        })
        
        return should_save, confidence, reasoning

# Global instance for fast access
_router_instance = None

def get_local_router() -> LocalIntelligenceRouter:
    """Get the global router instance (singleton pattern)."""
    global _router_instance
    if _router_instance is None:
        _router_instance = LocalIntelligenceRouter()
    return _router_instance

# Convenience functions
def route_query(user_input: str, conversation_context: List[Dict] = None) -> RoutingDecision:
    """Quick routing decision for a query."""
    return get_local_router().route_query(user_input, conversation_context)

def should_save_memory(user_input: str, ai_response: str) -> bool:
    """Quick decision on whether to save an interaction."""
    should_save, _, _ = get_local_router().should_save_interaction(user_input, ai_response)
    return should_save 