"""
Intelligence Amplification System for ZackGPT

This module contains the core intelligence components that make ZackGPT
truly adaptive and smarter than static chatbots through:
- Memory-driven token optimization
- Dynamic personality emergence
- Contextual intelligence amplification
- Predictive user modeling
"""

import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
# Optional imports with fallbacks
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None
    HAS_SKLEARN = False
from ..data.database import get_database
from .logger import debug_log, debug_info, debug_success, debug_error

@dataclass
class UserPattern:
    """Represents learned patterns about user behavior and preferences."""
    pattern_type: str  # communication_style, expertise_level, preference, etc.
    pattern_value: str
    confidence: float
    evidence_count: int
    last_observed: str
    context_tags: List[str]

@dataclass
class ContextSignal:
    """Represents a contextual signal that influences response strategy."""
    signal_type: str  # emotion, urgency, complexity, etc.
    strength: float  # 0.0 to 1.0
    evidence: List[str]
    timestamp: str

class IntelligentContextCompressor:
    """Compresses memories into maximum information density for token optimization."""
    
    def __init__(self):
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        else:
            self.vectorizer = None
            debug_info("Scikit-learn not available - using simple text matching for relevance")
            
        self.compression_strategies = {
            'semantic_clustering': self._semantic_clustering,
            'importance_weighting': self._importance_weighting,
            'temporal_decay': self._temporal_decay,
            'relevance_filtering': self._relevance_filtering
        }
    
    def compress_memory_context(self, memories: List[Dict], current_query: str, 
                              token_budget: int = 1000) -> Tuple[str, Dict]:
        """Compress memories into maximum information density within token budget."""
        
        if not memories:
            return "", {"compression_ratio": 0.0, "memories_processed": 0}
        
        debug_info("🧠 Starting intelligent memory compression", {
            "memories_count": len(memories),
            "token_budget": token_budget,
            "query_preview": current_query[:100] + "..." if len(current_query) > 100 else current_query
        })
        
        # Stage 1: Relevance filtering
        relevant_memories = self._relevance_filtering(memories, current_query)
        
        # Stage 2: Semantic clustering to avoid redundancy  
        clustered_memories = self._semantic_clustering(relevant_memories)
        
        # Stage 3: Importance weighting
        weighted_memories = self._importance_weighting(clustered_memories, current_query)
        
        # Stage 4: Temporal decay application
        temporal_memories = self._temporal_decay(weighted_memories)
        
        # Stage 5: Compress to token budget
        compressed_context, compression_stats = self._compress_to_budget(
            temporal_memories, token_budget
        )
        
        debug_success("🎯 Memory compression complete", {
            "original_memories": len(memories),
            "final_memories": compression_stats["memories_included"],
            "compression_ratio": f"{compression_stats['compression_ratio']:.2%}",
            "token_usage": f"{compression_stats['token_count']}/{token_budget}",
            "information_density": f"{compression_stats['information_density']:.3f}"
        })
        
        return compressed_context, compression_stats
    
    def _relevance_filtering(self, memories: List[Dict], query: str, threshold: float = 0.3) -> List[Dict]:
        """Filter memories by semantic relevance to current query."""
        if not memories:
            return []
        
        # Extract text from memories for similarity calculation
        memory_texts = []
        for memory in memories:
            text = f"{memory.get('question', '')} {memory.get('answer', '')}"
            memory_texts.append(text)
        
        if not any(memory_texts):
            return memories  # Fallback if no text content
        
        if HAS_SKLEARN and self.vectorizer is not None:
            try:
                # Calculate TF-IDF similarity
                all_texts = memory_texts + [query]
                tfidf_matrix = self.vectorizer.fit_transform(all_texts)
                query_vector = tfidf_matrix[-1]
                memory_vectors = tfidf_matrix[:-1]
                
                similarities = cosine_similarity(query_vector, memory_vectors).flatten()
                
                # Filter by threshold
                relevant_memories = [
                    memories[i] for i, sim in enumerate(similarities) 
                    if sim >= threshold
                ]
                
                debug_info("🔍 Relevance filtering complete", {
                    "original_count": len(memories),
                    "relevant_count": len(relevant_memories),
                    "avg_similarity": f"{np.mean(similarities):.3f}",
                    "threshold": threshold
                })
                
                return relevant_memories
                
            except Exception as e:
                debug_error(f"Error in relevance filtering: {e}")
        
        # Fallback: simple text matching
        query_lower = query.lower()
        relevant_memories = []
        
        for memory in memories:
            text = f"{memory.get('question', '')} {memory.get('answer', '')}".lower()
            # Simple relevance check - if query words appear in memory
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in text)
            relevance_score = matches / len(query_words) if query_words else 0
            
            if relevance_score >= threshold:
                relevant_memories.append(memory)
        
        debug_info("🔍 Simple text relevance filtering complete", {
            "original_count": len(memories),
            "relevant_count": len(relevant_memories),
            "method": "simple_text_matching"
        })
        
        return relevant_memories
    
    def _semantic_clustering(self, memories: List[Dict]) -> List[Dict]:
        """Group semantically similar memories and represent clusters efficiently."""
        if len(memories) <= 1:
            return memories
        
        # Simple clustering by extracting representative memories
        # In a full implementation, this would use actual clustering algorithms
        
        # For now, deduplicate very similar memories
        unique_memories = []
        processed_texts = set()
        
        for memory in memories:
            text = f"{memory.get('question', '')} {memory.get('answer', '')}"
            text_hash = hash(text.lower().replace(' ', ''))
            
            if text_hash not in processed_texts:
                unique_memories.append(memory)
                processed_texts.add(text_hash)
        
        debug_info("🗂️ Semantic clustering complete", {
            "original_count": len(memories),
            "unique_count": len(unique_memories),
            "duplicates_removed": len(memories) - len(unique_memories)
        })
        
        return unique_memories
    
    def _importance_weighting(self, memories: List[Dict], query: str) -> List[Dict]:
        """Weight memories by importance and relevance."""
        for memory in memories:
            # Base importance from memory metadata
            base_importance = memory.get('importance_score', 0.5)
            
            # Boost based on recency
            created_time = memory.get('created_at', datetime.now().isoformat())
            try:
                created_dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                days_old = (datetime.now() - created_dt.replace(tzinfo=None)).days
                recency_boost = max(0.1, 1.0 - (days_old / 30))  # Decay over 30 days
            except:
                recency_boost = 0.5
            
            # Boost based on tags matching query intent
            tag_boost = 1.0
            query_lower = query.lower()
            for tag in memory.get('tags', []):
                if tag.lower() in query_lower:
                    tag_boost += 0.2
            
            # Calculate final weight
            memory['compression_weight'] = base_importance * recency_boost * min(tag_boost, 2.0)
        
        # Sort by weight
        memories.sort(key=lambda m: m.get('compression_weight', 0), reverse=True)
        
        debug_info("⚖️ Importance weighting complete", {
            "memories_weighted": len(memories),
            "top_weight": f"{memories[0].get('compression_weight', 0):.3f}" if memories else "N/A",
            "avg_weight": f"{np.mean([m.get('compression_weight', 0) for m in memories]):.3f}"
        })
        
        return memories
    
    def _temporal_decay(self, memories: List[Dict]) -> List[Dict]:
        """Apply temporal decay to reduce importance of old memories."""
        current_time = datetime.now()
        
        for memory in memories:
            created_time = memory.get('created_at', current_time.isoformat())
            try:
                created_dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                age_days = (current_time - created_dt.replace(tzinfo=None)).days
                
                # Exponential decay with half-life of 14 days
                decay_factor = 0.5 ** (age_days / 14)
                current_weight = memory.get('compression_weight', 0.5)
                memory['compression_weight'] = current_weight * decay_factor
                
            except Exception as e:
                debug_log(f"Error processing memory timestamp: {e}")
                # Keep current weight if timestamp parsing fails
        
        return memories
    
    def _compress_to_budget(self, memories: List[Dict], token_budget: int) -> Tuple[str, Dict]:
        """Compress memories to fit within token budget while maximizing information."""
        
        if not memories:
            return "", {"compression_ratio": 0.0, "memories_included": 0, "token_count": 0, "information_density": 0.0}
        
        compressed_parts = []
        token_count = 0
        memories_included = 0
        
        for memory in memories:
            # Create compressed representation
            question = memory.get('question', '')
            answer = memory.get('answer', '')
            importance = memory.get('compression_weight', 0.5)
            
            # Smart compression based on importance
            if importance > 0.8:  # High importance - keep full detail
                compressed = f"Q: {question}\nA: {answer}"
            elif importance > 0.5:  # Medium importance - summarize
                compressed = f"Key: {question[:100]} → {answer[:150]}"
            else:  # Low importance - just essence
                compressed = f"Note: {answer[:100]}"
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            estimated_tokens = len(compressed) // 4
            
            if token_count + estimated_tokens <= token_budget:
                compressed_parts.append(compressed)
                token_count += estimated_tokens
                memories_included += 1
            else:
                break  # Budget exceeded
        
        # Combine all compressed parts
        compressed_context = "\n\n".join(compressed_parts)
        
        # Calculate statistics
        original_content = sum(len(f"{m.get('question', '')} {m.get('answer', '')}") for m in memories)
        compression_ratio = len(compressed_context) / max(original_content, 1)
        information_density = memories_included / max(token_count, 1)
        
        stats = {
            "compression_ratio": compression_ratio,
            "memories_included": memories_included,
            "memories_total": len(memories),
            "token_count": token_count,
            "token_budget": token_budget,
            "information_density": information_density
        }
        
        return compressed_context, stats

