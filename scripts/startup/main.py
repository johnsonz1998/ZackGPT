import signal
import config
from voice.whisper_listener import listen_until_silence, reload_whisper_model
from llm.query_assistant import load_index, ask_gpt
from llm.context_engine import analyze_context
from app.core_assistant import get_response
from voice.elevenlabs import speak as eleven_speak
from voice.tts_mac import speak as mac_speak
from app.memory_engine import save_memory, get_context_block
from llm.prompt_builder import build_prompt

def get_speaker():
    return eleven_speak if config.USE_ELEVENLABS else mac_speak

def graceful_exit(sig, frame):
    exit(0)

def main():
    signal.signal(signal.SIGINT, graceful_exit)
    reload_whisper_model()
    index = load_index()

    while True:
        user_question = listen_until_silence()

        if not user_question:
            get_speaker()("Didn't catch that. Try again.")
            continue

        if user_question.lower() in {"quit", "exit"}:
            get_speaker()("Shutting down.")
            break

        try:
            tags = context_analysis.get("memory_tags", [])
            memory_context = get_context_block(config.MAX_CONTEXT_HISTORY, tags=tags)
            context_analysis = analyze_context(user_question, memory_context)
            system_goal = context_analysis.get("system_goal", "")

            prompt = build_prompt(user_question, memory_context, system_goal)
            response = ask_gpt(prompt)
            print(response)
            get_speaker()(response)
            save_memory(
                question=user_question,
                answer=response,
                tags=tags
            )

        except Exception as e:
            print(f"Error: {e}")
            get_speaker()("Something went wrong.")

if __name__ == "__main__":
    main()
