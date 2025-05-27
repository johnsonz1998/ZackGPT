import os
import json
import config
from app.memory_engine import get_context_block, get_conversation_history, clear_conversation_history
from voice import whisper_listener
import voice.elevenlabs as eleven
import voice.tts_mac as mac
import app.config_profiles as profiles

def show_dev_menu():
    print("\n🛠️  ZackGPT Dev Menu\n")
    print("CONFIGURATION")
    print("1. Change Whisper model")
    print("2. Set Voice Engine")
    print("3. Choose ElevenLabs voice")
    print("4. Set macOS voice")
    print("5. Modify assistant tone")
    print("6. Save current config as profile")
    print("7. Load config profile")
    print("8. Reset to default profile")

    print("\nMEMORY TOOLS")
    print("9. View long-term memory log")
    print("10. View short-term conversation history")
    print("11. Clear conversation history")
    print("12. Clear memory log")

    print("\nTEST MODE")
    print("13. Run one-off voice interaction")
    print("14. Run one-off text interaction")

    print("\nFULL INTERACTION")
    print("15. Run full text interaction loop")
    print("16. Enter full voice assistant mode")

    print("\n0. Exit")

    choice = input("Select an option: ").strip()

    if choice == "1":
        print("\n🎙️ Select Transcription Engine:")
        print("1. Faster-Whisper (fast, less accurate)")
        print("2. OpenAI Whisper (slower, more accurate)")
        engine_input = input("Enter engine option: ").strip()
        if engine_input == "1":
            config.TRANSCRIBE_ENGINE = "faster-whisper"
        elif engine_input == "2":
            config.TRANSCRIBE_ENGINE = "openai-whisper"
        else:
            print("❌ Invalid engine option.")
            return

        print(f"✅ Transcription engine set to {config.TRANSCRIBE_ENGINE}")
        models = ["tiny", "base", "small", "medium"]
        if config.TRANSCRIBE_ENGINE == "faster-whisper":
            models.append("large-v2")
        else:
            models.append("large")
        print("\n🎛️ Available models:")
        for i, name in enumerate(models, 1):
            print(f"{i}. {name}")
        model_input = input("Choose model number or type custom name: ").strip()
        if model_input.isdigit() and 1 <= int(model_input) <= len(models):
            config.WHISPER_MODEL = models[int(model_input) - 1]
        else:
            config.WHISPER_MODEL = model_input
        whisper_listener.reload_whisper_model()
        print("✅ Whisper model set to", config.WHISPER_MODEL)

    elif choice == "2":
        print("\n🎙️ Choose Voice Engine:")
        print("1. ElevenLabs")
        print("2. macOS (say command)")
        sub = input("Enter option: ").strip()
        config.USE_ELEVENLABS = sub == "1"
        print("✅ Voice engine set to", "ElevenLabs" if config.USE_ELEVENLABS else "macOS")

    elif choice == "3":
        print("\n🎤 Select ElevenLabs Voice:")
        voices = {
            "1": ("Rachel", "21m00Tcm4TlvDq8ikWAM"),
            "2": ("Domi", "AZnzlk1XvdvUeBnXmlld"),
            "3": ("Antoni", "ErXwobaYiN019PkySvjV"),
            "4": ("Custom input", None)
        }
        for key, (name, vid) in voices.items():
            print(f"{key}. {name}" + (f" — {vid}" if vid else ""))
        sub = input("Choose voice: ").strip()
        if sub in voices and voices[sub][1]:
            config.ELEVENLABS_VOICE_ID = voices[sub][1]
        elif sub == "4":
            config.ELEVENLABS_VOICE_ID = input("Paste custom ElevenLabs Voice ID: ").strip()
        print("✅ Voice ID set to", config.ELEVENLABS_VOICE_ID)

    elif choice == "4":
        config.MACOS_VOICE = input("Enter new macOS voice: ").strip()

    elif choice == "5":
        config.DEFAULT_PERSONALITY = input("Enter new assistant tone: ").strip()

    elif choice == "6":
        profile_name = input("Enter a name for this profile: ").strip().lower().replace(" ", "_")
        os.makedirs("profiles", exist_ok=True)
        profile_path = f"profiles/{profile_name}.json"
        settings = {
            "TRANSCRIBE_ENGINE": config.TRANSCRIBE_ENGINE,
            "WHISPER_MODEL": config.WHISPER_MODEL,
            "USE_ELEVENLABS": config.USE_ELEVENLABS,
            "ELEVENLABS_VOICE_ID": config.ELEVENLABS_VOICE_ID,
            "MACOS_VOICE": config.MACOS_VOICE,
            "DEFAULT_PERSONALITY": config.DEFAULT_PERSONALITY
        }
        with open(profile_path, "w") as f:
            json.dump(settings, f, indent=2)
        print(f"✅ Saved config to {profile_path}")

    elif choice == "7":
        profiles_list = [f for f in os.listdir("profiles") if f.endswith(".json")]
        if not profiles_list:
            print("⚠️ No profiles found.")
            return
        print("\n📂 Available profiles:")
        for i, p in enumerate(profiles_list, 1):
            print(f"{i}. {p}")
        idx = input("Select a profile number: ").strip()
        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(profiles_list):
            print("❌ Invalid selection.")
            return
        with open(f"profiles/{profiles_list[int(idx) - 1]}", "r") as f:
            settings = json.load(f)
        config.TRANSCRIBE_ENGINE = settings.get("TRANSCRIBE_ENGINE", config.TRANSCRIBE_ENGINE)
        config.WHISPER_MODEL = settings.get("WHISPER_MODEL", config.WHISPER_MODEL)
        config.USE_ELEVENLABS = settings.get("USE_ELEVENLABS", config.USE_ELEVENLABS)
        config.ELEVENLABS_VOICE_ID = settings.get("ELEVENLABS_VOICE_ID", config.ELEVENLABS_VOICE_ID)
        config.MACOS_VOICE = settings.get("MACOS_VOICE", config.MACOS_VOICE)
        config.DEFAULT_PERSONALITY = settings.get("DEFAULT_PERSONALITY", config.DEFAULT_PERSONALITY)
        whisper_listener.reload_whisper_model()
        print("✅ Loaded profile:", profiles_list[int(idx) - 1])

    elif choice == "8":
        profiles.reset_to_default()

    elif choice == "9":
        from pathlib import Path

        print("\n📜 Long-Term Memory Files (latest 5):")
        memory_dir = config.MEMORY_DIR
        files = sorted(Path(memory_dir).glob("*.json"), reverse=True)

        if not files:
            print("📭 No memory files found.")
        else:
            for file in files[:5]:
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                        print(f"📄 {file.name}")
                        print(json.dumps(data, indent=2))
                        print("-" * 40)
                except Exception as e:
                    print(f"⚠️ Error reading {file.name}: {e}")

    elif choice == "10":
        print("\n💬 Short-Term Conversation History:")
        print(get_conversation_history())

    elif choice == "11":
        clear_conversation_history()
        print("🧹 Short-term conversation history cleared.")

    elif choice == "12":
        open(config.CHAT_LOG_PATH, "w").close()
        print("🧹 Memory log cleared.")

    elif choice == "13":
        run_test_interaction()

    elif choice == "14":
        os.system("python -m scripts.startup.main --text --once")

    elif choice == "15":
        os.system("python -m scripts.startup.main --text")

    elif choice == "16":
        print("🎤 Launching full voice assistant with current config...")
        os.makedirs("profiles", exist_ok=True)
        temp_profile = "__dev_temp_profile.json"
        with open(f"profiles/{temp_profile}", "w") as f:
            json.dump({
                "TRANSCRIBE_ENGINE": config.TRANSCRIBE_ENGINE,
                "WHISPER_MODEL": config.WHISPER_MODEL,
                "USE_ELEVENLABS": config.USE_ELEVENLABS,
                "ELEVENLABS_VOICE_ID": config.ELEVENLABS_VOICE_ID,
                "MACOS_VOICE": config.MACOS_VOICE,
                "DEFAULT_PERSONALITY": config.DEFAULT_PERSONALITY
            }, f, indent=2)
        os.system(f"python -m scripts.startup.main profiles/{temp_profile}")
    elif choice == "90":
        from app.vector_index import VectorMemoryIndex
        memory_index = VectorMemoryIndex()
        memory_index.load_memory_documents()
        memory_index.build_index()

        query = input("🔍 Enter semantic memory query: ")
        response = memory_index.query(query)
        print("🧠 Best memory match:", response.response)
    elif choice == "90":
        from app.vector_memory import VectorMemoryEngine
        engine = VectorMemoryEngine()
        engine.build_index()

        user_query = input("🔍 Ask the assistant something it should remember: ")
        result = engine.query(user_query)
        print("🧠 Memory response:", result.response)


    elif choice == "0":
        print("👋 Exiting test menu.")
        exit()

    else:
        print("❌ Invalid option.")

def run_test_interaction():
    from app.core_assistant import get_response
    from llm.query_assistant import load_index
    index = load_index()
    question = input("🧪 Enter test question: ")
    response = get_response(user_input=question, agent="core_assistant")
    print("💬 Assistant:", response)
    speaker = eleven.speak if config.USE_ELEVENLABS else mac.speak
    try:
        parsed = json.loads(response)
        spoken_text = parsed["data"]["text"]
    except Exception:
        spoken_text = response
    speaker(spoken_text)

if __name__ == "__main__":
    print("🚀 Test config menu loaded.")
    while True:
        show_dev_menu()
        print()
