# 🤖 ZackGPT - Advanced AI Assistant with Adaptive Prompt Enhancement

A sophisticated, self-improving AI assistant featuring intelligent prompt enhancement, voice interaction, persistent memory, and modular architecture. Built for privacy, performance, and continuous learning.

---

## ✨ Key Features

### 🧠 **AI-Enhanced Evolutionary Prompt System** (CORE INNOVATION!)
- **Hybrid AI + Statistical Evolution** - Combines genetic algorithm-style evolution with GPT-4 intelligence
- **Self-improving prompts** that learn from conversation quality using multi-dimensional AI assessment
- **AI-powered component generation** with intelligent pattern recognition
- **Context-aware adaptation** based on conversation patterns and user expertise
- **Experimentation system** - 10% rate for discovering new effective strategies
- **Multi-dimensional scoring** - accuracy, relevance, clarity, tone, completeness

### 🎙️ **Advanced Voice Capabilities**
- **Voice input** via OpenAI Whisper (local processing)
- **High-quality voice output** with ElevenLabs TTS
- **Fallback TTS** using macOS `say` command
- **Real-time audio processing** with voice activity detection

### 💾 **Persistent Memory System**
- **Vector-based memory** using FAISS for semantic search
- **MongoDB storage** for conversation history and metadata
- **Context-aware recall** - retrieves relevant past interactions
- **Memory threshold filtering** to focus on important information

### 🧱 **Modular Architecture**
- **Core assistant** with customizable personality (witty, sarcastic, helpful)
- **Component-based prompts** - personality, memory guidelines, task instructions, context framers, output formatters
- **Docker containerization** with automatic environment management
- **Development tools** for testing and debugging

### ⚡ **Performance & Privacy**
- **Local processing** where possible (Whisper, memory)
- **Efficient API usage** with smart generation rate limiting
- **Hybrid intelligence** - local models + cloud AI for optimal cost/performance
- **Comprehensive logging** and performance monitoring

---

## 🧬 How the AI-Enhanced Evolution Works

### **Hybrid Intelligence Architecture**
The system combines multiple AI approaches for optimal learning:

1. **AI-Powered Assessment**: GPT-4 evaluates response quality across multiple dimensions
2. **Intelligent Component Generation**: AI creates new prompt components based on successful patterns  
3. **Local Model Integration**: Fast local assessments for real-time feedback
4. **Cloud Intelligence**: Detailed analysis and pattern recognition
5. **Statistical Tracking**: Performance metrics and weighted selection

### **Component-Based Prompt Building**
Prompts are dynamically built from modular components:

- **`personality`** - How the assistant behaves (witty, direct, technical)
- **`memory_guidelines`** - How to handle memory saving and recall
- **`task_instructions`** - Specific guidance for different task types
- **`context_framers`** - How to interpret and use conversation context
- **`output_formatters`** - Response structure and formatting preferences

### **AI-Enhanced Learning Process**
1. **Intelligent Selection**: AI analyzes context to pick optimal components
2. **Response Generation**: Uses dynamically built prompts
3. **Multi-Dimensional Assessment**: AI evaluates accuracy, relevance, clarity, tone, completeness
4. **Component Evolution**: Updates weights and generates new components based on AI feedback
5. **Pattern Recognition**: Identifies successful strategies and conversation patterns
6. **Smart Experimentation**: Tries new AI-generated components 10% of the time

### **Context Awareness**
The system adapts based on:
- **Conversation Type**: technical, troubleshooting, learning, creative, general
- **User Expertise**: beginner, medium, high (inferred from technical language)
- **Recent Performance**: Adjusts when assistant has been uncertain or made errors
- **Conversation Length**: Different strategies for quick questions vs. long discussions
- **Task Complexity**: Simple queries vs. complex multi-step problems

### **Evolution Examples**

**Initial Seed Component:**
```
personality: "Be witty and efficient"
```

**After AI Learning:**
```
personality: "Be witty and efficient - more personalized to Zack's style approach. 
Focus on technical accuracy and implementation details."
```

**Context-Aware Evolution:**
- **Technical contexts**: Components emphasize code examples, precision
- **Troubleshooting**: Components focus on step-by-step problem resolution
- **General chat**: Components maintain personality while being helpful

---

## 📦 Project Structure

