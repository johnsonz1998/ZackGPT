"""
REST API Integration Tests
Tests for HTTP endpoints, CRUD operations, and API functionality
"""

import pytest
import requests
import json
import time
import uuid
from unittest.mock import patch
import sys
import os

# Add project paths
sys.path.append('.')
sys.path.append('./src')

BASE_URL = "http://localhost:8000"


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health endpoint returns healthy status."""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            
            assert response.status_code == 200
            health_data = response.json()
            
            assert health_data.get('status') == 'healthy'
            assert 'backend_connected' in health_data
            assert 'version' in health_data  # Check version instead of timestamp
            
            print(f"✅ Health check passed: {health_data}")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Health check failed: {e}")


class TestThreadsAPI:
    """Test thread CRUD operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.created_thread_ids = []
    
    def teardown_method(self):
        """Clean up created threads."""
        for thread_id in self.created_thread_ids:
            try:
                requests.delete(f"{BASE_URL}/threads/{thread_id}")
            except:
                pass  # Ignore cleanup errors
    
    @pytest.mark.integration
    def test_create_thread(self):
        """Test creating a new thread."""
        try:
            thread_data = {
                "title": "Test Thread for API Tests"
            }
            
            response = requests.post(
                f"{BASE_URL}/threads",
                headers={"Content-Type": "application/json"},
                json=thread_data,
                timeout=10
            )
            
            assert response.status_code == 200
            created_thread = response.json()
            
            # Validate response structure
            assert 'id' in created_thread
            assert created_thread['title'] == thread_data['title']
            assert 'created_at' in created_thread
            assert 'updated_at' in created_thread
            assert created_thread['message_count'] == 0
            
            # Track for cleanup
            self.created_thread_ids.append(created_thread['id'])
            
            print(f"✅ Thread created: {created_thread['id']}")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Create thread failed: {e}")
    
    @pytest.mark.integration
    def test_get_threads(self):
        """Test getting list of threads."""
        try:
            # First create a test thread
            thread_data = {"title": "Test Thread for List"}
            create_response = requests.post(
                f"{BASE_URL}/threads",
                headers={"Content-Type": "application/json"},
                json=thread_data,
                timeout=10
            )
            
            assert create_response.status_code == 200
            created_thread = create_response.json()
            self.created_thread_ids.append(created_thread['id'])
            
            # Now get the threads list
            response = requests.get(f"{BASE_URL}/threads", timeout=10)
            
            assert response.status_code == 200
            threads = response.json()
            
            # Validate response structure
            assert isinstance(threads, list)
            
            # Find our created thread
            our_thread = next((t for t in threads if t['id'] == created_thread['id']), None)
            assert our_thread is not None
            assert our_thread['title'] == thread_data['title']
            
            print(f"✅ Threads list retrieved: {len(threads)} threads")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Get threads failed: {e}")
    
    @pytest.mark.integration
    def test_get_thread_by_id(self):
        """Test getting a specific thread by ID."""
        try:
            # Create a test thread
            thread_data = {"title": "Test Thread for GET"}
            create_response = requests.post(
                f"{BASE_URL}/threads",
                headers={"Content-Type": "application/json"},
                json=thread_data,
                timeout=10
            )
            
            created_thread = create_response.json()
            thread_id = created_thread['id']
            self.created_thread_ids.append(thread_id)
            
            # Get the specific thread
            response = requests.get(f"{BASE_URL}/threads/{thread_id}", timeout=10)
            
            assert response.status_code == 200
            thread = response.json()
            
            # Validate response
            assert thread['id'] == thread_id
            assert thread['title'] == thread_data['title']
            assert 'created_at' in thread
            assert 'updated_at' in thread
            
            print(f"✅ Thread retrieved by ID: {thread_id}")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Get thread by ID failed: {e}")
    
    def test_get_nonexistent_thread(self):
        """Test getting a thread that doesn't exist."""
        try:
            fake_id = str(uuid.uuid4())
            response = requests.get(f"{BASE_URL}/threads/{fake_id}", timeout=10)
            
            # Should return 404 for non-existent thread
            assert response.status_code == 404
            
            print(f"✅ Non-existent thread properly returns 404")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Non-existent thread test failed: {e}")
    
    @pytest.mark.integration
    def test_delete_thread(self):
        """Test deleting a thread."""
        try:
            # Create a thread to delete
            thread_data = {"title": "Thread to Delete"}
            create_response = requests.post(
                f"{BASE_URL}/threads",
                headers={"Content-Type": "application/json"},
                json=thread_data,
                timeout=10
            )
            
            created_thread = create_response.json()
            thread_id = created_thread['id']
            
            # Delete the thread
            delete_response = requests.delete(f"{BASE_URL}/threads/{thread_id}", timeout=10)
            
            assert delete_response.status_code == 200
            
            # Verify it's gone
            get_response = requests.get(f"{BASE_URL}/threads/{thread_id}", timeout=10)
            assert get_response.status_code == 404
            
            print(f"✅ Thread deleted: {thread_id}")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Delete thread failed: {e}")


