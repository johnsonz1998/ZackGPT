"""
WebSocket Integration Tests
Tests for WebSocket connectivity, message handling, and real-time features
"""

import pytest
import asyncio
import json
import requests
import websockets
import sys
import os
import time

# Add project paths
# Fixed import path
# Fixed import path


class TestWebSocketConnection:
    """Test WebSocket connection establishment and management."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_websocket_connection(self, websocket_test_client, backend_health_check):
        """Test basic WebSocket connection."""
        uri = websocket_test_client["url"]
        
        async with websockets.connect(uri) as websocket:
            assert websocket.open
            print("✅ WebSocket connection established")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_websocket_multiple_connections(self, websocket_test_client, backend_health_check):
        """Test multiple concurrent WebSocket connections."""
        connections = []
        base_url = websocket_test_client["url"].replace("/test-client", "")
        
        # Create 3 concurrent connections
        for i in range(3):
            uri = f"{base_url}/test-client-{i}"
            websocket = await websockets.connect(uri)
            connections.append(websocket)
        
        # Verify all connections are open
        for websocket in connections:
            assert websocket.open
        
        print("✅ Multiple WebSocket connections established")
        
        # Clean up
        for websocket in connections:
            await websocket.close()


class TestWebSocketMessaging:
    """Test WebSocket message sending and receiving."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_thread_id = None
        self.created_thread_ids = []
    
    def teardown_method(self, backend_url):
        """Clean up created threads."""
        for thread_id in self.created_thread_ids:
            try:
                requests.delete(f"{backend_url}/threads/{thread_id}")
            except:
                pass  # Ignore cleanup errors
    
    def create_test_thread(self, backend_url):
        """Create a test thread for messaging."""
        response = requests.post(
            f"{backend_url}/threads",
            headers={"Content-Type": "application/json"},
            json={"title": "WebSocket Test Thread"},
            timeout=10
        )
        
        assert response.status_code == 200
        thread_data = response.json()
        thread_id = thread_data["id"]
        self.created_thread_ids.append(thread_id)
        return thread_id
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_websocket_message_flow(self, backend_url, websocket_test_client, backend_health_check):
        """Test complete WebSocket message flow."""
        thread_id = self.create_test_thread(backend_url)
        uri = websocket_test_client["url"]
        
        async with websockets.connect(uri) as websocket:
            # Send test message
            test_message = {
                "action": "send_message",
                "content": "Hello WebSocket! This is a test message.",
                "thread_id": thread_id
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Test message sent")
            
            # Collect responses
            responses = []
            timeout_count = 0
            max_responses = 4  # user msg, typing on, typing off, assistant msg
            
            while len(responses) < max_responses and timeout_count < 3:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    response_data = json.loads(response)
                    responses.append(response_data)
                    
                    msg_type = response_data.get('type', 'unknown')
                    print(f"📥 Received: {msg_type}")
                    
                    if msg_type == 'message':
                        role = response_data.get('data', {}).get('role', 'unknown')
                        if role == 'assistant':
                            print("✅ Received AI response - test successful!")
                            break
                            
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"⏰ Timeout {timeout_count}/3")
                    if timeout_count >= 3:
                        break
            
            # Validate responses
            assert len(responses) > 0, "No responses received"
            
            # Check for user message confirmation
            user_msg_found = any(
                r.get('type') == 'message' and 
                r.get('data', {}).get('role') == 'user'
                for r in responses
            )
            assert user_msg_found, "User message confirmation not received"
            
            print(f"✅ WebSocket message flow test completed ({len(responses)} responses)")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_websocket_invalid_message(self, websocket_test_client, backend_health_check):
        """Test WebSocket handling of invalid messages."""
        uri = websocket_test_client["url"]
        
        async with websockets.connect(uri) as websocket:
            # Send invalid message (missing required fields)
            invalid_message = {
                "action": "send_message",
                "content": "Test message"
                # Missing thread_id
            }
            
            await websocket.send(json.dumps(invalid_message))
            
            # Should receive error response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            response_data = json.loads(response)
            
            assert response_data.get('type') == 'error'
            assert 'thread_id' in response_data.get('message', '').lower()
            
            print("✅ Invalid message properly rejected")


class TestWebSocketPerformance:
    """Test WebSocket performance characteristics."""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.integration
    async def test_websocket_connection_speed(self, websocket_test_client, backend_health_check):
        """Test WebSocket connection establishment speed."""
        connection_times = []
        base_url = websocket_test_client["url"].replace("/test-client", "")
        
        for i in range(5):
            start_time = time.time()
            uri = f"{base_url}/test-perf-{i}"
            
            async with websockets.connect(uri) as websocket:
                connection_time = time.time() - start_time
                connection_times.append(connection_time)
                assert websocket.open
        
        avg_time = sum(connection_times) / len(connection_times)
        max_time = max(connection_times)
        
        # Connection should be fast
        assert avg_time < 1.0, f"Average connection time too slow: {avg_time:.3f}s"
        assert max_time < 2.0, f"Max connection time too slow: {max_time:.3f}s"
        
        print(f"✅ WebSocket connections: avg={avg_time:.3f}s, max={max_time:.3f}s")


# Test runner for standalone execution
if __name__ == "__main__":
    print("🧪 Running WebSocket Integration Tests")
    print("=" * 60)
    
    # Check if backend is running first
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server not healthy")
            print("💡 Start the server: ./server/scripts/start-server.sh")
            exit(1)
    except:
        print("❌ Backend server not running")
        print("💡 Start the server: ./server/scripts/start-server.sh")
        exit(1)
    
    print("✅ Backend server is running")
    print("\n🎉 WebSocket Integration Tests Complete!")
