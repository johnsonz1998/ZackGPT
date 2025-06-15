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
# Fixed import path
# Fixed import path


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @pytest.mark.integration
    def test_health_check(self, backend_url, backend_health_check):
        """Test health endpoint returns healthy status."""
        response = requests.get(f"{backend_url}/health", timeout=10)
        
        assert response.status_code == 200
        health_data = response.json()
        
        assert health_data.get('status') == 'healthy'
        assert 'backend_connected' in health_data
        assert 'version' in health_data  # Check version instead of timestamp
        
        print(f"✅ Health check passed: {health_data}")


class TestThreadsAPI:
    """Test thread CRUD operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.created_thread_ids = []
    
    def teardown_method(self, backend_url):
        """Clean up created threads."""
        for thread_id in self.created_thread_ids:
            try:
                requests.delete(f"{backend_url}/threads/{thread_id}")
            except:
                pass  # Ignore cleanup errors
    
    @pytest.mark.integration
    def test_create_thread(self, backend_url, backend_health_check):
        """Test creating a new thread."""
        thread_data = {
            "title": "Test Thread for API Tests"
        }
        
        response = requests.post(
            f"{backend_url}/threads",
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
    
    @pytest.mark.integration
    def test_get_threads(self, backend_url, backend_health_check):
        """Test getting list of threads."""
        # First create a test thread
        thread_data = {"title": "Test Thread for List"}
        create_response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            json=thread_data,
            timeout=10
        )
        
        assert create_response.status_code == 200
        created_thread = create_response.json()
        self.created_thread_ids.append(created_thread['id'])
        
        # Now get the threads list
        response = requests.get(f"{backend_url}/threads", timeout=10)
        
        assert response.status_code == 200
        threads = response.json()
        
        # Validate response structure
        assert isinstance(threads, list)
        
        # Find our created thread
        our_thread = next((t for t in threads if t['id'] == created_thread['id']), None)
        assert our_thread is not None
        assert our_thread['title'] == thread_data['title']
        
        print(f"✅ Threads list retrieved: {len(threads)} threads")
    
    @pytest.mark.integration
    def test_get_thread_by_id(self, backend_url, backend_health_check):
        """Test getting a specific thread by ID."""
        # Create a test thread
        thread_data = {"title": "Test Thread for GET"}
        create_response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            json=thread_data,
            timeout=10
        )
        
        created_thread = create_response.json()
        thread_id = created_thread['id']
        self.created_thread_ids.append(thread_id)
        
        # Get the specific thread
        response = requests.get(f"{backend_url}/threads/{thread_id}", timeout=10)
        
        assert response.status_code == 200
        thread = response.json()
        
        # Validate response
        assert thread['id'] == thread_id
        assert thread['title'] == thread_data['title']
        assert 'created_at' in thread
        assert 'updated_at' in thread
        
        print(f"✅ Thread retrieved by ID: {thread_id}")
    
    @pytest.mark.integration
    def test_get_nonexistent_thread(self, backend_url, backend_health_check):
        """Test getting a thread that doesn't exist."""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{backend_url}/threads/{fake_id}", timeout=10)
        
        # Should return 404 for non-existent thread
        assert response.status_code == 404
        
        print(f"✅ Non-existent thread properly returns 404")
    
    @pytest.mark.integration
    def test_delete_thread(self, backend_url, backend_health_check):
        """Test deleting a thread."""
        # Create a thread to delete
        thread_data = {"title": "Thread to Delete"}
        create_response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            json=thread_data,
            timeout=10
        )
        
        created_thread = create_response.json()
        thread_id = created_thread['id']
        
        # Delete the thread
        delete_response = requests.delete(f"{backend_url}/threads/{thread_id}", timeout=10)
        
        assert delete_response.status_code == 200
        
        # Verify it's gone
        get_response = requests.get(f"{backend_url}/threads/{thread_id}", timeout=10)
        assert get_response.status_code == 404
        
        print(f"✅ Thread deleted: {thread_id}")


class TestMessagesAPI:
    """Test message-related API endpoints."""
    
    def setup_method(self):
        """Set up test environment."""
        self.created_thread_ids = []
        self.test_thread_id = None
    
    def teardown_method(self, backend_url):
        """Clean up created threads."""
        for thread_id in self.created_thread_ids:
            try:
                requests.delete(f"{backend_url}/threads/{thread_id}")
            except:
                pass  # Ignore cleanup errors
    
    def create_test_thread(self, backend_url):
        """Helper to create a test thread."""
        thread_data = {"title": "Test Thread for Messages"}
        response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            json=thread_data,
            timeout=10
        )
        assert response.status_code == 200
        thread = response.json()
        self.created_thread_ids.append(thread['id'])
        return thread['id']
    
    @pytest.mark.integration
    def test_get_messages_empty_thread(self, backend_url, backend_health_check):
        """Test getting messages from an empty thread."""
        thread_id = self.create_test_thread(backend_url)
        
        response = requests.get(f"{backend_url}/threads/{thread_id}/messages", timeout=10)
        
        assert response.status_code == 200
        messages = response.json()
        
        # Should be empty list for new thread
        assert isinstance(messages, list)
        assert len(messages) == 0
        
        print(f"✅ Empty thread messages retrieved: {len(messages)} messages")
    
    @pytest.mark.integration
    def test_get_messages_nonexistent_thread(self, backend_url, backend_health_check):
        """Test getting messages from non-existent thread."""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{backend_url}/threads/{fake_id}/messages", timeout=10)
        
        # Should return 404 for non-existent thread
        assert response.status_code == 404
        
        print(f"✅ Non-existent thread messages properly returns 404")


class TestConfigAPI:
    """Test configuration endpoints."""
    
    @pytest.mark.integration
    def test_get_config(self, backend_url, backend_health_check):
        """Test getting configuration."""
        response = requests.get(f"{backend_url}/config", timeout=10)
        
        assert response.status_code == 200
        config = response.json()
        
        # Validate config structure
        assert isinstance(config, dict)
        # Should have some config keys (don't test specific values for security)
        assert len(config) > 0
        
        print(f"✅ Configuration retrieved: {list(config.keys())}")


class TestAPIPerformance:
    """Test API performance characteristics."""
    
    @pytest.mark.performance
    @pytest.mark.integration
    def test_api_response_times(self, backend_url, backend_health_check):
        """Test API response times are reasonable."""
        endpoints = [
            "/health",
            "/threads",
            "/config"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # API should respond within 2 seconds
            assert response_time < 2.0
            assert response.status_code in [200, 404]  # Allow 404 for some endpoints
            
            print(f"✅ {endpoint} responded in {response_time:.3f}s")


class TestAPIErrorHandling:
    """Test API error handling."""
    
    @pytest.mark.integration
    def test_invalid_json(self, backend_url, backend_health_check):
        """Test API handles invalid JSON gracefully."""
        response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            data="invalid json",
            timeout=10
        )
        
        # Should return 422 for invalid JSON
        assert response.status_code == 422
        
        print("✅ Invalid JSON properly handled")
    
    @pytest.mark.integration
    def test_missing_required_fields(self, backend_url, backend_health_check):
        """Test API validates required fields."""
        # Try to create thread without title
        response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            json={},  # Missing title
            timeout=10
        )
        
        # Should return 422 for missing required fields
        assert response.status_code == 422
        
        print("✅ Missing required fields properly validated")


 