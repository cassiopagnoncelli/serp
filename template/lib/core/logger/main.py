import os
import logging
import pathlib
from logging.handlers import RotatingFileHandler

from app.config.settings import get_settings

settings = get_settings()
app_env = settings.APP_ENV

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

PROJECT_ROOT = pathlib.Path(".")
LOG_DIR = PROJECT_ROOT / "log"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"{app_env}.log"

def setup_logger():
    """
    Set up and configure the logger
    """
    # Create a logger
    logger = logging.getLogger("app_logger")
    
    # Set the log level
    logger.setLevel(LOG_LEVELS.get(DEFAULT_LOG_LEVEL, logging.INFO))
    
    # Create handlers
    # File handler with rotation (10MB max size, keep 5 backup files)
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    
    # Create formatters and add them to handlers
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize the logger
logger = setup_logger()

def log(message, level="info"):
    """
    Log a message with the specified level
    
    Args:
        message (str): The message to log
        level (str): The log level (debug, info, warning, error, critical)
    """
    level = level.lower()
    
    if level == "debug":
        logger.debug(message)
    elif level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    elif level == "critical":
        logger.critical(message)
    else:
        # Default to info if an invalid level is provided
        logger.info(message)

# Export the log function
__all__ = ["log"]
