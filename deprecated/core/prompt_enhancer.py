"""
Simple Prompt Enhancement - No Cloud Generation Bullshit
Just basic local prompt assessment without over-engineering.
"""

from typing import Dict
from ..utils.logger import debug_info

class SimplePromptScorer:
    """SIMPLIFIED: Basic prompt scoring without cloud complexity."""
    
    def __init__(self):
        debug_info("Simple prompt scorer initialized")
    
    def assess_response(self, response: str, user_input: str, context: Dict = None) -> Dict:
        """Simple response quality assessment using basic heuristics."""
        
        if not response or not user_input:
            return {
                "quality_score": 0.0,
                "assessment": "invalid_input",
                "reasoning": "Empty response or input"
            }
        
        # Basic quality indicators
        score = 0.5  # Start neutral
        reasons = []
        
        # Length check
        if len(response) < 20:
            score -= 0.2
            reasons.append("too_short")
        elif len(response) > 1000:
            score += 0.1
            reasons.append("comprehensive")
        
        # Error indicators
        if any(phrase in response.lower() for phrase in ["error", "apologize", "sorry"]):
            score -= 0.3
            reasons.append("contains_error")
        
        # Personal info check (for memory queries)
        if any(word in user_input.lower() for word in ["remember", "know", "about me"]):
            if any(word in response.lower() for word in ["golden", "british", "interest"]):
                score += 0.3
                reasons.append("includes_personal_info")
            else:
                score -= 0.2
                reasons.append("missing_personal_info")
        
        # Clamp score
        score = max(0.0, min(1.0, score))
        
        return {
            "quality_score": score,
            "assessment": "good" if score > 0.7 else "poor" if score < 0.3 else "okay",
            "reasoning": " + ".join(reasons) if reasons else "basic_assessment"
        }

# DELETED ALL THE CLOUD GENERATION BULLSHIT:
# - CloudPromptGenerator (200+ lines of OpenAI API complexity)
# - HybridPromptEnhancer (150+ lines of over-engineering)
# - PromptEnhancerConfig (unnecessary configuration)