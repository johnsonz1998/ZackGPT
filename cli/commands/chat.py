#!/usr/bin/env python3
"""
ZackGPT CLI Chat Mode
Text-based interactive chat interface
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from dotenv import load_dotenv
from app.core_assistant import CoreAssistant
from app.logger import debug_info, debug_success
from cli.utils.output import print_success, print_error, print_info, print_banner

def run_text_mode():
    """Run the text interaction mode."""
    # Load environment variables
    load_dotenv()
    
    # Ensure debug mode is on
    os.environ["DEBUG_MODE"] = "True"
    
    # Initialize assistant
    assistant = CoreAssistant()
    debug_success("Assistant initialized")
    
    print_banner()
    print_info("ZackGPT CLI Chat Mode")
    print_info("Type 'exit' to quit")
    print()
    
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
            print(f"AI: {response}")
            
            # Get simple rating
            try:
                rating_input = input("Rating (0-5): ").strip()
                if rating_input and rating_input.isdigit():
                    rating = int(rating_input)
                    if 0 <= rating <= 5:
                        debug_info(f"👤 User provided rating: {rating}/5", {
                            "rating_value": rating,
                            "will_trigger_learning": rating > 0,
                            "response_preview": response[:50] + "..." if len(response) > 50 else response
                        })
                        
                        # Convert to quality assessment format
                        user_assessment = {
                            "overall_score": rating / 5.0,
                            "success": rating >= 3,
                            "user_rating": rating,
                            "assessment_type": "user_rating"
                        }
                        
                        # Record the feedback
                        if hasattr(assistant, 'prompt_builder') and assistant.prompt_builder.current_prompt_metadata:
                            debug_info("🔄 Feeding rating into learning system", {
                                "metadata_available": True,
                                "components_to_update": list(assistant.prompt_builder.current_prompt_metadata.get('components', {}).keys()),
                                "learning_impact": "high" if rating in [1,2,4,5] else "moderate"
                            })
                            
                            assistant.prompt_builder.record_response_feedback(
                                assistant.prompt_builder.current_prompt_metadata,
                                user_assessment
                            )
                            
                            debug_success("✅ Learning update complete", {
                                "rating_processed": f"{rating}/5",
                                "system_learning": "active"
                            })
                        else:
                            debug_info("⚠️ No prompt metadata available for learning")
                    else:
                        debug_info("❌ Invalid rating provided", {"input": rating_input})
                else:
                    debug_info("⏭️ No rating provided, skipping learning update")
            except (ValueError, KeyboardInterrupt):
                debug_info("⏭️ Rating interrupted or invalid, continuing without feedback")
                pass  # Skip rating if invalid input or user interrupts
            
            print()  # Add spacing
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            debug_info("Error in main loop", str(e))
            print("I encountered an error. Please try again.")

if __name__ == "__main__":
    run_text_mode() 