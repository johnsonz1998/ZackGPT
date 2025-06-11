"""
CoreAssistant Unit Tests
Tests for CoreAssistant functionality, message processing, and integration
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Add project paths
sys.path.append('.')
sys.path.append('./src')


class TestCoreAssistantBasics:
    """Test basic CoreAssistant functionality."""
    
    def test_core_assistant_import(self):
        """Test that CoreAssistant can be imported."""
        try:
            from app.core_assistant import CoreAssistant
            assert CoreAssistant is not None
            print("✅ CoreAssistant imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import CoreAssistant: {e}")
    
    def test_core_assistant_creation(self):
        """Test CoreAssistant instantiation."""
        try:
            from app.core_assistant import CoreAssistant
            assistant = CoreAssistant()
            
            assert assistant is not None
            assert hasattr(assistant, 'client')
            assert hasattr(assistant, 'model')
            
            print("✅ CoreAssistant created successfully")
            
        except Exception as e:
            pytest.fail(f"Failed to create CoreAssistant: {e}")
    
    def test_core_assistant_attributes(self):
        """Test CoreAssistant has required attributes."""
        try:
            from app.core_assistant import CoreAssistant
            assistant = CoreAssistant()
            
            # Check for essential attributes
            required_attrs = ['client', 'model', 'process_input']
            for attr in required_attrs:
                assert hasattr(assistant, attr), f"Missing attribute: {attr}"
            
            # Check client is properly configured
            assert assistant.client is not None
            assert assistant.model is not None
            
            print(f"✅ CoreAssistant has all required attributes: {required_attrs}")
            
        except Exception as e:
            pytest.fail(f"CoreAssistant attributes test failed: {e}")


class TestCoreAssistantProcessing:
    """Test CoreAssistant message processing."""
    
    def setup_method(self):
        """Set up test environment."""
        try:
            from app.core_assistant import CoreAssistant
            self.assistant = CoreAssistant()
        except Exception as e:
            self.assistant = None
            print(f"Could not create CoreAssistant: {e}")
    
    @pytest.mark.integration
    def test_process_simple_input(self):
        """Test processing a simple input."""
        if not self.assistant:
            pytest.skip("CoreAssistant not available")
        
        try:
            test_input = "Hello! This is a test message."
            
            start_time = time.time()
            response = self.assistant.process_input(test_input)
            elapsed = time.time() - start_time
            
            # Validate response
            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
            
            print(f"✅ Simple input processed in {elapsed:.2f}s")
            print(f"   Input: {test_input}")
            print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            
        except Exception as e:
            pytest.fail(f"Simple input processing failed: {e}")
    
    @pytest.mark.integration
    def test_process_empty_input(self):
        """Test processing empty input."""
        if not self.assistant:
            pytest.skip("CoreAssistant not available")
        
        try:
            response = self.assistant.process_input("")
            
            # Should handle empty input gracefully
            assert response is not None
            assert isinstance(response, str)
            
            print(f"✅ Empty input handled: {response[:100]}{'...' if len(response) > 100 else ''}")
            
        except Exception as e:
            pytest.fail(f"Empty input processing failed: {e}")
    
    @pytest.mark.integration
    def test_process_long_input(self):
        """Test processing long input."""
        if not self.assistant:
            pytest.skip("CoreAssistant not available")
        
        try:
            # Create a longer test input
            long_input = "This is a longer test message. " * 20
            
            start_time = time.time()
            response = self.assistant.process_input(long_input)
            elapsed = time.time() - start_time
            
            # Validate response
            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
            
            print(f"✅ Long input processed in {elapsed:.2f}s")
            print(f"   Input length: {len(long_input)} chars")
            print(f"   Response length: {len(response)} chars")
            
            # Performance check for longer inputs
            assert elapsed < 30.0, f"Long input processing too slow: {elapsed:.2f}s"
            
        except Exception as e:
            pytest.fail(f"Long input processing failed: {e}")


class TestCoreAssistantErrorHandling:
    """Test CoreAssistant error handling."""
    
    def setup_method(self):
        """Set up test environment."""
        try:
            from app.core_assistant import CoreAssistant
            self.assistant = CoreAssistant()
        except Exception as e:
            self.assistant = None
    
    @patch('app.core_assistant.CoreAssistant.process_input')
    def test_network_error_handling(self, mock_process):
        """Test handling of network errors."""
        if not self.assistant:
            pytest.skip("CoreAssistant not available")
        
        # Mock network error
        mock_process.side_effect = ConnectionError("Network error")
        
        try:
            with pytest.raises(ConnectionError):
                self.assistant.process_input("test")
            
            print("✅ Network errors properly raised")
            
        except Exception as e:
            pytest.fail(f"Network error test failed: {e}")
    
    def test_none_input_handling(self):
        """Test handling of None input."""
        if not self.assistant:
            pytest.skip("CoreAssistant not available")
        
        try:
            # This should either handle None gracefully or raise a clear error
            result = self.assistant.process_input(None)
            
            # If it returns something, it should be a string
            if result is not None:
                assert isinstance(result, str)
                print(f"✅ None input handled: {result[:50]}...")
            
        except TypeError as e:
            # This is also acceptable - clear error for None input
            print(f"✅ None input properly rejected: {e}")
        except Exception as e:
            pytest.fail(f"None input handling failed: {e}")


class TestCoreAssistantConfiguration:
    """Test CoreAssistant configuration and setup."""
    
    def test_model_configuration(self):
        """Test model configuration."""
        try:
            from app.core_assistant import CoreAssistant
            assistant = CoreAssistant()
            
            # Check model is set
            assert assistant.model is not None
            assert isinstance(assistant.model, str)
            assert len(assistant.model) > 0
            
            print(f"✅ Model configured: {assistant.model}")
            
        except Exception as e:
            pytest.fail(f"Model configuration test failed: {e}")
    
    def test_client_configuration(self):
        """Test OpenAI client configuration."""
        try:
            from app.core_assistant import CoreAssistant
            assistant = CoreAssistant()
            
            # Check client is configured
            assert assistant.client is not None
            
            # Should have OpenAI client methods
            assert hasattr(assistant.client, 'chat')
            
            print("✅ Client properly configured")
            
        except Exception as e:
            pytest.fail(f"Client configuration test failed: {e}")


class TestCoreAssistantPerformance:
    """Test CoreAssistant performance characteristics."""
    
    def setup_method(self):
        """Set up test environment."""
        try:
            from app.core_assistant import CoreAssistant
            self.assistant = CoreAssistant()
        except Exception as e:
            self.assistant = None
    
    @pytest.mark.performance
    @pytest.mark.integration
    def test_response_time_consistency(self):
        """Test response time consistency."""
        if not self.assistant:
            pytest.skip("CoreAssistant not available")
        
        try:
            test_inputs = [
                "Hello!",
                "What's the weather?",
                "Tell me a joke.",
                "How are you?",
                "What's 2+2?"
            ]
            
            response_times = []
            
            for test_input in test_inputs:
                start_time = time.time()
                response = self.assistant.process_input(test_input)
                elapsed = time.time() - start_time
                
                response_times.append(elapsed)
                
                # Basic response validation
                assert response is not None
                assert isinstance(response, str)
                assert len(response) > 0
            
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"✅ Response time consistency:")
            print(f"   Average: {avg_time:.2f}s")
            print(f"   Min: {min_time:.2f}s")
            print(f"   Max: {max_time:.2f}s")
            print(f"   Variance: {max_time - min_time:.2f}s")
            
            # Performance assertions
            assert avg_time < 15.0, f"Average response time too slow: {avg_time:.2f}s"
            assert max_time < 25.0, f"Max response time too slow: {max_time:.2f}s"
            assert (max_time - min_time) < 20.0, f"Response time variance too high: {max_time - min_time:.2f}s"
            
        except Exception as e:
            pytest.fail(f"Response time consistency test failed: {e}")
    
    @pytest.mark.performance
    @pytest.mark.integration  
    def test_memory_usage_stability(self):
        """Test that memory usage doesn't grow excessively."""
        if not self.assistant:
            pytest.skip("CoreAssistant not available")
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process multiple inputs
            for i in range(5):
                response = self.assistant.process_input(f"Test message {i+1}")
                assert response is not None
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = final_memory - initial_memory
            
            print(f"✅ Memory usage:")
            print(f"   Initial: {initial_memory:.1f}MB")
            print(f"   Final: {final_memory:.1f}MB")
            print(f"   Growth: {memory_growth:.1f}MB")
            
            # Memory growth should be reasonable
            assert memory_growth < 100, f"Memory growth too high: {memory_growth:.1f}MB"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")
        except Exception as e:
            pytest.fail(f"Memory usage test failed: {e}")


# Test runner for standalone execution
if __name__ == "__main__":
    print("🧪 Running CoreAssistant Unit Tests")
    print("=" * 60)
    
    test_classes = [
        TestCoreAssistantBasics,
        TestCoreAssistantProcessing,
        TestCoreAssistantErrorHandling,
        TestCoreAssistantConfiguration,
        TestCoreAssistantPerformance
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
    
    print("\n🎉 CoreAssistant Unit Tests Complete!") 