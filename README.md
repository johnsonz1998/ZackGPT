# ZackGPT 🧠⚡

A sophisticated personal AI assistant with **evolutionary prompt learning**, **persistent memory systems**, and **adaptive intelligence** that learns and improves through every interaction.

## 🎯 Core Philosophy

ZackGPT isn't just another chatbot - it's a **learning AI companion** that:
- **Remembers everything** and gets smarter over time
- **Adapts its personality** based on your communication patterns
- **Optimizes responses** using advanced memory systems
- **Evolves its prompting strategies** through statistical learning
- **Anticipates your needs** before you ask

## 🏗️ Current Architecture

### **Memory-Driven Intelligence**
- **MongoDB Conscious Memory**: Fast retrieval of recent conversations and patterns
- **Semantic Search**: OpenAI embeddings for intelligent memory retrieval
- **Statistical Learning**: Components learn and adapt based on success rates
- **Context Compression**: Efficient token usage through smart memory selection

### **Evolutionary Prompt System**
- **Modular Components**: Personality, memory guidelines, task instructions evolve independently
- **Performance Tracking**: Each component tracks success rates and usage patterns
- **Dynamic Selection**: Weighted random selection based on statistical performance
- **AI-Powered Enhancement**: Generate new components using successful examples

### **Adaptive Conversation Management**
- **Token-Aware History**: Automatic conversation trimming with intelligent summarization
- **Context Classification**: Adapts behavior based on conversation type (technical, creative, etc.)
- **User Expertise Assessment**: Adjusts explanations based on detected skill level
- **Real-Time Pattern Recognition**: Learns communication preferences during conversation

## 🚀 Key Features

### **🧠 Intelligent Memory System**
```python
# Semantic memory retrieval with importance weighting
memories = memory_db.query_memories(
    query=user_input,
    limit=3,
    importance="high",
    similarity_threshold=0.7
)
```

### **📈 Statistical Learning Components**
```python
# Components evolve based on real performance data
component.update_performance(success=True)
# → Increases weight and success_rate automatically
```

### **🎯 Context-Aware Responses**
```python
# Adapts strategy based on conversation analysis
strategy = analyze_context({
    'conversation_type': 'technical',
    'user_expertise': 'high', 
    'recent_errors': 0,
    'task_complexity': 'complex'
})
```

### **🔍 Web Search Integration**
- Automatic web search detection
- Intelligent query extraction
- Context-aware result integration

### **💬 Advanced Conversation Threading**
- Persistent conversation threads
- Message history with metadata
- Cross-thread memory connections

### **🎨 Modern Web Interface**
- React frontend with real-time chat
- Memory graph visualization
- Component performance tracking
- Settings and API key management

## 📁 Project Structure

```
ZackGPT/
├── src/zackgpt/
│   ├── core/                   # Core AI logic
│   │   ├── core_assistant.py   # Main assistant with memory integration
│   │   ├── prompt_builder.py   # Evolutionary prompt system
│   │   ├── prompt_enhancer.py  # AI-powered prompt enhancement
│   │   └── logger.py          # Debug and analytics logging
│   ├── data/                   # Data persistence
│   │   ├── database.py        # MongoDB operations
│   │   ├── memory_manager.py  # Memory storage and retrieval
│   │   └── thread_manager.py  # Conversation management
│   ├── tools/                  # External integrations
│   │   └── web_search.py      # Web search capabilities
│   ├── cli/                    # Command-line interface
│   ├── web/                    # Web API
│   └── voice/                  # Voice interaction
├── frontend/                   # React web interface
├── config/                     # Configuration and prompts
└── tests/                      # Comprehensive test suite
```

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.8+
- MongoDB
- Node.js 16+ (for frontend)
- OpenAI API key

### **Quick Start**
```bash
# Clone the repository
git clone https://github.com/your-username/ZackGPT.git
cd ZackGPT

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your API keys to .env

# Start MongoDB
mongod

# Run the backend
python -m src.zackgpt.web.web_api

# Install and run frontend
cd frontend
npm install
npm start
```

### **Environment Variables**
```env
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017
WEB_SEARCH_ENABLED=true
DEBUG_MODE=true
```

## 💻 Usage Examples

### **CLI Interaction**
```bash
# Start interactive session
python -m src.zackgpt.cli.main

# Development menu with memory tools
python -m src.zackgpt.cli.dev
```

### **Web Interface**
- Navigate to `http://localhost:3000`
- Chat interface with memory visualization
- Real-time component evolution tracking

