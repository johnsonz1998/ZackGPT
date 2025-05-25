import signal
import config
from voice.whisper_listener import listen_until_silence, reload_whisper_model
from llm.query_assistant import load_index, ask_gpt
from llm.context_engine import analyze_context
from voice.elevenlabs import speak as eleven_speak
from voice.tts_mac import speak as mac_speak
from app.memory_engine import save_memory, get_context_block
from llm.prompt_builder import build_prompt
from app.core_assistant import should_save_memory
import traceback
import json
import os
import sys

def get_speaker():
    return eleven_speak if config.USE_ELEVENLABS else mac_speak

def graceful_exit(sig, frame):
    print("\n👋 Exiting cleanly.")
    exit(0)

def load_profile(path):
    if not os.path.exists(path):
        print(f"⚠️ Profile not found at {path}. Skipping profile load.")
        return

    with open(path, "r") as f:
        settings = json.load(f)

    config.TRANSCRIBE_ENGINE = settings.get("TRANSCRIBE_ENGINE", config.TRANSCRIBE_ENGINE)
    config.WHISPER_MODEL = settings.get("WHISPER_MODEL", config.WHISPER_MODEL)
    config.USE_ELEVENLABS = settings.get("USE_ELEVENLABS", config.USE_ELEVENLABS)
    config.ELEVENLABS_VOICE_ID = settings.get("ELEVENLABS_VOICE_ID", config.ELEVENLABS_VOICE_ID)
    config.MACOS_VOICE = settings.get("MACOS_VOICE", config.MACOS_VOICE)
    config.DEFAULT_PERSONALITY = settings.get("DEFAULT_PERSONALITY", config.DEFAULT_PERSONALITY)

    reload_whisper_model()
    print(f"✅ Loaded profile from {path}")

def run_voice_loop():
    index = load_index()
    print("\n🎙️ ZackGPT is live. Speak to begin or say 'quit' to exit.\n")
    while True:
        user_question = listen_until_silence()

        if not user_question:
            get_speaker()("Didn't catch that. Try again.")
            continue

        if user_question.lower() in {"quit", "exit"}:
            get_speaker()("Shutting down.")
            break

        try:
            print(f"YOU: {user_question}")

            memory_context = get_context_block(config.MAX_CONTEXT_HISTORY)
            context_analysis = analyze_context(user_question, memory_context)
            tags = context_analysis.get("memory_tags", [])
            system_goal = context_analysis.get("system_goal", "")

            prompt = build_prompt(user_question, memory_context, system_goal)
            response = ask_gpt(prompt)

            print(f"AI: {response}\n")
            get_speaker()(response)

            if config.MEMORY_MODE == "all":
                save_memory(question=user_question, answer=response, tags=tags)
            elif config.MEMORY_MODE == "ai":
                decision = should_save_memory(user_question, response)
                if decision and decision.get("remember") is True:
                    save_memory(
                        question=user_question,
                        answer=response,
                        tags=decision.get("tags", []),
                        importance=decision.get("importance", "medium"),
                        context=decision.get("context")
                    )

        except Exception as e:
            print("⚠️ Error during response generation:")
            traceback.print_exc()
            get_speaker()("Something went wrong.")

def main():
    signal.signal(signal.SIGINT, graceful_exit)

    profile_arg = next((arg for arg in sys.argv[1:] if arg.endswith(".json")), None)
    if profile_arg:
        load_profile(profile_arg)
    else:
        load_profile(os.path.join("profiles", "default.json"))

    if "--text" in sys.argv:
        if "--once" in sys.argv:
            question = input("YOU: ")
            memory_context = get_context_block(config.MAX_CONTEXT_HISTORY)
            context_analysis = analyze_context(question, memory_context)
            tags = context_analysis.get("memory_tags", [])
            system_goal = context_analysis.get("system_goal", "")
            prompt = build_prompt(question, memory_context, system_goal)
            response = ask_gpt(prompt)
            print("AI:", response)
            if config.MEMORY_MODE == "all":
                save_memory(question=question, answer=response, tags=tags)
            elif config.MEMORY_MODE == "ai":
                decision = should_save_memory(question, response)
                if decision and decision.get("remember") is True:
                    save_memory(
                        question=question,
                        answer=response,
                        tags=decision.get("tags", []),
                        importance=decision.get("importance", "medium"),
                        context=decision.get("context")
                    )
        else:
            while True:
                question = input("YOU: ").strip()
                if question.lower() in {"exit", "quit"}:
                    print("👋 Goodbye.")
                    break

                memory_context = get_context_block(config.MAX_CONTEXT_HISTORY)
                context_analysis = analyze_context(question, memory_context)
                tags = context_analysis.get("memory_tags", [])
                system_goal = context_analysis.get("system_goal", "")
                prompt = build_prompt(question, memory_context, system_goal)
                response = ask_gpt(prompt)
                print("AI:", response)
                if config.MEMORY_MODE == "all":
                    save_memory(question=question, answer=response, tags=tags)
                elif config.MEMORY_MODE == "ai":
                    decision = should_save_memory(question, response)
                    if decision and decision.get("remember") is True:
                        save_memory(
                            question=question,
                            answer=response,
                            tags=decision.get("tags", []),
                            importance=decision.get("importance", "medium"),
                            context=decision.get("context")
                        )
    else:
        run_voice_loop()

if __name__ == "__main__":
    main()
