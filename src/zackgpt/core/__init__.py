"""
ZackGPT Core Package
Core logic, AI assistant, and utilities
"""

from .core_assistant import CoreAssistant
from .logger import debug_info, debug_success, debug_error, debug_log
from .memory_db import MemoryDatabase
from .web_search import search_web, WEB_SEARCH_ENABLED
from .prompt_builder import EvolutionaryPromptBuilder

__all__ = [
    'CoreAssistant',
    'MemoryDatabase', 
    'EvolutionaryPromptBuilder',
    'debug_info',
    'debug_success', 
    'debug_error',
    'debug_log',
    'search_web',
    'WEB_SEARCH_ENABLED'
] 