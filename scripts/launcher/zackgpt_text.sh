#!/bin/bash

# Set default environment variables if not provided
export DEBUG_MODE=${DEBUG_MODE:-"true"}
export LLM_MODEL=${LLM_MODEL:-"gpt-4"}
export LLM_TEMPERATURE=${LLM_TEMPERATURE:-"0.7"}

# Activate virtual environment
source .venv/bin/activate

# Run text mode
python3 scripts/startup/main_text.py 