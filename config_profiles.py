# config_profiles.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

CONFIG = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
    "USE_ELEVENLABS": os.getenv("USE_ELEVENLABS", "false").lower() == "true",
    "USE_WHISPER": os.getenv("USE_WHISPER", "false").lower() == "true",
    "DEBUG_MODE": os.getenv("DEBUG_MODE", "false").lower() == "true",
    "MACOS_VOICE": os.getenv("MACOS_VOICE"),
    "ELEVENLABS_VOICE_ID": os.getenv("ELEVENLABS_VOICE_ID"),
    "ELEVENLABS_STABILITY": float(os.getenv("ELEVENLABS_STABILITY", "0.5")),
    "ELEVENLABS_SIMILARITY": float(os.getenv("ELEVENLABS_SIMILARITY", "0.5")),
    "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
    "LLM_MODEL": os.getenv("LLM_MODEL", "gpt-4"),
    "DEFAULT_PERSONALITY": os.getenv("DEFAULT_PERSONALITY"),
    "MAX_CONTEXT_HISTORY": int(os.getenv("MAX_CONTEXT_HISTORY", "3")),
    "WHISPER_MODEL": os.getenv("WHISPER_MODEL", "medium"),
    "TRANSCRIBE_ENGINE": os.getenv("TRANSCRIBE_ENGINE", "whisper")
}