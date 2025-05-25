# llm/query_assistant.py

import logging
import config
from openai import OpenAI
from llama_index.storage.storage_context import StorageContext
from llama_index.indices.vector_store import load_index_from_storage
from llama_index.llms import OpenAI as LlamaOpenAI
from llama_index import ServiceContext

log_debug = logging.getLogger("zackgpt").debug

client = OpenAI(api_key=config.OPENAI_API_KEY)
llama_llm = LlamaOpenAI(api_key=config.OPENAI_API_KEY)
service_context = ServiceContext.from_defaults(llm=llama_llm)


def load_index():
    """Load a previously saved vector index from disk."""
    try:
        storage_context = StorageContext.from_defaults(persist_dir="data/index")
        index = load_index_from_storage(storage_context, service_context=service_context)
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
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        log_debug(f"GPT response: {reply[:60]}...")
        return reply
    except Exception as e:
        log_debug(f"OpenAI request failed: {e}")
        return "I'm having trouble responding right now."
