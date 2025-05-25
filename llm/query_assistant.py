# llm/query_assistant.py

import logging
import config
from openai import OpenAI
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import load_index_from_storage
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.core import Settings

log_debug = logging.getLogger("zackgpt").debug

# Set LlamaIndex global LLM
Settings.llm = LlamaOpenAI(
    api_key=config.OPENAI_API_KEY,
    model=config.LLM_MODEL,
    temperature=config.LLM_TEMPERATURE
)

# Separate OpenAI client (not LlamaIndex) for raw prompts
client = OpenAI(api_key=config.OPENAI_API_KEY)

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