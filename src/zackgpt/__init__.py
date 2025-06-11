"""
ZackGPT Main Package
Advanced AI Assistant with Evolutionary Prompt Learning
"""

__version__ = "1.0.0"
__author__ = "ZackGPT Team"

# Core imports for easy access
from .core.core_assistant import CoreAssistant
from .core.logger import debug_info, debug_success, debug_error, debug_log

__all__ = [
    'CoreAssistant',
    'debug_info', 
    'debug_success',
    'debug_error',
    'debug_log'
] 