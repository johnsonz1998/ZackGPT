import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from openai import OpenAI
import config.config as config
from .logger import debug_log, debug_info, debug_error, debug_success

class PromptEnhancerConfig:
    """Configuration for prompt enhancement system."""
    def __init__(self):
        # Model selection
        self.use_cloud_generation = getattr(config, "PROMPT_ENHANCER_USE_CLOUD", True)
        self.use_local_fallback = getattr(config, "PROMPT_ENHANCER_USE_LOCAL", True)
        self.cloud_model = getattr(config, "PROMPT_ENHANCER_MODEL", "gpt-4-turbo")
        
        # Generation rates (don't generate constantly - too expensive!)
        self.generation_rate = getattr(config, "PROMPT_ENHANCER_GENERATION_RATE", 0.3)  # 30% of experiments
        
        # Logging
        self.debug_mode = getattr(config, "PROMPT_ENHANCER_DEBUG", config.DEBUG_MODE)
        
        debug_info("Prompt enhancer config loaded", {
            "cloud_generation": self.use_cloud_generation,
            "local_fallback": self.use_local_fallback,
            "generation_rate": self.generation_rate,
            "cloud_model": self.cloud_model
        })

class SimplePromptScorer:
    """Simple, fast, heuristic-based scoring that we understand and can debug."""
    
    def __init__(self):
        # These are simple rules we can understand and adjust
        self.uncertainty_phrases = [
            "i don't know", "i'm not sure", "i can't help", "unclear", "uncertain"
        ]
        self.apology_starts = ["sorry", "i apologize", "unfortunately"]
        self.good_indicators = [
            "here's how", "you can", "try this", "the solution", "here are", "first", "next"
        ]
        self.bad_indicators = [
            "i cannot", "i'm unable", "not possible", "can't do that"
        ]
    
    def assess_response(self, response: str, user_input: str, context: Dict = None) -> Dict:
        """Simple, debuggable assessment that doesn't rely on AI judging AI."""
        response_lower = response.lower()
        user_lower = user_input.lower()
        
        # Start with neutral score
        score = 0.5
        issues = []
        reasoning = []
        
        # Penalize uncertainty (but not always bad - sometimes "I don't know" is honest!)
        uncertainty_count = sum(1 for phrase in self.uncertainty_phrases if phrase in response_lower)
        if uncertainty_count > 0:
            score -= uncertainty_count * 0.15
            issues.append(f"uncertainty_phrases_{uncertainty_count}")
            reasoning.append(f"Found {uncertainty_count} uncertainty phrases")
        
        # Penalize excessive apologies
        if any(response_lower.startswith(apology) for apology in self.apology_starts):
            score -= 0.1
            issues.append("apologetic_start")
            reasoning.append("Response starts with apology")
        
        # Reward helpful indicators
        helpful_count = sum(1 for indicator in self.good_indicators if indicator in response_lower)
        if helpful_count > 0:
            score += helpful_count * 0.1
            reasoning.append(f"Found {helpful_count} helpful indicators")
        
        # Penalize outright refusals
        refusal_count = sum(1 for indicator in self.bad_indicators if indicator in response_lower)
        if refusal_count > 0:
            score -= refusal_count * 0.1
            issues.append(f"refusal_phrases_{refusal_count}")
            reasoning.append(f"Found {refusal_count} refusal phrases")
        
        # Length heuristics
        if len(response) < 20:
            score -= 0.2
            issues.append("too_short")
            reasoning.append("Response very short")
        elif len(response) > 100:
            score += 0.1
            reasoning.append("Substantial response length")
        
        # Question matching - did we answer what they asked?
        if "?" in user_input and len(response) > 50:
            score += 0.1
            reasoning.append("Substantial answer to question")
        
        # Code/technical response bonuses
        if any(word in user_lower for word in ["code", "function", "error", "debug", "implement"]):
            if any(word in response_lower for word in ["here's", "try", "you can", "solution"]):
                score += 0.15
                reasoning.append("Technical question with actionable response")
        
        # Clamp score
        score = max(0.0, min(1.0, score))
        
        result = {
            "overall_score": score,
            "success": score > 0.6,
            "issues": issues,
            "reasoning": " | ".join(reasoning),
            "assessment_type": "simple_heuristic",
            "transparency": {
                "uncertainty_count": uncertainty_count,
                "helpful_count": helpful_count,
                "refusal_count": refusal_count,
                "response_length": len(response),
                "question_detected": "?" in user_input,
                "technical_context": any(word in user_lower for word in ["code", "function", "error", "debug"])
            }
        }
        
        if getattr(config, "PROMPT_ENHANCER_DEBUG", False):
            debug_log("Simple prompt scoring", result)
        
        return result

