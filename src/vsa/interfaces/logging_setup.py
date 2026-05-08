"""
Logging setup for VSA Phase2-Core

Configures structlog with JSON output and optional file handler.
"""

import structlog
import logging
import sys
from typing import Optional

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup structlog configuration
    
    Args:
        log_level: Log level (DEBUG/INFO/WARNING/ERROR)
        log_file: Optional log file path
    """
    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    if log_level.upper() not in valid_levels:
        log_level = "INFO"
    
    log_level_int = getattr(logging, log_level.upper())
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level_int,
    )
    
    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level_int)
        logging.getLogger().addHandler(file_handler)
    
    logger = structlog.get_logger(__name__)
    logger.info("Logging initialized", log_level=log_level)
