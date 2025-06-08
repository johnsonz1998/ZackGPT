#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv
from app.core_assistant import CoreAssistant
from app.logger import debug_info, debug_success

def run_text_mode():
    """Run the text interaction mode."""
    # Load environment variables
    load_dotenv()
    
    # Ensure debug mode is on
    os.environ["DEBUG_MODE"] = "True"
    
    # Initialize assistant
    assistant = CoreAssistant()
    debug_success("Assistant initialized")
    
    print("\n=== ZackGPT Text Mode ===")
    print("Type 'exit' to quit\n")
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input("YOU: ").strip()
            
            # Check for exit command
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nGoodbye!")
                break
                
            # Skip empty input
            if not user_input:
                continue
                
            # Get response
            response = assistant.process_input(user_input)
            print(f"AI: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            debug_info("Error in main loop", str(e))
            print("I encountered an error. Please try again.")

if __name__ == "__main__":
    run_text_mode() 