class CloudPromptGenerator:
    """Cloud-based component generation when we need new ideas."""
    
    def __init__(self, enhancer_config: PromptEnhancerConfig):
        self.config = enhancer_config
        try:
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        except:
            self.client = OpenAI()  # Use default API key
        
    def generate_component(self, component_type: str, context: Dict, successful_examples: List[str] = None) -> str:
        """Generate new prompt components using cloud AI - this IS useful."""
        
        if not self.config.use_cloud_generation:
            return self._fallback_component(component_type, context)
        
        debug_info("Generating component with cloud AI", {
            "type": component_type,
            "context_type": context.get("conversation_type", "unknown"),
            "examples_count": len(successful_examples or [])
        })
        
        examples_text = ""
        if successful_examples:
            examples_text = "\nSuccessful examples:\n" + "\n".join(f"- {ex}" for ex in successful_examples[:3])
        
        # Context-aware generation
        context_desc = f"Conversation type: {context.get('conversation_type', 'general')}"
        if context.get('user_expertise'):
            context_desc += f", User expertise: {context['user_expertise']}"
        if context.get('recent_errors', 0) > 0:
            context_desc += f", Recent errors: {context['recent_errors']}"
        
        prompt = f"""You are helping improve an AI assistant's prompts for Zack.

Create a {component_type} component that will improve responses.

{context_desc}
{examples_text}

Zack's preferences:
- Witty and sarcastic but helpful
- Efficient, no fluff
- Technically competent
- Direct and actionable

Generate ONE concise sentence (max 15 words) that improves {component_type}.
Examples:
- personality: "Be direct and witty while providing actionable solutions."
- memory_guidelines: "Save technical details and user preferences specifically."
- task_instructions: "For technical questions, provide code examples and step-by-step solutions."

Component:"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.cloud_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=50,
                timeout=15
            )
            
            component = response.choices[0].message.content.strip()
            # Clean up the response
            component = component.replace('"', '').replace('Component:', '').strip()
            
            debug_success("Cloud component generated", {
                "type": component_type,
                "generated": component[:60] + "..." if len(component) > 60 else component,
                "context": context.get("conversation_type", "general")
            })
            
            return component
            
        except Exception as e:
            debug_error("Cloud component generation failed", e)
            return self._fallback_component(component_type, context)
    
    def _fallback_component(self, component_type: str, context: Dict) -> str:
        """Context-aware fallback components."""
        conversation_type = context.get("conversation_type", "general")
        user_expertise = context.get("user_expertise", "medium")
        
        fallbacks = {
            'personality': {
                'technical': "Be precise and efficient with technical solutions.",
                'troubleshooting': "Focus on quick problem resolution with clear steps.",
                'general': "Be witty and direct while staying helpful."
            },
            'memory_guidelines': {
                'technical': "Save code snippets, error solutions, and configuration details.",
                'general': "Save user preferences and important factual information."
            },
            'task_instructions': {
                'technical': "Provide code examples and implementation details.",
                'troubleshooting': "Break down problems into clear diagnostic steps.",
                'general': "Focus on actionable, practical solutions."
            },
            'context_framers': {
                'high': "Assume technical competence, skip basic explanations.",
                'medium': "Balance detail with clarity for moderate expertise.",
                'beginner': "Provide more context and explanation for complex topics."
            },
            'output_formatters': {
                'technical': "Use code blocks and structured examples.",
                'general': "Keep responses concise with clear action items."
            }
        }
        
        type_fallbacks = fallbacks.get(component_type, {})
        
        # Try conversation type first, then user expertise, then default
        component = (type_fallbacks.get(conversation_type) or 
                    type_fallbacks.get(user_expertise) or 
                    type_fallbacks.get('general', 'Improve response quality and relevance.'))
        
        debug_log("Generated fallback component", {
            "type": component_type,
            "context": conversation_type,
            "expertise": user_expertise,
            "component": component
        })
        
        return component

class LocalPromptHelper:
    """Local model assistance if available."""
    
    def __init__(self, enhancer_config: PromptEnhancerConfig):
        self.config = enhancer_config
        self.available = False
        
        if enhancer_config.use_local_fallback:
            try:
                from .local_llm import run_local_model
                self.run_local_model = run_local_model
                self.available = True
                debug_info("Local model helper available")
            except ImportError:
                debug_log("Local model not available")
    
    def quick_quality_check(self, response: str, user_input: str) -> bool:
        """Quick local quality check if available."""
        if not self.available:
            return True  # Default optimistic
        
        # Keep the prompt simple for local models
        prompt = f"""Rate this assistant response as GOOD or BAD:

User asked: {user_input[:100]}
Assistant replied: {response[:200]}

GOOD = helpful, clear, answers the question
BAD = vague, unhelpful, says "I don't know"

