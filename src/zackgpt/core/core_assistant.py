import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from openai import OpenAI
from ..data.database import get_database
from ..utils.logger import debug_log, debug_info, debug_error, debug_success
from config import config
# Removed deprecated prompt_utils import - using EvolutionaryPromptBuilder instead
import tiktoken
# Lazy imports to speed up module loading
# from .prompt_builder import EvolutionaryPromptBuilder  # Import when needed
from ..tools.web_search import search_web, get_webpage_content, WEB_SEARCH_ENABLED

class ConversationManager:
    def __init__(self, max_tokens=4000, max_messages=10):
        # Apply lightweight mode limits if enabled
        lightweight_mode = os.getenv("ZACKGPT_LIGHTWEIGHT", "false").lower() == "true"
        if lightweight_mode:
            max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
            max_messages = int(os.getenv("MAX_CONVERSATION_HISTORY", "3"))
            
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.messages = []
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        self.lightweight_mode = lightweight_mode
        
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
        self._trim_history()
        
    def _trim_history(self):
        """Trim history to stay within token and message limits."""
        while len(self.messages) > self.max_messages:
            self.messages.pop(0)
            
        # If still over token limit, summarize older messages
        while self._count_tokens() > self.max_tokens and len(self.messages) > 2:
            # Keep the system message and last message
            system_msg = self.messages[0]
            last_msg = self.messages[-1]
            middle_msgs = self.messages[1:-1]
            
            # Summarize middle messages
            summary = self._summarize_messages(middle_msgs)
            
            # Rebuild conversation with summary
            self.messages = [system_msg, {"role": "system", "content": f"Previous conversation summary: {summary}"}, last_msg]
            
    def _count_tokens(self) -> int:
        """Count total tokens in conversation history."""
        return sum(len(self.encoding.encode(msg["content"])) for msg in self.messages)
        
    def _summarize_messages(self, messages: list) -> str:
        """Summarize a list of messages."""
        if not messages:
            return ""
            
        # Extract key information
        summary_points = []
        for msg in messages:
            if msg["role"] == "user":
                # Extract key phrases (questions, statements, etc.)
                content = msg["content"]
                if "?" in content:
                    summary_points.append(f"Asked about: {content.split('?')[0]}")
                elif len(content.split()) > 3:
                    summary_points.append(f"Discussed: {content}")
                    
        return " | ".join(summary_points)
        
    def get_context(self) -> list:
        """Get the current conversation context."""
        return self.messages.copy()

