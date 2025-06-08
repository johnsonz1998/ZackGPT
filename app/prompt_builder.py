import json
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from config import config
from app.prompt_utils import load_prompt
from app.logger import debug_log, debug_info
from app.prompt_enhancer import HybridPromptEnhancer

# Modular memory guidelines
AGGRESSIVE_MEMORY_GUIDELINES = """
Memory Guidelines:
- Save any factual, behavioral, or preference-based information that appears new and relevant
- If the assistant already knows it, skip it
- Don't save emotional filler or vague references
- Prioritize saving preferences, goals, setup info, and Zack's style or rules
"""

CONSERVATIVE_MEMORY_GUIDELINES = """
Memory Guidelines:
- Only save memories you're 100% confident about
- If you're unsure about information, don't save it
- If you make a mistake, acknowledge it and let Zack correct you
- Don't save memories about preferences or facts unless explicitly confirmed
"""

class PromptComponent:
    """Represents a modular prompt component that can be combined with others."""
    def __init__(self, name: str, content: str, weight: float = 1.0, 
                 success_rate: float = 0.5, usage_count: int = 0):
        self.name = name
        self.content = content
        self.weight = weight  # How likely to be selected
        self.success_rate = success_rate  # Performance metric
        self.usage_count = usage_count
        self.last_used = None
    
    def update_performance(self, success: bool):
        """Update performance based on feedback using simple statistical learning."""
        self.usage_count += 1
        self.last_used = datetime.now().isoformat()
        
        # Exponential moving average for success rate
        alpha = 0.1  # Learning rate
        if success:
            self.success_rate = self.success_rate * (1 - alpha) + alpha
        else:
            self.success_rate = self.success_rate * (1 - alpha)
        
        # Adjust weight based on success rate
        self.weight = max(0.1, self.success_rate * 2)

