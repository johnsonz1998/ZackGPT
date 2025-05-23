# config.py — Centralized assistant settings

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env
load_dotenv()

# ========== API KEYS ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ========== Core Toggles ==========
USE_ELEVENLABS = os.getenv("USE_ELEVENLABS", "True") == "True"
USE_WHISPER = os.getenv("USE_WHISPER", "True") == "True"
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"

# ========== Paths ==========
BASE_DIR = Path(__file__).resolve().parent
MEMORY_LOG_PATH = BASE_DIR / "logs/memory_log.jsonl"
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
DATA_DIR = BASE_DIR / "data"
TEMP_AUDIO_FILE = BASE_DIR / "voice/tmp/temp.wav"
TEMP_AUDIO_FILE.parent.mkdir(parents=True, exist_ok=True)

# ========== Audio Settings ==========
SAMPLE_RATE = 16000
RECORD_DURATION = 3
MACOS_VOICE = os.getenv("MACOS_VOICE", "Evan (Enhanced)")

# ========== ElevenLabs ==========
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "NFG5qt843uXKj4pFvR7C")
ELEVENLABS_STABILITY = float(os.getenv("ELEVENLABS_STABILITY", 0.4))
ELEVENLABS_SIMILARITY = float(os.getenv("ELEVENLABS_SIMILARITY", 0.75))

# ========== OpenAI ==========
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")

# ========== Prompt Defaults ==========
DEFAULT_PERSONALITY = os.getenv("DEFAULT_PERSONALITY", (
    "You are Zack’s AI assistant. You are witty, sarcastic, and brutally efficient. "
    "Keep things short and smart. Never waste words."
))

# ========== Memory ==========
MAX_CONTEXT_HISTORY = int(os.getenv("MAX_CONTEXT_HISTORY", 3))

# ========== Whisper ==========
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")
TRANSCRIBE_ENGINE = os.getenv("TRANSCRIBE_ENGINE", "faster-whisper")
TRANSCRIBE_LOG_DIR = BASE_DIR / "logs/transcribe"