class PersonalityEmergenceEngine:
    """Learns and develops dynamic personality based on user interactions."""
    
    def __init__(self):
        self.db = get_database()
        self.user_patterns = {}
        self.personality_traits = defaultdict(float)  # trait_name -> strength
        self.interaction_history = deque(maxlen=1000)  # Recent interactions
        
    def analyze_user_interaction(self, user_input: str, ai_response: str, 
                               user_feedback: Optional[str] = None) -> ContextSignal:
        """Analyze a single interaction to extract personality insights."""
        
        signals = []
        
        # Analyze communication style
        if any(word in user_input.lower() for word in ['please', 'thank you', 'thanks']):
            signals.append("polite_communication")
        
        if '?' in user_input and len(user_input.split()) < 10:
            signals.append("prefers_concise_questions")
        
        if any(word in user_input.lower() for word in ['explain', 'how', 'why', 'what']):
            signals.append("seeks_explanations")
        
        # Analyze technical language
        technical_words = ['function', 'class', 'variable', 'algorithm', 'implementation', 'code', 'debug']
        if any(word in user_input.lower() for word in technical_words):
            signals.append("technical_communication")
        
        # Analyze urgency
        urgency_words = ['urgent', 'quickly', 'asap', 'fast', 'immediately']
        if any(word in user_input.lower() for word in urgency_words):
            signals.append("high_urgency")
        
        # Analyze feedback
        if user_feedback:
            if any(word in user_feedback.lower() for word in ['good', 'great', 'perfect', 'thanks']):
                signals.append("positive_feedback")
            elif any(word in user_feedback.lower() for word in ['wrong', 'bad', 'no', 'incorrect']):
                signals.append("negative_feedback")
        
        # Create context signal
        context_signal = ContextSignal(
            signal_type="interaction_analysis",
            strength=len(signals) / 10.0,  # Normalize strength
            evidence=signals,
            timestamp=datetime.now().isoformat()
        )
        
        # Update personality traits
        self._update_personality_traits(signals)
        
        # Store interaction
        self.interaction_history.append({
            'user_input': user_input,
            'ai_response': ai_response,
            'user_feedback': user_feedback,
            'signals': signals,
            'timestamp': datetime.now().isoformat()
        })
        
        debug_info("🧬 Personality analysis complete", {
            "signals_detected": len(signals),
            "signals": signals,
            "context_strength": f"{context_signal.strength:.3f}",
            "personality_traits_count": len(self.personality_traits)
        })
        
        return context_signal
    
    def _update_personality_traits(self, signals: List[str]):
        """Update personality traits based on detected signals."""
        
        # Map signals to personality adjustments
        trait_updates = {
            "polite_communication": {"formality": +0.1, "warmth": +0.05},
            "prefers_concise_questions": {"conciseness": +0.1, "efficiency": +0.05},
            "seeks_explanations": {"detail_level": +0.1, "educational": +0.05},
            "technical_communication": {"technical_depth": +0.1, "precision": +0.05},
            "high_urgency": {"responsiveness": +0.1, "efficiency": +0.1},
            "positive_feedback": {"current_approach": +0.05},
            "negative_feedback": {"current_approach": -0.1}
        }
        
        for signal in signals:
            if signal in trait_updates:
                for trait, adjustment in trait_updates[signal].items():
                    self.personality_traits[trait] += adjustment
                    # Keep traits in reasonable bounds
                    self.personality_traits[trait] = max(-1.0, min(1.0, self.personality_traits[trait]))
    
    def generate_personality_adaptation(self) -> str:
        """Generate personality adaptation text for the prompt."""
        
        if not self.personality_traits:
            return "Observe user communication patterns and adapt accordingly."
        
        adaptations = []
        
        # Generate adaptation instructions based on learned traits
        for trait, strength in self.personality_traits.items():
            if abs(strength) > 0.2:  # Only significant traits
                if trait == "formality" and strength > 0:
                    adaptations.append("Use polite, formal language")
                elif trait == "conciseness" and strength > 0:
                    adaptations.append("Keep responses brief and to the point")
                elif trait == "technical_depth" and strength > 0:
                    adaptations.append("Include technical details and precision")
                elif trait == "detail_level" and strength > 0:
                    adaptations.append("Provide comprehensive explanations")
                elif trait == "efficiency" and strength > 0:
                    adaptations.append("Prioritize speed and directness")
        
        if adaptations:
            adaptation_text = "Based on learned user preferences: " + "; ".join(adaptations) + "."
        else:
            adaptation_text = "Continue learning user communication preferences."
        
        debug_info("🎭 Generated personality adaptation", {
            "active_traits": len([t for t, s in self.personality_traits.items() if abs(s) > 0.2]),
            "adaptations": len(adaptations),
            "adaptation_preview": adaptation_text[:100] + "..." if len(adaptation_text) > 100 else adaptation_text
        })
        
        return adaptation_text

