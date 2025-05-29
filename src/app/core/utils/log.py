import os
import json

from typing import Any
from pathlib import Path
from fastapi import HTTPException

from app.core.connectors.config import config


class LogUtils:
    def __init__(self):
        self._logs_dir = Path(config.log_path)
        self._logs_dir.mkdir(parents=True, exist_ok=True)

    def __get_files(self, pattern: str) -> list[str]:
        """
        Get list of available log files

        Args:
            pattern (str): Pattern to match log files

        Returns:
            list[str]: List of log files
        """

        return [f.name for f in self._logs_dir.glob(pattern)]

    def __parse_exception(self, exception_text: str) -> dict[str, Any]:
        """
        Parse exception text into structured JSON format

        Args:
            exception_text (str): Exception text

        Returns:
            dict[str, Any]: Structured JSON format
        """

        lines = exception_text.strip().split("\n")
        if not lines:
            return {}

        request_id = lines[0].strip("[]")
        traceback_lines = []
        error_message = ""

        for line in lines[1:]:
            if line.startswith("Traceback"):
                continue
            if line.startswith("Exception:"):
                error_message = line.replace("Exception:", "").strip()
                break
            traceback_lines.append(line.strip())

        return {
            "request_id": request_id,
            "error_message": error_message,
            "traceback": traceback_lines,
            "level": "ERROR",
        }

    def get_available_dates(self, pattern: str = "log_*.log") -> list[str]:
        """
        Get list of available log dates

        Args:
            pattern (str): Pattern to match log files

        Returns:
            list[str]: List of log dates
        """

        log_files = self.__get_files(pattern)
        dates = []
        for log_file in log_files:
            try:
                date = log_file.replace(pattern.split("*")[0], "").replace(
                    pattern.split("*")[1], ""
                )
                dates.append(date)
            except ValueError:
                continue
        return sorted(dates, reverse=True)

    def get_log_content(self, date: str, pattern: str = "log") -> dict[str, Any]:
        """
        Get content of log file for specific date

        Args:
            date (str): Date to get log content for
            pattern (str): Pattern to match log files

        Returns:
            dict[str, Any]: Structured log data with metadata
        """

        log_file = self._logs_dir / f"{pattern}_{date}.log"
        if not log_file.exists():
            raise HTTPException(status_code=404, detail="log file not found")

        logs = []
        current_exception = []

        with open(log_file, encoding="utf-8") as f:
            for line in f:
                if line.strip() == "------------------":
                    if current_exception:
                        exception_json = self.__parse_exception("\n".join(current_exception))
                        if exception_json:
                            logs.append(exception_json)
                        current_exception = []
                    continue

                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    current_exception.append(line)

            if current_exception:
                exception_json = self.__parse_exception("\n".join(current_exception))
                if exception_json:
                    logs.append(exception_json)

        return {
            "status": "success",
            "date": date,
            "total_entries": len(logs),
            "entries": logs,
            "metadata": {
                "error_count": sum(
                    1 for log in logs if isinstance(log, dict) and log.get("level") == "ERROR"
                ),
                "info_count": sum(
                    1 for log in logs if isinstance(log, dict) and log.get("level") == "INFO"
                ),
                "warning_count": sum(
                    1 for log in logs if isinstance(log, dict) and log.get("level") == "WARNING"
                ),
                "debug_count": sum(
                    1 for log in logs if isinstance(log, dict) and log.get("level") == "DEBUG"
                ),
            },
        }

    def delete_log(self, date: str, pattern: str = "log") -> dict[str, str]:
        """
        Delete log file for specific date

        Args:
            date (str): Date to delete log file for
            pattern (str): Pattern to match log files

        Returns:
            dict[str, str]: Message
        """

        log_file = self._logs_dir / f"{pattern}_{date}.log"
        if not log_file.exists():
            raise HTTPException(status_code=404, detail="log file not found")

        os.remove(log_file)

        return {
            "status": "success",
            "message": f"log file for date {date} deleted successfully",
        }