### **API Integration**
```python
from src.zackgpt.core import CoreAssistant

assistant = CoreAssistant()
response = assistant.process_input("Help me understand machine learning")
```

## 📊 Memory & Learning System

### **Memory Types**
- **Semantic Memories**: Facts, preferences, and knowledge
- **Episodic Memories**: Conversation history and context
- **Pattern Memories**: Learned behavioral patterns
- **Component Memories**: Successful prompt strategies

### **Learning Mechanisms**
- **Statistical Learning**: Component weights adjust based on success rates
- **Pattern Recognition**: Detects user communication preferences
- **Adaptive Prompting**: Generates new strategies based on context
- **Cross-Memory Insights**: Connects related information automatically

## 🧪 Development Tools

### **Debug & Analytics**
```bash
# View prompt evolution stats
python -m src.zackgpt.cli.dev
# → Option 17: View prompt evolution stats

# Inspect memory system
python -m src.zackgpt.cli.dev  
# → Option 9: View long-term memory log
```

### **Testing**
```bash
# Run comprehensive tests
pytest tests/

# Test specific components
pytest tests/backend/core/test_memory_manager.py
```

---

## 🚀 Coming Soon: Advanced Intelligence Features

> **Note**: The following features represent the next evolution of ZackGPT into a truly superintelligent personal assistant. Implementation is planned for the coming weeks.

### **🧠 Memory-Driven Token Optimization**
- **Intelligent Context Compression**: Transform memories into ultra-high information density
- **Dynamic Token Allocation**: Smart resource distribution based on query complexity
- **Semantic Clustering**: Eliminate redundant information automatically
- **Relevance Scoring**: Rank memories by information value per token

### **🔮 Predictive Intelligence Engine**
- **Intent Prediction**: Anticipate user needs before they're expressed
- **Proactive Context Preparation**: Pre-load relevant information
- **Conversation Trajectory Analysis**: Understand where discussions are heading
- **Information Gap Detection**: Identify missing knowledge automatically

### **⚡ Real-Time Learning & Adaptation**
- **Live Learning Engine**: Adapt response strategy during conversation
- **Micro-Pattern Recognition**: Detect subtle user preference changes
- **Dynamic Response Structuring**: Personalize format based on proven preferences
- **Immediate Feedback Integration**: Learn from every interaction signal

### **🧩 Neo4j Subconscious Memory**
- **Knowledge Graph Construction**: Rich relationship mapping of all memories
- **Intelligent Graph Traversal**: Deep insight generation through relationship analysis
- **Cross-Memory Synthesis**: Connect seemingly unrelated information
- **Meta-Insight Generation**: Understand patterns about patterns

### **📈 Advanced User Modeling**
- **Deep Behavioral Analysis**: Cognitive load, information processing, communication style
- **Personality Model Evolution**: Dynamic personality emergence from interactions
- **Learning Style Adaptation**: Tailor explanations to user's proven learning patterns
- **Predictive User Modeling**: Anticipate how user preferences will evolve

### **🎯 Contextual Intelligence Amplification**
- **Multi-Stage Response Generation**: Planning → Synthesis → Optimization → Enhancement
- **Predictive Response Elements**: Anticipate follow-up questions and needs
- **Proactive Problem-Solving**: Address potential issues before they arise
- **Intelligence Multiplication**: Progressive response enhancement through memory context

### **🌐 3D Component Visualization**
- **Component Relationship Mapping**: Visualize how prompt components interact
- **Evolution Tracking**: See component performance over time in 3D space
- **Strategy Visualization**: Understand prompt selection patterns
- **Interactive Component Management**: Manually adjust component relationships

### **🏗️ Advanced Architecture Features**
- **Zero Hardcoded Personality**: Completely learned behavior from user interactions
- **Generative Component Creation**: AI-generated prompt components based on needs
- **Daily Memory Consolidation**: Intelligent cleanup with insight generation
- **Cross-Pattern Analysis**: Understand relationships between different behavior patterns

### **📊 Superintelligent Analytics**
- **Conversation Intelligence Metrics**: Measure response quality improvement over time
- **Learning Velocity Tracking**: Monitor how quickly the system adapts
- **Prediction Accuracy Scoring**: Validate anticipatory features
- **Memory Efficiency Analysis**: Optimize token usage through memory insights

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run tests before submitting
pytest tests/ --cov=src/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models and embeddings
- MongoDB for flexible data storage
- Neo4j for graph database capabilities (coming soon)
- React community for frontend components
- Open source contributors

---

**ZackGPT**: Because your AI assistant should get smarter, not just respond smarter. 🧠✨ 