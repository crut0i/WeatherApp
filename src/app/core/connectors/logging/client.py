import os
import sys
import logging
import colorlog

from typing import Any
from rich import traceback
from functools import wraps
from datetime import datetime
from traceback import format_tb
from collections.abc import Callable

from .formatters import JsonFormatter
from app.core.connectors.config import config


class Logging:
    """
    Logger class for handling application logging
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return

        self.initialized = True
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self._setup_logging()

    def _setup_logging(self) -> None:
        """
        Setup logging handlers and formatters
        """

        log_errors_directory = os.path.abspath(config.log_path)
        log_errors_file = os.path.join(log_errors_directory, f"log_{self.current_date}.log")
        traceback_file = os.path.join(log_errors_directory, f"exception_{self.current_date}.log")

        os.makedirs(log_errors_directory, exist_ok=True)

        traceback.install(show_locals=True)

        # Main log formatters
        default_formatter = JsonFormatter(
            '{"level": "%(levelname_padded)s", "time": "%(asctime)s", "content": %(message)s}',
            datefmt="%Y-%m-%d %H:%M",
        )
        color_formatter = colorlog.ColoredFormatter(
            '{"level": "%(log_color)s[%(levelname)s]%(reset)s", "time": "%(blue)s%(asctime)s%(reset)s", "content": %(white)s%(message)s%(reset)s}',  # noqa: E501
            datefmt="%Y-%m-%d %H:%M",
        )

        # Main log handlers
        self.file_handler = logging.FileHandler(log_errors_file, delay=True, encoding="utf-8")
        self.stream_handler = colorlog.StreamHandler(sys.stdout)
        self.file_handler.setFormatter(default_formatter)
        self.stream_handler.setFormatter(color_formatter)

        # Traceback handler
        self.traceback_handler = logging.FileHandler(traceback_file, delay=True, encoding="utf-8")

        # Main logger
        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.INFO)

        # Remove existing handlers to prevent double logging
        for handler in self.__logger.handlers[:]:
            self.__logger.removeHandler(handler)

        self.__logger.addHandler(self.file_handler)
        self.__logger.addHandler(self.stream_handler)

        # Traceback logger
        self.__traceback_logger = logging.getLogger("traceback")
        self.__traceback_logger.setLevel(logging.ERROR)

        # Remove existing handlers to prevent double logging
        for handler in self.__traceback_logger.handlers[:]:
            self.__traceback_logger.removeHandler(handler)

        self.__traceback_logger.addHandler(self.traceback_handler)
        self.__traceback_logger.propagate = False

        sys.excepthook = self._handle_exception
        self._suppress_external_loggers()

    def _update_handlers_if_needed(self) -> None:
        """
        Update handlers if date has changed
        """

        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self.current_date:
            self.current_date = current_date
            self._setup_logging()

    def _suppress_external_loggers(self) -> None:
        """
        Suppress noisy loggers
        """

        noisy_loggers = [
            "apscheduler",
            "apscheduler.executors.default",
            "sqlalchemy",
            "asyncio",
            "aiohttp",
            "aiohttp.access",
            "aiohttp.client",
            "aiohttp.internal",
            "aiohttp.server",
            "aiohttp.web",
            "aiohttp.websocket",
            "aiohttp.connector",
            "hypercorn",
            "hypercorn.error",
            "hypercorn.access",
            "hypercorn.asgi",
            "httpx",
        ]

        for name in noisy_loggers:
            logging.getLogger(name).setLevel(logging.CRITICAL)

    def _handle_exception(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Global exception handler that logs uncaught exceptions
        Preserves keyboard interrupt functionality

        Args:
            exc_type (type): Exception type
            exc_value (Exception): Exception value
            exc_traceback (traceback): Exception traceback
        """

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self.__logger.error(
            {
                "type": "uncaught exception",
                "exc_type": str(exc_type),
                "error": str(exc_value),
            }
        )

        self.__traceback_logger.error(str(format_tb(exc_traceback)))

    def get_logger(self, name: str) -> logging.Logger | None:
        """
        Returns logger instance

        Args:
            name (str): Logger name

        Returns:
            logging.Logger | None: Logger instance
        """

        if name == "main":
            return self.__logger
        elif name == "traceback":
            return self.__traceback_logger

        return None


class LoggerMeta(type):
    """
    Metaclass that wraps all public methods of the class
    so that __handle_traceback is called before each method
    """

    def __new__(cls, name: str, bases: Any, namespace: dict):
        for attr_name, attr_value in list(namespace.items()):
            if callable(attr_value) and not attr_name.startswith("_"):
                namespace[attr_name] = cls.__wrap_method(attr_name, attr_value, name)
        return super().__new__(cls, name, bases, namespace)

    @staticmethod
    def __wrap_method(_: Any, method: Callable, class_name: str) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if "message" in kwargs:
                message = kwargs["message"]
            elif args:
                message = args[0]
            else:
                message = None

            if isinstance(message, dict):
                mangled = f"_{class_name}__handle_traceback"
                getattr(self, mangled)(message)

            return method(self, *args, **kwargs)

        return wrapper


class CustomLogger(metaclass=LoggerMeta):
    """
    Custom logger class for handling application logging
    """

    def __init__(self):
        self.__logger = Logging().get_logger("main")
        self.__traceback_logger = Logging().get_logger("traceback")

    def __handle_traceback(self, message: dict) -> None:
        """
        Handle traceback in message

        Args:
            message (dict): Message to handle
        """

        if "traceback" in message:
            request_id = message.get("request_id", None)
            error = f"[{request_id}]\n\n{message['traceback']}\n------------------\n"
            self.__traceback_logger.error(error)
            del message["traceback"]

    def info(self, message: dict) -> None:
        """
        Log an info message

        Args:
            message (dict): Message to log
        """

        Logging()._update_handlers_if_needed()
        self.__logger.info(message)

    def error(self, message: dict) -> None:
        """
        Log an error message

        Args:
            message (dict): Message to log
        """

        Logging()._update_handlers_if_needed()
        self.__logger.error(message)

    def exception(self, message: dict) -> None:
        """
        Log a traceback message

        Args:
            message (dict): Message to log
        """

        Logging()._update_handlers_if_needed()
        self.__logger.exception(message)

    def warning(self, message: dict) -> None:
        """
        Log a warning message

        Args:
            message (dict): Message to log
        """

        Logging()._update_handlers_if_needed()
        self.__logger.warning(message)

    def debug(self, message: dict) -> None:
        """
        Log a debug message

        Args:
            message (dict): Message to log
        """

        Logging()._update_handlers_if_needed()
        self.__logger.debug(message)
