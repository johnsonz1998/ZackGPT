import logging
from pathlib import Path

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
