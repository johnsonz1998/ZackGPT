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
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from dotenv import load_dotenv
from ..core.core_assistant import CoreAssistant
from ..utils.logger import debug_info, debug_success, debug_error

# Import performance toggle service and lightweight mode
try:
    from config.performance_toggles import should_enable, get_performance_config, performance_toggles
    from config.lightweight_mode import enable_lightweight_mode, is_lightweight_mode
    PERFORMANCE_TOGGLES_AVAILABLE = True
    
    # Auto-enable lightweight mode if requested
    if os.getenv("ZACKGPT_LIGHTWEIGHT", "false").lower() == "true":
        enable_lightweight_mode()
        
except ImportError:
    print("⚠️ Performance toggles not available - using default settings")
    PERFORMANCE_TOGGLES_AVAILABLE = False
    def should_enable(feature: str) -> bool:
        return feature in ["external_search", "perplexity_integration"]  # Safe defaults
    def is_lightweight_mode() -> bool:
        return False

# Load environment variables
load_dotenv()

# Ensure debug mode is on
os.environ["DEBUG_MODE"] = "True"

# =============================
#      THREAD POOL EXECUTOR
# =============================

# Create a thread pool executor for blocking operations (resource-aware)
max_workers = 1 if is_lightweight_mode() else int(os.getenv("THREAD_POOL_SIZE", "4"))
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

if is_lightweight_mode():
    print(f"⚡ Lightweight mode: Using single-threaded executor")
else:
    print(f"🔧 Using thread pool with {max_workers} workers")

# =============================
#         DATA MODELS
# =============================

class Thread(BaseModel):
    """Thread data model for API responses."""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

class ChatMessage(BaseModel):
    """Chat message data model for API responses."""
    id: str
    thread_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

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

# Import the managers
from ..data.thread_manager import ThreadManager
from ..data.memory_manager import MemoryManager
from ..data.database import get_database

# Import the memory graph API router
from .memory_graph_api import router as memory_graph_router

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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include sub-routers
app.include_router(memory_graph_router)

# Global instances
connection_manager = ConnectionManager()
thread_manager = ThreadManager()
memory_manager = MemoryManager()

# Assistant instance per thread (for conversation continuity) - with cleanup
assistants: Dict[str, CoreAssistant] = {}
assistant_last_used: Dict[str, datetime] = {}

def get_assistant(thread_id: str) -> CoreAssistant:
    """Get or create an assistant instance for a specific thread."""
    # Clean up old assistants first (older than 1 hour)
    cleanup_old_assistants()
    
    if thread_id not in assistants:
        assistants[thread_id] = CoreAssistant()
        debug_info(f"Created new assistant instance for thread: {thread_id}", {
            "total_assistants": len(assistants)
        })
    
    # Update last used time
    assistant_last_used[thread_id] = datetime.now()
    return assistants[thread_id]

def cleanup_old_assistants():
    """Clean up assistant instances that haven't been used in over 1 hour."""
    cutoff_time = datetime.now() - timedelta(hours=1)
    threads_to_remove = []
    
    for thread_id, last_used in assistant_last_used.items():
        if last_used < cutoff_time:
            threads_to_remove.append(thread_id)
    
    for thread_id in threads_to_remove:
        if thread_id in assistants:
            del assistants[thread_id]
        if thread_id in assistant_last_used:
            del assistant_last_used[thread_id]
        debug_info(f"Cleaned up inactive assistant for thread: {thread_id}")
    
    if threads_to_remove:
        debug_info(f"Cleaned up {len(threads_to_remove)} inactive assistants", {
            "remaining_assistants": len(assistants)
        })

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
    # Sort by updated_at descending (threads are already dictionaries)
    threads.sort(key=lambda t: t.get("updated_at", ""), reverse=True)
    return threads

