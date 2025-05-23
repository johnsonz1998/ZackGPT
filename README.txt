# 🤖 Zach’s Local Voice Assistant

A modular AI assistant with real voice interaction, memory, and personality — powered by OpenAI + ElevenLabs + Whisper.

---

## ✨ Features

- 🎙️ **Voice input** via Whisper
- 🔊 **Voice output** with ElevenLabs or macOS `say`
- 🧠 **Context-aware memory** using LlamaIndex + FAISS
- 💬 **Custom assistant tone** (sarcastic, helpful, etc.)
- 🧱 **Modular agent system** (finance, calendar, etc.)
- ⚡ Built for speed, privacy, and local control

---

## 📦 Project Structure
RAG/
├── main.py # 🧠 Entry point
├── config.py # Global settings and API keys
├── memory_engine.py # Memory storage + recall
├── logs/ # Chat memory logs
│ └── memory_log.jsonl
├── data/ # Ingested reference documents
├── embeddings/ # Vector index files
├── assistants/ # Personality logic
│ └── core_assistant.py
├── voice/ # Voice output modules
│ ├── elevenlabs.py
│ └── tts_mac.py
├── input/ # Whisper audio listener
│ └── whisper_listener.py
├── llm/ # (optional) GPT logic
│ └── query_assistant.py
├── tools/ # (optional) one-off scripts
│ └── ingest_text.py
└── README.md


---

## 🔧 Setup

1. **Install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   brew install ffmpeg

In config,py configure API keys:

OPENAI_API_KEY = "sk-..."
ELEVENLABS_API_KEY = "sk-..."
ELEVENLABS_VOICE_ID = "..."

🚀 Run the Assistant

python main.py

(Press Enter to talk. Say “quit” or press Ctrl+C to exit.)

🧠 Adding Knowledge
Drop .txt or .pdf files into /data
Then run: 

python tools/ingest_text.py

🧱 Future Goals
🧠 Long-term summarization & memory retention

🔄 Agent switching by domain (scheduler, analyst, etc.)

📞 Voice control via Twilio

💾 Local LLM fallback with Ollama or Mistral