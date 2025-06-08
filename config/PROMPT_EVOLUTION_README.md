# AI-Enhanced Evolutionary Prompt System

ZackGPT now includes a **self-learning prompt system** powered by **hybrid AI intelligence** that evolves and improves over time through both statistical learning AND intelligent AI analysis!

## How It Works

### 🧬 **Hybrid AI + Statistical Evolution**
The system combines **genetic algorithm-style** evolution with **intelligent AI analysis**:
- **AI-Powered Assessment**: GPT-4 evaluates response quality across multiple dimensions
- **Intelligent Component Generation**: AI creates new prompt components based on successful patterns
- **Local Model Integration**: Fast local assessments for real-time feedback
- **Cloud Intelligence**: Detailed analysis and pattern recognition
- **Statistical Tracking**: Performance metrics and weighted selection

### 🧩 **Component-Based Architecture**
Prompts are built from modular components:
- **Personality**: How the assistant behaves (witty, direct, etc.)
- **Memory Guidelines**: How to handle memory saving
- **Task Instructions**: Specific guidance for different tasks
- **Context Framers**: How to use conversation context
- **Output Formatters**: Response structure preferences

### 🔄 **AI-Enhanced Learning Process**
1. **Intelligent Selection**: AI analyzes context to pick optimal components
2. **AI Generation**: GPT-4 creates new components based on successful patterns
3. **Hybrid Assessment**: Local model + cloud AI evaluate response quality
4. **Multi-Dimensional Feedback**: Track accuracy, relevance, clarity, tone, completeness
5. **Smart Evolution**: AI-guided component improvement and pattern recognition
6. **Experimentation**: 10% rate for discovering new effective strategies

### 📊 **AI-Powered Performance Tracking**
Each component tracks:
- **Multi-dimensional AI scores**: accuracy, relevance, clarity, tone, completeness
- **Success rate**: exponential moving average from AI assessments
- **Detailed assessments**: GPT-4 analysis with reasoning and issue identification  
- **Usage patterns**: frequency, context, and performance correlations
- **Selection weight**: dynamically adjusted based on AI feedback

## Configuration

### Seed Components (`config/prompt_components.json`)
Initial components to bootstrap the system. The system will evolve beyond these.

### Evolution Settings
- `experimentation_rate`: How often to try new components (default: 10%)
- `learning_rate`: How quickly to adapt success rates (default: 10%)
- `max_components_per_type`: Prevents bloat by limiting component count

### Evolution Data (`config/prompt_evolution/evolution_data.json`)
Persistent storage of learned components and experiment results.

## Integration with core_assistant.txt

The evolutionary system **enhances** your existing `prompts/core_assistant.txt`:
- Uses it as the foundation template
- Dynamically replaces/enhances specific sections
- Adds contextual components based on conversation type
- Preserves your core style and instructions

## Context Awareness

The system adapts prompts based on:
- **Conversation Type**: technical, troubleshooting, learning, creative
- **User Expertise**: beginner, medium, high (based on technical terms used)
- **Recent Errors**: Adjusts when the assistant has been uncertain
- **Conversation Length**: Different strategies for long vs. short conversations

## Viewing Progress

Use the dev menu (option 17) to see:
- Total components evolved
- Success rates by component type  
- Recent experimentation results
- Evolution settings

## Training Data Collection

The system automatically logs:
- Which prompt components were used
- Conversation context
- Response quality assessments
- Experiment outcomes

This data can be exported (option 18) for future training of specialized models.

## Example Evolution

**Initial**: "Be witty and efficient"
**After Learning**: "Be witty and efficient - more personalized to Zack's style approach. Focus on technical accuracy and implementation details."

The system learns what works through actual usage!

## Benefits

✅ **Automatic Improvement**: Gets better without manual prompt engineering  
✅ **Context Adaptive**: Different strategies for different conversation types  
✅ **Lightweight**: No GPU required, just statistics  
✅ **Data Collection**: Builds training corpus for future AI model training  
✅ **Preserves Style**: Enhances rather than replaces your existing prompts  
✅ **Experimentation**: Constantly discovers new effective patterns  

## Future Possibilities

The collected data could train:
- A specialized prompt optimization model
- Context-aware prompt selection networks
- Local prompt generation models

But for now, simple statistics provide surprisingly effective learning! 