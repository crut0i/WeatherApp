import json
import logging


class JsonFormatter(logging.Formatter):
    """
    Custom formatter for JSON logging
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record

        Args:
            record (logging.LogRecord): Log record

        Returns:
            str: Formatted log record
        """

        if hasattr(record, "levelname"):
            record.levelname_padded = f"{record.levelname:<9}"

        if isinstance(record.msg, dict):
            record.msg = json.dumps(record.msg, separators=(",", ":"))
        else:
            record.msg = json.dumps(record.msg.replace('"', "'"))
        return super().format(record)
