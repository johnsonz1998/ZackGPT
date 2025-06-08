#!/usr/bin/env python3
"""
ZackGPT Main Launcher
Provides options for both CLI and Web modes
"""

import os
import sys
import threading
import time
from pathlib import Path

# Add the project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_banner():
    """Print the ZackGPT banner."""
    print("\n" + "="*60)
    print("🚀 ZackGPT - Advanced AI Assistant")
    print("   Powered by Evolutionary Prompt Learning")
    print("="*60)

def run_text_mode():
    """Run the CLI text mode."""
    from scripts.startup.main_text import run_text_mode as run_cli
    print("\n🖥️  Starting CLI Text Mode...")
    print("Type 'exit' to quit\n")
    run_cli()

def run_web_mode():
    """Run the web API server."""
    from app.web_api import run_server
    print("\n🌐 Starting Web API Server...")
    run_server(host="0.0.0.0", port=8000, debug=True)

def run_hybrid_mode():
    """Run both CLI and Web modes simultaneously."""
    print("\n🔄 Starting Hybrid Mode (CLI + Web API)...")
    print("   - Web API will run in background on port 8000")
    print("   - CLI will run in foreground")
    print("   - Press Ctrl+C to stop both\n")
    
    # Start web server in a background thread
    web_thread = threading.Thread(target=run_web_mode, daemon=True)
    web_thread.start()
    
    # Give the web server time to start
    time.sleep(2)
    print("✅ Web API started at http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 WebSocket endpoint: ws://localhost:8000/ws/{client_id}")
    print("\n" + "-"*50)
    print("Now starting CLI mode...")
    
    # Run CLI in foreground
    try:
        run_text_mode()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

def main():
    """Main entry point."""
    print_banner()
    
    print("\nChoose how you want to run ZackGPT:")
    print("1) 🖥️  CLI Mode (Text-based interface)")
    print("2) 🌐 Web Mode (API server for frontend)")
    print("3) 🔄 Hybrid Mode (Both CLI + Web)")
    print("4) ❌ Cancel")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                run_text_mode()
                break
            elif choice == "2":
                run_web_mode()
                break
            elif choice == "3":
                run_hybrid_mode()
                break
            elif choice == "4":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main() 