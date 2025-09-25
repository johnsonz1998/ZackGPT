#!/usr/bin/env python3
"""
Dynamic Memory Retrieval Engine for ZackGPT
Uses intelligent formulas to dynamically scale memory retrieval based on:
- Database size
- Query complexity 
- User patterns
- Performance constraints
- Conversation context

Features:
- Formula-based scaling with configurable constants
- Static fallbacks for reliability
- Performance monitoring and profiling
- Complete configuration integration
- Adaptive search strategy selection
"""

import math
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from ..utils.logger import debug_info, debug_success, debug_error

# Import configuration
try:
    from config import config
    HAS_CONFIG = True
except ImportError:
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from config import config
        HAS_CONFIG = True
    except ImportError:
        HAS_CONFIG = False

@dataclass
class DynamicMemoryPlan:
    """A comprehensive dynamic plan for memory retrieval."""
    recent_memories: int          # How many recent memories to fetch
    semantic_memories: int        # How many semantic matches to fetch  
    max_total_memories: int       # Upper bound on total memories
    token_budget: int            # Max tokens for memory context
    search_strategies: List[str] # Which search strategies to use
    compression_ratio: float     # How aggressively to compress (0.1-0.9)
    confidence: float            # How confident we are in this plan (0.0-1.0)
    reasoning: str              # Why we made these choices
    estimated_time_ms: float    # Predicted processing time
    fallback_used: bool         # Whether static fallback was used
    config_profile: str         # Which configuration mode was used
    complexity_score: float     # Calculated query complexity
    size_factor: float          # Database size scaling factor
    performance_scaled: bool    # Whether plan was scaled for performance

