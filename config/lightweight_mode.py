#!/usr/bin/env python3
"""
Lightweight Mode Configuration for Resource-Constrained Servers

This module provides an ultra-minimal configuration that disables all
non-essential features to run ZackGPT on resource-constrained environments.
"""

import os
from typing import Dict, Any

class LightweightConfig:
    """Ultra-minimal configuration for resource-constrained environments"""
    
    def __init__(self):
        self.enabled = os.getenv("ZACKGPT_LIGHTWEIGHT", "false").lower() == "true"
        
    def apply_lightweight_settings(self) -> Dict[str, Any]:
        """Apply ultra-lightweight settings"""
        if not self.enabled:
            return {}
            
        print("🔧 LIGHTWEIGHT MODE ENABLED - Maximum resource optimization")
        
        # Disable ALL non-essential features
        lightweight_settings = {
            # Background Tasks - ALL DISABLED
            "ENABLE_PERIODIC_CLEANUP": "false",
            "ENABLE_MEMORY_ANALYTICS": "false", 
            "ENABLE_AUTO_BACKUP": "false",
            
            # Database & Logging - MINIMAL
            "ENABLE_DEBUG_ANALYTICS": "false",
            "ENABLE_MONGODB_LOGGING": "false",
            "ENABLE_DETAILED_METRICS": "false",
            
            # Memory Management - BASIC ONLY
            "ENABLE_MEMORY_CACHING": "false",
            "ENABLE_CONVERSATION_CACHING": "false",
            "ENABLE_THREAD_PRELOADING": "false",
            
            # Network - ESSENTIAL ONLY
            "ENABLE_WEBSOCKET_KEEPALIVE": "false",
            "ENABLE_EXTERNAL_SEARCH": "false",  # Disable web search to save resources
            "ENABLE_PERPLEXITY_INTEGRATION": "false",
            
            # AI Features - SIMPLIFIED
            "ENABLE_AI_MEMORY_EXTRACTION": "false",  # Use simple patterns only
            "ENABLE_PROMPT_EVOLUTION": "false",
            "ENABLE_RESPONSE_QUALITY_ASSESSMENT": "false",
            
            # Performance - AGGRESSIVE LIMITS
            "MAX_CONVERSATION_HISTORY": "3",  # Keep only 3 messages in memory
            "MAX_MEMORY_RETRIEVAL": "5",     # Retrieve max 5 memories
            "MAX_TOKENS": "1000",            # Reduce token limit
            "THREAD_POOL_SIZE": "1",         # Single thread only
            
            # Development - MINIMAL
            "ENABLE_HOT_RELOAD": "false",
            "ENABLE_DEBUG_ENDPOINTS": "false",
            "ENABLE_CORS_ALL": "true",       # Keep for frontend
            
            # Set performance mode
            "ZACKGPT_MODE": "lightweight"
        }
        
        # Apply settings to environment
        for key, value in lightweight_settings.items():
            os.environ[key] = value
            
        print("📊 Lightweight settings applied:")
        print("  🚫 All background tasks disabled")
        print("  🚫 Web search disabled") 
        print("  🚫 AI memory extraction disabled")
        print("  🚫 Prompt evolution disabled")
        print("  ⚡ Max 3 conversation messages")
        print("  ⚡ Max 5 memory retrievals")
        print("  ⚡ Single thread pool")
        print("  💾 Reduced token limits")
        
        return lightweight_settings

# Global instance
lightweight_config = LightweightConfig()

def enable_lightweight_mode():
    """Enable lightweight mode programmatically"""
    os.environ["ZACKGPT_LIGHTWEIGHT"] = "true" 
    return lightweight_config.apply_lightweight_settings()

def is_lightweight_mode() -> bool:
    """Check if lightweight mode is enabled"""
    return lightweight_config.enabled

if __name__ == "__main__":
    # Test lightweight mode
    print("🧪 Testing Lightweight Mode Configuration")
    print("=" * 50)
    
    # Enable and show settings
    settings = enable_lightweight_mode()
    
    print(f"\n✅ Lightweight mode configured with {len(settings)} optimizations")
    print("🚀 Ready for resource-constrained deployment!") 