class ContextualIntelligenceAmplifier:
    """Amplifies contextual understanding for more intelligent responses."""
    
    def __init__(self, thread_manager=None):
        self.context_patterns = {}
        self.conversation_analysis = {}
        self.thread_manager = thread_manager
        
    def analyze_conversation_context(self, conversation_history: List[Dict], 
                                   current_query: str, thread_id: str = None) -> Dict[str, Any]:
        """Analyze conversation context for intelligent adaptations with persistent storage."""
        
        # Load existing persistent context if available
        persistent_context = {}
        if thread_id and self.thread_manager:
            try:
                persistent_context = self.thread_manager.get_thread_context(thread_id) or {}
            except Exception as e:
                debug_error("Failed to load persistent context", e)
        
        # Start with base context, then merge with persistent data
        context = {
            'conversation_length': len(conversation_history),
            'conversation_type': 'general',
            'user_expertise': 'medium',
            'task_complexity': 'simple',
            'emotional_tone': 'neutral',
            'recent_errors': 0,
            'topic_continuity': True,
            'context_switches': 0,
            # Add persistent context tracking
            'context_evolution_count': persistent_context.get('context_evolution_count', 0) + 1,
            'learned_patterns': persistent_context.get('learned_patterns', {}),
            'expertise_progression': persistent_context.get('expertise_progression', []),
            'conversation_themes': persistent_context.get('conversation_themes', {})
        }
        
        # Merge with historical patterns from persistent context
        if persistent_context:
            # Inherit learned user expertise trend
            if 'learned_user_expertise' in persistent_context:
                context['user_expertise'] = persistent_context['learned_user_expertise']
            
            # Inherit conversation type patterns
            if 'dominant_conversation_type' in persistent_context:
                context['conversation_type'] = persistent_context['dominant_conversation_type']
        
        if not conversation_history:
            # Even with no current conversation, save context evolution
            if thread_id and self.thread_manager:
                self._save_context_to_thread(thread_id, context)
            return context
        
        # Analyze conversation type
        technical_indicators = sum(1 for msg in conversation_history[-5:] 
                                 if any(word in msg.get('content', '').lower() 
                                       for word in ['code', 'function', 'class', 'algorithm', 'debug', 'implementation']))
        
        if technical_indicators >= 2:
            context['conversation_type'] = 'technical'
            context['user_expertise'] = 'high' if technical_indicators >= 4 else 'medium'
        
        # Analyze task complexity
        complexity_indicators = sum(1 for msg in conversation_history[-3:]
                                  if len(msg.get('content', '').split()) > 50 or
                                     any(word in msg.get('content', '').lower() 
                                        for word in ['complex', 'difficult', 'advanced', 'detailed']))
        
        if complexity_indicators >= 2:
            context['task_complexity'] = 'complex'
        elif complexity_indicators >= 1:
            context['task_complexity'] = 'medium'
        
        # Analyze recent errors (simplified)
        error_indicators = ['wrong', 'incorrect', 'error', 'mistake', 'not right']
        context['recent_errors'] = sum(1 for msg in conversation_history[-5:]
                                     if any(word in msg.get('content', '').lower() 
                                           for word in error_indicators))
        
        # Analyze emotional tone (simplified)
        positive_words = ['thanks', 'great', 'good', 'awesome', 'perfect', 'excellent']
        negative_words = ['frustrated', 'confused', 'difficult', 'problem', 'issue', 'stuck']
        
        recent_content = ' '.join(msg.get('content', '') for msg in conversation_history[-3:]).lower()
        positive_count = sum(1 for word in positive_words if word in recent_content)
        negative_count = sum(1 for word in negative_words if word in recent_content)
        
        if positive_count > negative_count:
            context['emotional_tone'] = 'positive'
        elif negative_count > positive_count:
            context['emotional_tone'] = 'negative'
        
        # Update learned patterns for persistence
        self._update_learned_patterns(context, conversation_history, current_query)
        
        # Save updated context to thread if available
        if thread_id and self.thread_manager:
            self._save_context_to_thread(thread_id, context)
        
        debug_info("🧠 Context analysis complete", {
            "conversation_length": context['conversation_length'],
            "conversation_type": context['conversation_type'],
            "user_expertise": context['user_expertise'],
            "task_complexity": context['task_complexity'],
            "emotional_tone": context['emotional_tone'],
            "recent_errors": context['recent_errors'],
            "context_evolution": context['context_evolution_count'],
            "persistent_patterns": len(context.get('learned_patterns', {}))
        })
        
        return context
    
    def generate_context_awareness(self, context: Dict[str, Any]) -> str:
        """Generate context awareness instructions for the prompt."""
        
        awareness_parts = []
        
        # Adapt to conversation type
        if context.get('conversation_type') == 'technical':
            awareness_parts.append("This is a technical discussion - use precise terminology and provide implementation details")
        
        # Adapt to user expertise
        if context.get('user_expertise') == 'high':
            awareness_parts.append("User shows high expertise - skip basic explanations and focus on advanced concepts")
        elif context.get('user_expertise') == 'low':
            awareness_parts.append("Provide clear explanations and avoid overly technical language")
        
        # Adapt to task complexity
        if context.get('task_complexity') == 'complex':
            awareness_parts.append("This is a complex task - break down responses into clear steps")
        
        # Adapt to emotional tone
        if context.get('emotional_tone') == 'negative':
            awareness_parts.append("User may be frustrated - be extra patient and clear")
        elif context.get('emotional_tone') == 'positive':
            awareness_parts.append("User seems satisfied - maintain current approach")
        
        # Adapt to recent errors
        if context.get('recent_errors', 0) > 1:
            awareness_parts.append("Recent errors detected - be extra careful about accuracy and acknowledge uncertainties")
        
        if awareness_parts:
            return "Context awareness: " + "; ".join(awareness_parts) + "."
        else:
            return "Maintain general contextual awareness and adapt as needed."
    
    def _update_learned_patterns(self, context: Dict, conversation_history: List[Dict], current_query: str):
        """Update learned patterns for persistent storage."""
        
        # Update expertise progression
        expertise_levels = ['beginner', 'low', 'medium', 'high', 'expert']
        current_expertise = context.get('user_expertise', 'medium')
        if current_expertise not in context.get('expertise_progression', []):
            context.setdefault('expertise_progression', []).append({
                'level': current_expertise,
                'timestamp': datetime.now().isoformat(),
                'evidence_query': current_query[:100]
            })
        
        # Update conversation themes
        if context.get('conversation_type') != 'general':
            themes = context.setdefault('conversation_themes', {})
            theme_key = context['conversation_type']
            themes[theme_key] = themes.get(theme_key, 0) + 1
        
        # Learn dominant patterns
        patterns = context.setdefault('learned_patterns', {})
        
        # Update dominant conversation type
        if context.get('conversation_themes'):
            most_common_theme = max(context['conversation_themes'].items(), key=lambda x: x[1])
            if most_common_theme[1] >= 3:  # At least 3 occurrences
                context['dominant_conversation_type'] = most_common_theme[0]
        
        # Learn user expertise trend  
        if len(context.get('expertise_progression', [])) >= 3:
            recent_levels = [entry['level'] for entry in context['expertise_progression'][-3:]]
            if len(set(recent_levels)) == 1:  # Consistent level
                context['learned_user_expertise'] = recent_levels[0]
        
        # Track pattern confidence
        patterns['pattern_confidence'] = len(context.get('expertise_progression', [])) * 0.1
        patterns['last_updated'] = datetime.now().isoformat()
    
    def _save_context_to_thread(self, thread_id: str, context: Dict):
        """Save context to thread storage."""
        try:
            # Prepare context for storage (remove non-serializable data)
            storage_context = {}
            for key, value in context.items():
                if isinstance(value, (str, int, float, bool, list, dict)):
                    storage_context[key] = value
                else:
                    # Convert other types to string representation
                    storage_context[key] = str(value)
            
            success = self.thread_manager.update_thread_context(thread_id, storage_context)
            if success:
                debug_success("💾 Context saved to thread", {
                    "thread_id": thread_id,
                    "context_keys": len(storage_context),
                    "evolution_count": storage_context.get('context_evolution_count', 0)
                })
            else:
                debug_error("Failed to save context to thread")
                
        except Exception as e:
            debug_error(f"Error saving context to thread: {e}")

