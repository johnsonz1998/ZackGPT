# query_utils.py — Combined LLM and memory query utilities

import logging
import config
from openai import OpenAI
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import load_index_from_storage
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.core import Settings
import os
# --- LLM Query Logic ---

log_debug = logging.getLogger("zackgpt").debug

# Set LlamaIndex global LLM
Settings.llm = LlamaOpenAI(
    api_key=config.OPENAI_API_KEY,
    model=config.LLM_MODEL,
    temperature=config.LLM_TEMPERATURE,
    http_client=None,  # Prevent proxy inheritance
    base_url=None  # Use default OpenAI URL
)

# Separate OpenAI client (not LlamaIndex) for raw prompts
if not config.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

print(f"Debug: API Key length: {len(config.OPENAI_API_KEY) if config.OPENAI_API_KEY else 0}")
print(f"Debug: API Key prefix: {config.OPENAI_API_KEY[:8] if config.OPENAI_API_KEY else 'None'}...")

# Debug: Check for proxy settings
print("Debug: Checking for proxy settings...")
print(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
print(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
print(f"NO_PROXY: {os.environ.get('NO_PROXY')}")

# Initialize OpenAI client with explicit configuration
client = OpenAI(
    api_key=config.OPENAI_API_KEY,
    http_client=None,  # Prevent proxy inheritance
    base_url=None  # Use default OpenAI URL
)

def load_index():
    """Load a previously saved vector index from disk."""
    try:
        storage_context = StorageContext.from_defaults(persist_dir="data/index")
        index = load_index_from_storage(storage_context)
        log_debug("Vector index loaded successfully.")
        return index
    except Exception as e:
        log_debug(f"Failed to load index: {e}")
        return None

def ask_gpt(prompt: str) -> str:
    """Send prompt to OpenAI and return the response."""
    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": config.DEFAULT_PERSONALITY},
                {"role": "user", "content": prompt}
            ],
            temperature=config.LLM_TEMPERATURE
        )
        reply = response.choices[0].message.content.strip()
        log_debug(f"GPT response: {reply[:60]}...")
        return reply
    except Exception as e:
        log_debug(f"OpenAI request failed: {e}")
        return "I'm having trouble responding right now."

# --- Memory Query Logic ---

def handle_memory_query_request(tags: list = None, agent: str = None) -> list:
    """
    Returns a filtered list of memory entries based on tag and/or agent.
    """
    # NOTE: This depends on memory_web.load_all_memory, which should be available in your project.
    from memory_web import load_all_memory
    all_memory = load_all_memory(agent=agent)
    results = []
    for category, entries in all_memory.items():
        for entry in entries:
            if tags:
                if not any(tag in entry.get("tags", []) for tag in tags):
                    continue
            results.append({
                "category": category,
                "text": entry["text"],
                "tags": entry.get("tags", []),
                "agents": entry.get("agents", []),
                "importance": entry.get("importance", "medium"),
                "created": entry.get("created"),
            })
    return results 