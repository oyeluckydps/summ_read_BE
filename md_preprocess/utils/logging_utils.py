"""
Logging utilities for MD Preprocess library.
"""

import logging
from typing import Optional


def setup_logger(
    name: str = "md_preprocess", 
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging with appropriate formatting.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional path to log file
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_progress(message: str, level: str = "info") -> None:
    """
    Log progress message with specified level.
    
    Args:
        message: Message to log
        level: Logging level (info, warning, error, debug)
    """
    logger = logging.getLogger("md_preprocess")
    
    # Map level string to logging method
    if level.lower() == "info":
        logger.info(message)
    elif level.lower() == "warning":
        logger.warning(message)
    elif level.lower() == "error":
        logger.error(message)
    elif level.lower() == "debug":
        logger.debug(message)
    else:
        # Default to info
        logger.info(message)
        
    # Print to console for immediate feedback
    if level.lower() == "error":
        print(f"ERROR: {message}")
    else:
        print(message)