import logging
import json
from datetime import datetime
from functools import wraps

class StructuredLogger:
    def __init__(self, name="PaySure"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers if logger is imported multiple times
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)

    def _log(self, level, event, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "event": event,
            **kwargs
        }
        
        # Serialize dict to JSON string for structured output
        message = json.dumps(log_entry)
        
        if level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)

    def info(self, event, **kwargs):
        self._log("INFO", event, **kwargs)

    def warning(self, event, **kwargs):
        self._log("WARNING", event, **kwargs)

    def error(self, event, **kwargs):
        self._log("ERROR", event, **kwargs)

# Singleton instance to be used across the app
logger = StructuredLogger()
