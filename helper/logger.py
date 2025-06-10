import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_logger(name=None, level=None):
    """
    Configure and return a logger with file and console handlers.
    
    :param name: Name of the logger (optional)
    :param level: Logging level (optional, defaults to DEBUG or INFO based on settings)
    :return: Configured logger
    """
    try:
        # Get configuration from environment variables
        debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        logs_dir = os.getenv('LOGS_DIR', './logs')
        
        # Ensure log directory exists
        os.makedirs(logs_dir, exist_ok=True)

        # Create logger
        logger = logging.getLogger(name) if name else logging.getLogger()
        
        # Clear existing handlers to prevent duplicates
        logger.handlers = []

        # Set log level
        if level is None:
            level = logging.DEBUG if debug_mode else logging.INFO
        logger.setLevel(level)

        # Common formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Info log handler (captures INFO and WARNING)
        info_handler = RotatingFileHandler(
            filename=os.path.join(logs_dir, 'info.log'),
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5
        )
        info_handler.setLevel(logging.INFO)
        info_handler.addFilter(lambda record: record.levelno <= logging.WARNING)
        info_handler.setFormatter(formatter)

        # Error log handler
        error_handler = RotatingFileHandler(
            filename=os.path.join(logs_dir, 'error.log'),
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(info_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

        return logger

    except Exception as e:
        print(f"Failed to configure logging: {e}")
        raise 