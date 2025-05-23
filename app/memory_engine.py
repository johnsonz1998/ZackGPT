import json
import os
import re
from datetime import datetime
import config
log_debug = logging.getLogger("zackgpt").debug

MEMORY_LOG = config.MEMORY_LOG_PATH

def extract_tags_from_text(text):
    """Simple keyword-based tag extractor"""
    common_tags = [
        "finance", "identity", "goals", "projects", "health", "travel",
        "robot", "AI", "memory", "assistant", "preferences", "personality"
    ]
    return [tag for tag in common_tags if re.search(rf"\b{tag}\b", text, re.IGNORECASE)]

def save_memory(
    question,
    answer,
    tags=None,
    agent="core_assistant",
    importance="medium",
    source="user",
    context=None
):
    if os.path.exists(MEMORY_LOG):
        with open(MEMORY_LOG, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("answer") == answer and agent in entry.get("agents", []):
                        if config.DEBUG_MODE:
                            log_debug("Duplicate memory skipped.")
                        return
                except json.JSONDecodeError:
                    continue

    if tags is None or not tags:
        tags = extract_tags_from_text(question + " " + answer)


    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "tags": tags,
        "agents": [agent],
        "importance": importance,
        "source": source,
        "context": context
    }

    with open(MEMORY_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

    if config.DEBUG_MODE:
        log_debug(f"Memory saved: {answer[:60]}...")
    else:
        print("[Memory updated]")

def get_context_block(n=3, tags: list[str] = None) -> str:
    """
    Return the last `n` question/answer pairs,
    optionally filtered by tag.
    """
    if not os.path.exists(config.MEMORY_LOG_PATH):
        return ""

    with open(config.MEMORY_LOG_PATH, "r") as f:
        lines = f.readlines()

    entries = []
    for line in reversed(lines):
        try:
            entry = json.loads(line)
            if tags:
                if not any(tag in entry.get("tags", []) for tag in tags):
                    continue
            entries.append(entry)
            if len(entries) >= n:
                break
        except json.JSONDecodeError:
            continue

    context = "\n\n".join(
        f"User: {e['question']}\nAssistant: {e['answer']}" for e in reversed(entries)
    )
    return context


def load_memory_by_tags(input_text, agent="core_assistant"):
    """Return relevant memory entries based on tags in the input text"""
    if not os.path.exists(MEMORY_LOG):
        return []

    tags = extract_tags_from_text(input_text)
    relevant = []

    with open(MEMORY_LOG, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if not set(tags).intersection(set(entry.get("tags", []))):
                    continue
                if agent in entry.get("agents", ["core_assistant"]):
                    relevant.append(entry)
            except json.JSONDecodeError:
                continue

    return relevant