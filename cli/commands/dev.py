#!/usr/bin/env python3
"""
ZackGPT CLI Development Tools
Development and testing utilities for ZackGPT
"""

import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from config import config
from voice import whisper_listener
import voice.elevenlabs as eleven
import voice.tts_mac as mac
from config import config_profiles as profiles
from app.query_utils import load_index
from cli.utils.output import print_success, print_error, print_info, print_banner, get_user_choice, confirm_action

# Stubs for removed memory_engine functions
def get_context_block(max_items):
    return ""
def get_conversation_history():
    return []
def clear_conversation_history():
    pass

def show_dev_menu():
    print("\n🛠️  ZackGPT Dev Menu\n")
    print("CONFIGURATION")
    print("1. Change Whisper model")
    print("2. Set Voice Engine")
    print("3. Choose ElevenLabs voice")
    print("4. Set macOS voice")
    print("5. Modify assistant tone")
    print("6. Save current config as profile")
    print("7. Load config profile")
    print("8. Reset to default profile")

    print("\nMEMORY TOOLS")
    print("9. View long-term memory log")
    print("10. View short-term conversation history")
    print("11. Clear conversation history")
    print("12. Clear memory log")
    
    print("\nPROMPT EVOLUTION")
    print("17. View prompt evolution stats")
    print("18. Export prompt training data")
    print("19. Test prompt enhancement system")
    print("20. Generate enhanced prompt component")
    print("21. View prompt enhancer stats")

    print("\nTEST MODE")
    print("13. Run one-off voice interaction")
    print("14. Run one-off text interaction")

    print("\nFULL INTERACTION")
    print("15. Run full text interaction loop")
    print("16. Enter full voice assistant mode")

    print("\n0. Exit")

    choice = input("Select an option: ").strip()

    if choice == "1":
        print("\n🎙️ Select Transcription Engine:")
        print("1. Faster-Whisper (fast, less accurate)")
        print("2. OpenAI Whisper (slower, more accurate)")
        engine_input = input("Enter engine option: ").strip()
        if engine_input == "1":
            config.TRANSCRIBE_ENGINE = "faster-whisper"
        elif engine_input == "2":
            config.TRANSCRIBE_ENGINE = "openai-whisper"
        else:
            print("❌ Invalid engine option.")
            return

        print(f"✅ Transcription engine set to {config.TRANSCRIBE_ENGINE}")
        models = ["tiny", "base", "small", "medium"]
        if config.TRANSCRIBE_ENGINE == "faster-whisper":
            models.append("large-v2")
        else:
            models.append("large")
        print("\n🎛️ Available models:")
        for i, name in enumerate(models, 1):
            print(f"{i}. {name}")
        model_input = input("Choose model number or type custom name: ").strip()
        if model_input.isdigit() and 1 <= int(model_input) <= len(models):
            config.WHISPER_MODEL = models[int(model_input) - 1]
        else:
            config.WHISPER_MODEL = model_input
        whisper_listener.reload_whisper_model()
        print("✅ Whisper model set to", config.WHISPER_MODEL)

    elif choice == "2":
        print("\n🎙️ Choose Voice Engine:")
        print("1. ElevenLabs")
        print("2. macOS (say command)")
        sub = input("Enter option: ").strip()
        config.USE_ELEVENLABS = sub == "1"
        print("✅ Voice engine set to", "ElevenLabs" if config.USE_ELEVENLABS else "macOS")

    elif choice == "3":
        print("\n🎤 Select ElevenLabs Voice:")
        voices = {
            "1": ("Rachel", "21m00Tcm4TlvDq8ikWAM"),
            "2": ("Domi", "AZnzlk1XvdvUeBnXmlld"),
            "3": ("Antoni", "ErXwobaYiN019PkySvjV"),
            "4": ("Custom input", None)
        }
        for key, (name, vid) in voices.items():
            print(f"{key}. {name}" + (f" — {vid}" if vid else ""))
        sub = input("Choose voice: ").strip()
        if sub in voices and voices[sub][1]:
            config.ELEVENLABS_VOICE_ID = voices[sub][1]
        elif sub == "4":
            config.ELEVENLABS_VOICE_ID = input("Paste custom ElevenLabs Voice ID: ").strip()
        print("✅ Voice ID set to", config.ELEVENLABS_VOICE_ID)

    elif choice == "4":
        config.MACOS_VOICE = input("Enter new macOS voice: ").strip()

    elif choice == "5":
        config.DEFAULT_PERSONALITY = input("Enter new assistant tone: ").strip()

    elif choice == "6":
        profile_name = input("Enter a name for this profile: ").strip().lower().replace(" ", "_")
        os.makedirs("config/profiles", exist_ok=True)
        profile_path = f"config/profiles/{profile_name}.json"
        settings = {
            "TRANSCRIBE_ENGINE": config.TRANSCRIBE_ENGINE,
            "WHISPER_MODEL": config.WHISPER_MODEL,
            "USE_ELEVENLABS": config.USE_ELEVENLABS,
            "ELEVENLABS_VOICE_ID": config.ELEVENLABS_VOICE_ID,
            "MACOS_VOICE": config.MACOS_VOICE,
            "DEFAULT_PERSONALITY": config.DEFAULT_PERSONALITY
        }
        with open(profile_path, "w") as f:
            json.dump(settings, f, indent=2)
        print(f"✅ Saved config to {profile_path}")

    elif choice == "7":
        profiles_list = [f for f in os.listdir("config/profiles") if f.endswith(".json")]
        if not profiles_list:
            print("⚠️ No profiles found.")
            return
        print("\n📂 Available profiles:")
        for i, p in enumerate(profiles_list, 1):
            print(f"{i}. {p}")
        idx = input("Select a profile number: ").strip()
        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(profiles_list):
            print("❌ Invalid selection.")
            return
        with open(f"config/profiles/{profiles_list[int(idx) - 1]}", "r") as f:
            settings = json.load(f)
        config.TRANSCRIBE_ENGINE = settings.get("TRANSCRIBE_ENGINE", config.TRANSCRIBE_ENGINE)
        config.WHISPER_MODEL = settings.get("WHISPER_MODEL", config.WHISPER_MODEL)
        config.USE_ELEVENLABS = settings.get("USE_ELEVENLABS", config.USE_ELEVENLABS)
        config.ELEVENLABS_VOICE_ID = settings.get("ELEVENLABS_VOICE_ID", config.ELEVENLABS_VOICE_ID)
        config.MACOS_VOICE = settings.get("MACOS_VOICE", config.MACOS_VOICE)
        config.DEFAULT_PERSONALITY = settings.get("DEFAULT_PERSONALITY", config.DEFAULT_PERSONALITY)
        whisper_listener.reload_whisper_model()
        print("✅ Loaded profile:", profiles_list[int(idx) - 1])

    elif choice == "8":
        profiles.reset_to_default()

    elif choice == "9":
        from pathlib import Path

        print("\n📜 Long-Term Memory Files (latest 5):")
        memory_dir = config.MEMORY_DIR
        files = sorted(Path(memory_dir).glob("*.json"), reverse=True)

        if not files:
            print("📭 No memory files found.")
        else:
            for file in files[:5]:
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                        print(f"📄 {file.name}")
                        print(json.dumps(data, indent=2))
                        print("-" * 40)
                except Exception as e:
                    print(f"⚠️ Error reading {file.name}: {e}")

    elif choice == "10":
        print("\n💬 Short-Term Conversation History:")
        print(get_conversation_history())

    elif choice == "11":
        clear_conversation_history()
        print("🧹 Short-term conversation history cleared.")

    elif choice == "12":
        open(config.CHAT_LOG_PATH, "w").close()
        print("🧹 Memory log cleared.")

    elif choice == "13":
        run_test_interaction()

    elif choice == "14":
        os.system("python -m scripts.startup.main_text --once")

    elif choice == "15":
        os.system("python -m scripts.startup.main_text")

    elif choice == "16":
        print("🎤 Launching full voice assistant with current config...")
        os.makedirs("config/profiles", exist_ok=True)
        temp_profile = "__dev_temp_profile.json"
        with open(f"config/profiles/{temp_profile}", "w") as f:
            json.dump({
                "TRANSCRIBE_ENGINE": config.TRANSCRIBE_ENGINE,
                "WHISPER_MODEL": config.WHISPER_MODEL,
                "USE_ELEVENLABS": config.USE_ELEVENLABS,
                "ELEVENLABS_VOICE_ID": config.ELEVENLABS_VOICE_ID,
                "MACOS_VOICE": config.MACOS_VOICE,
                "DEFAULT_PERSONALITY": config.DEFAULT_PERSONALITY
            }, f, indent=2)
        os.system(f"python -m scripts.startup.main_voice config/profiles/{temp_profile}")

    elif choice == "17":
        from app.core_assistant import CoreAssistant
        assistant = CoreAssistant()
        stats = assistant.get_evolution_stats()
        
        print("\n🧬 Prompt Evolution Statistics:")
        print(f"Total Components: {stats.get('total_components', 0)}")
        print(f"Total Experiments: {stats.get('total_experiments', 0)}")
        success_rate = stats.get('recent_success_rate')
        if isinstance(success_rate, (int, float)):
            print(f"Recent Success Rate: {success_rate:.2%}")
        else:
            print(f"Recent Success Rate: {success_rate}")
        
        print("\nComponent Breakdown:")
        for comp_type, count in stats.get('component_breakdown', {}).items():
            avg_success = stats.get(f'{comp_type}_avg_success', 0)
            if isinstance(avg_success, (int, float)):
                print(f"  {comp_type}: {count} components (avg success: {avg_success:.2%})")
            else:
                print(f"  {comp_type}: {count} components")
        
        print("\nEvolution Settings:")
        settings = stats.get('settings', {})
        for key, value in settings.items():
            print(f"  {key}: {value}")

    elif choice == "18":
        import time
        print("📊 Exporting prompt training data...")
        try:
            evolution_file = "config/prompt_evolution/evolution_data.json"
            if os.path.exists(evolution_file):
                with open(evolution_file, "r") as f:
                    data = json.load(f)
                
                export_file = f"config/prompt_evolution/training_data_export_{int(time.time())}.json"
                with open(export_file, "w") as f:
                    json.dump(data, f, indent=2)
                
                print(f"✅ Exported training data to: {export_file}")
                print(f"Contains {len(data.get('experiments', []))} experiments")
            else:
                print("❌ No evolution data found.")
        except Exception as e:
            print(f"❌ Error exporting data: {e}")

    elif choice == "19":
        print("🤖 Testing Prompt Enhancement System...")
        try:
            from app.prompt_enhancer import HybridPromptEnhancer
            enhancer = HybridPromptEnhancer()
            
            user_input = input("Enter test user input: ").strip()
            response = input("Enter test assistant response: ").strip()
            
            if user_input and response:
                assessment = enhancer.assess_response_quality(response, user_input)
                print("\n📊 Assessment Results:")
                print(f"Overall Score: {assessment.get('overall_score', 'N/A'):.3f}")
                print(f"Success: {assessment.get('success', 'N/A')}")
                print(f"Issues: {assessment.get('issues', [])}")
                print(f"Reasoning: {assessment.get('reasoning', 'N/A')}")
                print(f"Assessment Type: {assessment.get('assessment_type', 'N/A')}")
                
                # Show transparency details for debugging
                if 'transparency' in assessment:
                    print("\n🔍 Debug Details:")
                    for key, value in assessment['transparency'].items():
                        print(f"  {key}: {value}")
            else:
                print("❌ Please provide both user input and response.")
        except Exception as e:
            print(f"❌ Error testing enhancement: {e}")

    elif choice == "20":
        print("🧠 Generating Enhanced Prompt Component...")
        try:
            from app.prompt_enhancer import HybridPromptEnhancer
            enhancer = HybridPromptEnhancer()
            
            print("Component types: personality, memory_guidelines, task_instructions, context_framers, output_formatters")
            comp_type = input("Enter component type: ").strip()
            
            if comp_type in ["personality", "memory_guidelines", "task_instructions", "context_framers", "output_formatters"]:
                print("Context options:")
                print("1. Technical/debugging")
                print("2. General conversation")
                print("3. Troubleshooting")
                context_choice = input("Choose context (1-3): ").strip()
                
                context_map = {
                    "1": {"conversation_type": "technical", "user_expertise": "high"},
                    "2": {"conversation_type": "general", "user_expertise": "medium"},
                    "3": {"conversation_type": "troubleshooting", "user_expertise": "medium"}
                }
                
                context = context_map.get(context_choice, {"conversation_type": "general", "user_expertise": "medium"})
                
                component = enhancer.generate_enhanced_component(comp_type, context)
                print(f"\n✨ Generated {comp_type} component:")
                print(f'"{component}"')
                
                # Show enhancer stats
                stats = enhancer.get_enhancement_stats()
                print(f"\n📊 Enhancement Stats:")
                print(f"  Cloud generations: {stats['cloud_generations']}")
                print(f"  Fallback generations: {stats['fallback_generations']}")
                print(f"  Cloud usage rate: {stats['efficiency']['cloud_usage_rate']:.2%}")
            else:
                print("❌ Invalid component type.")
        except Exception as e:
            print(f"❌ Error generating component: {e}")

    elif choice == "21":
        print("📊 Prompt Enhancement System Statistics:")
        try:
            from app.prompt_enhancer import HybridPromptEnhancer
            enhancer = HybridPromptEnhancer()
            stats = enhancer.get_enhancement_stats()
            
            print(f"\n🔢 Usage Statistics:")
            print(f"  Assessments performed: {stats['assessments_performed']}")
            print(f"  Components generated: {stats['components_generated']}")
            print(f"  Cloud generations: {stats['cloud_generations']}")
            print(f"  Local validations: {stats['local_checks']}")
            print(f"  Fallback generations: {stats['fallback_generations']}")
            
            print(f"\n⚙️ Configuration:")
            config_info = stats['config']
            print(f"  Cloud generation enabled: {config_info['cloud_generation_enabled']}")
            print(f"  Generation rate: {config_info['generation_rate']:.1%}")
            print(f"  Cloud model: {config_info['cloud_model']}")
            print(f"  Debug mode: {config_info['debug_mode']}")
            
            print(f"\n⚡ Efficiency Metrics:")
            efficiency = stats['efficiency']
            print(f"  Cloud usage rate: {efficiency['cloud_usage_rate']:.1%}")
            print(f"  Local validation rate: {efficiency['local_validation_rate']:.1%}")
            
            print(f"\n🤖 System Status:")
            print(f"  Local helper available: {stats['local_helper_available']}")
            
        except Exception as e:
            print(f"❌ Error getting enhancer stats: {e}")

    elif choice == "0":
        print("👋 Exiting test menu.")
        exit()

    else:
        print("❌ Invalid option.")

def run_test_interaction():
    from app.core_assistant import get_response
    index = load_index()
    question = input("🧪 Enter test question: ")
    response = get_response(user_input=question, agent="core_assistant")
    print("💬 Assistant:", response)
    speaker = eleven.speak if config.USE_ELEVENLABS else mac.speak
    try:
        parsed = json.loads(response)
        spoken_text = parsed["data"]["text"]
    except Exception:
        spoken_text = response
    speaker(spoken_text)

if __name__ == "__main__":
    print("🚀 Test config menu loaded.")
    while True:
        show_dev_menu()
        print()
