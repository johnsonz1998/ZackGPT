#!/usr/bin/env python3
"""
ZackGPT Web API Server
Provides REST and WebSocket endpoints for the ZackGPT frontend
"""

import os
import sys
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from dotenv import load_dotenv
from ..core.core_assistant import CoreAssistant
from ..core.logger import debug_info, debug_success, debug_error

# Load environment variables
load_dotenv()

# Ensure debug mode is on
os.environ["DEBUG_MODE"] = "True"

# =============================
#         DATA MODELS
# =============================

# Thread and ChatMessage models are now imported from thread_manager

class SendMessageRequest(BaseModel):
    content: str
    thread_id: str
    force_web_search: bool = False

class CreateThreadRequest(BaseModel):
    title: str

class HealthStatus(BaseModel):
    status: str
    version: str
    backend_connected: bool
    features: Dict[str, bool]

class SystemStats(BaseModel):
    total_threads: int
    total_messages: int
    evolution_stats: Dict[str, Any]
    memory_stats: Dict[str, Any]

class ZackGPTConfig(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    model_name: str
    max_tokens: int
    temperature: float
    voice_enabled: bool
    voice_model: str
    tts_voice: str
    memory_enabled: bool
    max_memory_entries: int
    evolution_enabled: bool
    evolution_frequency: int
    
    # Web Search Settings
    web_search_enabled: bool
    web_search_max_results: int
    
    # API Keys (masked for security)
    openai_api_key_masked: str
    elevenlabs_api_key_masked: str
    serpapi_key_masked: str
    google_api_key_masked: str
    google_cse_id_masked: str
    
    debug_mode: bool
    log_level: str

# =============================
#      CONNECTION MANAGER
# =============================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        debug_info(f"WebSocket connected: {client_id}", {"total_connections": len(self.active_connections)})
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            debug_info(f"WebSocket disconnected: {client_id}", {"total_connections": len(self.active_connections)})
            
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
            
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

# Import the new persistent managers
from ..core.thread_manager import PersistentThreadManager, Thread, ChatMessage
from ..core.memory_manager import PersistentMemoryManager

# =============================
#        GLOBAL INSTANCES
# =============================

# Initialize FastAPI app
app = FastAPI(
    title="ZackGPT API",
    description="AI Assistant API with real-time chat capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global instances
connection_manager = ConnectionManager()
thread_manager = PersistentThreadManager()
memory_manager = PersistentMemoryManager()

# Assistant instance per thread (for conversation continuity)
assistants: Dict[str, CoreAssistant] = {}

def get_assistant(thread_id: str) -> CoreAssistant:
    """Get or create an assistant instance for a specific thread."""
    if thread_id not in assistants:
        assistants[thread_id] = CoreAssistant()
        debug_info(f"Created new assistant instance for thread: {thread_id}")
    return assistants[thread_id]

# =============================
#         REST ENDPOINTS
# =============================

@app.get("/")
async def root():
    """Root endpoint for basic connectivity testing."""
    return {"message": "ZackGPT API is running", "status": "ok"}

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint."""
    try:
        # Test if we can create an assistant instance
        test_assistant = CoreAssistant()
        backend_connected = True
    except Exception as e:
        debug_error("Backend health check failed", e)
        backend_connected = False
        
    return HealthStatus(
        status="healthy" if backend_connected else "degraded",
        version="1.0.0",
        backend_connected=backend_connected,
        features={
            "websocket_chat": True,
            "thread_management": True,
            "memory_persistence": backend_connected,
            "prompt_evolution": backend_connected
        }
    )

@app.get("/threads", response_model=List[Thread])
async def get_threads():
    """Get all conversation threads."""
    threads = thread_manager.get_all_threads()
    # Sort by updated_at descending
    threads.sort(key=lambda t: t.updated_at, reverse=True)
    return threads

@app.post("/threads", response_model=Thread)
async def create_thread(request: CreateThreadRequest):
    """Create a new conversation thread."""
    thread = thread_manager.create_thread(request.title)
    return thread

@app.get("/threads/{thread_id}", response_model=Thread)
async def get_thread(thread_id: str):
    """Get a specific thread."""
    thread = thread_manager.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread

@app.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a thread and all its messages."""
    success = thread_manager.delete_thread(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Clean up assistant instance
    if thread_id in assistants:
        del assistants[thread_id]
        
    return {"message": "Thread deleted successfully"}

@app.get("/threads/{thread_id}/messages", response_model=List[ChatMessage])
async def get_messages(thread_id: str):
    """Get all messages in a thread."""
    thread = thread_manager.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    messages = thread_manager.get_messages(thread_id)
    return messages

@app.post("/threads/{thread_id}/messages", response_model=ChatMessage)
async def send_message(thread_id: str, request: SendMessageRequest):
    """Send a message to a thread (REST endpoint, alternative to WebSocket)."""
    thread = thread_manager.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    try:
        # Add user message to database
        user_message = thread_manager.add_user_message(thread_id, request.content)
        
        # Get AI response with optional web search
        assistant = get_assistant(thread_id)
        if request.force_web_search:
            # Force web search by modifying the input to trigger search
            search_input = f"[WEB_SEARCH_FORCED] {request.content}"
            ai_response = assistant.process_input(search_input)
        else:
            ai_response = assistant.process_input(request.content)
        
        # Add assistant message to database
        assistant_message = thread_manager.add_assistant_message(thread_id, ai_response)
        
        # Save interaction to memory if appropriate
        memory_manager.save_interaction(request.content, ai_response)
        
        return assistant_message
        
    except Exception as e:
        debug_error("Error processing message", e)
        raise HTTPException(status_code=500, detail="Failed to process message")

@app.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system statistics."""
    try:
        # Get stats from database
        db_stats = thread_manager.get_stats()
        memory_stats = memory_manager.get_stats()
        
        # Create a temporary assistant to get evolution stats
        temp_assistant = CoreAssistant()
        evolution_stats = temp_assistant.get_evolution_stats()
        
        return SystemStats(
            total_threads=db_stats["threads"]["total"],
            total_messages=db_stats["threads"]["total_messages"],
            evolution_stats=evolution_stats,
            memory_stats=memory_stats
        )
    except Exception as e:
        debug_error("Error getting system stats", e)
        return SystemStats(
            total_threads=0,
            total_messages=0,
            evolution_stats={"status": "unavailable"},
            memory_stats={"status": "unavailable"}
        )

@app.get("/config", response_model=ZackGPTConfig)
async def get_config():
    """Get current configuration."""
    from config import config
    
    # Helper function to mask API keys
    def mask_key(key_value):
        if not key_value:
            return ''
        return f"{'*' * max(0, len(str(key_value)) - 8)}{str(key_value)[-4:] if len(str(key_value)) > 4 else '***'}"
    
    return ZackGPTConfig(
        model_name=getattr(config, 'LLM_MODEL', 'gpt-4'),
        max_tokens=getattr(config, 'MAX_TOKENS', 2000),
        temperature=getattr(config, 'LLM_TEMPERATURE', 0.7),
        voice_enabled=getattr(config, 'USE_ELEVENLABS', False),
        voice_model=getattr(config, 'VOICE_MODEL', 'whisper-1'),
        tts_voice=getattr(config, 'ELEVENLABS_VOICE', 'alloy'),
        memory_enabled=getattr(config, 'MEMORY_ENABLED', True),
        max_memory_entries=getattr(config, 'MAX_MEMORY_ENTRIES', 1000),
        evolution_enabled=getattr(config, 'EVOLUTION_ENABLED', True),
        evolution_frequency=getattr(config, 'EVOLUTION_FREQUENCY', 10),
        
        # Web Search Settings
        web_search_enabled=getattr(config, 'WEB_SEARCH_ENABLED', False),
        web_search_max_results=getattr(config, 'WEB_SEARCH_MAX_RESULTS', 5),
        
        # API Keys (masked)
        openai_api_key_masked=mask_key(getattr(config, 'OPENAI_API_KEY', '')),
        elevenlabs_api_key_masked=mask_key(getattr(config, 'ELEVENLABS_API_KEY', '')),
        serpapi_key_masked=mask_key(getattr(config, 'SERPAPI_KEY', '')),
        google_api_key_masked=mask_key(getattr(config, 'GOOGLE_API_KEY', '')),
        google_cse_id_masked=mask_key(getattr(config, 'GOOGLE_CSE_ID', '')),
        
        debug_mode=getattr(config, 'DEBUG_MODE', False),
        log_level=getattr(config, 'LOG_LEVEL', 'INFO')
    )

@app.patch("/config", response_model=ZackGPTConfig)
async def update_config(updates: Dict[str, Any]):
    """Update configuration (partial update)."""
    debug_info("Config update requested", {"keys": list(updates.keys())})
    
    # For now, just return the current config
    # TODO: Implement actual config updates to environment variables or config file
    return await get_config()

@app.post("/config/api-keys")
async def update_api_keys(api_keys: Dict[str, str]):
    """Update API keys securely."""
    import os
    from pathlib import Path
    
    debug_info("API keys update requested", {"keys": list(api_keys.keys())})
    
    # Define the .env file path
    env_file = Path(".env")
    
    try:
        # Read existing .env file or create new content
        env_content = {}
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()
        
        # Update with new API keys
        key_mapping = {
            'serpapi_key': 'SERPAPI_KEY',
            'google_api_key': 'GOOGLE_API_KEY',
            'google_cse_id': 'GOOGLE_CSE_ID',
            'openai_api_key': 'OPENAI_API_KEY',
            'elevenlabs_api_key': 'ELEVENLABS_API_KEY'
        }
        
        updated_keys = []
        for frontend_key, env_key in key_mapping.items():
            if frontend_key in api_keys and api_keys[frontend_key].strip():
                env_content[env_key] = api_keys[frontend_key].strip()
                updated_keys.append(env_key)
                # Also update the current environment
                os.environ[env_key] = api_keys[frontend_key].strip()
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        debug_info("API keys updated successfully", {"updated_keys": updated_keys})
        
        return {
            "success": True,
            "message": f"Updated {len(updated_keys)} API keys successfully",
            "updated_keys": updated_keys
        }
        
    except Exception as e:
        debug_error("Failed to update API keys", {"error": str(e)})
        return {
            "success": False,
            "message": f"Failed to update API keys: {str(e)}"
        }

@app.post("/config/reset", response_model=ZackGPTConfig)
async def reset_config():
    """Reset configuration to defaults."""
    debug_info("Config reset requested")
    
    # TODO: Implement actual config reset
    return await get_config()

# =============================
#      WEBSOCKET ENDPOINT
# =============================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat."""
    await connection_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            action = message_data.get("action")
            
            if action == "send_message":
                thread_id = message_data.get("thread_id")
                content = message_data.get("content")
                force_web_search = message_data.get("force_web_search", False)
                
                if not thread_id or not content:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Missing thread_id or content"
                    }))
                    continue
                
                try:
                    # Add user message to database
                    user_message = thread_manager.add_user_message(thread_id, content)
                    
                    # Send user message confirmation
                    await websocket.send_text(json.dumps({
                        "type": "message",
                        "data": user_message.model_dump(mode='json')
                    }))
                    
                    # Send typing indicator
                    await websocket.send_text(json.dumps({
                        "type": "typing",
                        "typing": True
                    }))
                    
                    # Get AI response with optional web search
                    assistant = get_assistant(thread_id)
                    if force_web_search:
                        # Force web search by modifying the input to trigger search
                        search_input = f"[WEB_SEARCH_FORCED] {content}"
                        ai_response = assistant.process_input(search_input)
                    else:
                        ai_response = assistant.process_input(content)
                    
                    # Add assistant message to database
                    assistant_message = thread_manager.add_assistant_message(thread_id, ai_response)
                    
                    # Save interaction to memory if appropriate
                    memory_manager.save_interaction(content, ai_response)
                    
                    # Send typing indicator off
                    await websocket.send_text(json.dumps({
                        "type": "typing",
                        "typing": False
                    }))
                    
                    # Send assistant response
                    await websocket.send_text(json.dumps({
                        "type": "message",
                        "data": assistant_message.model_dump(mode='json')
                    }))
                    
                except Exception as e:
                    debug_error("Error processing WebSocket message", e)
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Failed to process message"
                    }))
                    
            elif action == "get_messages":
                thread_id = message_data.get("thread_id")
                if thread_id:
                    messages = thread_manager.get_messages(thread_id)
                    await websocket.send_text(json.dumps({
                        "type": "messages",
                        "data": [msg.model_dump(mode='json') for msg in messages]
                    }))
                    
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)
    except Exception as e:
        debug_error("WebSocket error", e)
        connection_manager.disconnect(client_id)

# =============================
#          STARTUP LOGIC
# =============================

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    debug_success("ZackGPT Web API started", {
        "port": "8000",
        "cors_origins": ["http://localhost:4200", "http://127.0.0.1:4200"],
        "websocket_enabled": True
    })

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    debug_info("ZackGPT Web API shutting down")

# =============================
#           MAIN RUNNER
# =============================

def run_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = True):
    """Run the FastAPI server."""
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info" if debug else "warning",
        reload=debug
    )
    server = uvicorn.Server(config)
    
    print("\n=== ZackGPT Web API Server ===")
    print(f"🚀 Starting server at http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 WebSocket endpoint: ws://{host}:{port}/ws/{{client_id}}")
    print("=" * 50)
    
    server.run()

if __name__ == "__main__":
    run_server() 