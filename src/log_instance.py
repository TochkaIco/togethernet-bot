"""Singleton logger instance for the TogetherNet bot.

Both `src.bot` and any other modules can import this to get a shared
configured logger without creating circular imports.
"""

from .logger import setup_logging

# Create a module‑level logger that is configured once.
logger = setup_logging()
