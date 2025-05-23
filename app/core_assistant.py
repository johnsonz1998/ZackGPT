import json
import re
from app.prompt_loader import load_prompt
from app.memory_engine import load_memory_by_tags, get_context_block
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

conversation_history = []

def summarize_memory_for_context(mem_entries, max_items=5):
    summary = []
    for entry in mem_entries[:max_items]:
        summary.append(f"- {entry['answer']} (tags: {', '.join(entry.get('tags', []))})")
    return "\n".join(summary)

def build_context(user_input: str, agent: str = "core_assistant") -> list:
    # Long-term memory retrieved by tags
    long_term_memory = load_memory_by_tags(user_input, agent)
    memory_context = summarize_memory_for_context(long_term_memory)

    # Short-term memory from recent messages
    short_term = get_context_block(config.MAX_CONTEXT_HISTORY)

    # Build dynamic system prompt
    system_prompt = load_prompt(agent, {
        "MEMORY_CONTEXT": memory_context,
        "SHORT_TERM": short_term
    })

    context = [{"role": "system", "content": system_prompt}]
    context += conversation_history[-config.MAX_CONTEXT_HISTORY:]
    context.append({"role": "user", "content": user_input})
    return context

def run_assistant(user_input: str, agent: str = "core_assistant"):
    if not user_input.strip():
        print("⚠️ Empty transcription. Ignoring.")
        return

    messages = build_context(user_input, agent=agent)

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.7,
            stream=False
        )
    except Exception as e:
        print(f"❌ GPT API call failed: {e}")
        return

    content = response.choices[0].message.content
    print("\n🧠 Full GPT response:\n", content)

    handle_gpt_response(content, user_input=user_input)

def get_response(user_input: str, agent: str = "core_assistant") -> str:
    messages = build_context(user_input, agent=agent)

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.7,
            stream=False
        )
    except Exception as e:
        print(f"❌ GPT API call failed: {e}")
        return ""

    content = response.choices[0].message.content
    print("\n🧠 Full GPT response:\n", content)
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
