import config

def build_prompt(input_text: str, memory_block: str, system_goal: str = "") -> str:
    """
    Constructs the full prompt for GPT from input + memory + system goal.
    """
    system_header = config.DEFAULT_PERSONALITY
    if system_goal:
        system_header += f"\n\nSystem Goal: {system_goal}"

    prompt = f"""{system_header}

{memory_block}

User: {input_text}
Assistant:"""

    return prompt