class CoreAssistant:
    def __init__(self):
        """Initialize the core assistant with OpenAI client and memory database."""
        try:
            # Use the robust client creation from query_utils
            from .query_utils import create_openai_client
            self.client = create_openai_client()
        except Exception as e:
            debug_error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
        self.model = config.LLM_MODEL
        self._memory_db = None
        self.conversation = ConversationManager()
        self._prompt_builder = None  # Lazy initialization
        
    @property
    def memory_db(self):
        """Lazy load unified database."""
        if self._memory_db is None:
            self._memory_db = get_database()
        return self._memory_db
    
    @property
    def prompt_builder(self):
        """Lazy load prompt builder to speed up imports."""
        if self._prompt_builder is None:
            from .prompt_builder import PromptBuilder
            self._prompt_builder = PromptBuilder()
        return self._prompt_builder
        
    # Removed deprecated prompt property - using EvolutionaryPromptBuilder instead
        
    def build_context(self, user_input: str, agent: str = "core_assistant") -> list:
        """Build context using dynamic memory retrieval system."""
        try:
            # STEP 1: LOCAL INTELLIGENCE ROUTING - Get base memory level
            from .local_router import route_query
            
            # Get conversation context for the router
            conversation_context = [{"content": msg["content"], "role": msg["role"]} 
                                  for msg in self.conversation.messages[-5:]]
            
            # Make routing decision in <1ms
            routing_decision = route_query(user_input, conversation_context)
            
            debug_info(f"Local router decision ({routing_decision.processing_time_ms:.1f}ms)", {
                "memory_level": routing_decision.memory_level,
                "reasoning": routing_decision.reasoning,
                "confidence": f"{routing_decision.confidence:.2f}"
            })
            
            # STEP 2: SIMPLE MEMORY PLANNING
            from .dynamic_memory_engine import create_memory_plan
            
            # Create simple memory plan
            memory_plan = create_memory_plan(
                user_input=user_input,
                memory_level=routing_decision.memory_level
            )
            
            debug_info(f"Simple memory plan", {
                "recent": memory_plan.recent_memories,
                "semantic": memory_plan.semantic_memories,
                "strategies": memory_plan.search_strategies
            })
            
            # STEP 3: EXECUTE SIMPLE RETRIEVAL PLAN
            return self._build_dynamic_context(user_input, agent, memory_plan)
                
        except Exception as e:
            debug_error("Failed to build dynamic context", e)
            # Fallback to simple context on error
            return [{"role": "user", "content": user_input}]
    

            
    def _build_simple_context(self, user_input: str) -> list:
        """Build a simplified context for very short queries."""
        short_term = ""
        for msg in self.conversation.messages[-3:]: # Use fewer messages for simple queries
            if msg["role"] in ("user", "assistant"):
                short_term += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        # For very simple queries, we might not have a full memory context
        # or it might be too complex to process.
        # We'll just use the short-term context and a placeholder for memories.
        memory_context = "No detailed memory context available for this simple query."
        
        conversation_context = {
            'conversation_length': len(self.conversation.messages),
            'recent_errors': self._count_recent_errors(),
            'user_expertise': self._assess_user_expertise(),
            'conversation_type': self._classify_conversation_type(user_input),
            'task_complexity': 'simple',
            'current_query': user_input,
            'conversation_history': [{"content": msg["content"], "role": msg["role"]} 
                                   for msg in self.conversation.messages[-5:]],
            'memories': [], # No detailed memories for simple queries
            'max_tokens': 4000,
            'compressed_memory_context': memory_context
        }
        
        system_prompt = self.prompt_builder.build_system_prompt(
            short_term, 
            memory_context,
            conversation_context
        )
        
        # Add system message to conversation
        if not self.conversation.messages or self.conversation.messages[0]["role"] != "system":
            self.conversation.add_message("system", system_prompt)
        else:
            self.conversation.messages[0]["content"] = system_prompt
        
        # Add user message
        self.conversation.add_message("user", user_input)
        
        debug_info("Built fast context for simple query", {
            "query": user_input[:50] + "...",
            "conversation_length": len(self.conversation.messages)
        })
        
        return self.conversation.get_context()
    
    def _count_recent_errors(self) -> int:
        """Count recent errors/uncertainty in conversation."""
        recent_messages = self.conversation.messages[-10:]
        error_phrases = ["don't know", "not sure", "uncertain", "unclear", "can't help"]
        
        count = 0
        for msg in recent_messages:
            if msg.get('role') == 'assistant':
                content = msg.get('content', '').lower()
                if any(phrase in content for phrase in error_phrases):
                    count += 1
        return count
    
    def _assess_user_expertise(self) -> str:
        """Assess user's expertise level from conversation."""
        technical_terms = ["api", "database", "algorithm", "function", "server", "docker", 
                          "config", "backend", "frontend", "deployment", "debug", "git"]
        
        recent_user_messages = [msg.get('content', '') for msg in self.conversation.messages[-10:] 
                               if msg.get('role') == 'user']
        
        tech_score = sum(1 for msg in recent_user_messages 
                        for term in technical_terms 
                        if term.lower() in msg.lower())
        
        if tech_score > 5:
            return 'high'
        elif tech_score > 2:
            return 'medium'
        else:
            return 'beginner'
    
    def _classify_conversation_type(self, user_input: str) -> str:
        """Classify the type of conversation."""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["error", "bug", "problem", "issue", "broken"]):
            return 'troubleshooting'
        elif any(word in user_lower for word in ["how", "what", "explain", "help", "learn"]):
            return 'learning'
        elif any(word in user_lower for word in ["build", "create", "make", "develop", "implement"]):
            return 'creation'
        elif any(word in user_lower for word in ["remember", "recall", "my", "save"]):
            return 'memory'
        elif self._needs_web_search(user_input):
            return 'web_search'
        else:
            return 'general'
    
    def _needs_web_search(self, user_input: str) -> bool:
        """Determine if the user input requires web search."""
        if not WEB_SEARCH_ENABLED:
            return False
            
        user_lower = user_input.lower()
        
        # Current events and news
        time_indicators = ["today", "now", "current", "latest", "recent", "new", "breaking"]
        news_keywords = ["news", "happening", "events", "updates", "reports"]
        
        # Specific information requests (EXCLUDING conversational questions)
        search_triggers = [
            "search for", "look up", "find information about",
            "price of", "cost of", "weather", "stock", "exchange rate"
        ]
        
        # Conversational questions that should NOT trigger web search
        conversational_exclusions = [
            "what is your name", "who are you", "tell me about yourself",
            "what are you", "how are you", "what can you do"
        ]
        
        # Check for conversational exclusions first
        for exclusion in conversational_exclusions:
            if exclusion in user_lower:
                return False
        
        # Real-time data requests
        realtime_keywords = ["weather", "temperature", "forecast", "stock price", 
                           "exchange rate", "cryptocurrency", "bitcoin", "score"]
        
        # Check for explicit search requests
        if any(trigger in user_lower for trigger in search_triggers):
            return True
            
        # Check for current events
        if any(indicator in user_lower for indicator in time_indicators) and \
           any(keyword in user_lower for keyword in news_keywords):
            return True
            
        # Check for real-time data
        if any(keyword in user_lower for keyword in realtime_keywords):
            return True
            
        # Check for specific years (current events)
        import datetime
        current_year = datetime.datetime.now().year
        recent_years = [str(year) for year in range(current_year - 2, current_year + 1)]
        if any(year in user_input for year in recent_years):
            return True
            
        return False
    
    def _perform_web_search(self, user_input: str) -> str:
        """Perform web search and return results."""
        try:
            debug_info("Performing web search", {"query": user_input})
            
            # Extract search query from user input
            search_query = self._extract_search_query(user_input)
            
            # Perform the search
            search_results = search_web(search_query, max_results=5)
            
            debug_info("Web search completed", {
                "query": search_query,
                "results_length": len(search_results)
            })
            
            return search_results
            
        except Exception as e:
            debug_error("Web search failed", {"error": str(e)})
            return f"I apologize, but I couldn't search the web right now. Error: {str(e)}"
    
    def _extract_search_query(self, user_input: str) -> str:
        """Extract the actual search query from user input."""
        user_lower = user_input.lower()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "search for ", "look up ", "find information about ",
            "tell me about ", "what is ", "who is ", "when did ",
            "where is ", "how much ", "price of ", "cost of "
        ]
        
        query = user_input
        for prefix in prefixes_to_remove:
            if user_lower.startswith(prefix):
                query = user_input[len(prefix):]
                break
        
        # Clean up the query
        query = query.strip().strip("?").strip()
        
        return query if query else user_input
    
    def _assess_response_quality_ai(self, response: str, user_input: str, conversation_context: Dict) -> Dict:
        """AI-powered response quality assessment."""
        try:
            from .prompt_enhancer import SimplePromptScorer
            scorer = SimplePromptScorer()
            return scorer.assess_response(response, user_input, conversation_context)
        except Exception as e:
            debug_error("AI assessment failed, using fallback", e)
            return self._assess_response_quality_fallback(response, user_input)
    
    def _assess_response_quality_fallback(self, response: str, user_input: str) -> Dict:
        """Fallback heuristic assessment (original method)."""
        response_lower = response.lower()
        
        # Bad signs
        bad_phrases = [
            "i don't know", "i'm not sure", "i can't help", 
            "sorry, i don't", "i'm unable to", "i don't have",
            "unclear", "uncertain", "not confident"
        ]
        
        issues = []
        if any(phrase in response_lower for phrase in bad_phrases):
            issues.append("uncertainty")
        
        if len(response) < 10:
            issues.append("too_short")
            
        if response.lower().startswith("sorry"):
            issues.append("overly_apologetic")
        
        success = len(issues) == 0 and len(response) > 20
        score = 0.8 if success else 0.3
        
        return {
            "overall_score": score,
            "success": success,
            "issues": issues,
            "assessment_type": "fallback_heuristic",
            "reasoning": "Fallback assessment due to AI failure"
        }
    
    def get_evolution_stats(self) -> dict:
        """Get statistics about prompt evolution for debugging."""
        return {"note": "Evolution stats removed - simplified system"}
        
    def process_input(self, user_input: str, short_term_context: str = "") -> str:
        """Process user input and generate a response."""
        try:
            debug_info("Processing input", {
                "input": user_input,
                "context_length": len(short_term_context)
            })
            
            # Check for forced web search
            force_web_search = user_input.startswith("[WEB_SEARCH_FORCED]")
            if force_web_search:
                # Remove the force flag and get the actual query
                user_input = user_input.replace("[WEB_SEARCH_FORCED]", "").strip()
                debug_info("Forced web search detected", {"original_query": user_input})
            
            # Check if web search is needed (either forced or automatic)
            search_results = ""
            if force_web_search or self._needs_web_search(user_input):
                search_results = self._perform_web_search(user_input)
                debug_info("Web search completed", {
                    "query": user_input,
                    "forced": force_web_search,
                    "results_preview": search_results[:200] + "..." if len(search_results) > 200 else search_results
                })
            
            # Build context (including search results if available)
            context = self.build_context(user_input)
            
            # Add search results to context if available
            if search_results:
                search_context = f"\n\nWeb Search Results:\n{search_results}\n\nPlease use this information to provide a comprehensive and up-to-date answer."
                if context and context[-1]["role"] == "user":
                    context[-1]["content"] += search_context
            
            # Log (context, prompt) pair for future training
            debug_log("LLM prompt context", context)
            if context and context[0]["role"] == "system":
                debug_log("System prompt for training", context[0]["content"])
            
            # Get response from OpenAI
            if self.client is None:
                return "I apologize, but I cannot connect to the AI service right now. Please check your OpenAI API configuration."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=context,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # Add assistant's response to conversation
            self.conversation.add_message("assistant", answer)
            
            # DISABLED: AI-powered feedback (too slow for now)
            # conversation_context = {
            #     'conversation_length': len(self.conversation.messages),
            #     'recent_errors': self._count_recent_errors(),
            #     'user_expertise': self._assess_user_expertise(),
            #     'conversation_type': self._classify_conversation_type(user_input),
            #     'task_complexity': 'complex' if len(user_input) > 100 else 'simple',
            #     'used_web_search': bool(search_results)
            # }
            # quality_assessment = self._assess_response_quality_ai(answer, user_input, conversation_context)
            # self.prompt_builder.record_response_feedback(
            #     self.prompt_builder.current_prompt_metadata, 
            #     quality_assessment,
            #     user_feedback=None,
            #     user_input=user_input,
            #     ai_response=answer
            # )
            
            debug_info("Generated response", {
                "response_length": len(answer),
                "used_web_search": bool(search_results)
            })
            
            # SIMPLIFIED MEMORY SAVING: Just save if it looks important  
            try:
                # Simple heuristic: save if user shares personal info or asks about memory
                user_lower = user_input.lower()
                should_save = any(phrase in user_lower for phrase in [
                    "my", "i am", "i work", "i live", "i like", "i prefer", "remember that"
                ])
                
                if should_save:
                    memory_id = self.memory_db.save_memory(
                        question=user_input,
                        answer=answer,
                        agent='core_assistant',
                        importance='medium',
                        tags=['auto_saved']
                    )
                    if memory_id:
                        debug_success("Memory auto-saved", {"memory_id": memory_id})
                        
            except Exception as e:
                debug_error("Memory saving failed", e)
            
            return answer
            
        except Exception as e:
            debug_error("Failed to process input", e)
            import traceback
            print("FULL ERROR:", traceback.format_exc())
            return "I apologize, but I encountered an error processing your request."

    def _build_light_context(self, user_input: str, agent: str) -> list:
        """Build context with light memory retrieval (5-10 memories)."""
        try:
            # Light memory retrieval
            memories = self.memory_db.get_all_memories(limit=5)
            memory_context = ""
            
            if memories:
                # SIMPLIFIED: Just concatenate memories without compression
                memory_parts = []
                for memory in memories[:10]:  # Limit to 10 memories
                    question = memory.get('question', '')
                    answer = memory.get('answer', '')
                    if question and answer:
                        memory_parts.append(f"Q: {question}\nA: {answer}")
                memory_context = "\n\n".join(memory_parts)
            
            # Short conversation history
            short_term = ""
            for msg in self.conversation.messages[-3:]:
                if msg["role"] in ("user", "assistant"):
                    short_term += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
            system_prompt = self.prompt_builder.build_system_prompt(
                short_term, memory_context, self._build_conversation_context(user_input, memories)
            )
            
            self._add_context_to_conversation(system_prompt, user_input)
            return self.conversation.get_context()
            
        except Exception as e:
            debug_error("Light context building failed", e)
            return self._build_simple_context(user_input)
    
    def _build_moderate_context(self, user_input: str, agent: str) -> list:
        """Build context with moderate memory retrieval (10-20 memories)."""
        try:
            # Moderate memory retrieval
            memories = self.memory_db.get_all_memories(limit=10)
            semantic_memories = []
            
            try:
                semantic_memories = self.memory_db.query_memories(
                    query=user_input, limit=5, agent=agent
                )
            except:
                pass
            
            # Combine and deduplicate
            all_memories = list({m.get('id', m.get('_id')): m for m in memories + semantic_memories}.values())
            memory_context = ""
            
            if all_memories:
                # SIMPLIFIED: Just concatenate memories without compression
                memory_parts = []
                for memory in all_memories[:15]:  # Limit to 15 memories
                    question = memory.get('question', '')
                    answer = memory.get('answer', '')
                    if question and answer:
                        memory_parts.append(f"Q: {question}\nA: {answer}")
                memory_context = "\n\n".join(memory_parts)
            
            # Medium conversation history
            short_term = ""
            for msg in self.conversation.messages[-5:]:
                if msg["role"] in ("user", "assistant"):
                    short_term += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
            system_prompt = self.prompt_builder.build_system_prompt(
                short_term, memory_context, self._build_conversation_context(user_input, all_memories)
            )
            
            self._add_context_to_conversation(system_prompt, user_input)
            return self.conversation.get_context()
            
        except Exception as e:
            debug_error("Moderate context building failed", e)
            return self._build_simple_context(user_input)
    
    def _build_full_context(self, user_input: str, agent: str) -> list:
        """Build context with full memory retrieval (SIMPLIFIED - no more neural nonsense)."""
        try:
            # SIMPLIFIED: Just get recent memories and use dynamic context
            return self._build_dynamic_context(user_input, agent, self._create_simple_memory_plan(user_input, "full"))
            
        except Exception as e:
            debug_error("Full context building failed", e)
            return self._build_moderate_context(user_input, agent)
    
    def _build_conversation_context(self, user_input: str, memories: list) -> dict:
        """Build conversation context dictionary."""
        return {
            'conversation_length': len(self.conversation.messages),
            'recent_errors': self._count_recent_errors(),
            'user_expertise': self._assess_user_expertise(),
            'conversation_type': self._classify_conversation_type(user_input),
            'task_complexity': 'complex' if len(user_input) > 100 else 'simple',
            'current_query': user_input,
            'conversation_history': [{"content": msg["content"], "role": msg["role"]} 
                                   for msg in self.conversation.messages[-10:]],
            'memories': memories,
            'max_tokens': 4000
        }
    
    def _add_context_to_conversation(self, system_prompt: str, user_input: str):
        """Add system prompt and user input to conversation."""
        # Add system message to conversation
        if not self.conversation.messages or self.conversation.messages[0]["role"] != "system":
            self.conversation.add_message("system", system_prompt)
        else:
            self.conversation.messages[0]["content"] = system_prompt
        
        # Add user message
        self.conversation.add_message("user", user_input)
    
    def _get_database_stats(self) -> dict:
        """Get current database statistics for dynamic memory scaling."""
        try:
            # Get total memory count
            total_memories = len(self.memory_db.get_all_memories(limit=10000)) if self.memory_db else 0
            
            # Calculate recent activity (memories from last 24 hours)
            recent_activity = 0
            try:
                from datetime import datetime, timedelta
                yesterday = datetime.now() - timedelta(days=1)
                recent_memories = self.memory_db.get_all_memories(limit=100) if self.memory_db else []
                for memory in recent_memories:
                    if memory.get('timestamp'):
                        # Parse timestamp and check if recent
                        # This is a rough estimate - adjust based on your timestamp format
                        recent_activity += 1
            except:
                recent_activity = min(10, total_memories // 10)  # Fallback estimate
            
            return {
                'total_memories': total_memories,
                'recent_activity': recent_activity,
                'avg_memory_size': 150,  # Rough estimate
                'database_type': 'mongodb'
            }
        except Exception as e:
            debug_error("Failed to get database stats", e)
            return {
                'total_memories': 50,
                'recent_activity': 5,
                'avg_memory_size': 100,
                'database_type': 'unknown'
            }
    
    def _build_dynamic_context(self, user_input: str, agent: str, memory_plan) -> list:
        """Build context using the dynamic memory plan."""
        try:
            # If no memory needed, return simple context
            if memory_plan.recent_memories == 0 and memory_plan.semantic_memories == 0:
                return self._build_simple_context(user_input)
            
            # Fetch memories according to the plan
            all_memories = []
            
            # PRIORITIZE DIVERSE MEMORIES: Skip recent, focus on variety
            if memory_plan.recent_memories > 0:
                # Instead of recent memories, get diverse topic-based memories
                diverse_queries = ['tech preferences', 'hobbies', 'work', 'location', 'food preferences', 'personality traits']
                
                unique_memories = []
                seen_answers = set()
                
                for query in diverse_queries:
                    if len(unique_memories) >= memory_plan.recent_memories:
                        break
                        
                    topic_memories = self.memory_db.query_memories(query, limit=3)
                    for memory in topic_memories:
                        answer_signature = memory.get('answer', '')[:100].lower().strip()
                        
                        if answer_signature not in seen_answers and len(unique_memories) < memory_plan.recent_memories:
                            unique_memories.append(memory)
                            seen_answers.add(answer_signature)
                
                # Fill remaining slots with actual recent memories if needed
                if len(unique_memories) < memory_plan.recent_memories:
                    recent_fill = self.memory_db.get_all_memories(limit=20)
                    for memory in recent_fill:
                        answer_signature = memory.get('answer', '')[:100].lower().strip()
                        if answer_signature not in seen_answers and len(unique_memories) < memory_plan.recent_memories:
                            unique_memories.append(memory)
                            seen_answers.add(answer_signature)
                
                all_memories.extend(unique_memories)
                debug_info(f"Diverse memories: {len(unique_memories)} from topic-based search")
            
            # Get semantic memories
            if memory_plan.semantic_memories > 0:
                try:
                    semantic_memories = self.memory_db.query_memories(
                        query=user_input, 
                        limit=memory_plan.semantic_memories, 
                        agent=agent
                    )
                    # Deduplicate by ID and content
                    existing_ids = {m.get('id', m.get('_id')) for m in all_memories}
                    existing_answers = {m.get('answer', '')[:100].lower().strip() for m in all_memories}
                    
                    for memory in semantic_memories:
                        memory_id = memory.get('id', memory.get('_id'))
                        answer_sig = memory.get('answer', '')[:100].lower().strip()
                        
                        if memory_id not in existing_ids and answer_sig not in existing_answers:
                            all_memories.append(memory)
                            existing_answers.add(answer_sig)
                            
                except Exception as e:
                    debug_error("Semantic search failed", e)
            
            # Apply personal info search strategy for comprehensive personal queries
            if "personal_info" in memory_plan.search_strategies:
                try:
                    # Search for different categories of personal information
                    personal_categories = ["pets", "background", "interests", "preferences", "personality"]
                    
                    for category in personal_categories:
                        if len(all_memories) >= memory_plan.max_total_memories:
                            break
                            
                        category_results = self.memory_db.query_memories(
                            query=category,
                            limit=2,  # Get a few from each category
                            agent=agent
                        )
                        
                        # Add unique results with content deduplication
                        existing_ids = {m.get('id', m.get('_id')) for m in all_memories}
                        existing_answers = {m.get('answer', '')[:100].lower().strip() for m in all_memories}
                        
                        for memory in category_results:
                            memory_id = memory.get('id', memory.get('_id'))
                            answer_sig = memory.get('answer', '')[:100].lower().strip()
                            
                            if memory_id not in existing_ids and answer_sig not in existing_answers:
                                all_memories.append(memory)
                                existing_answers.add(answer_sig)
                                
                    debug_info(f"Personal info search added {len(all_memories) - len(recent_memories)} additional memories")
                    
                except Exception as e:
                    debug_error("Personal info search failed", e)
            
            # Neural retrieval removed - over-engineered bullshit
            
            # Limit total memories
            all_memories = all_memories[:memory_plan.max_total_memories]
            
            # Build memory context with simple concatenation
            memory_context = ""
            if all_memories:
                memory_parts = []
                for memory in all_memories[:20]:  # Limit to 20 memories
                    question = memory.get('question', '')
                    answer = memory.get('answer', '')
                    if question and answer:
                        memory_parts.append(f"Q: {question}\nA: {answer}")
                memory_context = "\n\n".join(memory_parts)
            
            # Build conversation history according to plan
            conversation_history_length = min(8, max(3, memory_plan.token_budget // 200))
            short_term = ""
            for msg in self.conversation.messages[-conversation_history_length:]:
                if msg["role"] in ("user", "assistant"):
                    short_term += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
            # Build system prompt
            conversation_context = self._build_conversation_context(user_input, all_memories)
            system_prompt = self.prompt_builder.build_system_prompt(
                short_term, memory_context, conversation_context
            )
            
            # Add to conversation and return
            self._add_context_to_conversation(system_prompt, user_input)
            return self.conversation.get_context()
            
        except Exception as e:
            debug_error("Dynamic context building failed", e)
        # Fallback to moderate context
        return self._build_moderate_context(user_input, agent)
    
    def _create_simple_memory_plan(self, user_input: str, memory_level: str):
        """Create a simple memory plan without the complexity."""
        from .dynamic_memory_engine import create_memory_plan
        return create_memory_plan(
            user_input=user_input,
            memory_level=memory_level,
            database_stats={'total_memories': 100}  # Simple default
        )