import os
import logging
from pathlib import Path
from typing import Any, Optional
from datetime import datetime
import json

# Create logs dir if not exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Set up logger
logger = logging.getLogger("zackgpt")
logger.setLevel(logging.DEBUG)  # Set to INFO or WARNING for production

handler = logging.FileHandler(log_dir / "dev.log")
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# Avoid adding duplicate handlers
if not logger.hasHandlers():
    logger.addHandler(handler)

# Quick aliases
log_debug = logger.debug
log_info = logger.info
log_warn = logger.warning
log_error = logger.error

# Get DEBUG_MODE from environment
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

def _sanitize_sensitive_data(data: Any) -> Any:
    """Sanitize sensitive data before logging."""
    if isinstance(data, str):
        # Hide API keys
        if "sk-" in data:
            return "sk-***"
        # Hide proxy information
        if any(x in data.lower() for x in ["proxy", "http_proxy", "https_proxy"]):
            return "***"
    elif isinstance(data, dict):
        return {k: _sanitize_sensitive_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_sanitize_sensitive_data(item) for item in data]
    return data

def debug_log(message: str, data: Optional[Any] = None, prefix: str = "🔍") -> None:
    """
    Log debug messages only when DEBUG_MODE is enabled.
    Args:
        message: The debug message to log
        data: Optional data to log (will be formatted as JSON if dict/list)
        prefix: Optional emoji prefix for the message
    """
    if not DEBUG_MODE:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = f"{prefix} [{timestamp}] {message}"
    if data is not None:
        sanitized_data = _sanitize_sensitive_data(data)
        if isinstance(sanitized_data, (dict, list)):
            output += f"\n{json.dumps(sanitized_data, indent=2)}"
        else:
            output += f"\n{sanitized_data}"
    print(output)

def debug_error(message: str, error: Optional[Exception] = None) -> None:
    if not DEBUG_MODE:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = f"❌ [{timestamp}] {message}"
    if error:
        output += f"\nError details: {str(error)}"
    print(output)

def debug_success(message: str, data: Optional[Any] = None) -> None:
    if not DEBUG_MODE:
        return
    debug_log(message, data, prefix="✅")

def debug_warning(message: str, data: Optional[Any] = None) -> None:
    if not DEBUG_MODE:
        return
    debug_log(message, data, prefix="⚠️")

def debug_info(message: str, data: Optional[Any] = None) -> None:
    if not DEBUG_MODE:
        return
    debug_log(message, data, prefix="ℹ️")
