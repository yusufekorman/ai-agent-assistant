import logging
import os
from datetime import datetime

class CustomLogger:
    def __init__(self):
        # Create log directory
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Daily log file name
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(self.log_dir, f"assistant_{current_date}.log")

        # Configure logger
        self.logger = logging.getLogger("AIAssistant")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Set format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        """Log at debug level"""
        self.logger.debug(message)

    def info(self, message):
        """Log at info level"""
        self.logger.info(message)

    def warning(self, message):
        """Log at warning level"""
        self.logger.warning(message)

    def error(self, message):
        """Log at error level"""
        self.logger.error(message)

    def critical(self, message):
        """Log at critical level"""
        self.logger.critical(message)

    def log_exception(self, exc_type, exc_value, exc_traceback):
        """Log an exception"""
        self.logger.error(
            "Exception occurred",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

# Singleton instance
_logger_instance = None

def get_logger():
    """Return logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = CustomLogger()
    return _logger_instance