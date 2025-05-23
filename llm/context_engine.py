import json
from llm.local_llm import run_local_model

def analyze_context(input_text: str, memory_summary: str = "") -> dict:
    prompt = f"""
You are the context engine for a local AI assistant.

Your job is to analyze the user input and decide:
- What kind of task is this? (e.g. "chat", "plan", "reflect", "retrieve", "generate")
- Which memory tags are most relevant to this input?
- What system goal should guide the assistant's response?

Respond ONLY with a JSON object like this:
{{
  "intent": "plan",
  "memory_tags": ["goals", "projects"],
  "system_goal": "Help Zack make a weekly plan"
}}

User input:
\"\"\"{input_text}\"\"\"

Memory summary:
\"\"\"{memory_summary}\"\"\"
"""

    try:
        result = run_local_model(prompt)
        return json.loads(result)
    except Exception as e:
        print(f"⚠️ Context engine failed: {e}")
        return {
            "intent": "chat",
            "memory_tags": [],
            "system_goal": ""
        }
