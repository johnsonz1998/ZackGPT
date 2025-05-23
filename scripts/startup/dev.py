import config
from app.memory_engine import get_context_block, MEMORY_LOG
from voice import whisper_listener
import voice.elevenlabs as eleven
import voice.tts_mac as mac
import app.config_profiles as profiles

def update_config():
    print("\n🔧 Settings Menu")
    print("1. Change Whisper model (Currently: {})".format(config.WHISPER_MODEL))
    print("2. Set Voice Engine (Currently: {})".format("ElevenLabs" if config.USE_ELEVENLABS else "macOS"))
    print("4. Choose ElevenLabs voice (Current ID: {})".format(config.ELEVENLABS_VOICE_ID))
    print("4. Set macOS voice (Currently: {})".format(config.MACOS_VOICE))
    print("5. Modify assistant tone")
    print("6. View last memory log")
    print("7. Clear memory log")
    print("8. Run test interaction")
    print("9. Save current config as profile")
    print("10. Load config profile")
    print("11. Reset to default profile")
    print("0. Exit")

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

        # Whisper model selection based on engine
        if config.TRANSCRIBE_ENGINE == "faster-whisper":
            models = ["tiny", "base", "small", "medium", "large-v2"]
        else:
            models = ["tiny", "base", "small", "medium", "large"]

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
        if sub == "1":
            config.USE_ELEVENLABS = True
        elif sub == "2":
            config.USE_ELEVENLABS = False
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
        print("\n🧠 Recent memory:")
        print(get_context_block(config.MAX_CONTEXT_HISTORY))

    elif choice == "7":
        open(MEMORY_LOG, "w").close()
        print("🧹 Memory log cleared.")

    elif choice == "8":
        run_test_interaction()

    elif choice == "9":
        import json, os
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
    elif choice == "10":
        import json, os
        profiles = [f for f in os.listdir("profiles") if f.endswith(".json")]

        if not profiles:
            print("⚠️ No profiles found.")
            return

        print("\n📂 Available profiles:")
        for i, p in enumerate(profiles, 1):
            print(f"{i}. {p}")

        idx = input("Select a profile number: ").strip()
        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(profiles):
            print("❌ Invalid selection.")
            return

        with open(f"profiles/{profiles[int(idx) - 1]}", "r") as f:
            settings = json.load(f)

        config.TRANSCRIBE_ENGINE = settings.get("TRANSCRIBE_ENGINE", config.TRANSCRIBE_ENGINE)
        config.WHISPER_MODEL = settings.get("WHISPER_MODEL", config.WHISPER_MODEL)
        config.USE_ELEVENLABS = settings.get("USE_ELEVENLABS", config.USE_ELEVENLABS)
        config.ELEVENLABS_VOICE_ID = settings.get("ELEVENLABS_VOICE_ID", config.ELEVENLABS_VOICE_ID)
        config.MACOS_VOICE = settings.get("MACOS_VOICE", config.MACOS_VOICE)
        config.DEFAULT_PERSONALITY = settings.get("DEFAULT_PERSONALITY", config.DEFAULT_PERSONALITY)

        whisper_listener.reload_whisper_model()
        print("✅ Loaded profile:", profiles[int(idx) - 1])

    elif choice == "11":
        profiles.reset_to_default() 

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
    response = get_response(index, question)
    print("💬 Assistant:", response)

    speaker = eleven.speak if config.USE_ELEVENLABS else mac.speak
    speaker(response)

# 🔁 Loop menu until exit
if __name__ == "__main__":
    print("🚀 Test config menu loaded.")
    while True:
        update_config()
        print()