class DynamicTokenAllocator:
    """Intelligently allocates tokens based on query complexity and user patterns."""
    
    def __init__(self):
        self.allocation_history = deque(maxlen=100)
        self.optimal_allocations = {}
        
    def calculate_optimal_allocation(self, query: str, available_tokens: int = 4000,
                                   context: Dict = None) -> Dict[str, int]:
        """Calculate optimal token allocation for different prompt components."""
        
        context = context or {}
        
        # Base allocation percentages
        base_allocation = {
            'memory_context': 0.4,    # 40% for memories
            'conversation_history': 0.3,  # 30% for recent chat
            'system_prompt': 0.2,     # 20% for system instructions
            'response_buffer': 0.1    # 10% buffer for response
        }
        
        # Adjust based on query complexity
        query_length = len(query.split())
        if query_length > 50:  # Complex query
            base_allocation['memory_context'] += 0.1
            base_allocation['response_buffer'] += 0.1
            base_allocation['conversation_history'] -= 0.2
        elif query_length < 10:  # Simple query
            base_allocation['conversation_history'] += 0.1
            base_allocation['memory_context'] -= 0.1
        
        # Adjust based on conversation type
        if context.get('conversation_type') == 'technical':
            base_allocation['memory_context'] += 0.1
            base_allocation['system_prompt'] -= 0.1
        
        # Adjust based on recent errors
        if context.get('recent_errors', 0) > 1:
            base_allocation['memory_context'] += 0.15
            base_allocation['conversation_history'] -= 0.15
        
        # Calculate final token allocation
        allocation = {}
        for component, percentage in base_allocation.items():
            allocation[component] = max(100, int(available_tokens * percentage))
        
        # Ensure total doesn't exceed available tokens
        total_allocated = sum(allocation.values())
        if total_allocated > available_tokens:
            scale_factor = available_tokens / total_allocated
            allocation = {k: int(v * scale_factor) for k, v in allocation.items()}
        
        debug_info("🎯 Token allocation calculated", {
            "available_tokens": available_tokens,
            "allocation": allocation,
            "total_allocated": sum(allocation.values()),
            "query_complexity": "high" if query_length > 50 else "low" if query_length < 10 else "medium"
        })
        
        return allocation 