import json
import os
import re
import uuid
import logging
from datetime import datetime, timedelta
from llama_index.embeddings.openai import OpenAIEmbedding
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from openai import OpenAI

import config
from app.debug_logger import debug_log, debug_info, debug_error, debug_warning


CHAT_LOG = config.CHAT_LOG_PATH
MEMORY_DIR = Path("memories")
MEMORY_DIR.mkdir(exist_ok=True)
conversation_history = []

os.makedirs(MEMORY_DIR, exist_ok=True)

log_debug = logging.getLogger("zackgpt").debug
log_error = logging.getLogger("zackgpt").error

embed_model = OpenAIEmbedding(model="text-embedding-3-small")

client = OpenAI(api_key=config.OPENAI_API_KEY)

def extract_tags_from_text(text):
    if not isinstance(text, str):
        return []

    common_tags = [
        "finance", "identity", "goals", "projects", "health", "travel",
        "robot", "AI", "memory", "assistant", "preferences", "personality"
    ]
    return [tag for tag in common_tags if re.search(rf"\b{tag}\b", text, re.IGNORECASE)]

def save_chat_line(question, answer):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer
    }
    with open(CHAT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def save_memory_entry(entry: dict):
    try:
        raw_id = entry.get("id") or str(uuid.uuid4())
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', raw_id)
        filename = f"{safe_id}.json"
        path = MEMORY_DIR / filename

        if config.DEBUG_MODE:
            print(f"📝 Writing to path: {path}")
            print(f"🔍 MEMORY_DIR type: {type(MEMORY_DIR)}")

        with open(path, "w") as f:
            json.dump(entry, f, indent=2)

        if config.DEBUG_MODE:
            print(f"✅ Memory written to {path}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise

def get_embedding(text: str) -> List[float]:
    """Get embedding for text using OpenAI's API."""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        debug_error("Failed to get embedding", e)
        return []

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def is_duplicate_memory(question: str, answer: str, threshold: float = 0.85) -> bool:
    """
    Check if a memory is a duplicate of an existing one.
    Uses semantic similarity to detect duplicates.
    """
    new_embedding = get_embedding(f"{question} {answer}")
    if not new_embedding:
        return False
        
    for file in MEMORY_DIR.glob("*.json"):
        try:
            with open(file, 'r') as f:
                memory = json.load(f)
                if "embedding" not in memory:
                    continue
                    
                similarity = cosine_similarity(new_embedding, memory["embedding"])
                if similarity > threshold:
                    debug_info("Found duplicate memory", {
                        "file": file.name,
                        "similarity": similarity,
                        "existing": memory["question"],
                        "new": question
                    })
                    return True
        except Exception as e:
            debug_error(f"Error checking file {file}", e)
            continue
            
    return False

def score_memory_importance(question: str, answer: str, tags: list = None) -> str:
    """
    Score the importance of a memory based on various factors:
    - Content type (personal info, preferences, etc.)
    - Question/answer length and complexity
    - Presence of key tags
    - Emotional content
    """
    score = 0
    
    # Check for personal information
    personal_keywords = ["name", "birthday", "address", "phone", "email", "password", "account"]
    if any(keyword in question.lower() or keyword in answer.lower() for keyword in personal_keywords):
        score += 3
        
    # Check for preferences and habits
    preference_keywords = ["like", "prefer", "favorite", "usually", "always", "never"]
    if any(keyword in question.lower() or keyword in answer.lower() for keyword in preference_keywords):
        score += 2
        
    # Check for emotional content
    emotional_keywords = ["love", "hate", "angry", "happy", "sad", "excited", "worried"]
    if any(keyword in question.lower() or keyword in answer.lower() for keyword in emotional_keywords):
        score += 2
        
    # Check for important tags
    important_tags = ["identity", "preferences", "goals", "health"]
    if tags and any(tag in important_tags for tag in tags):
        score += 2
        
    # Length and complexity bonus
    content_length = len(question) + len(answer)
    if content_length > 200:
        score += 1
        
    # Determine importance level
    if score >= 5:
        return "high"
    elif score >= 3:
        return "medium"
    else:
        return "low"

def save_memory(
    question: str,
    answer: str,
    tags: List[str] = None,
    importance: str = "medium",
    context: str = None,
    source: str = "user",
    agents: List[str] = None
) -> Optional[str]:
    """
    Save a new memory entry.
    Returns the memory ID if successful, None otherwise.
    """
    try:
        # Check for duplicates
        if is_duplicate_memory(question, answer):
            debug_info("Skipping duplicate memory", {
                "question": question,
                "answer": answer
            })
            return None
            
        # Generate embedding
        embedding = get_embedding(f"{question} {answer}")
        if not embedding:
            debug_error("Failed to generate embedding")
            return None
            
        # Create memory entry
        memory = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "tags": tags or [],
            "importance": importance,
            "context": context,
            "source": source,
            "agents": agents or ["core_assistant"],
            "embedding": embedding
        }
        
        # Save to file
        file = MEMORY_DIR / f"{memory['id']}.json"
        with open(file, 'w') as f:
            json.dump(memory, f, indent=2)
            
        debug_success("Memory saved", {
            "id": memory["id"],
            "question": question
        })
        
        return memory["id"]
        
    except Exception as e:
        debug_error("Failed to save memory", e)
        return None

def get_context_block(max_items: int = 5) -> str:
    """Get a formatted block of recent memories for context."""
    memories = []
    for file in sorted(MEMORY_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            with open(file, 'r') as f:
                memory = json.load(f)
                memories.append(memory)
                if len(memories) >= max_items:
                    break
        except Exception as e:
            debug_error(f"Error loading file {file}", e)
            continue
            
    if not memories:
        return ""
        
    context_parts = []
    for memory in memories:
        context_parts.append(
            f"Memory: {memory['question']}\n"
            f"Answer: {memory['answer']}\n"
            f"Tags: {', '.join(memory.get('tags', []))}\n"
            f"Importance: {memory.get('importance', 'medium')}\n"
        )
        
    return "\n".join(context_parts)

def load_memory_by_tags(tags: List[str]) -> List[Dict[str, Any]]:
    """Load memories that match any of the given tags."""
    memories = []
    for file in MEMORY_DIR.glob("*.json"):
        try:
            with open(file, 'r') as f:
                memory = json.load(f)
                if any(tag in memory.get("tags", []) for tag in tags):
                    memories.append(memory)
        except Exception as e:
            debug_error(f"Error loading file {file}", e)
            continue
    return memories

def get_conversation_history(n=5):
    return "\n\n".join(
        f"You: {msg['content']}" if msg['role'] == "user" else f"Assistant: {msg['content']}"
        for msg in conversation_history[-2 * n:]
    )

def clear_conversation_history():
    conversation_history.clear()

def save_conversation_log(path="conversation_log.txt"):
    try:
        with open(path, "w") as f:
            for msg in conversation_history:
                prefix = "You:" if msg['role'] == "user" else "Assistant:"
                f.write(f"{prefix} {msg['content']}\n")
        if config.DEBUG_MODE:
            print(f"✅ Conversation history saved to {path}")
    except Exception as e:
        log_error(f"Failed to save conversation log: {e}")

def consolidate_memories(similarity_threshold: float = 0.85):
    """
    Consolidate similar memories by merging them and updating importance.
    This helps reduce redundancy and strengthen important memories.
    """
    if config.DEBUG_MODE:
        print("🔄 Starting memory consolidation...")
        
    memories = []
    for file in MEMORY_DIR.glob("*.json"):
        try:
            with open(file, "r") as f:
                entry = json.load(f)
                if "embedding" not in entry:
                    continue
                memories.append((file, entry))
        except Exception:
            continue
            
    # Sort by timestamp to process oldest first
    memories.sort(key=lambda x: x[1]["timestamp"])
    
    consolidated = set()
    for i, (file1, mem1) in enumerate(memories):
        if file1 in consolidated:
            continue
            
        for file2, mem2 in memories[i+1:]:
            if file2 in consolidated:
                continue
                
            # Calculate similarity
            similarity = np.dot(mem1["embedding"], mem2["embedding"]) / (
                np.linalg.norm(mem1["embedding"]) * np.linalg.norm(mem2["embedding"])
            )
            
            if similarity > similarity_threshold:
                # Merge memories
                merged = {
                    "id": mem1["id"],
                    "timestamp": mem1["timestamp"],  # Keep older timestamp
                    "question": mem1["question"],
                    "answer": mem1["answer"],
                    "tags": list(set(mem1.get("tags", []) + mem2.get("tags", []))),
                    "agents": list(set(mem1.get("agents", []) + mem2.get("agents", []))),
                    "importance": "high" if "high" in [mem1.get("importance"), mem2.get("importance")] else "medium",
                    "source": mem1["source"],
                    "context": f"{mem1.get('context', '')} {mem2.get('context', '')}".strip(),
                    "embedding": mem1["embedding"]  # Keep original embedding
                }
                
                # Save merged memory
                save_memory_entry(merged)
                
                # Delete the second memory
                try:
                    os.remove(file2)
                    if config.DEBUG_MODE:
                        print(f"🗑️ Deleted duplicate memory: {file2}")
                except Exception:
                    pass
                    
                consolidated.add(file2)
                
    if config.DEBUG_MODE:
        print(f"✅ Memory consolidation complete. Consolidated {len(consolidated)} memories.")

def cleanup_memories(max_age_days: int = 30, keep_high_importance: bool = True):
    """
    Clean up old or low-importance memories to prevent memory bloat.
    Args:
        max_age_days: Maximum age of memories to keep (in days)
        keep_high_importance: Whether to keep high-importance memories regardless of age
    """
    if config.DEBUG_MODE:
        print("🧹 Starting memory cleanup...")
        
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    cleaned = 0
    
    for file in MEMORY_DIR.glob("*.json"):
        try:
            with open(file, "r") as f:
                entry = json.load(f)
                
            # Skip if memory is high importance and we're keeping those
            if keep_high_importance and entry.get("importance") == "high":
                continue
                
            # Check memory age
            memory_date = datetime.fromisoformat(entry["timestamp"])
            if memory_date < cutoff_date:
                try:
                    os.remove(file)
                    cleaned += 1
                    if config.DEBUG_MODE:
                        print(f"🗑️ Cleaned up old memory: {file}")
                except Exception:
                    pass
                    
        except Exception:
            continue
            
    if config.DEBUG_MODE:
        print(f"✅ Memory cleanup complete. Removed {cleaned} old memories.")

def update_memory(memory_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update an existing memory with new information.
    
    Args:
        memory_id: The ID of the memory to update
        updates: Dictionary of fields to update
        
    Returns:
        bool: True if update was successful
    """
    try:
        file = MEMORY_DIR / f"{memory_id}.json"
        if not file.exists():
            debug_warning(f"Memory file not found: {file}")
            return False
            
        with open(file, 'r') as f:
            memory = json.load(f)
            
        # Update fields
        for key, value in updates.items():
            if key in memory:
                memory[key] = value
                
        # Update embedding if question or answer changed
        if "question" in updates or "answer" in updates:
            memory["embedding"] = get_embedding(f"{memory['question']} {memory['answer']}")
            
        # Update timestamp
        memory["timestamp"] = datetime.now().isoformat()
        
        with open(file, 'w') as f:
            json.dump(memory, f, indent=2)
            
        debug_success("Memory updated", {
            "id": memory_id,
            "updates": updates
        })
        return True
        
    except Exception as e:
        debug_error("Failed to update memory", e)
        return False

__all__ = [
    "save_memory",
    "save_memory_entry",
    "save_chat_line",
    "get_context_block",
    "load_memory_by_tags",
    "extract_tags_from_text",
    "get_conversation_history",
    "clear_conversation_history",
    "save_conversation_log",
    "is_duplicate_memory",
    "consolidate_memories",
    "score_memory_importance",
    "cleanup_memories",
    "MEMORY_DIR",
    "CHAT_LOG",
    "conversation_history"
]