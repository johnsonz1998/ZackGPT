import os
from pathlib import Path
import config

# Point to /ZACKGPT/prompts instead of app/prompts
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

PROMPT_MAP = {
    "core_assistant": None  # can define overrides like "fin_assistant": "You are..."
}

def load_prompt(agent: str, variables: dict = None) -> str:
    """
    Load a prompt template for the specified agent and fill in any variables.
    Args:
        agent: The name of the agent (e.g. 'core_assistant')
        variables: Dictionary of variables to fill in the prompt template
    Returns:
        The filled prompt template as a string
    """
    prompt_file = PROMPTS_DIR / f"{agent}.txt"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    with open(prompt_file, 'r') as f:
        prompt = f.read()
    if variables:
        prompt = prompt.format(**variables)
    return prompt

def build_prompt(input_text: str, memory_block: str, system_goal: str = "") -> str:
    """
    Constructs the full prompt for GPT from input + memory + system goal.
    """
    system_header = config.DEFAULT_PERSONALITY
    if system_goal:
        system_header += f"\n\nSystem Goal: {system_goal}"
    prompt = f"""{system_header}\n\n{memory_block}\n\nUser: {input_text}\nAssistant:"""
    return prompt 