class GenerativePromptEvolver:
    """Statistical learning system that evolves prompt generation strategies over time."""
    
    def __init__(self, data_dir: str = "config/prompt_evolution"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Core component types
        self.components = {
            'personality': [],
            'memory_guidelines': [],
            'task_instructions': [],
            'context_framers': [],
            'output_formatters': []
        }
        
        # Settings
        self.settings = {}
        
        # Experimentation tracking
        self.experiments = []
        
        # AI-powered enhancement system
        self.ai_enhancer = HybridPromptEnhancer()
        
        self._load_settings()
        self.load_evolution_data()
        self._initialize_from_config()
    
    def _load_settings(self):
        """Load evolution settings from config."""
        try:
            with open("config/prompt_components.json", "r") as f:
                config_data = json.load(f)
                self.settings = config_data.get("evolution_settings", {
                    "experimentation_rate": 0.1,
                    "learning_rate": 0.1, 
                    "mutation_probability": 0.15,
                    "promotion_threshold": 0.3,
                    "max_components_per_type": 20
                })
        except Exception as e:
            debug_log(f"Could not load prompt config, using defaults: {e}")
            self.settings = {
                "experimentation_rate": 0.1,
                "learning_rate": 0.1,
                "mutation_probability": 0.15, 
                "promotion_threshold": 0.3,
                "max_components_per_type": 20
            }
    
    def _initialize_from_config(self):
        """Initialize components from config file if no learned components exist."""
        if any(self.components.values()):
            debug_info("🧬 Using existing evolved prompt components")
            return
            
        try:
            with open("config/prompt_components.json", "r") as f:
                config_data = json.load(f)
                seed_components = config_data.get("seed_components", {})
                
                for comp_type, comp_list in seed_components.items():
                    if comp_type in self.components:
                        for comp_data in comp_list:
                            component = PromptComponent(
                                name=comp_data["name"],
                                content=comp_data["content"],
                                weight=comp_data.get("weight", 1.0)
                            )
                            self.components[comp_type].append(component)
                            
                debug_info("🌱 Initialized with seed prompt components")
                
        except Exception as e:
            debug_log(f"Could not load seed components: {e}")
            # Fallback to minimal default
            self.components['memory_guidelines'].append(
                PromptComponent("default", "Follow the memory guidelines in the base prompt.", 1.0)
            )
    
    def generate_new_component(self, component_type: str, context: Dict) -> PromptComponent:
        """Generate a new component using AI-powered enhancement."""
        
        # Get successful examples for AI to learn from
        successful_components = [c for c in self.components[component_type] 
                               if c.success_rate > 0.6]
        successful_examples = [c.content for c in successful_components]
        
        # Use AI to generate enhanced component
        ai_generated_content = self.ai_enhancer.generate_enhanced_component(
            component_type, context, successful_examples
        )
        
        return PromptComponent(
            name=f"ai_generated_{component_type}_{int(time.time())}",
            content=ai_generated_content,
            weight=0.7  # Start with good weight since it's AI-generated
        )
    
    def _mutate_component(self, base: PromptComponent, context: Dict) -> PromptComponent:
        """Create a mutation of an existing component using simple heuristics."""
        mutations = [
            "more concise",
            "more specific", 
            "more contextual",
            "more adaptive",
            "more personalized to Zack's style"
        ]
        
        mutation = random.choice(mutations)
        
        # Simple mutation strategy
        if "concise" in mutation:
            new_content = base.content.replace(".", " - keep it brief.")
        elif "specific" in mutation:
            new_content = base.content + " Be precise and detailed."
        else:
            new_content = f"{base.content.rstrip('.')} - {mutation} approach."
        
        return PromptComponent(
            name=f"{base.name}_mut_{int(time.time())}",
            content=new_content,
            weight=base.weight * 0.8  # Start with slightly lower weight
        )
    
    def _create_contextual_component(self, component_type: str, context: Dict) -> PromptComponent:
        """Create a new component based on conversation context."""
        
        base_templates = {
            'personality': "Adapt your personality to be {style}.",
            'memory_guidelines': "When handling memories, {approach}.",
            'task_instructions': "For this type of task, {instruction}.",
            'context_framers': "Frame your response considering {context}.",
            'output_formatters': "Format your output to be {format}."
        }
        
        # Context-based content generation
        if context.get('conversation_type') == 'technical':
            style_map = {
                'personality': 'technically precise and efficient',
                'memory_guidelines': 'focus on technical details and implementation specifics',
                'task_instructions': 'prioritize accuracy and technical correctness',
                'context_framers': 'the technical complexity of the discussion',
                'output_formatters': 'structured and technically detailed'
            }
        else:
            style_map = {
                'personality': 'helpful and conversational',
                'memory_guidelines': 'balance detail with relevance',
                'task_instructions': 'focus on being helpful and clear',
                'context_framers': 'the conversational flow and user needs',
                'output_formatters': 'clear and easy to understand'
            }
        
        template = base_templates.get(component_type, "Handle this situation by {approach}.")
        content = template.format(**{k: style_map.get(component_type, 'appropriately') for k in ['style', 'approach', 'instruction', 'context', 'format']})
        
        return PromptComponent(
            name=f"contextual_{component_type}_{int(time.time())}",
            content=content,
            weight=0.7
        )
    
    def _evolve_component(self, successful_components: List[PromptComponent], 
                         context: Dict) -> PromptComponent:
        """Evolve a new component from successful ones using statistical combination."""
        
        # Simple combination strategy: merge ideas from successful components
        if len(successful_components) == 1:
            return self._mutate_component(successful_components[0], context)
        
        # Combine elements from multiple successful components
        base_content = successful_components[0].content
        enhancement = successful_components[1].content.split('.')[0].lower()
        
        # Add contextual elements based on recent conversation patterns
        if context.get('conversation_type') == 'technical':
            context_addition = "Focus on technical accuracy and implementation details."
        elif context.get('user_expertise') == 'high':
            context_addition = "Assume high technical competence and skip basic explanations."
        elif context.get('recent_errors', 0) > 2:
            context_addition = "Be extra careful about accuracy and acknowledge uncertainty."
        else:
            context_addition = "Adapt to the conversation flow and user needs."
        
        new_content = f"{base_content} Additionally, {enhancement}. {context_addition}"
        
        return PromptComponent(
            name=f"evolved_{int(time.time())}",
            content=new_content,
            weight=0.8  # Start with good weight since it's based on successful components
        )
    
    def build_adaptive_prompt(self, context: Dict) -> Tuple[str, Dict]:
        """Build a prompt that adapts based on context and statistical learning."""
        
        # Analyze context to determine prompt strategy
        strategy = self._analyze_context(context)
        
        # Select components based on strategy and performance
        selected_components = {}
        prompt_metadata = {'strategy': strategy, 'components': {}}
        
        for comp_type in self.components.keys():
            if self.components[comp_type]:  # Only if we have components of this type
                component = self._select_component(comp_type, strategy, context)
                selected_components[comp_type] = component
                prompt_metadata['components'][comp_type] = component.name
        
        # Occasionally experiment with new components
        if random.random() < self.settings["experimentation_rate"]:
            experiment_type = random.choice(list(self.components.keys()))
            new_component = self.generate_new_component(experiment_type, context)
            self.components[experiment_type].append(new_component)
            selected_components[experiment_type] = new_component
            prompt_metadata['experiment'] = {
                'type': experiment_type,
                'component': new_component.name
            }
            debug_info(f"🧪 Experimenting with new {experiment_type}: {new_component.name}")
        
        # Construct the final prompt using core_assistant.txt as base
        prompt = self._construct_prompt_with_base_template(selected_components, context)
        
        return prompt, prompt_metadata
    
    def _analyze_context(self, context: Dict) -> str:
        """Analyze conversation context to determine optimal prompting strategy."""
        
        # Simple heuristics based on conversation patterns
        if context.get('recent_errors', 0) > 2:
            return "error_recovery"
        elif context.get('task_complexity', 'simple') == 'complex':
            return "detailed_guidance"
        elif context.get('user_expertise', 'medium') == 'high':
            return "concise_expert"
        elif context.get('conversation_length', 0) > 10:
            return "context_aware"
        else:
            return "balanced"
    
    def _select_component(self, comp_type: str, strategy: str, context: Dict) -> PromptComponent:
        """Select the best component based on statistical performance and strategy fit."""
        
        candidates = self.components[comp_type]
        if not candidates:
            return self.generate_new_component(comp_type, context)
        
        # Weight selection by performance and strategy fit
        weights = []
        for comp in candidates:
            # Base weight from statistical performance
            weight = comp.weight * (comp.success_rate ** 2)  # Square to emphasize high performers
            
            # Strategy-specific bonuses (simple heuristics)
            if strategy == "concise_expert" and any(word in comp.content.lower() 
                                                  for word in ["efficient", "concise", "brief"]):
                weight *= 1.5
            elif strategy == "error_recovery" and any(word in comp.content.lower() 
                                                    for word in ["careful", "accurate", "confident"]):
                weight *= 1.3
            elif strategy == "detailed_guidance" and any(word in comp.content.lower() 
                                                       for word in ["detailed", "specific", "thorough"]):
                weight *= 1.4
            
            weights.append(max(0.1, weight))  # Ensure minimum weight
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(candidates)
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return candidates[i]
        
        return candidates[-1]  # Fallback
    
    def _construct_prompt_with_base_template(self, components: Dict[str, PromptComponent], 
                                           context: Dict) -> str:
        """Construct the final prompt using core_assistant.txt as foundation."""
        
        # Load the base template (your existing core_assistant.txt)
        base_prompt = load_prompt("core_assistant", {
            "SHORT_TERM": context.get('short_term', ''),
            "MEMORY_CONTEXT": context.get('memory_context', '')
        })
        
        # Strategy: Enhance specific sections while keeping the core structure
        sections = base_prompt.split('\n\n')
        enhanced_sections = []
        
        for section in sections:
            enhanced_section = section
            
            # Enhance personality section
            if "personality" in section.lower() or "witty" in section.lower():
                if 'personality' in components:
                    enhanced_section += f"\n\nAdditional personality guidance: {components['personality'].content}"
            
            # Enhance memory guidelines section
            elif "Memory Guidelines:" in section:
                if 'memory_guidelines' in components:
                    # Replace the existing memory guidelines
                    lines = section.split('\n')
                    header = lines[0]  # Keep "Memory Guidelines:"
                    enhanced_section = f"{header}\n{components['memory_guidelines'].content}"
            
            # Enhance core principles if we have task instructions
            elif "CORE PRINCIPLES:" in section:
                if 'task_instructions' in components:
                    enhanced_section += f"\n\nAdditional guidance: {components['task_instructions'].content}"
            
            enhanced_sections.append(enhanced_section)
        
        # Add any remaining components that didn't fit into existing sections
        additional_sections = []
        
        if 'context_framers' in components:
            additional_sections.append(f"Context Awareness: {components['context_framers'].content}")
        
        if 'output_formatters' in components:
            additional_sections.append(f"Response Format: {components['output_formatters'].content}")
        
        # Combine everything
        final_prompt = '\n\n'.join(enhanced_sections)
        if additional_sections:
            final_prompt += '\n\n' + '\n\n'.join(additional_sections)
        
        return final_prompt
    
    def record_feedback(self, prompt_metadata: Dict, quality_assessment: Dict, 
                       user_feedback: Optional[str] = None):
        """Record AI-powered feedback to improve future component selection."""
        
        # Extract success from AI assessment
        success = quality_assessment.get('success', quality_assessment.get('overall_score', 0) > 0.6)
        
        # Update component performance using AI-enhanced scoring
        for comp_type, comp_name in prompt_metadata.get('components', {}).items():
            for component in self.components[comp_type]:
                if component.name == comp_name:
                    # Use AI assessment for more nuanced feedback
                    overall_score = quality_assessment.get('overall_score', 0.5)
                    component.update_performance(overall_score > 0.6)
                    
                    # Store detailed assessment for analysis
                    if not hasattr(component, 'detailed_assessments'):
                        component.detailed_assessments = []
                    component.detailed_assessments.append({
                        'timestamp': datetime.now().isoformat(),
                        'assessment': quality_assessment,
                        'user_feedback': user_feedback
                    })
                    # Keep only last 10 assessments
                    component.detailed_assessments = component.detailed_assessments[-10:]
                    break
        
        # Record experiment results with AI assessment
        if 'experiment' in prompt_metadata:
            exp_data = {
                'timestamp': datetime.now().isoformat(),
                'experiment': prompt_metadata['experiment'],
                'success': success,
                'ai_assessment': quality_assessment,
                'feedback': user_feedback
            }
            self.experiments.append(exp_data)
            
            # If experiment was successful, boost its weight for future selection
            if success and random.random() < self.settings["promotion_threshold"]:
                self._promote_experimental_component(prompt_metadata['experiment'])
        
        # Periodic cleanup and saving
        if len(self.experiments) % 10 == 0:
            self._cleanup_components()
            self.save_evolution_data()
    
    def _promote_experimental_component(self, experiment: Dict):
        """Promote a successful experimental component by boosting its statistical weight."""
        comp_type = experiment['type']
        comp_name = experiment['component']
        
        # Find and promote the experimental component
        for component in self.components[comp_type]:
            if component.name == comp_name:
                component.weight = min(2.0, component.weight * 1.5)  # Boost weight
                component.success_rate = max(component.success_rate, 0.7)  # Boost success rate
                debug_info(f"🎯 Promoted experimental component: {comp_name}")
                break
    
    def _cleanup_components(self):
        """Remove poorly performing components to prevent bloat."""
        for comp_type in self.components:
            if len(self.components[comp_type]) > self.settings["max_components_per_type"]:
                # Sort by performance (weight * success_rate * usage_count)
                self.components[comp_type].sort(
                    key=lambda c: c.weight * c.success_rate * max(1, c.usage_count),
                    reverse=True
                )
                # Keep only the top performers
                kept = self.components[comp_type][:self.settings["max_components_per_type"]]
                removed = len(self.components[comp_type]) - len(kept)
                self.components[comp_type] = kept
                if removed > 0:
                    debug_info(f"🧹 Cleaned up {removed} low-performing {comp_type} components")
    
    def save_evolution_data(self):
        """Save statistical learning data to disk."""
        data = {
            'components': {},
            'experiments': self.experiments[-100:],  # Keep last 100 experiments
            'last_updated': datetime.now().isoformat(),
            'settings': self.settings
        }
        
        # Serialize components
        for comp_type, comp_list in self.components.items():
            data['components'][comp_type] = []
            for comp in comp_list:
                data['components'][comp_type].append({
                    'name': comp.name,
                    'content': comp.content,
                    'weight': comp.weight,
                    'success_rate': comp.success_rate,
                    'usage_count': comp.usage_count,
                    'last_used': comp.last_used
                })
        
        try:
            with open(os.path.join(self.data_dir, 'evolution_data.json'), 'w') as f:
                json.dump(data, f, indent=2)
            debug_info(f"💾 Saved prompt evolution data: {sum(len(comps) for comps in self.components.values())} components")
        except Exception as e:
            debug_log(f"Error saving evolution data: {e}")
    
    def load_evolution_data(self):
        """Load previous statistical learning data."""
        data_file = os.path.join(self.data_dir, 'evolution_data.json')
        
        if not os.path.exists(data_file):
            return
        
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            # Restore components
            for comp_type, comp_list in data.get('components', {}).items():
                if comp_type in self.components:
                    self.components[comp_type] = []
                    for comp_data in comp_list:
                        component = PromptComponent(
                            name=comp_data['name'],
                            content=comp_data['content'],
                            weight=comp_data.get('weight', 1.0),
                            success_rate=comp_data.get('success_rate', 0.5),
                            usage_count=comp_data.get('usage_count', 0)
                        )
                        component.last_used = comp_data.get('last_used')
                        self.components[comp_type].append(component)
            
            self.experiments = data.get('experiments', [])
            self.settings.update(data.get('settings', {}))
            debug_info(f"📚 Loaded prompt evolution data: {len(self.experiments)} experiments, {sum(len(comps) for comps in self.components.values())} components")
            
        except Exception as e:
            debug_log(f"Error loading evolution data: {e}")

# Enhanced PromptBuilder that uses the evolutionary system while preserving existing interface
class EvolutionaryPromptBuilder:
    """
    Evolutionary prompt builder that uses core_assistant.txt as foundation
    and evolves components through statistical learning (no AI model required).
    """
    def __init__(self):
        self.evolver = GenerativePromptEvolver()
        self.current_prompt_metadata = None
    
    def build_system_prompt(self, short_term: str, memory_context: str, 
                          conversation_context: Dict = None) -> str:
        """Build an adaptive system prompt that learns over time using statistical evolution."""
        
        context = {
            'short_term': short_term,
            'memory_context': memory_context,
            **(conversation_context or {})
        }
        
        prompt, metadata = self.evolver.build_adaptive_prompt(context)
        self.current_prompt_metadata = metadata
        
        return prompt
    
    def record_response_feedback(self, prompt_metadata: Dict, quality_assessment: Dict, user_feedback: str = None):
        """Record AI-powered feedback on the generated prompt."""
        self.evolver.record_feedback(
            prompt_metadata, 
            quality_assessment, 
            user_feedback
        )
    
    def get_evolution_stats(self) -> Dict:
        """Get statistics about the evolutionary learning process."""
        stats = {
            'total_components': sum(len(comps) for comps in self.evolver.components.values()),
            'total_experiments': len(self.evolver.experiments),
            'component_breakdown': {k: len(v) for k, v in self.evolver.components.items()},
            'settings': self.evolver.settings
        }
        
        # Performance stats
        if self.evolver.experiments:
            recent_experiments = self.evolver.experiments[-20:] if len(self.evolver.experiments) >= 20 else self.evolver.experiments
            recent_success_rate = sum(1 for exp in recent_experiments if exp['success']) / len(recent_experiments)
            stats['recent_success_rate'] = recent_success_rate
        
        # Component performance
        for comp_type, components in self.evolver.components.items():
            if components:
                avg_success = sum(c.success_rate for c in components) / len(components)
                stats[f'{comp_type}_avg_success'] = avg_success
        
        return stats

# Legacy compatibility - keep the old class name working
class PromptBuilder(EvolutionaryPromptBuilder):
    """Legacy compatibility class - redirects to EvolutionaryPromptBuilder."""
    pass 