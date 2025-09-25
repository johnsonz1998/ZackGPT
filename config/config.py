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

# ========== Web Search Configuration ==========
WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH_ENABLED", "True").lower() == "true"
SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # Primary search API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Fallback
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")  # Custom Search Engine ID
WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))
WEB_SEARCH_TIMEOUT = int(os.getenv("WEB_SEARCH_TIMEOUT", "10"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

# ========== DYNAMIC MEMORY SYSTEM CONFIGURATION ==========

# === Core Memory Settings ===
MEMORY_SYSTEM_MODE = os.getenv("MEMORY_SYSTEM_MODE", "dynamic")  # "dynamic", "static", "hybrid"
MEMORY_FALLBACK_TO_STATIC = os.getenv("MEMORY_FALLBACK_TO_STATIC", "true").lower() == "true"
MEMORY_ENGINE_DEBUG = os.getenv("MEMORY_ENGINE_DEBUG", "false").lower() == "true"

# === Dynamic Memory Scaling Formulas ===
# Database size scaling factors
DYNAMIC_SIZE_SCALING_BASE = float(os.getenv("DYNAMIC_SIZE_SCALING_BASE", "1.0"))
DYNAMIC_SIZE_SCALING_LOG_FACTOR = float(os.getenv("DYNAMIC_SIZE_SCALING_LOG_FACTOR", "0.5"))
DYNAMIC_SIZE_SCALING_MAX = float(os.getenv("DYNAMIC_SIZE_SCALING_MAX", "2.0"))
DYNAMIC_SIZE_SMALL_DB_THRESHOLD = int(os.getenv("DYNAMIC_SIZE_SMALL_DB_THRESHOLD", "50"))
DYNAMIC_SIZE_LARGE_DB_THRESHOLD = int(os.getenv("DYNAMIC_SIZE_LARGE_DB_THRESHOLD", "500"))

# Query complexity analysis factors
DYNAMIC_COMPLEXITY_LENGTH_WEIGHT = float(os.getenv("DYNAMIC_COMPLEXITY_LENGTH_WEIGHT", "0.3"))
DYNAMIC_COMPLEXITY_KEYWORD_BOOST = float(os.getenv("DYNAMIC_COMPLEXITY_KEYWORD_BOOST", "1.3"))
DYNAMIC_COMPLEXITY_MEMORY_BOOST = float(os.getenv("DYNAMIC_COMPLEXITY_MEMORY_BOOST", "1.4"))
DYNAMIC_COMPLEXITY_QUESTION_BOOST = float(os.getenv("DYNAMIC_COMPLEXITY_QUESTION_BOOST", "1.2"))
DYNAMIC_COMPLEXITY_MAX = float(os.getenv("DYNAMIC_COMPLEXITY_MAX", "3.0"))
DYNAMIC_COMPLEXITY_MIN = float(os.getenv("DYNAMIC_COMPLEXITY_MIN", "0.5"))

# Performance constraints and limits
DYNAMIC_MAX_PROCESSING_TIME_MS = int(os.getenv("DYNAMIC_MAX_PROCESSING_TIME_MS", "300"))
DYNAMIC_BASE_TOKEN_BUDGET = int(os.getenv("DYNAMIC_BASE_TOKEN_BUDGET", "2000"))
DYNAMIC_MAX_TOKEN_BUDGET = int(os.getenv("DYNAMIC_MAX_TOKEN_BUDGET", "4000"))
DYNAMIC_MIN_MEMORIES = int(os.getenv("DYNAMIC_MIN_MEMORIES", "3"))
DYNAMIC_MAX_MEMORIES = int(os.getenv("DYNAMIC_MAX_MEMORIES", "100"))

# === Static Memory Level Configurations (Fallbacks) ===
STATIC_MEMORY_NONE_RECENT = int(os.getenv("STATIC_MEMORY_NONE_RECENT", "0"))
STATIC_MEMORY_NONE_SEMANTIC = int(os.getenv("STATIC_MEMORY_NONE_SEMANTIC", "0"))
STATIC_MEMORY_NONE_TOKENS = int(os.getenv("STATIC_MEMORY_NONE_TOKENS", "200"))

STATIC_MEMORY_LIGHT_RECENT = int(os.getenv("STATIC_MEMORY_LIGHT_RECENT", "5"))
STATIC_MEMORY_LIGHT_SEMANTIC = int(os.getenv("STATIC_MEMORY_LIGHT_SEMANTIC", "2"))
STATIC_MEMORY_LIGHT_TOKENS = int(os.getenv("STATIC_MEMORY_LIGHT_TOKENS", "400"))

STATIC_MEMORY_MODERATE_RECENT = int(os.getenv("STATIC_MEMORY_MODERATE_RECENT", "10"))
STATIC_MEMORY_MODERATE_SEMANTIC = int(os.getenv("STATIC_MEMORY_MODERATE_SEMANTIC", "5"))
STATIC_MEMORY_MODERATE_TOKENS = int(os.getenv("STATIC_MEMORY_MODERATE_TOKENS", "800"))

STATIC_MEMORY_FULL_RECENT = int(os.getenv("STATIC_MEMORY_FULL_RECENT", "20"))
STATIC_MEMORY_FULL_SEMANTIC = int(os.getenv("STATIC_MEMORY_FULL_SEMANTIC", "10"))
STATIC_MEMORY_FULL_TOKENS = int(os.getenv("STATIC_MEMORY_FULL_TOKENS", "1200"))

# === Search Strategy Configuration ===
DYNAMIC_ENABLE_TAG_SEARCH = os.getenv("DYNAMIC_ENABLE_TAG_SEARCH", "true").lower() == "true"
DYNAMIC_ENABLE_KEYWORD_SEARCH = os.getenv("DYNAMIC_ENABLE_KEYWORD_SEARCH", "true").lower() == "true"
DYNAMIC_ENABLE_INTENT_SEARCH = os.getenv("DYNAMIC_ENABLE_INTENT_SEARCH", "true").lower() == "true"
DYNAMIC_ENABLE_TEMPORAL_SEARCH = os.getenv("DYNAMIC_ENABLE_TEMPORAL_SEARCH", "true").lower() == "true"
DYNAMIC_ENABLE_NEURAL_SEARCH = os.getenv("DYNAMIC_ENABLE_NEURAL_SEARCH", "true").lower() == "true"

# Complexity and database thresholds for enabling expensive search strategies
DYNAMIC_TAG_SEARCH_COMPLEXITY_THRESHOLD = float(os.getenv("DYNAMIC_TAG_SEARCH_COMPLEXITY_THRESHOLD", "1.5"))
DYNAMIC_INTENT_SEARCH_DB_SIZE_THRESHOLD = int(os.getenv("DYNAMIC_INTENT_SEARCH_DB_SIZE_THRESHOLD", "200"))
DYNAMIC_TEMPORAL_SEARCH_DB_SIZE_THRESHOLD = int(os.getenv("DYNAMIC_TEMPORAL_SEARCH_DB_SIZE_THRESHOLD", "500"))
DYNAMIC_NEURAL_SEARCH_COMPLEXITY_THRESHOLD = float(os.getenv("DYNAMIC_NEURAL_SEARCH_COMPLEXITY_THRESHOLD", "2.5"))

# === Memory Compression and Optimization ===
DYNAMIC_COMPRESSION_LIGHT_RATIO = float(os.getenv("DYNAMIC_COMPRESSION_LIGHT_RATIO", "0.1"))
DYNAMIC_COMPRESSION_AGGRESSIVE_THRESHOLD = float(os.getenv("DYNAMIC_COMPRESSION_AGGRESSIVE_THRESHOLD", "0.6"))
DYNAMIC_COMPRESSION_MAX_RATIO = float(os.getenv("DYNAMIC_COMPRESSION_MAX_RATIO", "0.9"))
DYNAMIC_CACHE_DB_STATS_SECONDS = int(os.getenv("DYNAMIC_CACHE_DB_STATS_SECONDS", "30"))
DYNAMIC_AVG_TOKENS_PER_MEMORY = int(os.getenv("DYNAMIC_AVG_TOKENS_PER_MEMORY", "80"))

# === Performance Monitoring and Debug ===
DYNAMIC_MEMORY_DEBUG = os.getenv("DYNAMIC_MEMORY_DEBUG", "false").lower() == "true"
DYNAMIC_MEMORY_METRICS = os.getenv("DYNAMIC_MEMORY_METRICS", "false").lower() == "true"
DYNAMIC_MEMORY_PROFILING = os.getenv("DYNAMIC_MEMORY_PROFILING", "false").lower() == "true"
DYNAMIC_PERFORMANCE_WARNING_THRESHOLD_MS = int(os.getenv("DYNAMIC_PERFORMANCE_WARNING_THRESHOLD_MS", "200"))

# === Formula Tuning Constants ===
DYNAMIC_FORMULA_COMPLEXITY_TO_MULTIPLIER_BASE = float(os.getenv("DYNAMIC_FORMULA_COMPLEXITY_TO_MULTIPLIER_BASE", "0.3"))
DYNAMIC_FORMULA_COMPLEXITY_TO_MULTIPLIER_RANGE = float(os.getenv("DYNAMIC_FORMULA_COMPLEXITY_TO_MULTIPLIER_RANGE", "1.7"))
DYNAMIC_FORMULA_SIZE_SQRT_SCALING = os.getenv("DYNAMIC_FORMULA_SIZE_SQRT_SCALING", "true").lower() == "true"
DYNAMIC_FORMULA_PERFORMANCE_SCALE_DOWN_FACTOR = float(os.getenv("DYNAMIC_FORMULA_PERFORMANCE_SCALE_DOWN_FACTOR", "0.3"))