@app.post("/threads", response_model=Thread)
async def create_thread(request: CreateThreadRequest):
    """Create a new conversation thread."""
    thread_id = thread_manager.create_thread(request.title)
    if thread_id:
        # Get the full thread object
        thread = thread_manager.get_thread(thread_id)
        return thread
    else:
        raise HTTPException(status_code=500, detail="Failed to create thread")

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
        
        # Get AI response with optional web search (run in thread pool to avoid blocking)
        assistant = get_assistant(thread_id)
        loop = asyncio.get_event_loop()
        
        try:
            if request.force_web_search:
                # Force web search by modifying the input to trigger search
                search_input = f"[WEB_SEARCH_FORCED] {request.content}"
                ai_response = await asyncio.wait_for(
                    loop.run_in_executor(
                        thread_pool, assistant.process_input, search_input
                    ),
                    timeout=30.0  # 30 second timeout to prevent hanging
                )
            else:
                ai_response = await asyncio.wait_for(
                    loop.run_in_executor(
                        thread_pool, assistant.process_input, request.content
                    ),
                    timeout=30.0  # 30 second timeout to prevent hanging
                )
        except asyncio.TimeoutError:
            debug_error("AI processing timeout", {"thread_id": thread_id, "content": request.content[:50]})
            raise HTTPException(status_code=504, detail="AI processing timeout - please try again")
        except Exception as processing_error:
            debug_error("AI processing error", {"error": str(processing_error), "thread_id": thread_id})
            raise HTTPException(status_code=500, detail=f"AI processing failed: {str(processing_error)}")
        
        # Add assistant message to database
        assistant_message = thread_manager.add_assistant_message(thread_id, ai_response)
        
        # Memory saving is handled inside assistant.process_input() to avoid duplicates
        
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

@app.get("/memories")
async def get_memories():
    """Get all memories for the memory graph visualization."""
    try:
        if not memory_manager.db:
            return []
        
        # Use the database method to get all memories
        memories = memory_manager.db.get_all_memories(limit=100)
        
        debug_info(f"Retrieved {len(memories)} memories for graph visualization")
        return memories
    except Exception as e:
        debug_error("Failed to get memories", e)
        raise HTTPException(status_code=500, detail=f"Failed to get memories: {str(e)}")

