#!/usr/bin/env python3
"""
Simple standalone API for managing ZackGPT configuration and API keys.
Run this on port 8001 alongside the main API on port 8000.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from pathlib import Path
from typing import Dict, Any
import subprocess
import sys

app = FastAPI(title="ZackGPT Config Manager", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ApiKeyUpdate(BaseModel):
    openai_api_key: str = ""
    serpapi_key: str = ""
    google_api_key: str = ""
    google_cse_id: str = ""
    elevenlabs_api_key: str = ""

class ConfigStatus(BaseModel):
    web_search_enabled: bool
    api_keys: Dict[str, str]
    search_engines: Dict[str, bool]
    web_search_working: bool = False

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "ZackGPT Config Manager", "docs": "/docs"}

@app.get("/status", response_model=ConfigStatus)
async def get_status():
    """Get current configuration status."""
    try:
        # Read .env file
        env_file = Path(".env")
        env_content = {}
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()
        
        # Mask API keys
        def mask_key(key):
            value = env_content.get(key, '')
            if not value:
                return ''
            return f"***{value[-4:]}" if len(value) > 4 else '***'
        
        # Check search engines
        search_engines = {
            'serpapi': bool(env_content.get('SERPAPI_KEY')),
            'google_custom': bool(env_content.get('GOOGLE_API_KEY') and env_content.get('GOOGLE_CSE_ID')),
            'duckduckgo': True  # Always available
        }
        
        # Test web search
        web_search_working = False
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from .web_search import search_web
            result = search_web("test", max_results=1)
            web_search_working = bool(result and len(result) > 10)
        except:
            web_search_working = False
        
        return ConfigStatus(
            web_search_enabled=env_content.get('WEB_SEARCH_ENABLED', '').lower() == 'true',
            api_keys={
                'openai_api_key': mask_key('OPENAI_API_KEY'),
                'serpapi_key': mask_key('SERPAPI_KEY'),
                'google_api_key': mask_key('GOOGLE_API_KEY'),
                'google_cse_id': mask_key('GOOGLE_CSE_ID'),
                'elevenlabs_api_key': mask_key('ELEVENLABS_API_KEY')
            },
            search_engines=search_engines,
            web_search_working=web_search_working
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.post("/update-keys")
async def update_api_keys(keys: ApiKeyUpdate):
    """Update API keys in .env file."""
    try:
        env_file = Path(".env")
        
        # Read existing content
        env_content = {}
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()
        
        # Update with new keys (only if provided)
        updated_keys = []
        key_mapping = {
            'openai_api_key': 'OPENAI_API_KEY',
            'serpapi_key': 'SERPAPI_KEY',
            'google_api_key': 'GOOGLE_API_KEY',
            'google_cse_id': 'GOOGLE_CSE_ID',
            'elevenlabs_api_key': 'ELEVENLABS_API_KEY'
        }
        
        for frontend_key, env_key in key_mapping.items():
            value = getattr(keys, frontend_key, '').strip()
            if value:
                env_content[env_key] = value
                updated_keys.append(env_key)
                # Also update current environment
                os.environ[env_key] = value
        
        # Ensure web search is enabled
        env_content['WEB_SEARCH_ENABLED'] = 'true'
        env_content['WEB_SEARCH_MAX_RESULTS'] = '5'
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.write("# ZackGPT Configuration\n")
            f.write("# Updated via Config Manager\n\n")
            
            # Write core settings
            core_keys = ['WEB_SEARCH_ENABLED', 'WEB_SEARCH_MAX_RESULTS', 'DEBUG_MODE']
            for key in core_keys:
                if key in env_content:
                    f.write(f"{key}={env_content[key]}\n")
            
            f.write("\n# API Keys\n")
            for key, value in env_content.items():
                if key not in core_keys:
                    f.write(f"{key}={value}\n")
        
        return {
            "success": True,
            "message": f"Updated {len(updated_keys)} API keys",
            "updated_keys": updated_keys
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update keys: {str(e)}")

@app.post("/test-search")
async def test_web_search():
    """Test web search functionality."""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from .web_search import search_web, WEB_SEARCH_ENABLED
        
        if not WEB_SEARCH_ENABLED:
            return {
                "success": False,
                "message": "Web search is disabled",
                "enabled": False
            }
        
        # Test search
        results = search_web("Python programming", max_results=2)
        
        if results and len(results) > 50:
            return {
                "success": True,
                "message": "Web search working",
                "enabled": True,
                "preview": results[:200] + "..."
            }
        else:
            return {
                "success": False,
                "message": "Web search returned no results",
                "enabled": True
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Web search error: {str(e)}",
            "enabled": False
        }

@app.get("/restart-main-server")
async def restart_main_server():
    """Restart the main ZackGPT server to reload configuration."""
    try:
        # Kill existing server
        subprocess.run(['pkill', '-f', 'uvicorn.*web_api'], check=False)
        
        # Start new server in background
        subprocess.Popen([
            'python3', '-m', 'uvicorn', 
            'app.web_api:app', 
            '--host', '0.0.0.0', 
            '--port', '8000',
            '--reload'
        ], cwd=Path(__file__).parent.parent)
        
        return {
            "success": True,
            "message": "Main server restarted"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to restart server: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    print("🔧 Starting ZackGPT Config Manager")
    print("🌐 Access at: http://localhost:8001/docs")
    print("📝 Configure API keys and test web search")
    uvicorn.run(app, host="0.0.0.0", port=8001) 