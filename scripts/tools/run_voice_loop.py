import sys
import os
import signal
import sounddevice as sd
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from voice.whisper_listener import listen_until_silence, whisper_model
except ImportError as e:
    print(f"❌ Failed to import whisper_listener: {e}")
    sys.exit(1)

try:
    from app.core_assistant import run_assistant
except ImportError as e:
    print(f"❌ Failed to import core_assistant: {e}")
    sys.exit(1)

def handle_exit(sig, frame):
    print("\n👋 Exiting voice assistant cleanly.")
    try:
        sd.stop()
    except Exception:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)

    if not whisper_model:
        print("❌ Whisper model failed to load. Exiting.")
        sys.exit(1)

    print("🎤 Voice Assistant Ready. Speak after the beep.")

    while True:
        try:
            user_input = listen_until_silence()
            print("🎙️ Listening for speech...")
            print(f"🗣️ You said: {user_input}\n")
            run_assistant(user_input)
            print("\n✅ Awaiting next input...\n")
        except Exception as e:
            print(f"⚠️ Error: {e}\n")
