import os
import json
from . import config
from voice import whisper_listener

PROFILE_DIR = "config/profiles"
DEFAULT_PROFILE = "default"

os.makedirs(PROFILE_DIR, exist_ok=True)

CONFIG_KEYS = [
    "TRANSCRIBE_ENGINE",
    "WHISPER_MODEL",
    "USE_ELEVENLABS",
    "ELEVENLABS_VOICE_ID",
    "MACOS_VOICE",
    "DEFAULT_PERSONALITY"
]

def _get_profile_path(name):
    return os.path.join(PROFILE_DIR, f"{name}.json")

def save_profile(name):
    path = _get_profile_path(name)
    data = {k: getattr(config, k) for k in CONFIG_KEYS}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved profile to {path}")

def load_profile(name):
    path = _get_profile_path(name)
    if not os.path.exists(path):
        print("❌ Profile not found.")
        return

    with open(path, "r") as f:
        data = json.load(f)

    for k in CONFIG_KEYS:
        if k in data:
            setattr(config, k, data[k])

    whisper_listener.reload_whisper_model()
    print(f"✅ Loaded profile: {name}")

def reset_to_default():
    load_profile(DEFAULT_PROFILE)

def list_profiles():
    return [f[:-5] for f in os.listdir(PROFILE_DIR) if f.endswith(".json")]
