"""
ZackGPT Core Package
Core AI logic and prompt management
"""

from .core_assistant import CoreAssistant
from .logger import debug_info, debug_success, debug_error, debug_log
from .prompt_builder import EvolutionaryPromptBuilder
from .query_utils import ask_gpt

# Import from new locations
from ..data import get_database, ZackGPTDatabase
from ..tools import search_web, WEB_SEARCH_ENABLED

__all__ = [
    'CoreAssistant',
    'EvolutionaryPromptBuilder',
    'debug_info',
    'debug_success', 
    'debug_error',
    'debug_log',
    'ask_gpt',
    'get_database',
    'ZackGPTDatabase',
    'search_web',
    'WEB_SEARCH_ENABLED'
] 