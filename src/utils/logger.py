import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name: str, log_file: str = "app.log"):
    """Configure and return a logger instance"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)

    # File Handler
    file_handler = RotatingFileHandler(
        log_dir / log_file,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger 