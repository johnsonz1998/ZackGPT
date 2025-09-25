#!/usr/bin/env python3
"""
Dynamic Memory Configuration Manager for ZackGPT

Provides easy switching between memory profiles and runtime configuration.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from . import config

class DynamicMemoryConfig:
    """Configuration manager for dynamic memory system."""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.profiles_dir = self.config_dir / "memory_profiles"
        self.current_profile = None
        self.original_values = {}
        
    def list_profiles(self) -> list:
        """List available memory profiles."""
        if not self.profiles_dir.exists():
            return []
        return [f.stem for f in self.profiles_dir.glob("*.json")]
    
    def load_profile(self, profile_name: str) -> bool:
        """Load a memory configuration profile."""
        profile_path = self.profiles_dir / f"{profile_name}.json"
        
        if not profile_path.exists():
            print(f"❌ Profile '{profile_name}' not found")
            return False
        
        try:
            with open(profile_path, 'r') as f:
                profile_data = json.load(f)
            
            # Backup original values
            if not self.original_values:
                self._backup_original_values(profile_data)
            
            # Apply profile settings
            applied_count = 0
            for key, value in profile_data.items():
                if key.startswith('profile_') or key == 'description':
                    continue  # Skip metadata
                
                if hasattr(config, key):
                    setattr(config, key, value)
                    applied_count += 1
            
            self.current_profile = profile_name
            
            print(f"✅ Loaded profile '{profile_name}' ({applied_count} settings applied)")
            if 'description' in profile_data:
                print(f"   {profile_data['description']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading profile '{profile_name}': {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to original defaults."""
        if not self.original_values:
            print("ℹ️ No original values to restore")
            return False
        
        try:
            applied_count = 0
            for key, value in self.original_values.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    applied_count += 1
            
            self.current_profile = None
            
            print(f"✅ Reset to defaults ({applied_count} settings restored)")
            return True
            
        except Exception as e:
            print(f"❌ Error resetting to defaults: {e}")
            return False
    
    def get_current_status(self) -> Dict:
        """Get current configuration status."""
        return {
            'current_profile': self.current_profile,
            'available_profiles': self.list_profiles(),
            'system_mode': getattr(config, 'MEMORY_SYSTEM_MODE', 'unknown'),
            'max_memories': getattr(config, 'DYNAMIC_MAX_MEMORIES', 'unknown'),
            'max_time_ms': getattr(config, 'DYNAMIC_MAX_PROCESSING_TIME_MS', 'unknown'),
            'has_backups': bool(self.original_values)
        }
    
    def create_profile(self, profile_name: str, settings: Dict, description: str = "") -> bool:
        """Create a new memory profile."""
        profile_path = self.profiles_dir / f"{profile_name}.json"
        
        try:
            # Ensure directory exists
            self.profiles_dir.mkdir(exist_ok=True)
            
            # Create profile data
            profile_data = {
                'profile_name': profile_name,
                'description': description,
                **settings
            }
            
            # Save to file
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            print(f"✅ Created profile '{profile_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error creating profile '{profile_name}': {e}")
            return False
    
    def _backup_original_values(self, profile_data: Dict):
        """Backup original configuration values."""
        for key in profile_data.keys():
            if key.startswith('profile_') or key == 'description':
                continue
            if hasattr(config, key):
                self.original_values[key] = getattr(config, key)

# Global instance
_memory_config = None

def get_memory_config() -> DynamicMemoryConfig:
    """Get the global memory configuration manager."""
    global _memory_config
    if _memory_config is None:
        _memory_config = DynamicMemoryConfig()
    return _memory_config

# Convenience functions
def load_memory_profile(profile_name: str) -> bool:
    """Load a memory profile."""
    return get_memory_config().load_profile(profile_name)

def list_memory_profiles() -> list:
    """List available memory profiles."""
    return get_memory_config().list_profiles()

def reset_memory_config() -> bool:
    """Reset memory config to defaults."""
    return get_memory_config().reset_to_defaults()

def get_memory_status() -> Dict:
    """Get current memory configuration status."""
    return get_memory_config().get_current_status()

def create_memory_profile(name: str, settings: Dict, description: str = "") -> bool:
    """Create a new memory profile."""
    return get_memory_config().create_profile(name, settings, description)

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Dynamic Memory Configuration Manager")
    parser.add_argument("--list", action="store_true", help="List available profiles")
    parser.add_argument("--load", type=str, help="Load a memory profile")
    parser.add_argument("--reset", action="store_true", help="Reset to defaults")
    parser.add_argument("--status", action="store_true", help="Show current status")
    
    args = parser.parse_args()
    
    manager = get_memory_config()
    
    if args.list:
        profiles = manager.list_profiles()
        print(f"Available profiles: {profiles}")
        
    elif args.load:
        manager.load_profile(args.load)
        
    elif args.reset:
        manager.reset_to_defaults()
        
    elif args.status:
        status = manager.get_current_status()
        print("Memory Configuration Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    
    else:
        print("Use --help for usage information") 