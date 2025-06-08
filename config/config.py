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
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

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

# ========== LLM / OpenAI ==========
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))  # For future dynamic control
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
DEFAULT_PERSONALITY = os.getenv("DEFAULT_PERSONALITY", (
    "You are Zack's AI assistant. You are witty, sarcastic, and brutally efficient. "
    "Keep things short and smart. Never waste words."
))

# ========== LlamaIndex ==========
MAX_CONTEXT_HISTORY = int(os.getenv("MAX_CONTEXT_HISTORY", 3))

# ========== Whisper ==========
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")
TRANSCRIBE_ENGINE = os.getenv("TRANSCRIBE_ENGINE", "faster-whisper")
TRANSCRIBE_LOG_DIR = BASE_DIR / "logs/transcribe"

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))

MEMORY_MODE = "ai" # "all" | "none"

CHAT_LOG_PATH = BASE_DIR / "logs/chat_history.jsonl"

MEMORY_DIR = BASE_DIR / "memories"

# ========== Memory Configuration ==========
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MEMORY_THRESHOLD = float(os.getenv("MEMORY_THRESHOLD", "0.6"))
MAX_MEMORIES = int(os.getenv("MAX_MEMORIES", "5"))

# ========== Voice Configuration ==========
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "False").lower() == "true"
VOICE_MODEL = os.getenv("VOICE_MODEL", "tts-1")
VOICE_ID = os.getenv("VOICE_ID", "alloy")

# ========== Proxy Configuration ==========
HTTP_PROXY = os.getenv("HTTP_PROXY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")
NO_PROXY = os.getenv("NO_PROXY")

# ========== Prompt Enhancement Configuration ==========
PROMPT_ENHANCER_USE_CLOUD = os.getenv("PROMPT_ENHANCER_USE_CLOUD", "true").lower() == "true"
PROMPT_ENHANCER_USE_LOCAL = os.getenv("PROMPT_ENHANCER_USE_LOCAL", "true").lower() == "true" 
PROMPT_ENHANCER_MODEL = os.getenv("PROMPT_ENHANCER_MODEL", "gpt-4-turbo")
PROMPT_ENHANCER_GENERATION_RATE = float(os.getenv("PROMPT_ENHANCER_GENERATION_RATE", "0.3"))
PROMPT_ENHANCER_DEBUG = os.getenv("PROMPT_ENHANCER_DEBUG", "false").lower() == "true"

# ========== Prompt System Configuration ==========
PROMPT_SYSTEM_ENABLED = os.getenv("PROMPT_SYSTEM_ENABLED", "true").lower() == "true"
PROMPT_EVOLUTION_ENABLED = os.getenv("PROMPT_EVOLUTION_ENABLED", "true").lower() == "true"
PROMPT_EVOLUTION_RATE = float(os.getenv("PROMPT_EVOLUTION_RATE", "0.3"))  # 30% evolution chance
