import json
from config import config
# Legacy memory actions removed. If needed, reimplement using memory_db.

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
        print("⚠️ update_memory action is not implemented in MongoDB mode.")
        speak_response(data.get("text"))

    elif action == "respond":
        speak_response(data.get("text") or data.get("message"))

    elif action == "suggest_new_category":
        category = data.get("category")
        print(f"📂 GPT suggests creating a new memory category: {category}")

    elif action == "query_memory":
        print("⚠️ query_memory action is not implemented in MongoDB mode.")

    elif action == "switch_agent":
        print("⚠️ Agent switch requested. This is reserved for local controller logic.")

    else:
        print(f"⚠️ Unknown action: {action}")
