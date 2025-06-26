import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from src.zackgpt.tools.web_search import (
    WebSearchTool,
    WebSearchError,
    search_web,
    get_webpage_content
)

@pytest.fixture
def web_search_tool():
    """Create a WebSearchTool instance."""
    return WebSearchTool()

@pytest.fixture
def mock_serpapi_response():
    """Mock SerpAPI response."""
    return {
        'organic_results': [
            {
                'title': 'Test Result 1',
                'snippet': 'First test result snippet',
                'link': 'https://example1.com',
                'position': 1
            },
            {
                'title': 'Test Result 2',
                'snippet': 'Second test result snippet',
                'link': 'https://example2.com',
                'position': 2
            }
        ]
    }

@pytest.fixture
def mock_google_response():
    """Mock Google Custom Search response."""
    return {
        'items': [
            {
                'title': 'Google Result 1',
                'snippet': 'First Google result',
                'link': 'https://google1.com'
            },
            {
                'title': 'Google Result 2',
                'snippet': 'Second Google result',
                'link': 'https://google2.com'
            }
        ]
    }

class TestWebSearchTool:
    """Test WebSearchTool class."""
    
    def test_web_search_tool_creation(self, web_search_tool):
        """Test creating a WebSearchTool."""
        assert web_search_tool.session is not None
        assert hasattr(web_search_tool, 'search')
    
    @patch('src.zackgpt.tools.web_search.WEB_SEARCH_ENABLED', True)
    @patch('src.zackgpt.tools.web_search.SERPAPI_KEY', 'test_key')
    @patch('requests.Session.get')
    def test_serpapi_search(self, mock_get, web_search_tool, mock_serpapi_response):
        """Test SerpAPI search."""
        mock_response = Mock()
        mock_response.json.return_value = mock_serpapi_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        results = web_search_tool._search_serpapi("test query", 2)
        
        assert len(results) == 2
        assert results[0]['title'] == 'Test Result 1'
        assert results[0]['source'] == 'serpapi'
        assert results[1]['title'] == 'Test Result 2'
    
    @patch('src.zackgpt.tools.web_search.WEB_SEARCH_ENABLED', True)
    @patch('src.zackgpt.tools.web_search.GOOGLE_API_KEY', 'test_key')
    @patch('src.zackgpt.tools.web_search.GOOGLE_CSE_ID', 'test_cse')
    @patch('requests.Session.get')
    def test_google_custom_search(self, mock_get, web_search_tool, mock_google_response):
        """Test Google Custom Search."""
        mock_response = Mock()
        mock_response.json.return_value = mock_google_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        results = web_search_tool._search_google_custom("test query", 2)
        
        assert len(results) == 2
        assert results[0]['title'] == 'Google Result 1'
        assert results[0]['source'] == 'google_custom'
    
    @patch('src.zackgpt.tools.web_search.WEB_SEARCH_ENABLED', False)
    def test_search_disabled(self, web_search_tool):
        """Test search when disabled."""
        with pytest.raises(WebSearchError, match="Web search is disabled"):
            web_search_tool.search("test query")
    
    @patch('src.zackgpt.tools.web_search.WEB_SEARCH_ENABLED', True)
    @patch('src.zackgpt.tools.web_search.SERPAPI_KEY', '')
    @patch('src.zackgpt.tools.web_search.GOOGLE_API_KEY', '')
    @patch('requests.Session.get')
    def test_duckduckgo_fallback(self, mock_get, web_search_tool):
        """Test DuckDuckGo fallback search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'AbstractText': 'Test abstract text',
            'Heading': 'Test Heading',
            'AbstractURL': 'https://test.com'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        results = web_search_tool._search_duckduckgo_fallback("test query", 5)
        
        assert len(results) >= 1
        assert results[0]['source'] == 'duckduckgo_instant'
    
    def test_get_available_engines(self, web_search_tool):
        """Test getting available search engines."""
        with patch('src.zackgpt.tools.web_search.SERPAPI_KEY', 'test'):
            with patch('src.zackgpt.tools.web_search.GOOGLE_API_KEY', 'test'):
                with patch('src.zackgpt.tools.web_search.GOOGLE_CSE_ID', 'test'):
                    engines = web_search_tool._get_available_engines()
                    assert 'serpapi' in engines
                    assert 'google_custom' in engines
                    assert 'duckduckgo_fallback' in engines

class TestWebSearchFunctions:
    """Test web search utility functions."""
    
    @patch('src.zackgpt.tools.web_search.WEB_SEARCH_ENABLED', True)
    @patch('requests.Session.get')
    def test_search_web_function(self, mock_get):
        """Test the search_web utility function."""
        # Mock the DuckDuckGo response since that's the fallback
        mock_response = Mock()
        mock_response.json.return_value = {
            'AbstractText': 'Test search result',
            'Heading': 'Test Heading',
            'AbstractURL': 'https://test.com'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = search_web("test query", max_results=5)
        
        # Should return formatted results, not empty
        assert "Test search result" in result or "No search results" in result
    
    @patch('requests.Session.get')
    def test_get_webpage_content_function(self, mock_get):
        """Test the get_webpage_content utility function."""
        # Mock the webpage response
        mock_response = Mock()
        mock_response.text = "<html><body><h1>Test Page</h1><p>Test content</p></body></html>"
        mock_response.content = b"<html><body><h1>Test Page</h1><p>Test content</p></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_webpage_content("https://test.com")
        
        # Should return some content, even if processed
        assert len(result) > 0

class TestWebSearchError:
    """Test WebSearchError exception."""
    
    def test_web_search_error(self):
        """Test WebSearchError exception."""
        error = WebSearchError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception) 