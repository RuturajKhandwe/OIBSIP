"""
Logging system for Voice Assistant.
Configures structured console and file output.
"""

import logging
import sys
from config import Config

def get_logger(name: str) -> logging.Logger:
    """Creates and returns a configured logger instance."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO))
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%H:%M:%S")
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

    return logger