```
ZackGPT/
├── app/                          # Core application modules
│   ├── core_assistant.py         # Main assistant logic with AI evolution
│   ├── prompt_enhancer.py        # AI-powered prompt enhancement
│   ├── prompt_builder.py         # Evolutionary prompt system
│   ├── memory_db.py              # MongoDB memory interface
│   ├── context_engine.py         # Context processing
│   ├── query_utils.py            # Query processing utilities
│   ├── action_router.py          # Action routing logic
│   ├── logger.py                 # Enhanced logging system
│   ├── prompt_utils.py           # Prompt utilities
│   └── local_llm.py              # Local model fallback
├── config/                       # Configuration and settings
│   ├── config.py                 # Main configuration
│   ├── config_profiles.py        # Environment profiles
│   ├── prompt_components.json    # Seed components for evolution
│   ├── profiles/                 # User profiles
│   ├── prompt_evolution/         # Evolution tracking and data
│   │   └── evolution_data.json   # Persistent learned components
│   └── voice/                    # Voice configuration
├── scripts/                      # Startup and utility scripts
│   ├── startup/
│   │   ├── main.py              # Full assistant launcher
│   │   ├── dev.py               # Development and testing tools
│   │   ├── main_voice.py        # Voice-enabled mode
│   │   └── watch_main.py        # File watching mode
│   └── tools/                    # Utility scripts
├── prompts/                      # Base prompt templates
│   └── core_assistant.txt        # Foundation template (enhanced by evolution)
├── logs/                         # Chat history and analytics
├── voice/                        # Voice processing modules
├── .env                          # Environment variables (create this)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container configuration
├── docker-compose.yml           # Multi-service setup
├── zackgpt.sh                   # Main launcher script
├── zackgpt_text.sh             # Text-only launcher
└── reboot.sh                    # System restart utility
```

---

## 🔧 Setup & Installation

### 1. **Prerequisites**
```bash
# macOS/Linux
brew install ffmpeg python3
# or
sudo apt-get install ffmpeg python3-pip  # Ubuntu/Debian
```

### 2. **Clone & Install**
```bash
git clone <your-repo>
cd ZackGPT
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. **Environment Configuration**
Create `.env` file in the project root:
```bash
# === Required API Keys ===
OPENAI_API_KEY=sk-your-openai-key-here

# === Optional Voice Features ===
ELEVENLABS_API_KEY=el_your-elevenlabs-key
ELEVENLABS_VOICE_ID=your-voice-id

# === Database (Optional - uses local files if not provided) ===
MONGODB_URI=mongodb://localhost:27017

# === AI-Enhanced Prompt Evolution ===
PROMPT_ENHANCER_USE_CLOUD=true           # Enable AI-powered generation
PROMPT_ENHANCER_GENERATION_RATE=0.3      # 30% generation rate for cost control
PROMPT_ENHANCER_DEBUG=false              # Detailed evolution logging
PROMPT_EVOLUTION_ENABLED=true            # Enable statistical learning
PROMPT_EVOLUTION_RATE=0.1                # 10% experimentation rate

# === Performance Tuning ===
LLM_MODEL=gpt-4-turbo                    # Primary model for intelligence
LLM_TEMPERATURE=0.7                      # Response creativity
MEMORY_THRESHOLD=0.6                     # Memory retrieval sensitivity
MAX_MEMORIES=5                           # Max memories per query
```

### 4. **Quick Start**
```bash
./zackgpt.sh
```
Choose your preferred mode:
1. 🖥️ **Host mode** - Run directly on your system
2. 🐳 **Docker mode** - Run in container (recommended for consistency)

---

## 🚀 Usage Guide

### **Basic Chat** (AI Evolution Active)
```bash
./zackgpt.sh
# Select option 1 (Host) or 2 (Docker)
# Select main.py for full assistant with evolution
```

### **Development Mode** (Monitor Evolution)
```bash
./zackgpt.sh
# Select option 1 (Host) 
# Select dev.py for development features
```

**Dev Mode Features:**
- **Option 17**: View evolution progress and component statistics
- **Option 18**: Export training data for future model development
- **Option 20**: Test prompt enhancement components manually
- View real-time AI assessments and component performance
- Monitor experimentation results and learning patterns

### **Text-Only Mode** (Fastest)
```bash
./zackgpt_text.sh
```

### **Voice Mode** (Full Experience)
```bash
./zackgpt.sh
# Select main.py, voice will auto-enable if configured
```

---

## 📊 Monitoring & Analytics

### **Real-time Evolution Tracking**
```bash
# In dev mode, access these features:
# Option 17: View evolution statistics
# Option 18: Export training data
# Option 20: Test component generation