@app.put("/memories/{memory_id}")
async def update_memory(memory_id: str, updates: Dict[str, Any]):
    """Update an existing memory."""
    try:
        if not memory_manager.db:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Find the existing memory
        existing_memory = memory_manager.db.get_memory_by_id(memory_id)
        if not existing_memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Prepare update data
        update_data = {}
        if "question" in updates:
            update_data["question"] = updates["question"]
        if "answer" in updates:
            update_data["answer"] = updates["answer"]
        if "tags" in updates:
            update_data["tags"] = updates["tags"] if isinstance(updates["tags"], list) else []
        if "importance" in updates and updates["importance"] in ["high", "medium", "low"]:
            update_data["importance"] = updates["importance"]
        
        # Update the memory using database method
        success = memory_manager.db.update_memory(memory_id, update_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="No changes made to memory")
        
        # Return updated memory
        updated_memory = memory_manager.db.get_memory_by_id(memory_id)
        debug_info(f"Updated memory {memory_id}")
        
        return {
            "id": updated_memory["_id"],
            "question": updated_memory["question"],
            "answer": updated_memory["answer"],
            "tags": updated_memory.get("tags", []),
            "importance": updated_memory.get("importance", "medium"),
            "timestamp": updated_memory.get("timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        debug_error("Failed to update memory", e)
        raise HTTPException(status_code=500, detail=f"Failed to update memory: {str(e)}")

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory."""
    try:
        if not memory_manager.db:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Check if memory exists
        existing_memory = memory_manager.db.get_memory_by_id(memory_id)
        if not existing_memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Delete the memory using database layer method
        deleted = memory_manager.db.delete_memory(memory_id)
        
        if not deleted:
            raise HTTPException(status_code=400, detail="Failed to delete memory")
        
        debug_info(f"Deleted memory {memory_id}")
        return {"message": "Memory deleted successfully", "id": memory_id}
        
    except HTTPException:
        raise
    except Exception as e:
        debug_error("Failed to delete memory", e)
        raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")

@app.post("/config/reset", response_model=ZackGPTConfig)
async def reset_config():
    """Reset configuration to defaults."""
    debug_info("Config reset requested")
    
    # TODO: Implement actual config reset
    return await get_config()

@app.get("/performance")
async def get_performance_config():
    """Get current performance toggle configuration."""
    if not PERFORMANCE_TOGGLES_AVAILABLE:
        return {"error": "Performance toggles not available", "mode": "unknown"}
    
    return performance_toggles.get_config_dict()

@app.post("/performance/mode")
async def set_performance_mode(data: Dict[str, str]):
    """Set performance mode (development, staging, production, testing)."""
    if not PERFORMANCE_TOGGLES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Performance toggles not available")
    
    new_mode = data.get("mode", "").lower()
    if new_mode not in ["development", "staging", "production", "testing"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be: development, staging, production, or testing")
    
    # Update environment variable and reload configuration
    import os
    os.environ["ZACKGPT_MODE"] = new_mode
    
    # Reload the performance toggles
    from config.performance_toggles import reload_config
    reload_config()
    
    return {
        "success": True,
        "message": f"Performance mode set to {new_mode}",
        "config": performance_toggles.get_config_dict()
    }

@app.post("/performance/reload")
async def reload_performance_config():
    """Reload performance configuration from environment variables."""
    if not PERFORMANCE_TOGGLES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Performance toggles not available")
    
    try:
        from config.performance_toggles import reload_config
        reload_config()
        return {
            "success": True,
            "message": "Performance configuration reloaded",
            "config": performance_toggles.get_config_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload configuration: {str(e)}")

# =============================
#      WEBSOCKET ENDPOINT
# =============================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time chat.
    
    IMPORTANT: This endpoint uses asyncio.run_in_executor() to run blocking AI processing
    operations (like OpenAI API calls) in a separate thread pool. This prevents the
    async event loop from being blocked, which was causing hanging responses.
    
    Without this fix, calling assistant.process_input() directly would block the entire
    WebSocket connection and cause the frontend to hang waiting for a response.
    """
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
                        "data": {
                            "id": user_message["id"],
                            "thread_id": user_message["thread_id"],
                            "role": user_message["role"],
                            "content": user_message["content"],
                            "timestamp": user_message["timestamp"].isoformat()
                        }
                    }))
                    
                    # Send typing indicator
                    await websocket.send_text(json.dumps({
                        "type": "typing",
                        "typing": True
                    }))
                    
                    # Get AI response with optional web search (run in thread pool to avoid blocking)
                    assistant = get_assistant(thread_id)
                    loop = asyncio.get_event_loop()
                    
                    try:
                        if force_web_search:
                            # Force web search by modifying the input to trigger search
                            search_input = f"[WEB_SEARCH_FORCED] {content}"
                            ai_response = await asyncio.wait_for(
                                loop.run_in_executor(
                                    thread_pool, assistant.process_input, search_input
                                ),
                                timeout=30.0  # 30 second timeout to prevent hanging
                            )
                        else:
                            ai_response = await asyncio.wait_for(
                                loop.run_in_executor(
                                    thread_pool, assistant.process_input, content
                                ),
                                timeout=30.0  # 30 second timeout to prevent hanging
                            )
                    except asyncio.TimeoutError:
                        debug_error("AI processing timeout", {"thread_id": thread_id, "content": content[:50]})
                        ai_response = "I apologize, but my response is taking longer than expected. This might be due to a slow connection or complex processing. Please try again."
                        
                        # Send timeout notification
                        await websocket.send_text(json.dumps({
                            "type": "typing",
                            "typing": False
                        }))
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Response timeout - please try again"
                        }))
                        continue
                    except Exception as processing_error:
                        debug_error("AI processing error", {"error": str(processing_error), "thread_id": thread_id})
                        ai_response = f"I apologize, but I encountered an error while processing your request: {str(processing_error)}"
                    
                    # Add assistant message to database
                    assistant_message = thread_manager.add_assistant_message(thread_id, ai_response)
                    
                    # Skip memory notifications for now (disabled for performance)
                    memory_notifications = []
                    
                    # Send typing indicator off
                    await websocket.send_text(json.dumps({
                        "type": "typing",
                        "typing": False
                    }))
                    
                    # Send assistant response
                    await websocket.send_text(json.dumps({
                        "type": "message",
                        "data": {
                            "id": assistant_message["id"],
                            "thread_id": assistant_message["thread_id"],
                            "role": assistant_message["role"],
                            "content": assistant_message["content"],
                            "timestamp": assistant_message["timestamp"].isoformat()
                        }
                    }))
                    
                    # Send memory notifications if any were created
                    for notification in memory_notifications:
                        await websocket.send_text(json.dumps({
                            "type": "memory_notification",
                            "data": notification
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
                        "data": [{
                            "id": msg["id"],
                            "thread_id": msg["thread_id"],
                            "role": msg["role"],
                            "content": msg["content"],
                            "timestamp": msg["timestamp"].isoformat() if hasattr(msg["timestamp"], 'isoformat') else str(msg["timestamp"])
                        } for msg in messages]
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
    try:
        # Log performance configuration
        if PERFORMANCE_TOGGLES_AVAILABLE:
            print(f"🔧 ZackGPT Performance Mode: {performance_toggles.mode.upper()}")
        
        # Conditionally start background tasks based on toggles
        if should_enable("periodic_cleanup"):
            print("🧹 Starting periodic cleanup task...")
            asyncio.create_task(periodic_cleanup())
        else:
            print("❌ Periodic cleanup disabled (performance mode)")
        
        # Try debug logging (might fail if MongoDB analytics is unavailable)
        if should_enable("debug_analytics"):
            debug_success("ZackGPT Web API started", {
                "port": "8000",
                "performance_mode": performance_toggles.mode if PERFORMANCE_TOGGLES_AVAILABLE else "unknown",
                "cors_origins": [
                    "http://localhost:3000", "http://127.0.0.1:3000",
                    "http://localhost:4200", "http://127.0.0.1:4200",
                    "http://localhost:8000", "http://127.0.0.1:8000"
                ],
                "websocket_enabled": True,
                "background_tasks_enabled": should_enable("periodic_cleanup")
            })
        else:
            print("✅ ZackGPT Web API started (analytics disabled)")
            
    except Exception as e:
        print(f"⚠️ Debug logging failed during startup: {e}")
        print("✅ ZackGPT Web API started (debug logging disabled)")

async def periodic_cleanup():
    """Periodically clean up old assistant instances to prevent memory leaks."""
    if not should_enable("periodic_cleanup"):
        print("🚫 Periodic cleanup task exiting - disabled by performance toggles")
        return
        
    cleanup_interval = 300 if should_enable("detailed_metrics") else 900  # 5 min vs 15 min
    print(f"🧹 Periodic cleanup running every {cleanup_interval//60} minutes")
    
    while True:
        try:
            # Check if cleanup is still enabled (in case toggles changed)
            if not should_enable("periodic_cleanup"):
                print("🚫 Periodic cleanup stopping - disabled by performance toggles")
                break
                
            # Wait before cleanup
            await asyncio.sleep(cleanup_interval)
            
            # Run cleanup in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, cleanup_old_assistants)
            
            # Log results based on performance settings
            if should_enable("detailed_metrics"):
                debug_info("Periodic cleanup completed", {
                    "active_assistants": len(assistants),
                    "next_cleanup_in": f"{cleanup_interval//60} minutes"
                })
            else:
                print(f"🧹 Cleanup completed - {len(assistants)} active assistants")
            
        except Exception as e:
            if should_enable("debug_analytics"):
                debug_error("Error in periodic cleanup", e)
            else:
                print(f"⚠️ Cleanup failed: {e}")
            # Wait a bit before retrying to avoid rapid failure loops
            await asyncio.sleep(60)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    debug_info("ZackGPT Web API shutting down")
    
    # Shutdown thread pool executor
    thread_pool.shutdown(wait=True)

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

def main():
    """Entry point for console script in pyproject.toml"""
    run_server() 