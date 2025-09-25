"""
ZackGPT Web Search Module
Provides internet search capabilities with multiple search engines and fallbacks.
"""

import json
import requests
import time
from typing import List, Dict, Optional, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re

from config.config import (
    WEB_SEARCH_ENABLED, SERPAPI_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID,
    WEB_SEARCH_MAX_RESULTS, WEB_SEARCH_TIMEOUT, USER_AGENT, DEBUG_MODE
)
from ..utils.logger import debug_info, debug_error, debug_warning


class WebSearchError(Exception):
    """Custom exception for web search errors."""
    pass


class WebSearchTool:
    """
    Comprehensive web search tool with multiple search engine support.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.session.timeout = WEB_SEARCH_TIMEOUT
        
    def search(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Search the web using available search engines.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, url, and source
        """
        if not WEB_SEARCH_ENABLED:
            raise WebSearchError("Web search is disabled in configuration")
            
        max_results = max_results or WEB_SEARCH_MAX_RESULTS
        
        debug_info(f"Performing web search: '{query}'", {
            "max_results": max_results,
            "search_engines": self._get_available_engines()
        })
        
        # Try search engines in order of preference
        search_methods = [
            self._search_serpapi,
            self._search_google_custom,
            self._search_duckduckgo_fallback
        ]
        
        for method in search_methods:
            try:
                results = method(query, max_results)
                if results:
                    debug_info(f"Search successful using {method.__name__}", {
                        "results_count": len(results)
                    })
                    return results
            except Exception as e:
                debug_warning(f"Search method {method.__name__} failed", {"error": str(e)})
                continue
        
        # If all methods fail, return empty results
        debug_error("All search methods failed")
        return []
    
    def _search_serpapi(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using SerpAPI (Google Search API)."""
        if not SERPAPI_KEY:
            raise WebSearchError("SerpAPI key not configured")
        
        url = "https://serpapi.com/search"
        params = {
            'engine': 'google',
            'q': query,
            'api_key': SERPAPI_KEY,
            'num': max_results,
            'gl': 'us',
            'hl': 'en'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        # Parse organic search results
        for item in data.get('organic_results', [])[:max_results]:
            results.append({
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'url': item.get('link', ''),
                'source': 'serpapi',
                'position': item.get('position', 0)
            })
        
        return results
    
    def _search_google_custom(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API."""
        if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
            raise WebSearchError("Google Custom Search not configured")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'q': query,
            'num': min(max_results, 10)  # Google CSE max is 10
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for i, item in enumerate(data.get('items', [])[:max_results]):
            results.append({
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'url': item.get('link', ''),
                'source': 'google_custom',
                'position': i + 1
            })
        
        return results
    
    def _search_duckduckgo_fallback(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback search using DuckDuckGo (no API key required)."""
        # This is a simplified fallback - DuckDuckGo doesn't have a free API
        # but we can scrape their instant answer API for basic results
        
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_redirect': '1',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        # Check for instant answer
        if data.get('AbstractText'):
            results.append({
                'title': data.get('Heading', query),
                'snippet': data.get('AbstractText', ''),
                'url': data.get('AbstractURL', ''),
                'source': 'duckduckgo_instant',
                'position': 1
            })
        
        # Check for related topics
        for i, topic in enumerate(data.get('RelatedTopics', [])[:max_results-len(results)]):
            if isinstance(topic, dict) and topic.get('Text'):
                results.append({
                    'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                    'snippet': topic.get('Text', ''),
                    'url': topic.get('FirstURL', ''),
                    'source': 'duckduckgo_related',
                    'position': i + len(results) + 1
                })
        
        return results
    
    def _get_available_engines(self) -> List[str]:
        """Get list of available search engines based on configuration."""
        engines = []
        if SERPAPI_KEY:
            engines.append('serpapi')
        if GOOGLE_API_KEY and GOOGLE_CSE_ID:
            engines.append('google_custom')
        engines.append('duckduckgo_fallback')  # Always available
        return engines
    
    def get_page_content(self, url: str, max_chars: int = 2000) -> str:
        """
        Get and extract readable content from a webpage.
        
        Args:
            url: URL to fetch
            max_chars: Maximum characters to return
            
        Returns:
            Cleaned text content from the page
        """
        try:
            response = self.session.get(url, timeout=WEB_SEARCH_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if too long
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            return text
            
        except Exception as e:
            debug_error(f"Failed to fetch page content from {url}", {"error": str(e)})
            return ""
    
    def format_search_results(self, results: List[Dict[str, Any]], query: str) -> str:
        """
        Format search results for AI consumption.
        
        Args:
            results: List of search results
            query: Original search query
            
        Returns:
            Formatted string with search results
        """
        if not results:
            return f"No search results found for: {query}"
        
        formatted = f"Web search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result['title']}**\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   Source: {result['source']}\n\n"
        
        return formatted


# Global web search instance
web_search = WebSearchTool()


def search_web(query: str, max_results: int = None) -> str:
    """
    Main function to search the web and return formatted results.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        Formatted search results string
    """
    try:
        results = web_search.search(query, max_results)
        return web_search.format_search_results(results, query)
    except Exception as e:
        debug_error(f"Web search failed for query: {query}", {"error": str(e)})
        return f"Sorry, I couldn't search the web right now. Error: {str(e)}"


def get_webpage_content(url: str) -> str:
    """
    Get content from a specific webpage.
    
    Args:
        url: URL to fetch
        
    Returns:
        Cleaned text content from the page
    """
    try:
        return web_search.get_page_content(url)
    except Exception as e:
        debug_error(f"Failed to get webpage content from {url}", {"error": str(e)})
        return f"Sorry, I couldn't fetch content from that webpage. Error: {str(e)}" 