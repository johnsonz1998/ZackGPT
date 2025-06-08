import json
import re
import uuid
from pathlib import Path
from openai import OpenAI
from app.memory_database import MemoryDatabase
from app.debug_logger import debug_log, debug_info, debug_error, debug_success

import config
from app.prompt_loader import load_prompt
from app.memory_engine import (
    load_memory_by_tags,
    get_context_block,
    save_memory,
    conversation_history
)

client = OpenAI(api_key=config.OPENAI_API_KEY)

_memory_db = None

def summarize_memory_for_context(mem_entries, max_items=5):
    return "\n".join(
        f"- {entry['answer']} (tags: {', '.join(entry.get('tags', []))})"
        for entry in mem_entries[:max_items]
    )

def build_context(user_input: str, agent: str = "core_assistant") -> list:
    global _memory_db
    if _memory_db is None:
        _memory_db = MemoryDatabase()
        _memory_db.load_memories()

    # Get relevant memories using the new database
    memory_context = _memory_db.get_memory_context(
        query=user_input,
        threshold=0.6,  # Adjust threshold as needed
        top_k=5
    )

    debug_info("Memory context retrieved", memory_context)

    short_term = get_context_block(config.MAX_CONTEXT_HISTORY)

    system_prompt = load_prompt(agent, {
        "MEMORY_CONTEXT": memory_context,
        "SHORT_TERM": short_term
    })

    context = [{"role": "system", "content": system_prompt}]
    context += conversation_history[-config.MAX_CONTEXT_HISTORY:]
    context.append({"role": "user", "content": user_input})

    return context

def should_save_memory(question: str, answer: str) -> bool:
    """
    Determine if this interaction should be saved to memory.
    Only saves if the answer is a direct, factual response that the assistant is 100% confident about.
    """
    # Skip if either question or answer is empty
    if not question.strip() or not answer.strip():
        return False
        
    # Skip if question is too short (likely a command or greeting)
    if len(question.split()) < 3:
        return False
        
    # Skip if answer is too short
    if len(answer.split()) < 5:
        return False
        
    # Skip if question contains common command patterns
    command_patterns = [
        r"^(hi|hello|hey|greetings)",
        r"^(thanks|thank you)",
        r"^(bye|goodbye|see you)",
        r"^(help|what can you do)",
        r"^(stop|exit|quit)"
    ]
    
    for pattern in command_patterns:
        if re.match(pattern, question.lower()):
            return False
            
    # Skip if answer contains uncertainty markers
    uncertainty_markers = [
        "i think",
        "i believe",
        "probably",
        "maybe",
        "perhaps",
        "i'm not sure",
        "i don't know",
        "i'm not certain",
        "i guess",
        "possibly",
        "likely",
        "might be",
        "could be",
        "seems like",
        "appears to be"
    ]
    
    answer_lower = answer.lower()
    for marker in uncertainty_markers:
        if marker in answer_lower:
            debug_info("Skipping memory save - answer contains uncertainty", {
                "marker": marker,
                "answer": answer
            })
            return False
            
    # Skip if answer is a question or contains a question
    if "?" in answer:
        debug_info("Skipping memory save - answer contains a question", {
            "answer": answer
        })
        return False
        
    return True

def maybe_save_memory(question: str, answer: str, agent: str = "core_assistant") -> None:
    """Save the interaction to memory if it meets the criteria."""
    if not should_save_memory(question, answer):
        debug_info("Skipping memory save - interaction doesn't meet criteria", {
            "question": question,
            "answer": answer
        })
        return
        
    try:
        save_memory(
            question=question,
            answer=answer,
            agent=agent,
            importance="high"  # Only save high-confidence memories
        )
        debug_success("Saved interaction to memory", {
            "question": question,
            "answer": answer,
            "agent": agent
        })
    except Exception as e:
        debug_error("Failed to save memory", e)

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
