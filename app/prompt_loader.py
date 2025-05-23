import os

PROMPT_DIR = "prompts"

PROMPT_MAP = {
    "core_assistant": None  # can define overrides like "fin_assistant": "You are..."
}

def load_prompt(agent: str, variables: dict = None) -> str:
    if agent in PROMPT_MAP and PROMPT_MAP[agent]:
        prompt_template = PROMPT_MAP[agent]
    else:
        path = os.path.join(PROMPT_DIR, f"{agent}.txt")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt for agent '{agent}' not found in PROMPT_MAP or {path}")
        with open(path, "r") as f:
            prompt_template = f.read()

    if variables:
        for key, val in variables.items():
            placeholder = f"{{{{{key}}}}}"
            prompt_template = prompt_template.replace(placeholder, val.strip())

    return prompt_template
