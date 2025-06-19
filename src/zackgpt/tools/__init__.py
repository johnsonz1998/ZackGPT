"""
ZackGPT Tools Package
External service integrations and utility tools
"""

from .web_search import search_web, WEB_SEARCH_ENABLED
from .perplexity_search import search_with_perplexity

__all__ = [
    'search_web',
    'WEB_SEARCH_ENABLED', 
    'search_with_perplexity'
] 