# Real-time logs:
tail -f logs/chat_history.jsonl     # Conversation history with AI assessments
tail -f logs/debug.log              # System debugging and evolution events
tail -f logs/performance.log        # Component performance and AI scores
```

### **Evolution Statistics**
Access via dev mode to see:
- **Component Success Rates**: Which components work best in different contexts
- **AI Assessment Trends**: How response quality improves over time
- **Experimentation Results**: Success rate of new AI-generated components
- **Context Adaptation**: Performance differences across conversation types
- **Cost Efficiency**: API usage optimization through smart generation rates

### **Training Data Collection**
The system automatically collects rich data for future model training:
- Conversation contexts and user expertise levels
- Multi-dimensional AI assessments with detailed reasoning
- Component selection patterns and success correlations
- Experiment outcomes and pattern discoveries
- User feedback and preference learning

---

## ⚙️ Configuration Reference

### **AI Evolution Settings** (`config/config.py`)
```python
# AI-Enhanced Prompt Evolution
PROMPT_ENHANCER_USE_CLOUD = True        # Enable GPT-4 powered generation
PROMPT_ENHANCER_GENERATION_RATE = 0.3   # 30% rate for cost control
PROMPT_ENHANCER_MODEL = "gpt-4-turbo"   # Model for AI assessments
PROMPT_ENHANCER_DEBUG = False           # Detailed evolution logging
PROMPT_EVOLUTION_ENABLED = True         # Enable statistical learning
PROMPT_EVOLUTION_RATE = 0.1             # 10% experimentation rate

# Model Configuration
LLM_MODEL = "gpt-4-turbo"               # Primary conversation model
LLM_TEMPERATURE = 0.7                   # Response creativity

# Memory System
MEMORY_THRESHOLD = 0.6                  # Similarity threshold for recall
MAX_MEMORIES = 5                        # Max memories per query
MONGODB_URI = "mongodb://localhost:27017"

# Voice Features
VOICE_ENABLED = True                    # Enable voice I/O
VOICE_MODEL = "tts-1"                  # TTS model
VOICE_ID = "alloy"                     # Voice selection
```

### **Integration with Foundation Prompts**
The evolution system **enhances** your existing `prompts/core_assistant.txt`:
- Uses it as the stable foundation template
- Dynamically replaces/enhances specific sections
- Adds contextual components based on conversation analysis
- Preserves your core style and instructions while improving performance

---

## 🛠️ Troubleshooting

### **Common Issues**

**Evolution not working / No component generation**
```bash
# Check AI enhancement settings
grep PROMPT_ENHANCER .env
# Enable debug mode to see detailed evolution logs
echo "PROMPT_ENHANCER_DEBUG=true" >> .env
# Verify OpenAI API key has GPT-4 access
```

**"No module named 'app'"**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or use the launcher: ./zackgpt.sh
```

**Voice not working**
```bash
# Check audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"
# Install system audio tools
brew install portaudio  # macOS
```

**MongoDB connection issues**
```bash
# Use file-based memory (fallback)
unset MONGODB_URI
# Or install MongoDB locally
brew install mongodb/brew/mongodb-community
```

### **Performance Optimization**
- **Cost Control**: Reduce `PROMPT_ENHANCER_GENERATION_RATE` (default: 30%)
- **Memory Tuning**: Increase `MEMORY_THRESHOLD` for more selective recall
- **Local Models**: Use local assessment models to reduce cloud dependency
- **Evolution Rate**: Adjust `PROMPT_EVOLUTION_RATE` for learning speed vs. stability

---

**🚀 Ready to experience AI that learns and improves with every conversation?**

**Run `./zackgpt.sh` and watch your assistant evolve! 🧬✨**

Your assistant will automatically:
- ✅ **Learn your preferences** through AI-powered conversation analysis
- ✅ **Improve response quality** using multi-dimensional assessment  
- ✅ **Adapt to contexts** with intelligent component selection
- ✅ **Generate new strategies** through AI-powered experimentation
- ✅ **Build training data** for future AI model development

*The future of AI assistance is here - and it's learning from you.*