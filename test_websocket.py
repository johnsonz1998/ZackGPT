#!/usr/bin/env python3
"""
Quick WebSocket Test
Test the WebSocket connection that's causing the frontend to hang
"""

import asyncio
import websockets
import json
import sys


async def test_websocket():
    """Test WebSocket connection to ZackGPT backend"""
    uri = "ws://localhost:8000/ws/test-client-123"
    
    try:
        print(f"🔌 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a test message (correct format)
            test_message = {
                "action": "send_message",
                "content": "Hello WebSocket!",
                "thread_id": "test-thread"
            }
            
            print("📤 Sending test message...")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            print("⏳ Waiting for response...")
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📥 Received: {response}")
                print("✅ WebSocket test successful!")
                return True
                
            except asyncio.TimeoutError:
                print("⏱️  Timeout waiting for response")
                return False
                
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - backend not running?")
        return False
    except websockets.exceptions.InvalidURI:
        print("❌ Invalid WebSocket URI")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False


def test_basic_connection():
    """Test basic HTTP connection first"""
    import requests
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ HTTP connection to backend works")
            return True
        else:
            print(f"❌ HTTP connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HTTP connection error: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 ZackGPT WebSocket Connection Test")
    print("=" * 50)
    
    # Test basic HTTP first
    if not test_basic_connection():
        print("❌ Basic HTTP connection failed - start the backend first")
        return
    
    # Test WebSocket
    success = await test_websocket()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 WebSocket connection is working!")
        print("The frontend hanging issue is likely something else.")
    else:
        print("❌ WebSocket connection failed!")
        print("This is likely why the frontend is hanging.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1) 