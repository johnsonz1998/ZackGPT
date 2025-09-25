#!/usr/bin/env python3
"""
Performance Toggle Service for ZackGPT

Controls which features are enabled to optimize performance during development.
Each toggle can be controlled individually for fine-grained performance tuning.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class PerformanceToggles:
    """Individual toggles for performance-intensive features"""
    
    # Background Tasks
    enable_periodic_cleanup: bool = False
    enable_memory_analytics: bool = False
    enable_auto_backup: bool = False
    
    # Database & Logging
    enable_debug_analytics: bool = False
    enable_mongodb_logging: bool = False
    enable_detailed_metrics: bool = False
    
    # Memory Management
    enable_memory_graph_caching: bool = True
    enable_conversation_caching: bool = True
    enable_thread_preloading: bool = False
    
    # Network & External Services
    enable_websocket_keepalive: bool = False
    enable_external_search: bool = True
    enable_perplexity_integration: bool = True
    
    # Development Features
    enable_hot_reload: bool = True
    enable_debug_endpoints: bool = True
    enable_cors_all_origins: bool = True
    
    # Production Optimizations
    enable_response_compression: bool = False
    enable_request_batching: bool = False
    enable_connection_pooling: bool = False


class PerformanceToggleService:
    """Service to manage performance toggles based on environment"""
    
    def __init__(self):
        self.mode = os.getenv("ZACKGPT_MODE", "development").lower()
        self.toggles = self._load_toggles()
        self._log_configuration()
    
    def _load_toggles(self) -> PerformanceToggles:
        """Load toggles based on environment and overrides"""
        
        if self.mode == "production":
            return self._production_config()
        elif self.mode == "staging":
            return self._staging_config()
        elif self.mode == "testing":
            return self._testing_config()
        elif self.mode == "lightweight":
            return self._lightweight_config()
        else:  # development
            return self._development_config()
    
    def _development_config(self) -> PerformanceToggles:
        """Optimized for fast development - minimal background tasks"""
        return PerformanceToggles(
            # Background Tasks - DISABLED for speed
            enable_periodic_cleanup=self._get_env_bool("ENABLE_PERIODIC_CLEANUP", False),
            enable_memory_analytics=self._get_env_bool("ENABLE_MEMORY_ANALYTICS", False),
            enable_auto_backup=self._get_env_bool("ENABLE_AUTO_BACKUP", False),
            
            # Database & Logging - Minimal
            enable_debug_analytics=self._get_env_bool("ENABLE_DEBUG_ANALYTICS", False),
            enable_mongodb_logging=self._get_env_bool("ENABLE_MONGODB_LOGGING", False),
            enable_detailed_metrics=self._get_env_bool("ENABLE_DETAILED_METRICS", False),
            
            # Memory Management - Basic caching only
            enable_memory_graph_caching=self._get_env_bool("ENABLE_MEMORY_CACHING", True),
            enable_conversation_caching=self._get_env_bool("ENABLE_CONVERSATION_CACHING", True),
            enable_thread_preloading=self._get_env_bool("ENABLE_THREAD_PRELOADING", False),
            
            # Network & External Services - Essential only
            enable_websocket_keepalive=self._get_env_bool("ENABLE_WEBSOCKET_KEEPALIVE", False),
            enable_external_search=self._get_env_bool("ENABLE_EXTERNAL_SEARCH", True),
            enable_perplexity_integration=self._get_env_bool("ENABLE_PERPLEXITY", True),
            
            # Development Features - ENABLED
            enable_hot_reload=self._get_env_bool("ENABLE_HOT_RELOAD", True),
            enable_debug_endpoints=self._get_env_bool("ENABLE_DEBUG_ENDPOINTS", True),
            enable_cors_all_origins=self._get_env_bool("ENABLE_CORS_ALL", True),
            
            # Production Optimizations - DISABLED
            enable_response_compression=self._get_env_bool("ENABLE_COMPRESSION", False),
            enable_request_batching=self._get_env_bool("ENABLE_BATCHING", False),
            enable_connection_pooling=self._get_env_bool("ENABLE_CONNECTION_POOLING", False),
        )
    
    def _production_config(self) -> PerformanceToggles:
        """Optimized for production - all optimizations enabled"""
        return PerformanceToggles(
            # Background Tasks - ENABLED
            enable_periodic_cleanup=True,
            enable_memory_analytics=True,
            enable_auto_backup=True,
            
            # Database & Logging - Full logging
            enable_debug_analytics=True,
            enable_mongodb_logging=True,
            enable_detailed_metrics=True,
            
            # Memory Management - Full optimization
            enable_memory_graph_caching=True,
            enable_conversation_caching=True,
            enable_thread_preloading=True,
            
            # Network & External Services - All enabled
            enable_websocket_keepalive=True,
            enable_external_search=True,
            enable_perplexity_integration=True,
            
            # Development Features - DISABLED
            enable_hot_reload=False,
            enable_debug_endpoints=False,
            enable_cors_all_origins=False,
            
            # Production Optimizations - ENABLED
            enable_response_compression=True,
            enable_request_batching=True,
            enable_connection_pooling=True,
        )
    
    def _staging_config(self) -> PerformanceToggles:
        """Balanced config for staging environment"""
        return PerformanceToggles(
            # Background Tasks - Limited
            enable_periodic_cleanup=True,
            enable_memory_analytics=False,
            enable_auto_backup=False,
            
            # Database & Logging - Moderate
            enable_debug_analytics=True,
            enable_mongodb_logging=False,
            enable_detailed_metrics=True,
            
            # Memory Management - Optimized
            enable_memory_graph_caching=True,
            enable_conversation_caching=True,
            enable_thread_preloading=False,
            
            # Network & External Services - Enabled
            enable_websocket_keepalive=True,
            enable_external_search=True,
            enable_perplexity_integration=True,
            
            # Development Features - Limited
            enable_hot_reload=False,
            enable_debug_endpoints=True,
            enable_cors_all_origins=True,
            
            # Production Optimizations - Some enabled
            enable_response_compression=True,
            enable_request_batching=False,
            enable_connection_pooling=True,
        )
    
    def _testing_config(self) -> PerformanceToggles:
        """Minimal config for testing - fastest possible"""
        return PerformanceToggles(
            # Background Tasks - ALL DISABLED
            enable_periodic_cleanup=False,
            enable_memory_analytics=False,
            enable_auto_backup=False,
            
            # Database & Logging - Minimal
            enable_debug_analytics=False,
            enable_mongodb_logging=False,
            enable_detailed_metrics=False,
            
            # Memory Management - Basic only
            enable_memory_graph_caching=False,
            enable_conversation_caching=False,
            enable_thread_preloading=False,
            
            # Network & External Services - Minimal
            enable_websocket_keepalive=False,
            enable_external_search=False,
            enable_perplexity_integration=False,
            
            # Development Features - Testing only
            enable_hot_reload=False,
            enable_debug_endpoints=True,
            enable_cors_all_origins=True,
            
            # Production Optimizations - DISABLED
            enable_response_compression=False,
            enable_request_batching=False,
            enable_connection_pooling=False,
        )
    
    def _lightweight_config(self) -> PerformanceToggles:
        """Ultra-minimal config for resource-constrained environments"""
        return PerformanceToggles(
            # Background Tasks - ALL DISABLED
            enable_periodic_cleanup=False,
            enable_memory_analytics=False,
            enable_auto_backup=False,
            
            # Database & Logging - DISABLED
            enable_debug_analytics=False,
            enable_mongodb_logging=False,
            enable_detailed_metrics=False,
            
            # Memory Management - DISABLED
            enable_memory_graph_caching=False,
            enable_conversation_caching=False,
            enable_thread_preloading=False,
            
            # Network & External Services - DISABLED
            enable_websocket_keepalive=False,
            enable_external_search=False,
            enable_perplexity_integration=False,
            
            # Development Features - MINIMAL
            enable_hot_reload=False,
            enable_debug_endpoints=False,
            enable_cors_all_origins=True,
            
            # Production Optimizations - DISABLED
            enable_response_compression=False,
            enable_request_batching=False,
            enable_connection_pooling=False,
        )
    
    def _get_env_bool(self, key: str, default: bool) -> bool:
        """Get boolean value from environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")
    
    def _log_configuration(self):
        """Log the current configuration"""
        print(f"🔧 ZackGPT Performance Mode: {self.mode.upper()}")
        print("📊 Feature Toggles:")
        
        # Background Tasks
        print("  Background Tasks:")
        print(f"    - Periodic Cleanup: {'✅' if self.toggles.enable_periodic_cleanup else '❌'}")
        print(f"    - Memory Analytics: {'✅' if self.toggles.enable_memory_analytics else '❌'}")
        print(f"    - Auto Backup: {'✅' if self.toggles.enable_auto_backup else '❌'}")
        
        # Memory Management
        print("  Memory Management:")
        print(f"    - Graph Caching: {'✅' if self.toggles.enable_memory_graph_caching else '❌'}")
        print(f"    - Conversation Caching: {'✅' if self.toggles.enable_conversation_caching else '❌'}")
        print(f"    - Thread Preloading: {'✅' if self.toggles.enable_thread_preloading else '❌'}")
        
        # External Services
        print("  External Services:")
        print(f"    - External Search: {'✅' if self.toggles.enable_external_search else '❌'}")
        print(f"    - Perplexity Integration: {'✅' if self.toggles.enable_perplexity_integration else '❌'}")
        
        # Development Features
        if self.mode == "development":
            print("  Development:")
            print(f"    - Hot Reload: {'✅' if self.toggles.enable_hot_reload else '❌'}")
            print(f"    - Debug Endpoints: {'✅' if self.toggles.enable_debug_endpoints else '❌'}")
    
    def is_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled"""
        return getattr(self.toggles, f"enable_{feature}", False)
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary for API responses"""
        return {
            "mode": self.mode,
            "toggles": {
                field.name: getattr(self.toggles, field.name)
                for field in self.toggles.__dataclass_fields__.values()
            }
        }


# Global instance
performance_toggles = PerformanceToggleService()


def should_enable(feature: str) -> bool:
    """Convenience function to check if a feature should be enabled"""
    return performance_toggles.is_enabled(feature)


def get_performance_config() -> PerformanceToggles:
    """Get the current performance configuration"""
    return performance_toggles.toggles


def reload_config():
    """Reload configuration (useful for development)"""
    global performance_toggles
    performance_toggles = PerformanceToggleService()


if __name__ == "__main__":
    # Demo the toggle service
    print("🎛️ ZackGPT Performance Toggle Service Demo")
    print("=" * 50)
    
    # Test different modes
    for mode in ["development", "staging", "production", "testing"]:
        os.environ["ZACKGPT_MODE"] = mode
        service = PerformanceToggleService()
        print(f"\n{mode.upper()} MODE CONFIGURATION:")
        print("-" * 30)
        service._log_configuration() 