Rating:"""

        try:
            result = self.run_local_model(prompt).strip().upper()
            assessment = "GOOD" in result
            
            if self.config.debug_mode:
                debug_log("Local quality check", {
                    "result": result[:20],
                    "assessment": assessment,
                    "response_preview": response[:50] + "..."
                })
            
            return assessment
        except Exception as e:
            debug_error("Local assessment failed", e)
            return True

class HybridPromptEnhancer:
    """Practical prompt enhancement focused on what actually works."""
    
    def __init__(self):
        self.config = PromptEnhancerConfig()
        self.scorer = SimplePromptScorer()
        self.generator = CloudPromptGenerator(self.config)
        self.local_helper = LocalPromptHelper(self.config)
        
        # Statistics for debugging
        self.stats = {
            "assessments_performed": 0,
            "components_generated": 0,
            "cloud_generations": 0,
            "local_checks": 0,
            "fallback_generations": 0
        }
        
        debug_success("Hybrid prompt enhancer initialized", {
            "cloud_generation_enabled": self.config.use_cloud_generation,
            "local_helper_available": self.local_helper.available,
            "generation_rate": self.config.generation_rate
        })
    
    def assess_response_quality(self, response: str, user_input: str, context: Dict = None) -> Dict:
        """Assess response quality using simple, understandable heuristics."""
        
        debug_info("🔍 Starting response quality assessment", {
            "response_length": len(response),
            "user_input_length": len(user_input),
            "has_context": context is not None,
            "assessment_method": "simple_heuristic"
        })
        
        # Always do simple scoring (fast and debuggable)
        assessment = self.scorer.assess_response(response, user_input, context)
        self.stats["assessments_performed"] += 1
        
        debug_info("📊 Heuristic assessment complete", {
            "overall_score": f"{assessment['overall_score']:.3f}",
            "success": assessment['success'],
            "issues_found": assessment.get('issues', []),
            "reasoning": assessment.get('reasoning', 'No reasoning'),
            "transparency_details": assessment.get('transparency', {})
        })
        
        # Occasionally validate with local model
        if self.local_helper.available and random.random() < 0.1:  # 10% of responses
            debug_info("🤖 Performing local model validation (10% chance)")
            local_check = self.local_helper.quick_quality_check(response, user_input)
            assessment["local_validation"] = local_check
            self.stats["local_checks"] += 1
            
            # Log disagreements for debugging
            simple_says_good = assessment["success"]
            if simple_says_good != local_check and self.config.debug_mode:
                debug_log("⚠️ Assessment disagreement detected", {
                    "heuristic_says": "good" if simple_says_good else "bad",
                    "local_model_says": "good" if local_check else "bad", 
                    "heuristic_score": assessment["overall_score"],
                    "response_preview": response[:100] + "..." if len(response) > 100 else response,
                    "disagreement_analysis": "Local model and heuristics have different opinions"
                })
            else:
                debug_success("✅ Assessment agreement", {
                    "both_agree": "good" if simple_says_good else "bad",
                    "confidence": "high"
                })
        
        debug_success("🎯 Quality assessment complete", {
            "final_score": f"{assessment['overall_score']:.3f}",
            "success_rating": assessment['success'],
            "had_local_validation": "local_validation" in assessment,
            "total_assessments_performed": self.stats["assessments_performed"]
        })
        
        return assessment
    
    def generate_enhanced_component(self, component_type: str, context: Dict, successful_examples: List[str] = None) -> str:
        """Generate new components using the best available method."""
        
        self.stats["components_generated"] += 1
        
        # Use cloud generation for novel components when we have context
        should_use_cloud = (
            self.config.use_cloud_generation and 
            random.random() < self.config.generation_rate and
            context.get("conversation_type") != "general"  # Save money on generic contexts
        )
        
        if should_use_cloud:
            self.stats["cloud_generations"] += 1
            return self.generator.generate_component(component_type, context, successful_examples)
        else:
            # Use smart fallback generation
            self.stats["fallback_generations"] += 1
            return self.generator._fallback_component(component_type, context)
    
    def get_enhancement_stats(self) -> Dict:
        """Get detailed stats for debugging and monitoring."""
        return {
            **self.stats,
            "local_helper_available": self.local_helper.available,
            "config": {
                "cloud_generation_enabled": self.config.use_cloud_generation,
                "generation_rate": self.config.generation_rate,
                "cloud_model": self.config.cloud_model,
                "debug_mode": self.config.debug_mode
            },
            "efficiency": {
                "cloud_usage_rate": self.stats["cloud_generations"] / max(1, self.stats["components_generated"]),
                "local_validation_rate": self.stats["local_checks"] / max(1, self.stats["assessments_performed"])
            }
        } 