class DynamicMemoryEngine:
    """
    Intelligent memory retrieval engine with mathematical scaling.
    
    Core Formula System:
    
    1. Size Scaling Factor:
       - Small DB (< 50): factor = 0.8
       - Medium DB (50-500): linear scale 1.0 → 1.5
       - Large DB (> 500): logarithmic scale up to 2.0
    
    2. Complexity Score:
       - Base: 1.0
       - Length factor: word_count scaling
       - Keyword boosts: technical/memory terms
       - Question structure multipliers
       - Range: 0.5 (simple) to 3.0 (complex)
    
    3. Memory Allocation:
       - recent = base_recent * size_factor * complexity_multiplier
       - semantic = base_semantic * sqrt(size_factor) * complexity_multiplier
       - tokens = base_tokens * complexity_multiplier
    
    4. Performance Constraints:
       - Auto-scale down if estimated_time > max_time
       - Respect min/max memory limits
       - Token budget caps
    """
    
    def __init__(self):
        self.start_time = time.time()
        self._load_configuration()
        self._initialize_metrics()
        
        init_time = (time.time() - self.start_time) * 1000
        debug_success(f"Dynamic memory engine initialized in {init_time:.1f}ms", {
            "config_available": HAS_CONFIG,
            "system_mode": self.system_mode,
            "max_time_ms": self.max_processing_time_ms,
            "max_memories": self.max_memories
        })
    
    def _load_configuration(self):
        """Load all configuration with intelligent fallbacks."""
        if HAS_CONFIG:
            # Core settings
            self.system_mode = getattr(config, 'MEMORY_SYSTEM_MODE', 'dynamic')
            self.fallback_to_static = getattr(config, 'MEMORY_FALLBACK_TO_STATIC', True)
            self.debug_enabled = getattr(config, 'DYNAMIC_MEMORY_DEBUG', False)
            
            # Dynamic scaling parameters
            self.size_scaling_base = getattr(config, 'DYNAMIC_SIZE_SCALING_BASE', 1.0)
            self.size_scaling_log_factor = getattr(config, 'DYNAMIC_SIZE_SCALING_LOG_FACTOR', 0.5)
            self.size_scaling_max = getattr(config, 'DYNAMIC_SIZE_SCALING_MAX', 2.0)
            self.size_small_threshold = getattr(config, 'DYNAMIC_SIZE_SMALL_DB_THRESHOLD', 50)
            self.size_large_threshold = getattr(config, 'DYNAMIC_SIZE_LARGE_DB_THRESHOLD', 500)
            
            # Complexity analysis parameters
            self.complexity_length_weight = getattr(config, 'DYNAMIC_COMPLEXITY_LENGTH_WEIGHT', 0.3)
            self.complexity_keyword_boost = getattr(config, 'DYNAMIC_COMPLEXITY_KEYWORD_BOOST', 1.3)
            self.complexity_memory_boost = getattr(config, 'DYNAMIC_COMPLEXITY_MEMORY_BOOST', 1.4)
            self.complexity_question_boost = getattr(config, 'DYNAMIC_COMPLEXITY_QUESTION_BOOST', 1.2)
            self.complexity_max = getattr(config, 'DYNAMIC_COMPLEXITY_MAX', 3.0)
            self.complexity_min = getattr(config, 'DYNAMIC_COMPLEXITY_MIN', 0.5)
            
            # Performance constraints
            self.max_processing_time_ms = getattr(config, 'DYNAMIC_MAX_PROCESSING_TIME_MS', 300)
            self.base_token_budget = getattr(config, 'DYNAMIC_BASE_TOKEN_BUDGET', 2000)
            self.max_token_budget = getattr(config, 'DYNAMIC_MAX_TOKEN_BUDGET', 4000)
            self.min_memories = getattr(config, 'DYNAMIC_MIN_MEMORIES', 3)
            self.max_memories = getattr(config, 'DYNAMIC_MAX_MEMORIES', 100)
            
            # Static configurations
            self.static_configs = {
                "none": {
                    "recent": getattr(config, 'STATIC_MEMORY_NONE_RECENT', 0),
                    "semantic": getattr(config, 'STATIC_MEMORY_NONE_SEMANTIC', 0),
                    "tokens": getattr(config, 'STATIC_MEMORY_NONE_TOKENS', 200)
                },
                "light": {
                    "recent": getattr(config, 'STATIC_MEMORY_LIGHT_RECENT', 5),
                    "semantic": getattr(config, 'STATIC_MEMORY_LIGHT_SEMANTIC', 2),
                    "tokens": getattr(config, 'STATIC_MEMORY_LIGHT_TOKENS', 400)
                },
                "moderate": {
                    "recent": getattr(config, 'STATIC_MEMORY_MODERATE_RECENT', 10),
                    "semantic": getattr(config, 'STATIC_MEMORY_MODERATE_SEMANTIC', 5),
                    "tokens": getattr(config, 'STATIC_MEMORY_MODERATE_TOKENS', 800)
                },
                "full": {
                    "recent": getattr(config, 'STATIC_MEMORY_FULL_RECENT', 20),
                    "semantic": getattr(config, 'STATIC_MEMORY_FULL_SEMANTIC', 10),
                    "tokens": getattr(config, 'STATIC_MEMORY_FULL_TOKENS', 1200)
                }
            }
            
            # Search strategy settings
            self.enable_strategies = {
                "tag": getattr(config, 'DYNAMIC_ENABLE_TAG_SEARCH', True),
                "keyword": getattr(config, 'DYNAMIC_ENABLE_KEYWORD_SEARCH', True),
                "intent": getattr(config, 'DYNAMIC_ENABLE_INTENT_SEARCH', True),
                "temporal": getattr(config, 'DYNAMIC_ENABLE_TEMPORAL_SEARCH', True),
                "neural": getattr(config, 'DYNAMIC_ENABLE_NEURAL_SEARCH', True)
            }
            
            # Strategy thresholds
            self.tag_search_threshold = getattr(config, 'DYNAMIC_TAG_SEARCH_COMPLEXITY_THRESHOLD', 1.5)
            self.intent_search_db_threshold = getattr(config, 'DYNAMIC_INTENT_SEARCH_DB_SIZE_THRESHOLD', 200)
            self.temporal_search_db_threshold = getattr(config, 'DYNAMIC_TEMPORAL_SEARCH_DB_SIZE_THRESHOLD', 500)
            self.neural_search_threshold = getattr(config, 'DYNAMIC_NEURAL_SEARCH_COMPLEXITY_THRESHOLD', 2.5)
            
            # Compression settings
            self.compression_light_ratio = getattr(config, 'DYNAMIC_COMPRESSION_LIGHT_RATIO', 0.1)
            self.compression_aggressive_threshold = getattr(config, 'DYNAMIC_COMPRESSION_AGGRESSIVE_THRESHOLD', 0.6)
            self.compression_max_ratio = getattr(config, 'DYNAMIC_COMPRESSION_MAX_RATIO', 0.9)
            self.avg_tokens_per_memory = getattr(config, 'DYNAMIC_AVG_TOKENS_PER_MEMORY', 80)
            
            # Performance monitoring
            self.metrics_enabled = getattr(config, 'DYNAMIC_MEMORY_METRICS', False)
            self.profiling_enabled = getattr(config, 'DYNAMIC_MEMORY_PROFILING', False)
            self.performance_warning_threshold = getattr(config, 'DYNAMIC_PERFORMANCE_WARNING_THRESHOLD_MS', 200)
            
            # Formula tuning constants
            self.formula_complexity_base = getattr(config, 'DYNAMIC_FORMULA_COMPLEXITY_TO_MULTIPLIER_BASE', 0.3)
            self.formula_complexity_range = getattr(config, 'DYNAMIC_FORMULA_COMPLEXITY_TO_MULTIPLIER_RANGE', 1.7)
            self.formula_size_sqrt_scaling = getattr(config, 'DYNAMIC_FORMULA_SIZE_SQRT_SCALING', True)
            self.formula_performance_scale_factor = getattr(config, 'DYNAMIC_FORMULA_PERFORMANCE_SCALE_DOWN_FACTOR', 0.3)
            
            # Database stats caching
            self.cache_duration = getattr(config, 'DYNAMIC_CACHE_DB_STATS_SECONDS', 30)
            
        else:
            debug_info("Config not available - using dynamic memory engine defaults")
            self._set_default_configuration()
    
    def _set_default_configuration(self):
        """Set intelligent defaults when config is unavailable."""
        # Core settings
        self.system_mode = "dynamic"
        self.fallback_to_static = True
        self.debug_enabled = False
        
        # Dynamic scaling
        self.size_scaling_base = 1.0
        self.size_scaling_log_factor = 0.5
        self.size_scaling_max = 2.0
        self.size_small_threshold = 50
        self.size_large_threshold = 500
        
        # Complexity analysis
        self.complexity_length_weight = 0.3
        self.complexity_keyword_boost = 1.3
        self.complexity_memory_boost = 1.4
        self.complexity_question_boost = 1.2
        self.complexity_max = 3.0
        self.complexity_min = 0.5
        
        # Performance constraints
        self.max_processing_time_ms = 300
        self.base_token_budget = 2000
        self.max_token_budget = 4000
        self.min_memories = 3
        self.max_memories = 100
        
        # Static fallbacks
        self.static_configs = {
            "none": {"recent": 0, "semantic": 0, "tokens": 200},
            "light": {"recent": 5, "semantic": 2, "tokens": 400},
            "moderate": {"recent": 10, "semantic": 5, "tokens": 800},
            "full": {"recent": 20, "semantic": 10, "tokens": 1200}
        }
        
        # Search strategies
        self.enable_strategies = {
            "tag": True, "keyword": True, "intent": True, 
            "temporal": True, "neural": True
        }
        
        # Thresholds
        self.tag_search_threshold = 1.5
        self.intent_search_db_threshold = 200
        self.temporal_search_db_threshold = 500
        self.neural_search_threshold = 2.5
        
        # Compression
        self.compression_light_ratio = 0.1
        self.compression_aggressive_threshold = 0.6
        self.compression_max_ratio = 0.9
        self.avg_tokens_per_memory = 80
        
        # Monitoring
        self.metrics_enabled = False
        self.profiling_enabled = False
        self.performance_warning_threshold = 200
        
        # Formulas
        self.formula_complexity_base = 0.3
        self.formula_complexity_range = 1.7
        self.formula_size_sqrt_scaling = True
        self.formula_performance_scale_factor = 0.3
        
        # Caching
        self.cache_duration = 30
    
    def _initialize_metrics(self):
        """Initialize performance metrics tracking."""
        self.metrics = {
            'total_plans_created': 0,
            'dynamic_plans': 0,
            'static_plans': 0,
            'fallback_plans': 0,
            'avg_processing_time_ms': 0.0,
            'avg_complexity_score': 0.0,
            'performance_warnings': 0
        }
        
        # Database size cache
        self.database_size_cache = None
        self.last_size_check = 0
    
    def create_retrieval_plan(
        self,
        user_input: str,
        memory_level: str,
        conversation_context: List[Dict] = None,
        database_stats: Dict = None
    ) -> DynamicMemoryPlan:
        """
        Create an optimal memory retrieval plan.
        
        Args:
            user_input: The user's query text
            memory_level: Base level from local router ("none", "light", "moderate", "full")
            conversation_context: Recent conversation messages
            database_stats: Current database statistics
            
        Returns:
            DynamicMemoryPlan with optimized retrieval strategy
        """
        plan_start_time = time.time()
        
        # Update metrics
        self.metrics['total_plans_created'] += 1
        
        # Route based on system mode
        try:
            if self.system_mode == "static":
                plan = self._create_static_plan(user_input, memory_level)
                self.metrics['static_plans'] += 1
            elif self.system_mode == "hybrid":
                try:
                    plan = self._create_dynamic_plan(user_input, memory_level, conversation_context, database_stats)
                    self.metrics['dynamic_plans'] += 1
                except Exception as e:
                    if self.debug_enabled:
                        debug_error(f"Dynamic plan failed in hybrid mode: {e}")
                    if self.fallback_to_static:
                        plan = self._create_static_plan(user_input, memory_level, fallback=True)
                        self.metrics['fallback_plans'] += 1
                    else:
                        raise
            else:  # "dynamic"
                plan = self._create_dynamic_plan(user_input, memory_level, conversation_context, database_stats)
                self.metrics['dynamic_plans'] += 1
                
        except Exception as e:
            debug_error(f"Memory plan creation failed: {e}")
            if self.fallback_to_static:
                plan = self._create_static_plan(user_input, memory_level, fallback=True)
                self.metrics['fallback_plans'] += 1
            else:
                raise
        
        # Performance monitoring
        plan_time = (time.time() - plan_start_time) * 1000
        self.metrics['avg_processing_time_ms'] = (
            (self.metrics['avg_processing_time_ms'] * (self.metrics['total_plans_created'] - 1) + plan_time) /
            self.metrics['total_plans_created']
        )
        
        if plan_time > self.performance_warning_threshold:
            self.metrics['performance_warnings'] += 1
            if self.debug_enabled:
                debug_info(f"⚠️ Slow memory plan creation: {plan_time:.1f}ms")
        
        if self.debug_enabled:
            debug_info(f"Memory plan created ({plan_time:.1f}ms)", {
                "system_mode": self.system_mode,
                "memory_level": memory_level,
                "plan_type": plan.config_profile,
                "fallback": plan.fallback_used,
                "estimated_time": f"{plan.estimated_time_ms:.1f}ms"
            })
        
        return plan
    
    def _create_static_plan(
        self, 
        user_input: str, 
        memory_level: str, 
        fallback: bool = False
    ) -> DynamicMemoryPlan:
        """Create a static plan using configured values."""
        config_data = self.static_configs.get(memory_level, self.static_configs["moderate"])
        
        # Basic strategy selection
        strategies = ["recent"]
        if memory_level in ["moderate", "full"] and config_data["semantic"] > 0:
            strategies.append("semantic")
        if memory_level == "full":
            if self.enable_strategies.get("tag", True):
                strategies.append("tag")
            if self.enable_strategies.get("keyword", True):
                strategies.append("keyword")
        
        return DynamicMemoryPlan(
            recent_memories=config_data["recent"],
            semantic_memories=config_data["semantic"],
            max_total_memories=config_data["recent"] + config_data["semantic"],
            token_budget=config_data["tokens"],
            search_strategies=strategies,
            compression_ratio=self.compression_light_ratio,
            confidence=0.9 if not fallback else 0.7,
            reasoning=f"static_{memory_level}" + ("_fallback" if fallback else ""),
            estimated_time_ms=self._estimate_processing_time(
                config_data["recent"], config_data["semantic"], len(strategies)
            ),
            fallback_used=fallback,
            config_profile="static",
            complexity_score=1.0,
            size_factor=1.0,
            performance_scaled=False
        )
    
    def _create_dynamic_plan(
        self,
        user_input: str,
        memory_level: str,
        conversation_context: List[Dict] = None,
        database_stats: Dict = None
    ) -> DynamicMemoryPlan:
        """Create a dynamic plan using mathematical formulas."""
        formula_start_time = time.time()
        
        # === STEP 1: Analyze Query Complexity ===
        complexity_score = self._analyze_query_complexity(user_input)
        self.metrics['avg_complexity_score'] = (
            (self.metrics['avg_complexity_score'] * (self.metrics['total_plans_created'] - 1) + complexity_score) /
            self.metrics['total_plans_created']
        )
        
        # Let the local router handle query complexity - no hardcoded detection
        
        # === STEP 2: Get Database Statistics ===
        db_stats = database_stats or self._get_database_stats()
        total_memories = db_stats.get('total_memories', 100)
        
        # === STEP 3: Apply Dynamic Scaling Formulas ===
        
        # Calculate database size scaling factor
        size_factor = self._calculate_size_scaling_factor(total_memories)
        
        # Convert complexity to multiplier
        complexity_multiplier = self._calculate_complexity_multiplier(complexity_score)
        
        # Get memory level base values
        base_recent, base_semantic, base_tokens = self._get_memory_level_base(memory_level)
        
        # === CORE MEMORY FORMULAS ===
        
        # Recent memories: Linear scaling with complexity and size
        recent_memories = max(
            self.min_memories if memory_level != "none" else 0,
            min(
                int(base_recent * size_factor * complexity_multiplier),
                self.max_memories // 2
            )
        )
        
        # Semantic memories: Square root scaling to prevent explosion
        semantic_multiplier = math.sqrt(size_factor) if self.formula_size_sqrt_scaling else size_factor
        semantic_memories = max(
            1 if memory_level not in ["none"] and base_semantic > 0 else 0,
            min(
                int(base_semantic * semantic_multiplier * complexity_multiplier),
                self.max_memories // 3
            )
        )
        
        # Token budget: Scale with complexity but respect hard limits
        token_budget = min(
            int(base_tokens * complexity_multiplier),
            self.max_token_budget
        )
        
        # === STEP 4: Select Search Strategies ===
        strategies = self._select_search_strategies_configured(
            memory_level, complexity_score, total_memories
        )
        
        # Personal info strategy added by configuration, not hardcoded detection
        
        # === STEP 5: Calculate Compression Ratio ===
        total_planned = recent_memories + semantic_memories
        compression_ratio = self._calculate_compression_ratio(total_planned, token_budget)
        
        # === STEP 6: Performance Constraint Check ===
        estimated_time = self._estimate_processing_time(
            recent_memories, semantic_memories, len(strategies)
        )
        
        performance_scaled = False
        if estimated_time > self.max_processing_time_ms:
            # Scale down to meet performance constraints
            scale_factor = self.max_processing_time_ms / estimated_time
            recent_memories = int(recent_memories * scale_factor)
            semantic_memories = int(semantic_memories * scale_factor)
            estimated_time = self.max_processing_time_ms
            performance_scaled = True
            
            if self.debug_enabled:
                debug_info(f"Performance scaling applied: factor={scale_factor:.2f}")
        
        # === STEP 7: Build Final Plan ===
        
        formula_time = (time.time() - formula_start_time) * 1000
        
        # Build detailed reasoning
        reasoning_parts = [
            f"complexity={complexity_score:.1f}",
            f"size_factor={size_factor:.2f}",
            f"db_size={total_memories}",
            f"formula_time={formula_time:.1f}ms"
        ]
        if performance_scaled:
            reasoning_parts.append("performance_scaled")
        
        plan = DynamicMemoryPlan(
            recent_memories=recent_memories,
            semantic_memories=semantic_memories,
            max_total_memories=min(total_planned, self.max_memories),
            token_budget=token_budget,
            search_strategies=strategies,
            compression_ratio=max(self.compression_light_ratio, compression_ratio),
            confidence=self._calculate_confidence(complexity_score, size_factor),
            reasoning=" + ".join(reasoning_parts),
            estimated_time_ms=estimated_time,
            fallback_used=False,
            config_profile="dynamic",
            complexity_score=complexity_score,
            size_factor=size_factor,
            performance_scaled=performance_scaled
        )
        
        return plan
    
    def _analyze_query_complexity(self, user_input: str) -> float:
        """
        Analyze query complexity on a scale from complexity_min to complexity_max.
        
        Factors considered:
        - Query length (word count)
        - Technical/complex keywords
        - Memory reference keywords
        - Question structure
        """
        complexity = 1.0  # Base complexity
        
        # Length factor
        word_count = len(user_input.split())
        if word_count <= 3:
            complexity *= (0.5 + self.complexity_length_weight)
        elif word_count <= 10:
            complexity *= (0.8 + self.complexity_length_weight * 0.5)
        elif word_count > 30:
            complexity *= (1.0 + self.complexity_length_weight)
        
        # Complex keywords boost
        complex_keywords = [
            'analyze', 'comprehensive', 'detailed', 'explain everything',
            'step by step', 'breakdown', 'thorough', 'complete overview',
            'in depth', 'systematic', 'methodical'
        ]
        if any(kw in user_input.lower() for kw in complex_keywords):
            complexity *= self.complexity_keyword_boost
        
        # Memory reference keywords boost  
        memory_keywords = [
            'remember', 'recall', 'discussed', 'mentioned', 'told me',
            'we talked', 'you said', 'previously', 'before', 'earlier',
            'last time', 'yesterday', 'last week'
        ]
        if any(kw in user_input.lower() for kw in memory_keywords):
            complexity *= self.complexity_memory_boost
        
        # Multiple questions boost
        question_count = user_input.count('?')
        if question_count > 1:
            complexity *= (self.complexity_question_boost ** (question_count - 1))
        
        # Clamp to configured range
        return max(self.complexity_min, min(complexity, self.complexity_max))
    
    def _calculate_size_scaling_factor(self, total_memories: int) -> float:
        """
        Calculate database size scaling factor using configured thresholds.
        
        Formula:
        - Small DB (< small_threshold): factor = 0.8
        - Medium DB (small_threshold to large_threshold): linear scale
        - Large DB (> large_threshold): logarithmic scale (capped)
        """
        if total_memories < self.size_small_threshold:
            return 0.8
        elif total_memories < self.size_large_threshold:
            # Linear scaling from base to base + 0.5
            progress = (total_memories - self.size_small_threshold) / (self.size_large_threshold - self.size_small_threshold)
            return self.size_scaling_base + progress * 0.5
        else:
            # Logarithmic scaling for large databases
            log_factor = math.log10(total_memories / self.size_large_threshold) * self.size_scaling_log_factor
            return min(self.size_scaling_base + 0.5 + log_factor, self.size_scaling_max)
    
    def _calculate_complexity_multiplier(self, complexity_score: float) -> float:
        """Convert complexity score to retrieval multiplier using configured formula."""
        # Map complexity (complexity_min to complexity_max) to multiplier range
        normalized = (complexity_score - self.complexity_min) / (self.complexity_max - self.complexity_min)
        return self.formula_complexity_base + normalized * self.formula_complexity_range
    
    def _get_memory_level_base(self, memory_level: str) -> Tuple[int, int, int]:
        """Get base values for memory level from static config."""
        static_config = self.static_configs.get(memory_level, self.static_configs["moderate"])
        return static_config["recent"], static_config["semantic"], static_config["tokens"]
    
    def _select_search_strategies_configured(
        self, 
        memory_level: str, 
        complexity_score: float, 
        total_memories: int
    ) -> List[str]:
        """Select search strategies based on configuration and thresholds."""
        strategies = ["recent"]  # Always include recent memories
        
        # Semantic search for moderate and full levels
        if memory_level in ["moderate", "full"]:
            strategies.append("semantic")
        
        # Additional strategies for full level based on complexity/size thresholds
        if memory_level == "full":
            
            # Tag search: enabled by config and complexity threshold
            if (self.enable_strategies.get("tag", True) and 
                complexity_score >= self.tag_search_threshold):
                strategies.append("tag")
            
            # Keyword search: enabled by config and complexity
            if (self.enable_strategies.get("keyword", True) and 
                complexity_score >= self.tag_search_threshold):
                strategies.append("keyword")
            
            # Intent search: enabled by config, complexity, and database size
            if (self.enable_strategies.get("intent", True) and 
                complexity_score >= self.tag_search_threshold and
                total_memories >= self.intent_search_db_threshold):
                strategies.append("intent")
            
            # Temporal search: enabled by config and large database
            if (self.enable_strategies.get("temporal", True) and 
                total_memories >= self.temporal_search_db_threshold):
                strategies.append("temporal")
            
            # Neural search: enabled by config and high complexity
            if (self.enable_strategies.get("neural", True) and 
                complexity_score >= self.neural_search_threshold):
                strategies.append("neural")
            
            # Personal info search: always enabled for full memory level
            # This handles comprehensive personal information retrieval
            strategies.append("personal_info")
        
        return strategies
    
    def _calculate_compression_ratio(self, total_memories: int, token_budget: int) -> float:
        """
        Calculate memory compression ratio based on token constraints.
        
        Higher values = more aggressive compression.
        """
        if total_memories == 0:
            return self.compression_light_ratio
        
        # Estimate total tokens needed
        estimated_tokens = total_memories * self.avg_tokens_per_memory
        
        if estimated_tokens <= token_budget:
            return self.compression_light_ratio
        else:
            # Compression ratio increases with token budget overage
            overage_ratio = estimated_tokens / token_budget
            compression = self.compression_light_ratio + (overage_ratio - 1) * 0.4
            return min(compression, self.compression_max_ratio)
    
    def _estimate_processing_time(
        self, 
        recent_memories: int, 
        semantic_memories: int, 
        strategy_count: int
    ) -> float:
        """Estimate memory retrieval processing time in milliseconds."""
        # Base processing times (rough estimates)
        recent_time = recent_memories * 0.5     # 0.5ms per recent memory
        semantic_time = semantic_memories * 2   # 2ms per semantic search
        strategy_time = strategy_count * 10     # 10ms per additional strategy
        overhead_time = 20                      # Base overhead
        
        return recent_time + semantic_time + strategy_time + overhead_time
    
    def _calculate_confidence(self, complexity_score: float, size_factor: float) -> float:
        """Calculate confidence in the retrieval plan."""
        base_confidence = 0.8
        
        # Reduce confidence for extreme values
        if complexity_score > 2.5 or size_factor > 1.8:
            base_confidence -= 0.2
        elif complexity_score < 0.7 or size_factor < 0.9:
            base_confidence -= 0.1
        
        return max(0.3, base_confidence)
    

    
    def _get_database_stats(self) -> Dict:
        """Get database statistics with caching."""
        current_time = time.time()
        
        # Use cached value if recent
        if (self.database_size_cache and 
            current_time - self.last_size_check < self.cache_duration):
            return self.database_size_cache
        
        try:
            # This will be injected/updated when integrated with actual database
            # For now, return reasonable defaults
            stats = {
                'total_memories': 100,
                'recent_activity': 10,
                'avg_memory_size': 150,
                'last_updated': current_time
            }
            
            self.database_size_cache = stats
            self.last_size_check = current_time
            return stats
            
        except Exception as e:
            debug_error("Failed to get database stats", e)
            return {
                'total_memories': 50,
                'recent_activity': 5, 
                'avg_memory_size': 100,
                'last_updated': current_time
            }
    
    def get_metrics(self) -> Dict:
        """Get current performance metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self._initialize_metrics()
        debug_info("Dynamic memory engine metrics reset")

# === GLOBAL SINGLETON INSTANCE ===

_dynamic_engine_instance = None

def get_dynamic_memory_engine() -> DynamicMemoryEngine:
    """Get the global dynamic memory engine instance (singleton pattern)."""
    global _dynamic_engine_instance
    if _dynamic_engine_instance is None:
        _dynamic_engine_instance = DynamicMemoryEngine()
    return _dynamic_engine_instance

# === CONVENIENCE FUNCTIONS ===

def create_memory_plan(
    user_input: str,
    memory_level: str,
    conversation_context: List[Dict] = None,
    database_stats: Dict = None
) -> DynamicMemoryPlan:
    """Create a dynamic memory retrieval plan."""
    return get_dynamic_memory_engine().create_retrieval_plan(
        user_input, memory_level, conversation_context, database_stats
    )

def get_engine_metrics() -> Dict:
    """Get current dynamic memory engine metrics."""
    return get_dynamic_memory_engine().get_metrics()

def reset_engine_metrics():
    """Reset dynamic memory engine metrics."""
    get_dynamic_memory_engine().reset_metrics() 