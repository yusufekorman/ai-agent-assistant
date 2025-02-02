import logging
import os
from datetime import datetime

class CustomLogger:
    def __init__(self):
        # Log dizini oluştur
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Günlük log dosyası adı
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(self.log_dir, f"assistant_{current_date}.log")

        # Logger'ı yapılandır
        self.logger = logging.getLogger("AIAssistant")
        self.logger.setLevel(logging.DEBUG)

        # Dosya handler'ı
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Konsol handler'ı
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Format belirle
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Handler'ları ekle
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        """Debug seviyesinde log"""
        self.logger.debug(message)

    def info(self, message):
        """Info seviyesinde log"""
        self.logger.info(message)

    def warning(self, message):
        """Warning seviyesinde log"""
        self.logger.warning(message)

    def error(self, message):
        """Error seviyesinde log"""
        self.logger.error(message)

    def critical(self, message):
        """Critical seviyesinde log"""
        self.logger.critical(message)

    def log_exception(self, exc_type, exc_value, exc_traceback):
        """Exception logla"""
        self.logger.error(
            "Exception occurred",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

# Singleton instance
_logger_instance = None

def get_logger():
    """Logger instance'ı döndür"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = CustomLogger()
    return _logger_instance