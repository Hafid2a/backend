import logging
import sys
import json
from app.core.config import settings


def setup_logging() -> logging.Logger:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    class JSONFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_entry: dict = {
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
            }
            if record.exc_info:
                log_entry["exc_info"] = self.formatException(record.exc_info)
            return json.dumps(log_entry, ensure_ascii=False)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    return root_logger


logger = logging.getLogger("najd")
