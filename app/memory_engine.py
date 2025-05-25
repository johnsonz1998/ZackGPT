import json
import os
import re
from datetime import datetime
import config
import logging
import uuid

log_debug = logging.getLogger("zackgpt").debug
log_error = logging.getLogger("zackgpt").error

CHAT_LOG = config.CHAT_LOG_PATH
MEMORY_DIR = config.MEMORY_DIR
conversation_history = []

os.makedirs(MEMORY_DIR, exist_ok=True)

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
    memory_id = entry.get("id") or datetime.now().isoformat().replace(":", "-")
    path = MEMORY_DIR / f"{memory_id}.json"

    with open(path, "w") as f:
        json.dump(entry, f, indent=2)

    if config.DEBUG_MODE:
        log_debug(f"Memory saved: {entry.get('answer', '')[:60]}...")
    elif config.MEMORY_MODE == "all":
        print("[Memory updated]")
    elif config.MEMORY_MODE == "ai":
        print("[Memory updated by AI]")

def save_memory(
    question,
    answer,
    tags=None,
    agent="core_assistant",
    importance="medium",
    source="user",
    context=None
):
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "tags": tags or extract_tags_from_text(f"{question} {answer}"),
        "agents": [agent],
        "importance": importance,
        "source": source,
        "context": context
    }
    save_memory_entry(entry)

def get_context_block(n=3, tags: list[str] = None) -> str:
    files = sorted(MEMORY_DIR.glob("*.json"), reverse=True)
    entries = []
    for file in files:
        try:
            with open(file, "r") as f:
                entry = json.load(f)
                if tags:
                    if not any(tag in entry.get("tags", []) for tag in tags):
                        continue
                entries.append(entry)
                if len(entries) >= n:
                    break
        except Exception:
            continue

    context = "\n\n".join(
        f"User: {e['question']}\nAssistant: {e['answer']}" for e in reversed(entries)
    )
    return context

def load_memory_by_tags(input_text, agent="core_assistant"):
    tags = extract_tags_from_text(input_text)
    relevant = []
    for file in MEMORY_DIR.glob("*.json"):
        try:
            with open(file, "r") as f:
                entry = json.load(f)
                if not set(tags).intersection(set(entry.get("tags", []))):
                    continue
                if agent in entry.get("agents", ["core_assistant"]):
                    relevant.append(entry)
        except Exception:
            continue
    return relevant

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
        print(f"✅ Conversation history saved to {path}")
    except Exception as e:
        log_error(f"Failed to save conversation log: {e}")

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
    "MEMORY_DIR",
    "CHAT_LOG",
    "conversation_history"
]