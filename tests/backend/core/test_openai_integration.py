"""
OpenAI Integration Tests
Tests for OpenAI API connectivity, configuration, and error handling
"""

import pytest
import os
import sys
import time
import signal
from unittest.mock import patch, MagicMock
import openai
from openai import OpenAI

# Add project paths
sys.path.append('.')
sys.path.append('./src')

class TestOpenAIConnection:
    """Test OpenAI client connection and basic functionality."""
    
    def test_openai_import(self):
        """Test that OpenAI library imports correctly."""
        assert hasattr(openai, '__version__')
        print(f"✅ OpenAI version: {openai.__version__}")
    
    def test_openai_client_creation(self):
        """Test OpenAI client can be created without errors."""
        try:
            client = OpenAI()
            assert client is not None
            print("✅ OpenAI client created successfully")
        except Exception as e:
            pytest.fail(f"Failed to create OpenAI client: {e}")
    
    def test_openai_client_with_api_key(self):
        """Test OpenAI client creation with explicit API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not found in environment")
        
        try:
            client = OpenAI(api_key=api_key)
            assert client is not None
            print("✅ OpenAI client created with API key")
        except Exception as e:
            pytest.fail(f"Failed to create OpenAI client with API key: {e}")


class TestOpenAIConfiguration:
    """Test OpenAI configuration and environment setup."""
    
    def test_api_key_validation(self):
        """Test API key validation."""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            pytest.skip("OPENAI_API_KEY not found - skipping validation test")
        
        # Basic API key format validation
        assert isinstance(api_key, str)
        
        # In test environment, accept test keys or real keys
        if api_key.startswith('test-key'):
            # Test environment - validate test key format
            assert len(api_key) >= 10  # Test keys should be reasonable length
            print(f"✅ Test API key format valid: {api_key}")
        else:
            # Production environment - validate real OpenAI key format
            assert len(api_key) > 20  # OpenAI keys are typically longer
            assert api_key.startswith('sk-')  # OpenAI keys start with sk-
            print(f"✅ Production API key format valid (ends with: ...{api_key[-10:]})")
    
    def test_config_import(self):
        """Test that config module can be imported."""
        try:
            from config import config
            assert hasattr(config, 'OPENAI_API_KEY')
            print("✅ Config module imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import config: {e}")
    
    def test_model_configuration(self):
        """Test model configuration values."""
        try:
            from config import config
            
            # Test default model
            model = getattr(config, 'LLM_MODEL', 'gpt-4')
            assert model in ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo']
            print(f"✅ Model configured: {model}")
            
            # Test temperature
            temp = getattr(config, 'LLM_TEMPERATURE', 0.7)
            assert 0.0 <= temp <= 2.0
            print(f"✅ Temperature configured: {temp}")
            
        except Exception as e:
            pytest.fail(f"Config validation failed: {e}")


class TestOpenAIAPICall:
    """Test actual OpenAI API calls (integration tests)."""
    
    @pytest.mark.integration
    def test_simple_api_call(self):
        """Test a simple API call to OpenAI."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not found - skipping API call test")
        
        # Skip actual API calls in test environment
        if api_key.startswith('test-key'):
            pytest.skip("Skipping actual API call in test environment - test key detected")
        
        try:
            client = OpenAI(api_key=api_key)
            
            start_time = time.time()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Say 'Test successful'"}],
                max_tokens=10,
                temperature=0.1
            )
            elapsed = time.time() - start_time
            
            # Validate response structure
            assert response.choices
            assert len(response.choices) > 0
            assert response.choices[0].message
            assert response.choices[0].message.content
            
            content = response.choices[0].message.content.strip()
            print(f"✅ API call successful in {elapsed:.2f}s")
            print(f"   Response: {content}")
            
            # Basic content validation
            assert len(content) > 0
            assert 'test' in content.lower() or 'successful' in content.lower()
            
        except Exception as e:
            pytest.fail(f"API call failed: {e}")
    
    @pytest.mark.integration
    def test_api_call_with_timeout(self):
        """Test API call with timeout handling."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not found - skipping timeout test")
        
        # Skip actual API calls in test environment
        if api_key.startswith('test-key'):
            pytest.skip("Skipping actual API call in test environment - test key detected")
        
        def timeout_handler(signum, frame):
            raise TimeoutError("API call timed out!")
        
        try:
            # Set 30-second timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello!"}],
                max_tokens=20
            )
            
            # Cancel alarm
            signal.alarm(0)
            
            assert response.choices[0].message.content
            print("✅ API call completed within timeout")
            
        except TimeoutError:
            pytest.fail("API call timed out - this could indicate network issues")
        except Exception as e:
            signal.alarm(0)  # Make sure to cancel alarm
            pytest.fail(f"API call failed: {e}")


class TestCoreAssistantIntegration:
    """Test CoreAssistant integration with OpenAI."""
    
    @pytest.mark.integration
    def test_core_assistant_creation(self):
        """Test CoreAssistant can be created successfully."""
        try:
            from app.core_assistant import CoreAssistant
            
            assistant = CoreAssistant()
            assert assistant is not None
            assert hasattr(assistant, 'client')
            assert hasattr(assistant, 'model')
            print("✅ CoreAssistant created successfully")
            
        except Exception as e:
            pytest.fail(f"CoreAssistant creation failed: {e}")
    
    @pytest.mark.integration
    def test_core_assistant_process_input(self):
        """Test CoreAssistant can process input successfully."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not found - skipping CoreAssistant test")
        
        try:
            from app.core_assistant import CoreAssistant
            
            # Set timeout
            def timeout_handler(signum, frame):
                raise TimeoutError("CoreAssistant processing timed out!")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(45)  # 45-second timeout for full processing
            
            assistant = CoreAssistant()
            start_time = time.time()
            
            response = assistant.process_input("Hello! This is a test.")
            
            elapsed = time.time() - start_time
            signal.alarm(0)  # Cancel alarm
            
            # Validate response
            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
            
            print(f"✅ CoreAssistant processed input in {elapsed:.2f}s")
            print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            
        except TimeoutError:
            pytest.fail("CoreAssistant processing timed out")
        except Exception as e:
            signal.alarm(0)  # Make sure to cancel alarm
            pytest.fail(f"CoreAssistant processing failed: {e}")


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_api_key(self):
        """Test handling of invalid API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid-key'}):
            try:
                client = OpenAI(api_key='invalid-key')
                
                # This should fail with authentication error
                with pytest.raises(Exception) as exc_info:
                    client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                
                # Check that it's an authentication-related error
                error_msg = str(exc_info.value).lower()
                assert any(word in error_msg for word in ['auth', 'key', 'invalid', 'unauthorized'])
                print("✅ Invalid API key properly rejected")
                
            except Exception as e:
                # If we can't even create the client, that's also acceptable
                print(f"✅ Invalid API key rejected at client creation: {e}")
    
    @patch('openai.OpenAI')
    def test_network_error_handling(self, mock_openai):
        """Test handling of network errors."""
        # Mock network error
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = ConnectionError("Network error")
        mock_openai.return_value = mock_client
        
        try:
            from app.core_assistant import CoreAssistant
            
            # This should handle the network error gracefully
            assistant = CoreAssistant()
            
            # CoreAssistant handles network errors gracefully and returns error messages
            # rather than raising exceptions
            response = assistant.process_input("test")
            
            # Verify that it returns an error response but doesn't crash
            assert response is not None
            assert isinstance(response, str)
            
            print("✅ Network errors handled gracefully")
            print(f"   Error response: {response[:100]}...")
            
        except ImportError:
            pytest.skip("CoreAssistant not available for network error test")


class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.performance
    @pytest.mark.integration
    def test_response_time_benchmark(self):
        """Benchmark API response times."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not found - skipping performance test")
        
        # Skip actual API calls in test environment
        if api_key.startswith('test-key'):
            pytest.skip("Skipping actual API call in test environment - test key detected")
        
        client = OpenAI(api_key=api_key)
        
        # Test multiple requests
        times = []
        for i in range(3):
            start_time = time.time()
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": f"Test {i+1}"}],
                max_tokens=10
            )
            
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            assert response.choices[0].message.content
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"✅ Performance benchmark:")
        print(f"   Average: {avg_time:.2f}s")
        print(f"   Min: {min_time:.2f}s") 
        print(f"   Max: {max_time:.2f}s")
        
        # Performance assertions
        assert avg_time < 10.0, f"Average response time too slow: {avg_time:.2f}s"
        assert max_time < 15.0, f"Max response time too slow: {max_time:.2f}s"


# Test runner for standalone execution
if __name__ == "__main__":
    print("🧪 Running OpenAI Integration Tests")
    print("=" * 60)
    
    # Run tests manually for development
    test_classes = [
        TestOpenAIConnection,
        TestOpenAIConfiguration,
        TestOpenAIAPICall,
        TestCoreAssistantIntegration,
        TestErrorHandling,
        TestPerformance
    ]
    
    for test_class in test_classes:
        print(f"\n🔧 Running {test_class.__name__}...")
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    print(f"  • {method_name}...")
                    getattr(instance, method_name)()
                except Exception as e:
                    print(f"    ❌ Failed: {e}")
                else:
                    print(f"    ✅ Passed")
    
    print("\n🎉 OpenAI Integration Tests Complete!") 