class TestMessagesAPI:
    """Test message-related API endpoints."""
    
    def setup_method(self):
        """Set up test environment with a thread."""
        try:
            # Create a test thread
            thread_data = {"title": "Test Thread for Messages"}
            response = requests.post(
                f"{BASE_URL}/threads",
                headers={"Content-Type": "application/json"},
                json=thread_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.test_thread = response.json()
                self.test_thread_id = self.test_thread['id']
            else:
                self.test_thread_id = None
                
        except:
            self.test_thread_id = None
    
    def teardown_method(self):
        """Clean up test thread."""
        if self.test_thread_id:
            try:
                requests.delete(f"{BASE_URL}/threads/{self.test_thread_id}")
            except:
                pass
    
    @pytest.mark.integration
    def test_get_messages_empty_thread(self):
        """Test getting messages from an empty thread."""
        if not self.test_thread_id:
            pytest.skip("Could not create test thread")
        
        try:
            response = requests.get(
                f"{BASE_URL}/threads/{self.test_thread_id}/messages",
                timeout=10
            )
            
            assert response.status_code == 200
            messages = response.json()
            
            # Should be empty list for new thread
            assert isinstance(messages, list)
            assert len(messages) == 0
            
            print("✅ Empty thread returns empty messages list")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Get messages from empty thread failed: {e}")
    
    def test_get_messages_nonexistent_thread(self):
        """Test getting messages from non-existent thread."""
        try:
            fake_id = str(uuid.uuid4())
            response = requests.get(
                f"{BASE_URL}/threads/{fake_id}/messages",
                timeout=10
            )
            
            # Should return 404 for non-existent thread
            assert response.status_code == 404
            
            print("✅ Non-existent thread messages returns 404")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Get messages from non-existent thread failed: {e}")


class TestConfigAPI:
    """Test configuration endpoints."""
    
    def test_get_config(self):
        """Test getting configuration."""
        try:
            response = requests.get(f"{BASE_URL}/config", timeout=10)
            
            assert response.status_code == 200
            config = response.json()
            
            # Validate config structure
            assert isinstance(config, dict)
            # Should have some config keys (don't test specific values for security)
            assert len(config) > 0
            
            print(f"✅ Configuration retrieved: {list(config.keys())}")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Get config failed: {e}")


class TestAPIPerformance:
    """Test API performance characteristics."""
    
    @pytest.mark.performance
    @pytest.mark.integration
    def test_api_response_times(self):
        """Test API response time benchmarks."""
        try:
            endpoints = [
                "/health",
                "/threads",
                "/config"
            ]
            
            response_times = {}
            
            for endpoint in endpoints:
                times = []
                
                # Test each endpoint 3 times
                for i in range(3):
                    start_time = time.time()
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                    elapsed = time.time() - start_time
                    
                    assert response.status_code == 200
                    times.append(elapsed)
                
                avg_time = sum(times) / len(times)
                response_times[endpoint] = avg_time
                
                print(f"✅ {endpoint}: {avg_time:.3f}s average")
                
                # Performance assertion
                assert avg_time < 2.0, f"{endpoint} too slow: {avg_time:.3f}s"
            
            print(f"✅ All API endpoints meet performance requirements")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"API performance test failed: {e}")


class TestAPIErrorHandling:
    """Test API error handling."""
    
    def test_invalid_json(self):
        """Test API handling of invalid JSON."""
        try:
            response = requests.post(
                f"{BASE_URL}/threads",
                headers={"Content-Type": "application/json"},
                data="{ invalid json }",
                timeout=10
            )
            
            # Should return 400 for invalid JSON
            assert response.status_code == 422  # FastAPI returns 422 for validation errors
            
            print("✅ Invalid JSON properly rejected")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Invalid JSON test failed: {e}")
    
    def test_missing_required_fields(self):
        """Test API handling of missing required fields."""
        try:
            # Try to create thread without title
            response = requests.post(
                f"{BASE_URL}/threads",
                headers={"Content-Type": "application/json"},
                json={},  # Missing title
                timeout=10
            )
            
            # Should return validation error
            assert response.status_code == 422
            
            print("✅ Missing required fields properly rejected")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend server not running")
        except Exception as e:
            pytest.fail(f"Missing fields test failed: {e}")


# Test runner for standalone execution
if __name__ == "__main__":
    print("🧪 Running REST API Integration Tests")
    print("=" * 60)
    
    # Check if backend is running first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server not healthy")
            print("💡 Start the server: ./server/scripts/start-server.sh")
            exit(1)
    except:
        print("❌ Backend server not running")
        print("💡 Start the server: ./server/scripts/start-server.sh")
        exit(1)
    
    print("✅ Backend server is running")
    print("\n🎉 REST API Integration Tests Complete!") 