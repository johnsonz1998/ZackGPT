#!/usr/bin/env python3
"""
ZackGPT CLI Main Entry Point
Unified command-line interface for ZackGPT AI Assistant
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from dotenv import load_dotenv
from cli.utils.output import (
    print_banner, print_success, print_error, print_info, 
    get_user_choice, confirm_action, Colors
)


def setup_environment():
    """Setup the CLI environment"""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print_error("OPENAI_API_KEY not found in environment")
        print_info("Please create a .env file with your OpenAI API key")
        print_info("Example: echo 'OPENAI_API_KEY=your_key_here' > .env")
        sys.exit(1)
    
    # Ensure debug mode is on for CLI
    os.environ["DEBUG_MODE"] = "True"
    
    print_success("Environment setup complete")


def run_chat_mode():
    """Run the text-based chat interface"""
    try:
        from cli.commands.chat import run_text_mode
        print_info("Starting CLI Chat Mode...")
        run_text_mode()
    except KeyboardInterrupt:
        print_info("Chat session ended by user")
    except Exception as e:
        print_error(f"Error in chat mode: {e}")


def run_voice_mode():
    """Run the voice-based interface"""
    try:
        from cli.commands.voice import main as voice_main
        print_info("Starting CLI Voice Mode...")
        # Pass text mode flag to voice command
        sys.argv = ['voice.py', '--text'] 
        voice_main()
    except KeyboardInterrupt:
        print_info("Voice session ended by user")
    except Exception as e:
        print_error(f"Error in voice mode: {e}")


def run_dev_tools():
    """Run the development tools"""
    try:
        from cli.commands.dev import show_dev_menu
        print_info("Starting Development Tools...")
        while True:
            try:
                show_dev_menu()
            except KeyboardInterrupt:
                break
        print_info("Development tools session ended")
    except Exception as e:
        print_error(f"Error in dev tools: {e}")


def run_interactive_menu():
    """Run the interactive CLI menu"""
    print_banner()
    print_info("Welcome to ZackGPT CLI Interface")
    
    while True:
        try:
            choices = [
                "💬 Chat Mode (Text-based conversation)",
                "🎤 Voice Mode (Voice interaction via text)",
                "🛠️  Development Tools",
                "❌ Exit"
            ]
            
            choice = get_user_choice("Select a mode:", choices)
            
            if "Chat Mode" in choice:
                run_chat_mode()
            elif "Voice Mode" in choice:
                run_voice_mode()
            elif "Development Tools" in choice:
                run_dev_tools()
            elif "Exit" in choice:
                print_info("Goodbye!")
                break
                
        except KeyboardInterrupt:
            print_info("\nGoodbye!")
            break
        except Exception as e:
            print_error(f"Error: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ZackGPT CLI - Advanced AI Assistant Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cli/main.py                    # Interactive menu
  cli/main.py --chat             # Direct to chat mode
  cli/main.py --voice            # Direct to voice mode  
  cli/main.py --dev              # Direct to dev tools
        """
    )
    
    parser.add_argument(
        '--chat', 
        action='store_true',
        help='Start in chat mode directly'
    )
    
    parser.add_argument(
        '--voice',
        action='store_true', 
        help='Start in voice mode directly'
    )
    
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Start development tools directly'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='ZackGPT CLI 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Route to appropriate mode
    if args.chat:
        run_chat_mode()
    elif args.voice:
        run_voice_mode()
    elif args.dev:
        run_dev_tools()
    else:
        run_interactive_menu()


if __name__ == "__main__":
    main() 