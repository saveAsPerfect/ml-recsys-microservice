import logging
import sys
from app.config import LOG_LEVEL, LOG_FORMAT


def setup_logging():
    """Setup logging configuration for the application"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )

    # Set specific loggers
    loggers = [
        'app.api',
        'app.core',
        'app.db',
        'sqlalchemy.engine',
        'uvicorn.access'
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper()))


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)
