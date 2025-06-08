def optimize_prompt(task_type: str, input_text: str, memory_block: str) -> str:
    prompt = f"""
You are a prompt engineer.

Your task is to craft the most effective system/user prompt for the model to perform this task:
- Task: {task_type}

User input: {input_text}
Relevant memory: {memory_block}

Return ONLY the optimized prompt to send to the assistant.
"""
    return run_local_model(prompt)


def run_local_model(prompt: str) -> str:
    # TEMP: using OpenAI as a stand-in until local model is integrated
    from app.query_utils import ask_gpt
    return ask_gpt(prompt)
