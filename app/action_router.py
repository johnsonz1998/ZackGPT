from app.memory_engine import save_memory, load_memory_by_tags
import json
import config

def speak_response(msg: str):
    """Speak the given message using configured voice backend."""
    if not msg:
        return
    print("🗣️ GPT response:", msg)
    if config.USE_ELEVENLABS:
        import voice.elevenlabs as eleven
        eleven.speak(msg)
    else:
        import voice.tts_mac as mac
        mac.speak(msg)

def handle_action_response(response: dict):
    action = response.get("action")
    data = response.get("data")

    if not action or not data:
        print("⚠️ Invalid response format.")
        return

    print(f"🔧 Action received: {action}")

    if action == "update_memory":
        update = data.get("update")
        if not update:
            print("⚠️ Missing update data.")
            return

        save_memory(
            question=update.get("text", ""),
            answer=update.get("text", ""),
            tags=update.get("tags", []),
            agent=update.get("agents", ["core_assistant"])[0],
            importance=update.get("importance", "medium"),
            source=update.get("source", "user"),
            context=update.get("context")
        )
        print(f"✅ Memory saved for agents: {update.get('agents', ['core_assistant'])}")
        speak_response(data.get("text"))

    elif action == "respond":
        speak_response(data.get("text") or data.get("message"))

    elif action == "suggest_new_category":
        category = data.get("category")
        print(f"📂 GPT suggests creating a new memory category: {category}")

    elif action == "query_memory":
        query = data.get("query", {})
        tags = query.get("tags", [])
        agents = query.get("agents", ["core_assistant"])
        results = load_memory_by_tags(" ".join(tags), agent=agents[0])
        print("🔍 Memory query results:")
        for r in results:
            print(json.dumps(r, indent=2))

    elif action == "switch_agent":
        print("⚠️ Agent switch requested. This is reserved for local controller logic.")

    else:
        print(f"⚠️ Unknown action: {action}")
