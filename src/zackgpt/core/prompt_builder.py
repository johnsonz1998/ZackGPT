import json
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from config import config
from ..archive.prompt_utils import load_prompt
from .logger import debug_log, debug_info, debug_success, log_component_selection, log_user_rating, log_component_performance_update
from .prompt_enhancer import HybridPromptEnhancer

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
        old_success_rate = self.success_rate
        old_weight = self.weight
        
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
        
        debug_info(f"📈 Component performance updated: {self.name}", {
            "success": success,
            "usage_count": self.usage_count,
            "success_rate": f"{old_success_rate:.3f} → {self.success_rate:.3f}",
            "weight": f"{old_weight:.3f} → {self.weight:.3f}",
            "change": f"{'+' if self.weight > old_weight else ''}{self.weight - old_weight:.3f}"
        })
        
        # Log for aggregation and analysis
        log_component_performance_update(
            component_name=self.name,
            success=success,
            weight_before=old_weight,
            weight_after=self.weight,
            success_rate_before=old_success_rate,
            success_rate_after=self.success_rate,
            usage_count=self.usage_count
        )

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
        """Build a prompt using statistical learning and contextual adaptation."""
        
        debug_info("🔨 Building adaptive prompt", {
            "context_type": context.get('conversation_type', 'general'),
            "context_keys": list(context.keys()),
            "total_components": sum(len(comps) for comps in self.components.values())
        })
        
        # Analyze context to determine strategy
        strategy = self._analyze_context(context)
        
        debug_info(f"📋 Selected strategy: {strategy}", {
            "context_analysis": {
                "conversation_length": context.get('conversation_length', 0),
                "recent_errors": context.get('recent_errors', 0),
                "user_expertise": context.get('user_expertise', 'unknown'),
                "task_complexity": context.get('task_complexity', 'unknown')
            }
        })
        
        # Select components for each type
        selected_components = {}
        for comp_type in self.components.keys():
            component = self._select_component(comp_type, strategy, context)
            selected_components[comp_type] = component
        
        debug_success("🎯 Component selection complete", {
            "components_selected": {k: v.name for k, v in selected_components.items()},
            "total_weight": sum(comp.weight for comp in selected_components.values()),
            "avg_success_rate": sum(comp.success_rate for comp in selected_components.values()) / len(selected_components)
        })
        
        # Build the final prompt
        prompt = self._construct_prompt_with_base_template(selected_components, context)
        
        # Create metadata for tracking
        metadata = {
            'strategy': strategy,
            'components': {k: v.name for k, v in selected_components.items()},
            'context_summary': {
                'type': context.get('conversation_type', 'general'),
                'complexity': context.get('task_complexity', 'unknown')
            },
            'component_stats': {
                k: {
                    'weight': v.weight,
                    'success_rate': v.success_rate,
                    'usage_count': v.usage_count
                } for k, v in selected_components.items()
            }
        }
        
        debug_log("📝 Final prompt metadata", metadata)
        debug_info(f"✅ Built adaptive prompt ({len(prompt)} chars)", {
            "prompt_length": len(prompt),
            "sections": prompt.count('\n\n') + 1,
            "enhancement_points": sum(1 for comp in selected_components.values() if comp.usage_count > 0)
        })
        
        return prompt, metadata
    
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
            debug_info(f"🔍 No components available for {comp_type}, generating new one")
            return self.generate_new_component(comp_type, context)
        
        debug_info(f"🎯 Selecting {comp_type} component", {
            "strategy": strategy,
            "candidates": len(candidates),
            "context": context.get('conversation_type', 'general')
        })
        
        # Weight selection by performance and strategy fit
        weights = []
        selection_details = []
        
        for comp in candidates:
            # Base weight from statistical performance
            base_weight = comp.weight * (comp.success_rate ** 2)  # Square to emphasize high performers
            weight = base_weight
            bonuses = []
            
            # Strategy-specific bonuses (simple heuristics)
            if strategy == "concise_expert" and any(word in comp.content.lower() 
                                                  for word in ["efficient", "concise", "brief"]):
                weight *= 1.5
                bonuses.append("concise_expert_bonus(1.5x)")
            elif strategy == "error_recovery" and any(word in comp.content.lower() 
                                                    for word in ["careful", "accurate", "confident"]):
                weight *= 1.3
                bonuses.append("error_recovery_bonus(1.3x)")
            elif strategy == "detailed_guidance" and any(word in comp.content.lower() 
                                                       for word in ["detailed", "specific", "thorough"]):
                weight *= 1.4
                bonuses.append("detailed_guidance_bonus(1.4x)")
            
            final_weight = max(0.1, weight)  # Ensure minimum weight
            weights.append(final_weight)
            
            selection_details.append({
                "name": comp.name[:30] + "..." if len(comp.name) > 30 else comp.name,
                "content_preview": comp.content[:50] + "..." if len(comp.content) > 50 else comp.content,
                "raw_weight": f"{comp.weight:.3f}",
                "success_rate": f"{comp.success_rate:.3f}",
                "base_calc": f"{comp.weight:.3f} × {comp.success_rate:.3f}² = {base_weight:.3f}",
                "bonuses": bonuses or ["none"],
                "final_weight": f"{final_weight:.3f}",
                "usage_count": comp.usage_count
            })
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            debug_info("⚠️ All weights are zero, using random selection")
            selected = random.choice(candidates)
        else:
            # Calculate probabilities for logging
            probabilities = [w/total_weight for w in weights]
            
            r = random.uniform(0, total_weight)
            cumulative = 0
            selected_index = -1
            
            for i, weight in enumerate(weights):
                cumulative += weight
                if r <= cumulative:
                    selected_index = i
                    break
            
            if selected_index == -1:
                selected_index = len(candidates) - 1  # Fallback
                
            selected = candidates[selected_index]
            
            debug_info(f"🎲 Component selection process for {comp_type}", {
                "total_weight": f"{total_weight:.3f}",
                "random_value": f"{r:.3f}",
                "selected_index": selected_index,
                "selected_component": selected.name,
                "selection_probability": f"{probabilities[selected_index]:.1%}"
            })
        
        # Log all candidates and their weights
        debug_log(f"📊 {comp_type} component candidates", selection_details)
        
        debug_success(f"✅ Selected {comp_type} component: {selected.name}", {
            "content": selected.content,
            "weight": f"{selected.weight:.3f}",
            "success_rate": f"{selected.success_rate:.3f}",
            "usage_count": selected.usage_count
        })
        
        # Log selection for analysis
        log_component_selection(
            component_name=selected.name,
            component_type=comp_type,
            selection_probability=probabilities[selected_index] if 'probabilities' in locals() and selected_index >= 0 else 0.0,
            strategy=strategy,
            context_type=context.get('conversation_type', 'general'),
            weight=selected.weight,
            success_rate=selected.success_rate,
            usage_count=selected.usage_count,
            total_candidates=len(candidates)
        )
        
        return selected
    
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
        """Record feedback to improve future component selection, prioritizing user ratings."""
        
        debug_info("🔄 Processing feedback for prompt components", {
            "has_user_rating": quality_assessment.get('user_rating') is not None,
            "assessment_type": quality_assessment.get('assessment_type', 'unknown'),
            "components_used": list(prompt_metadata.get('components', {}).keys())
        })
        
        # Prioritize user ratings over heuristic scoring
        if quality_assessment.get('user_rating') is not None:
            # User gave explicit rating - this is gold standard feedback!
            user_rating = quality_assessment.get('user_rating')
            success = user_rating >= 3  # 3+ out of 5 is success
            overall_score = user_rating / 5.0
            
            debug_success(f"⭐ User rated response: {user_rating}/5", {
                "converted_score": overall_score,
                "success": success,
                "rating_category": "excellent" if user_rating >= 4 else "good" if user_rating == 3 else "poor"
            })
            
            # Log user rating for analysis
            log_user_rating(
                rating=user_rating,
                component_name=prompt_metadata['components'][comp_type],
                weight_before=prompt_metadata['component_stats'][comp_type]['weight'],
                weight_after=prompt_metadata['component_stats'][comp_type]['weight'],
                component_type=comp_type,
                success_rate_before=prompt_metadata['component_stats'][comp_type]['success_rate'],
                success_rate_after=prompt_metadata['component_stats'][comp_type]['success_rate'],
                rating_impact="boost"
            )
        else:
            # Fall back to heuristic assessment
            success = quality_assessment.get('success', quality_assessment.get('overall_score', 0) > 0.6)
            overall_score = quality_assessment.get('overall_score', 0.5)
            
            debug_info("🤖 Using heuristic assessment", {
                "overall_score": overall_score,
                "success": success,
                "assessment_details": quality_assessment.get('reasoning', 'No details')
            })
        
        # Update component performance
        component_updates = []
        for comp_type, comp_name in prompt_metadata.get('components', {}).items():
            for component in self.components[comp_type]:
                if component.name == comp_name:
                    old_weight = component.weight
                    old_success_rate = component.success_rate
                    
                    # User ratings get stronger weight adjustment
                    weight_multiplier = 1.0
                    if quality_assessment.get('user_rating') is not None:
                        user_rating = quality_assessment.get('user_rating')
                        if user_rating >= 4:
                            weight_multiplier = 1.3
                            component.weight = min(2.0, component.weight * 1.3)  # Big boost for 4-5
                            debug_success(f"🚀 BOOSTING component {comp_name}", {
                                "user_rating": f"{user_rating}/5",
                                "weight_change": f"{old_weight:.3f} → {component.weight:.3f}",
                                "multiplier": "1.3x (excellent rating)"
                            })
                        elif user_rating <= 2:
                            weight_multiplier = 0.7
                            component.weight = max(0.3, component.weight * 0.7)  # Penalty for 1-2
                            debug_info(f"⬇️ PENALIZING component {comp_name}", {
                                "user_rating": f"{user_rating}/5", 
                                "weight_change": f"{old_weight:.3f} → {component.weight:.3f}",
                                "multiplier": "0.7x (poor rating)"
                            })
                        else:
                            debug_info(f"➡️ NEUTRAL component {comp_name}", {
                                "user_rating": f"{user_rating}/5",
                                "weight": f"{component.weight:.3f} (unchanged)"
                            })
                    
                    # Standard performance update
                    component.update_performance(success)
                    
                    component_updates.append({
                        "name": comp_name,
                        "type": comp_type,
                        "weight_change": f"{old_weight:.3f} → {component.weight:.3f}",
                        "success_rate_change": f"{old_success_rate:.3f} → {component.success_rate:.3f}",
                        "usage_count": component.usage_count,
                        "weight_multiplier": weight_multiplier
                    })
                    
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
        
        debug_log("📈 Component learning summary", component_updates)
        
        # Record experiment results
        if 'experiment' in prompt_metadata:
            exp_data = {
                'timestamp': datetime.now().isoformat(),
                'experiment': prompt_metadata['experiment'],
                'success': success,
                'assessment': quality_assessment,
                'feedback': user_feedback
            }
            self.experiments.append(exp_data)
            
            debug_info("🧪 Recorded experimental component result", {
                "experiment_type": prompt_metadata['experiment'].get('type', 'unknown'),
                "success": success,
                "total_experiments": len(self.experiments)
            })
            
            # If experiment was successful, boost its weight for future selection
            if success and random.random() < self.settings["promotion_threshold"]:
                self._promote_experimental_component(prompt_metadata['experiment'])
        
        # Periodic cleanup and saving
        if len(self.experiments) % 10 == 0:
            debug_info("🧹 Performing periodic cleanup and save")
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