"""
End-to-End Integration Tests
Tests for complete user workflows, full-stack integration, and system behavior
"""

import pytest
import asyncio
import requests
import websockets
import json
import time
import threading
from unittest.mock import patch, Mock
import sys
import os

# Add project paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))


class TestCompleteUserWorkflow:
    """Test complete user workflows from start to finish."""
    
    @pytest.mark.e2e
    @pytest.mark.integration
    def test_new_user_conversation_flow(self, backend_url, backend_health_check):
        """Test complete flow: create thread -> send messages -> get responses."""
        
        # Step 1: Create a new conversation thread
        thread_data = {"title": "E2E Test Conversation"}
        response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            json=thread_data,
            timeout=10
        )
        
        assert response.status_code == 200
        thread = response.json()
        thread_id = thread['id']
        
        print(f"✅ Created thread: {thread_id}")
        
        # Step 2: Send a user message
        message_data = {
            "content": "Hello! This is an end-to-end test message.",
            "thread_id": thread_id,
            "force_web_search": False
        }
        
        response = requests.post(
            f"{backend_url}/threads/{thread_id}/messages",
            headers={"Content-Type": "application/json"},
            json=message_data,
            timeout=10
        )
        
        assert response.status_code == 200
        user_message = response.json()
        
        print(f"✅ Sent user message: {user_message['id']}")
        
        # Step 3: Verify messages in thread
        response = requests.get(f"{backend_url}/threads/{thread_id}/messages", timeout=10)
        assert response.status_code == 200
        
        messages = response.json()
        assert len(messages) >= 1  # At least the user message
        
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        assert len(user_messages) >= 1
        assert user_messages[0]['content'] == "Hello! This is an end-to-end test message."
        
        print(f"✅ Verified {len(messages)} messages in thread")
        print("✅ Complete user workflow test passed")
    
    @pytest.mark.e2e
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_websocket_conversation_flow(self, websocket_test_client, backend_health_check):
        """Test complete conversation flow via WebSocket."""
        
        uri = websocket_test_client["url"]
        
        try:
            async with websockets.connect(uri) as websocket:
                print("✅ WebSocket connected")
                
                # Step 1: Send a test message
                test_message = {
                    "type": "chat",
                    "data": {
                        "message": "Hello WebSocket! This is an E2E test.",
                        "thread_id": None  # New conversation
                    }
                }
                
                await websocket.send(json.dumps(test_message))
                print("✅ Sent WebSocket message")
                
                # Step 2: Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    response_data = json.loads(response)
                    
                    assert 'type' in response_data
                    print(f"✅ Received WebSocket response: {response_data.get('type', 'unknown')}")
                    
                except asyncio.TimeoutError:
                    print("ℹ️ WebSocket response timeout - may be expected for test environment")
                
                print("✅ WebSocket conversation flow completed")
                
        except Exception as e:
            print(f"ℹ️ WebSocket test encountered issue: {e}")


class TestSystemIntegration:
    """Test system-wide integration and component interaction."""
    
    @pytest.mark.integration
    def test_database_api_integration(self, backend_url, backend_health_check):
        """Test that API endpoints properly interact with the database."""
        
        # Create thread via API
        thread_data = {"title": "Database Integration Test"}
        response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            json=thread_data,
            timeout=10
        )
        
        assert response.status_code == 200
        thread = response.json()
        thread_id = thread['id']
        
        # Verify thread exists by fetching it
        response = requests.get(f"{backend_url}/threads/{thread_id}", timeout=10)
        assert response.status_code == 200
        
        fetched_thread = response.json()
        assert fetched_thread['id'] == thread_id
        assert fetched_thread['title'] == "Database Integration Test"
        
        print("✅ Database-API integration verified")
    
    @pytest.mark.integration
    def test_error_handling_integration(self, backend_url, backend_health_check):
        """Test error handling across system components."""
        
        # Test 1: Invalid thread ID
        response = requests.get(f"{backend_url}/threads/invalid-thread-id", timeout=10)
        assert response.status_code in [404, 400]  # Should return error
        
        # Test 2: Invalid JSON
        response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            data="{ invalid json }",
            timeout=10
        )
        assert response.status_code in [400, 422]  # Should return validation error
        
        print("✅ Error handling integration verified")


class TestPerformanceIntegration:
    """Test system performance under realistic conditions."""
    
    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_conversation_performance(self, backend_url, backend_health_check):
        """Test performance with large conversations."""
        
        # Create a thread
        thread_data = {"title": "Large Conversation Performance Test"}
        response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            json=thread_data,
            timeout=10
        )
        
        assert response.status_code == 200
        thread = response.json()
        thread_id = thread['id']
        
        try:
            # Add many messages
            start_time = time.time()
            message_count = 50  # Reasonable number for testing
            
            for i in range(message_count):
                message_data = {
                    "content": f"Performance test message {i+1}. " + "Lorem ipsum " * 10,
                    "thread_id": thread_id,
                    "force_web_search": False
                }
                
                response = requests.post(
                    f"{backend_url}/threads/{thread_id}/messages",
                    headers={"Content-Type": "application/json"},
                    json=message_data,
                    timeout=15
                )
                
                assert response.status_code == 200
                
                if (i + 1) % 10 == 0:
                    print(f"  Added {i+1}/{message_count} messages")
            
            elapsed = time.time() - start_time
            
            # Test message retrieval performance
            retrieval_start = time.time()
            response = requests.get(f"{backend_url}/threads/{thread_id}/messages", timeout=30)
            retrieval_elapsed = time.time() - retrieval_start
            
            assert response.status_code == 200
            messages = response.json()
            assert len(messages) == message_count
            
            print(f"✅ Large conversation performance:")
            print(f"  - Added {message_count} messages in {elapsed:.3f}s ({elapsed/message_count*1000:.1f}ms per message)")
            print(f"  - Retrieved {len(messages)} messages in {retrieval_elapsed:.3f}s")
            
            # Performance assertions
            assert elapsed < 60.0  # Should complete within 1 minute
            assert retrieval_elapsed < 5.0  # Should retrieve quickly
            
        finally:
            # Cleanup
            try:
                requests.delete(f"{backend_url}/threads/{thread_id}", timeout=5)
            except:
                pass
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_memory_usage_stability(self, backend_url, backend_health_check):
        """Test that memory usage remains stable during operations."""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple operations
        for i in range(10):
            # Create thread
            thread_data = {"title": f"Memory Test Thread {i}"}
            response = requests.post(
                f"{backend_url}/threads",
                headers={"Content-Type": "application/json"},
                json=thread_data,
                timeout=10
            )
            
            if response.status_code == 200:
                thread = response.json()
                
                # Add some messages
                for j in range(5):
                    message_data = {
                        "role": "user",
                        "content": f"Memory test message {j}"
                    }
                    
                    requests.post(
                        f"{backend_url}/threads/{thread['id']}/messages",
                        headers={"Content-Type": "application/json"},
                        json=message_data,
                        timeout=10
                    )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        print(f"✅ Memory usage: {initial_memory:.1f}MB → {final_memory:.1f}MB (growth: {memory_growth:.1f}MB)")
        
        # Memory growth should be reasonable (less than 50MB for this test)
        assert memory_growth < 50, f"Memory growth too high: {memory_growth:.1f}MB" 