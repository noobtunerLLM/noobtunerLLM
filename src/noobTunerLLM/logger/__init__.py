from datetime import datetime
import logging
import os
import sys
from pathlib import Path

from noobTunerLLM.constants import LOG_FILE_DIR, LOG_FILE_NAME

class CustomLogger:
    """
    CustomLogger class with clearly identifiable components in log messages.
    Format: [timestamp] python_script:line_number - LOG_LEVEL - message
    """
    
    def __init__(self):
        # Create logs directory in root
        LOG_FILE_DIR.mkdir(exist_ok=True)
        
        # Set log file path
        self.log_filepath = LOG_FILE_DIR / LOG_FILE_NAME
        
        # Create formatter with clear component separation
        self.log_format = "[%(asctime)s] %(pathname)s:%(lineno)d - %(levelname)s - %(message)s"
        
        # Custom formatter to show only the script name instead of full path
        class ScriptNameFormatter(logging.Formatter):
            def format(self, record):
                # Extract just the script name from the full path
                record.pathname = os.path.basename(record.pathname)
                return super().format(record)
        
        self.formatter = ScriptNameFormatter(
            self.log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create logger
        self.logger = logging.getLogger("noobTunerLLM")
        self.logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        self.logger.handlers = []
        
        # File handler
        file_handler = logging.FileHandler(str(self.log_filepath))
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """Log info level messages"""
        self.logger.info(message)
    
    def error(self, message):
        """Log error level messages"""
        self.logger.error(message)
    
    def debug(self, message):
        """Log debug level messages"""
        self.logger.debug(message)
    
    def warning(self, message):
        """Log warning level messages"""
        self.logger.warning(message)
    
    def critical(self, message):
        """Log critical level messages"""
        self.logger.critical(message)

# Create singleton instance
logger = CustomLogger()

# Export logger instance
__all__ = ['logger']