#!/usr/bin/env python3
"""
Perplexity API Search Implementation
Better web search with AI-powered answers
"""

import os
import requests
from typing import List, Dict, Any
from .logger import debug_info, debug_error, debug_success

class PerplexitySearch:
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
    def search(self, query: str, max_results: int = 5) -> str:
        """
        Search using Perplexity API and return formatted results.
        """
        if not self.api_key:
            debug_error("Perplexity API key not configured")
            return "Perplexity API key not configured. Please add PERPLEXITY_API_KEY to your environment."
        
        try:
            debug_info("Performing Perplexity search", {"query": query})
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",  # Perplexity's best search model
                "messages": [
                    {
                        "role": "user",
                        "content": f"Search and provide current, accurate information about: {query}"
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1,
                "top_p": 0.9,
                "search_domain_filter": ["perplexity.ai"],
                "return_images": False,
                "return_related_questions": False,
                "search_recency_filter": "month",
                "top_k": max_results,
                "stream": False
            }
            
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            debug_success("Perplexity search completed", {
                "query": query,
                "response_length": len(content)
            })
            
            # Format the response nicely
            formatted_result = f"""🔍 **Web Search Results for: "{query}"**

{content}

*Source: Real-time web search via Perplexity AI*
"""
            
            return formatted_result
            
        except requests.exceptions.RequestException as e:
            debug_error("Perplexity API request failed", {"error": str(e)})
            return f"❌ Web search failed: {str(e)}"
        except Exception as e:
            debug_error("Perplexity search error", {"error": str(e)})
            return f"❌ Search error: {str(e)}"

# Initialize the search instance
perplexity_search = PerplexitySearch()

def search_with_perplexity(query: str, max_results: int = 5) -> str:
    """Simple function to search with Perplexity."""
    return perplexity_search.search(query, max_results) 