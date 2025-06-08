import json
import re
import uuid
from pathlib import Path
from typing import Dict
from openai import OpenAI
from app.memory_db import MemoryDatabase
from app.logger import debug_log, debug_info, debug_error, debug_success
from config import config
from app.prompt_utils import load_prompt
import tiktoken
from app.prompt_builder import EvolutionaryPromptBuilder

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
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.LLM_MODEL
        self._memory_db = None
        self._prompt = None
        self.conversation = ConversationManager()
        self.prompt_builder = EvolutionaryPromptBuilder()
        
    @property
    def memory_db(self) -> MemoryDatabase:
        """Lazy load memory database."""
        if self._memory_db is None:
            self._memory_db = MemoryDatabase()
        return self._memory_db
        
    @property
    def prompt(self) -> str:
        """Lazy load core assistant prompt."""
        if self._prompt is None:
            self._prompt = load_prompt("core_assistant")
        return self._prompt
        
    def build_context(self, user_input: str, agent: str = "core_assistant") -> list:
        """Build context from relevant memories and conversation history."""
        try:
            # Get relevant memories
            memories = self.memory_db.query_memories(
                query=user_input,
                limit=3,  # Reduced from 5 to save tokens
                min_importance="high"  # Only get high-importance memories
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
            
            # Use evolutionary prompt builder with conversation context
            conversation_context = {
                'conversation_length': len(self.conversation.messages),
                'recent_errors': self._count_recent_errors(),
                'user_expertise': self._assess_user_expertise(),
                'conversation_type': self._classify_conversation_type(user_input),
                'task_complexity': 'complex' if len(user_input) > 100 else 'simple'
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
        else:
            return 'general'
    
    def _assess_response_quality_ai(self, response: str, user_input: str, conversation_context: Dict) -> Dict:
        """AI-powered response quality assessment."""
        try:
            from app.prompt_enhancer import HybridPromptEnhancer
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
            # Save to MongoDB (optionally, use fact structure)
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
        # TODO: Implement more sophisticated tag extraction
        # For now, return basic tags based on content
        tags = []
        
        # Add topic-based tags
        if any(word in question.lower() for word in ["name", "called", "who"]):
            tags.append("identity")
        if any(word in question.lower() for word in ["like", "prefer", "favorite"]):
            tags.append("preferences")
        if any(word in question.lower() for word in ["feel", "think", "opinion"]):
            tags.append("opinion")
            
        return tags
        
    def process_input(self, user_input: str, short_term_context: str = "") -> str:
        """Process user input and generate a response."""
        try:
            debug_info("Processing input", {
                "input": user_input,
                "context_length": len(short_term_context)
            })
            
            # Build context
            context = self.build_context(user_input)
            
            # Log (context, prompt) pair for future training
            debug_log("LLM prompt context", context)
            if context and context[0]["role"] == "system":
                debug_log("System prompt for training", context[0]["content"])
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=context,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # Add assistant's response to conversation
            self.conversation.add_message("assistant", answer)
            
            # Record AI-powered feedback for prompt evolution
            conversation_context = {
                'conversation_length': len(self.conversation.messages),
                'recent_errors': self._count_recent_errors(),
                'user_expertise': self._assess_user_expertise(),
                'conversation_type': self._classify_conversation_type(user_input),
                'task_complexity': 'complex' if len(user_input) > 100 else 'simple'
            }
            quality_assessment = self._assess_response_quality_ai(answer, user_input, conversation_context)
            self.prompt_builder.record_response_feedback(
                self.prompt_builder.current_prompt_metadata, 
                quality_assessment
            )
            
            debug_info("Generated response", {
                "response_length": len(answer),
                "ai_quality_score": quality_assessment.get("overall_score"),
                "ai_assessment_issues": quality_assessment.get("issues", [])
            })
            
            # Maybe save to memory
            self.maybe_save_memory(user_input, answer)
            
            return answer
            
        except Exception as e:
            debug_error("Failed to process input", e)
            return "I apologize, but I encountered an error processing your request."

def summarize_memory_for_context(mem_entries, max_items=5):
    return "\n".join(
        f"- {entry['answer']} (tags: {', '.join(entry.get('tags', []))})"
        for entry in mem_entries[:max_items]
    )

def process_input(user_input: str, agent: str = "core_assistant") -> str:
    """Process user input and return the assistant's response."""
    try:
        # Check for memory correction
        if user_input.lower().startswith("correction:"):
            parts = user_input[len("correction:"):].strip().split("|")
            if len(parts) >= 2:
                memory_id = parts[0].strip()
                correction = parts[1].strip()
                if update_memory(memory_id, {"answer": correction}):
                    return f"Memory updated: {correction}"
                else:
                    return "Failed to update memory"
        
        context = build_context(user_input, agent)
        
        debug_info("Sending request to OpenAI", {
            "model": config.OPENAI_MODEL,
            "context_length": len(context)
        })
        
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=context,
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Save to memory if appropriate
        maybe_save_memory(user_input, answer, agent)
        
        return answer
        
    except Exception as e:
        debug_error("Error processing input", e)
        return "I encountered an error processing your request. Please try again."

def generate_response(user_input: str, agent: str = "core_assistant") -> str:
    messages = build_context(user_input, agent)
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        temperature=config.LLM_TEMPERATURE,
        stream=False
    )
    return response.choices[0].message.content.strip()

def get_response(*, user_input: str, agent: str = "core_assistant") -> str:
    content = generate_response(user_input, agent)
    if config.DEBUG_MODE:
        print("\n\U0001f9e0 Full GPT response:\n", content)

    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": content})

    maybe_save_memory(user_input, content)

    return content

def run_assistant(*, user_input: str, agent: str = "core_assistant"):
    if config.DEBUG_MODE:
        print("DEBUG_MODE is", config.DEBUG_MODE)
    if not user_input.strip():
        print("⚠️ Empty transcription. Ignoring.")
        return

    content = get_response(user_input=user_input, agent=agent)
    print("\n💬 Final assistant reply:", content)