import json
import re
import uuid
from pathlib import Path
from openai import OpenAI
from app.vector_memory import VectorMemoryEngine

import config
from app.prompt_loader import load_prompt
from app.memory_engine import (
    load_memory_by_tags,
    get_context_block,
    save_memory,
    conversation_history
)

client = OpenAI(api_key=config.OPENAI_API_KEY)

_memory_engine = None

def summarize_memory_for_context(mem_entries, max_items=5):
    return "\n".join(
        f"- {entry['answer']} (tags: {', '.join(entry.get('tags', []))})"
        for entry in mem_entries[:max_items]
    )

def build_context(user_input: str, agent: str = "core_assistant") -> list:
    global _memory_engine
    if _memory_engine is None:
        _memory_engine = VectorMemoryEngine()
        _memory_engine.build_index()

    vector_result = _memory_engine.query(user_input, top_k=5)

    memory_context = vector_result.response.strip() if hasattr(vector_result, "response") else ""
    if config.DEBUG_MODE:
        print("\n🔎 Vector memory result:\n", memory_context)

    short_term = get_context_block(config.MAX_CONTEXT_HISTORY)

    system_prompt = load_prompt(agent, {
        "MEMORY_CONTEXT": memory_context,
        "SHORT_TERM": short_term
    })

    context = [{"role": "system", "content": system_prompt}]
    context += conversation_history[-config.MAX_CONTEXT_HISTORY:]
    context.append({"role": "user", "content": user_input})

    if config.DEBUG_MODE:
        for doc in vector_result.source_nodes:
            print("📄 Match:", doc.metadata.get("question", ""), "| Tags:", doc.metadata.get("tags", []))

    return context

def should_save_memory(question: str, answer: str) -> dict:
    try:
        result = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "If the exchange below contains information worth remembering, respond with:\n"
                        "{\n  \"remember\": true,\n  \"memory\": {\n    \"question\": string,\n    \"answer\": string,\n    \"tags\": list,\n    \"importance\": string,\n    \"context\": string,\n    \"source\": \"user\",\n    \"agents\": [\"core_assistant\"]\n  }\n}\n"
                        "Otherwise, respond with: { \"remember\": false }"
                    )
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\nAnswer: {answer}"
                }
            ],
            temperature=0.2
        )

        content = result.choices[0].message.content.strip()
        if config.DEBUG_MODE:
            print("\n\U0001f9e0 RAW MEMORY DECISION STRING:\n", content)

        parsed = json.loads(content)
        memory = parsed.get("memory")

        if config.DEBUG_MODE:
            print("\n[AI Memory Decision Parsed JSON]:")
            print(json.dumps(parsed, indent=2))

        if parsed.get("remember") is True and memory:
            required_keys = ["question", "answer", "tags", "context", "importance", "source", "agents"]
            if all(k in memory for k in required_keys):
                memory["id"] = re.sub(r'[^a-zA-Z0-9_-]', '_', memory.get("id") or str(uuid.uuid4()))
                return memory
            else:
                if config.DEBUG_MODE:
                    print("⚠️ Skipping malformed memory:", memory)
        return None

    except Exception:
        if config.DEBUG_MODE:
            import traceback
            print("⚠️ Memory decision failed:")
            traceback.print_exc()
        return None

def maybe_save_memory(question, answer, tags=None, agent="core_assistant"):
    if config.MEMORY_MODE == "all":
        if config.DEBUG_MODE:
            print("💾 Saving unconditionally (all mode)")
        save_memory(question=question, answer=answer, tags=tags, agent=agent)
    elif config.MEMORY_MODE == "ai":
        full = should_save_memory(question, answer)
        if full:
            if config.DEBUG_MODE:
                print("💾 Saving memory from AI decision")
            save_memory(
                question=full["question"],
                answer=full["answer"],
                tags=full.get("tags", []),
                importance=full.get("importance", "medium"),
                context=full.get("context"),
                agent=agent
            )

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
