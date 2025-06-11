#!/usr/bin/env python3
"""
ZackGPT Web Server Main Entry Point
Dedicated launcher for the web API server
"""

import os
import sys

# Add the project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from dotenv import load_dotenv
from app.web_api import run_server

def main():
    """Run the ZackGPT web server."""
    # Load environment variables
    load_dotenv()
    
    # Ensure debug mode is on
    os.environ["DEBUG_MODE"] = "True"
    
    print("\n🌐 ZackGPT Web API Server")
    print("=" * 40)
    
    # Run the server
    run_server(host="0.0.0.0", port=8000, debug=True)

if __name__ == "__main__":
    main() 