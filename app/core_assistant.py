import json
import re
from app.prompt_loader import load_prompt
from app.memory_engine import load_memory_by_tags, get_context_block, save_memory_entry, conversation_history
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

def summarize_memory_for_context(mem_entries, max_items=5):
    summary = []
    for entry in mem_entries[:max_items]:
        summary.append(f"- {entry['answer']} (tags: {', '.join(entry.get('tags', []))})")
    return "\n".join(summary)

def get_recent_conversation(n=5):
    return "\n\n".join(
        f"You: {msg['content']}" if msg['role'] == "user" else f"Assistant: {msg['content']}"
        for msg in conversation_history[-2 * n:]
    )

def build_context(user_input: str, agent: str = "core_assistant") -> list:
    long_term_memory = load_memory_by_tags(user_input, agent)
    memory_context = summarize_memory_for_context(long_term_memory)
    short_term = get_context_block(config.MAX_CONTEXT_HISTORY)

    system_prompt = load_prompt(agent, {
        "MEMORY_CONTEXT": memory_context,
        "SHORT_TERM": short_term
    })

    context = [{"role": "system", "content": system_prompt}]
    context += conversation_history[-config.MAX_CONTEXT_HISTORY:]
    context.append({"role": "user", "content": user_input})
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
        print("\n🧠 RAW MEMORY DECISION STRING:\n", content)

        parsed = json.loads(content)

        if config.DEBUG_MODE:
            print("\n[AI Memory Decision Parsed JSON]:")
            print(json.dumps(parsed, indent=2))

        memory = parsed.get("memory")
        if parsed.get("remember") is True and memory:
            required_keys = ["question", "answer", "tags", "context", "importance", "source", "agents"]
            if all(k in memory for k in required_keys):
                return memory
            else:
                print("⚠️ Skipping malformed memory:", memory)
        return None

    except Exception as e:
        import traceback
        print("⚠️ Memory decision failed:")
        traceback.print_exc()
        return None

def run_assistant(*, user_input: str, agent: str = "core_assistant"):
    if not user_input.strip():
        print("⚠️ Empty transcription. Ignoring.")
        return

    messages = build_context(user_input, agent=agent)

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=config.LLM_TEMPERATURE,
            stream=False
        )
    except Exception as e:
        print(f"❌ GPT API call failed: {e}")
        return

    content = response.choices[0].message.content
    print("\n🧠 Full GPT response:\n", content)

    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": content})

    if config.MEMORY_MODE == "all":
        save_memory_entry({
            "question": user_input,
            "answer": content,
            "tags": [],
            "agents": [agent],
            "importance": "medium",
            "source": "user",
            "context": None
        })
    elif config.MEMORY_MODE == "ai":
        memory_obj = should_save_memory(user_input, content)
        if memory_obj:
            save_memory_entry(memory_obj)

def get_response(*, user_input: str, agent: str = "core_assistant") -> str:
    messages = build_context(user_input, agent=agent)

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=config.LLM_TEMPERATURE,
            stream=False
        )
    except Exception as e:
        print(f"❌ GPT API call failed: {e}")
        return ""

    content = response.choices[0].message.content
    print("\n🧠 Full GPT response:\n", content)

    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": content})

    if config.MEMORY_MODE == "all":
        save_memory_entry({
            "question": user_input,
            "answer": content,
            "tags": [],
            "agents": [agent],
            "importance": "medium",
            "source": "user",
            "context": None
        })
    elif config.MEMORY_MODE == "ai":
        memory_obj = should_save_memory(user_input, content)
        if memory_obj:
            save_memory_entry(memory_obj)

    return content

def handle_gpt_response(content: str, user_input: str = None):
    if not content.strip():
        print("⚠️ GPT returned no content.")
        return

    if user_input:
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": content})

    sanitized = sanitize_gpt_json(content)
    print("\n🔧 Sanitized JSON:\n", sanitized)

    try:
        parsed = json.loads(sanitized)

        if isinstance(parsed, str):
            print("🗣️ GPT response (plain string):", parsed)
            return

        print("🧾 Structured JSON response:\n", json.dumps(parsed, indent=2))
        from app.action_router import handle_action_response
        handle_action_response(parsed)

    except json.JSONDecodeError as e:
        print("⚠️ Could not parse response as JSON.")
        print("Raw output:", repr(content))
        print("Exception:", e)

def sanitize_gpt_json(raw: str) -> str:
    raw = raw.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
    raw = re.sub(r',(\s*[}\]])', r'\1', raw)
    return raw.strip()