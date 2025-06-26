import json
import re
import uuid
from pathlib import Path
from typing import Dict
from openai import OpenAI
from ..data.database import get_database
from .logger import debug_log, debug_info, debug_error, debug_success
from config import config
# Removed deprecated prompt_utils import - using EvolutionaryPromptBuilder instead
import tiktoken
# Lazy imports to speed up module loading
# from .prompt_builder import EvolutionaryPromptBuilder  # Import when needed
from ..tools.web_search import search_web, get_webpage_content, WEB_SEARCH_ENABLED

class ConversationManager:
    def __init__(self, max_tokens=4000, max_messages=10):
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.messages = []
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
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
            from .prompt_builder import EvolutionaryPromptBuilder
            self._prompt_builder = EvolutionaryPromptBuilder()
        return self._prompt_builder
        
    # Removed deprecated prompt property - using EvolutionaryPromptBuilder instead
        
    def build_context(self, user_input: str, agent: str = "core_assistant") -> list:
        """Build context from relevant memories and conversation history."""
        try:
            # Get relevant memories
            memories = self.memory_db.query_memories(
                query=user_input,
                limit=3,  # Reduced from 5 to save tokens
                agent=agent,
                importance="high"  # Only get high-importance memories
            )
            
            # Build memory context
            memory_context = ""
            if memories:
                memory_context = "Relevant memories:\n"
                for memory in memories:
                    memory_context += f"Q: {memory['question']}\n"
                    memory_context += f"A: {memory['answer']}\n"
                    if memory.get('tags'):
                        memory_context += f"Tags: {', '.join(memory['tags'])}\n"
                    memory_context += "---\n"
            
            # Build short-term context (recent conversation)
            short_term = ""
            for msg in self.conversation.messages[-6:]:
                if msg["role"] in ("user", "assistant"):
                    short_term += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
            # Use enhanced prompt builder with intelligence features
            conversation_context = {
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
            
            debug_info("Built context", {
                "query": user_input[:50] + "...",
                "memories_found": len(memories),
                "conversation_length": len(self.conversation.messages)
            })
            
            return self.conversation.get_context()
            
        except Exception as e:
            debug_error("Failed to build context", e)
            return [{"role": "user", "content": user_input}]
    
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
            # Lazy import to avoid slowing down module loading
            from .prompt_enhancer import HybridPromptEnhancer
            ai_enhancer = HybridPromptEnhancer()
            return ai_enhancer.assess_response_quality(response, user_input, conversation_context)
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
        return self.prompt_builder.get_evolution_stats()
        
    def should_save_memory(self, question: str, answer: str) -> bool:
        """
        Only save if the user explicitly asks to remember, or provides a fact (e.g., 'my X is Y').
        """
        q_lower = question.lower()
        # Save if user says 'remember'
        if "remember" in q_lower:
            debug_log("Memory save triggered by 'remember' keyword.", {"question": question})
            return True
        # Save if user provides a fact pattern: 'my X is Y'
        if re.match(r"my .+ is .+", q_lower):
            debug_log("Memory save triggered by fact pattern.", {"question": question})
            return True
        debug_log("Memory NOT saved: no explicit remember or fact pattern.", {"question": question})
        return False

    def extract_fact(self, question: str) -> dict:
        """Extract a simple fact from the user's statement."""
        match = re.match(r"my ([\w\s]+?) is ([\w\s]+)", question.lower())
        if match:
            key = match.group(1).strip().replace(" ", "_")
            value = match.group(2).strip().capitalize()
            return {"relation": key, "value": value}
        return None

    def maybe_save_memory(self, question: str, answer: str, agent: str = "core_assistant") -> None:
        debug_info("Evaluating memory save", {
            "question": question,
            "answer": answer,
            "agent": agent
        })
        if not self.should_save_memory(question, answer):
            debug_info("Skipping memory save - interaction doesn't meet criteria", {
                "question": question,
                "answer": answer
            })
            return
        try:
            # Try to extract a fact
            fact = self.extract_fact(question)
            tags = self._extract_tags(question, answer)
            debug_info("Extracted tags", {"tags": tags, "fact": fact})
            # Save to database (optionally, use fact structure)
            memory_id = self.memory_db.save_memory(
                question=question,
                answer=answer,
                agent=agent,
                importance="high",
                tags=tags
            )
            if memory_id:
                debug_success("Saved interaction to memory", {
                    "id": memory_id,
                    "question": question[:50] + "...",
                    "tags": tags,
                    "fact": fact
                })
            else:
                debug_error("Failed to save memory - no ID returned")
        except Exception as e:
            debug_error("Failed to save memory", e)
        
    def _extract_tags(self, question: str, answer: str) -> list:
        """Extract relevant tags from the interaction."""
        tags = []
        q_lower = question.lower()
        a_lower = answer.lower()
        
        # Identity-related tags
        if any(word in q_lower for word in ["name", "called", "who am i", "i am", "my name"]):
            tags.append("identity")
        
        # Family and relationships
        if any(word in q_lower for word in ["family", "mother", "father", "parent", "sister", "brother", "wife", "husband", "girlfriend", "boyfriend", "friend", "best friend", "child", "son", "daughter"]):
            tags.append("family")
        
        # Work and career
        if any(word in q_lower for word in ["work", "job", "career", "company", "office", "boss", "colleague", "employee", "profession"]):
            tags.append("work")
        
        # Preferences and likes
        if any(word in q_lower for word in ["like", "prefer", "favorite", "love", "enjoy", "hate", "dislike"]):
            tags.append("preferences")
        
        # Opinions and thoughts
        if any(word in q_lower for word in ["feel", "think", "opinion", "believe", "consider"]):
            tags.append("opinion")
        
        # Memories and facts
        if any(word in q_lower for word in ["remember", "recall", "forgot", "memory"]):
            tags.append("memory")
        
        # Hobbies and activities
        if any(word in q_lower for word in ["hobby", "sport", "game", "play", "music", "book", "movie", "travel"]):
            tags.append("hobbies")
        
        # Health and medical
        if any(word in q_lower for word in ["health", "doctor", "medicine", "sick", "illness", "medical", "hospital"]):
            tags.append("health")
        
        # Education and learning
        if any(word in q_lower for word in ["school", "university", "college", "study", "learn", "education", "degree"]):
            tags.append("education")
        
        # Location and places
        if any(word in q_lower for word in ["live", "address", "city", "country", "hometown", "location", "from"]):
            tags.append("location")
        
        # Default tag if no specific category found
        if not tags:
            tags.append("general")
            
        return tags
        
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
            
            # Record AI-powered feedback for prompt evolution with intelligence learning
            conversation_context = {
                'conversation_length': len(self.conversation.messages),
                'recent_errors': self._count_recent_errors(),
                'user_expertise': self._assess_user_expertise(),
                'conversation_type': self._classify_conversation_type(user_input),
                'task_complexity': 'complex' if len(user_input) > 100 else 'simple',
                'used_web_search': bool(search_results)
            }
            quality_assessment = self._assess_response_quality_ai(answer, user_input, conversation_context)
            self.prompt_builder.record_response_feedback(
                self.prompt_builder.current_prompt_metadata, 
                quality_assessment,
                user_feedback=None,  # Will be provided later if user gives explicit feedback
                user_input=user_input,
                ai_response=answer
            )
            
            debug_info("Generated response", {
                "response_length": len(answer),
                "ai_quality_score": quality_assessment.get("overall_score"),
                "ai_assessment_issues": quality_assessment.get("issues", []),
                "used_web_search": bool(search_results)
            })
            
            # Maybe save to memory
            self.maybe_save_memory(user_input, answer)
            
            return answer
            
        except Exception as e:
            debug_error("Failed to process input", e)
            return "I apologize, but I encountered an error processing your request."