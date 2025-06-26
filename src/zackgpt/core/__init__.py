"""
ZackGPT Core Package
Core AI logic and prompt management
"""

from .core_assistant import CoreAssistant
# Lazy imports - don't load heavy modules during import
# from .logger import debug_info, debug_success, debug_error, debug_log  # Import when needed
# from .prompt_builder import EvolutionaryPromptBuilder  # Import when needed
# from .query_utils import ask_gpt  # Import when needed

# Import from new locations with error handling
try:
    from ..data import get_database
    from ..data import Database as ZackGPTDatabase  # Alias for compatibility
    data_available = True
except ImportError as e:
    print(f"Warning: Could not import data components: {e}")
    get_database = None
    ZackGPTDatabase = None
    data_available = False

try:
    from ..tools import search_web, WEB_SEARCH_ENABLED
    tools_available = True
except ImportError as e:
    print(f"Warning: Could not import tools: {e}")
    search_web = None
    WEB_SEARCH_ENABLED = False
    tools_available = False

__all__ = [
    'CoreAssistant',
    # Heavy modules exported lazily
    # 'EvolutionaryPromptBuilder',
    # 'debug_info',
    # 'debug_success', 
    # 'debug_error',
    # 'debug_log',
    # 'ask_gpt',
]

# Add data components if available
if data_available:
    __all__.extend(['get_database', 'ZackGPTDatabase'])

# Add tools if available  
if tools_available:
    __all__.extend(['search_web', 'WEB_SEARCH_ENABLED']) 