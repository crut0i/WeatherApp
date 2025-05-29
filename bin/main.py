import os
import sys
import asyncio
import importlib

from hypercorn.asyncio import serve
from hypercorn.config import Config
from collections.abc import Callable


class Entrypoint:
    def __init__(self, app_path: str):
        self.app_path = app_path

    def __load_app(self) -> Callable:
        """
            Load ASGI application from string path

        Args:
            app_path: String in format 'module:app'

        Returns:
            ASGI application object
        """

        module_path, app_name = self.app_path.split(":")
        module = importlib.import_module(module_path)
        return getattr(module, app_name)

    def run(self) -> None:
        """
        Project entrypoint
        """

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(project_root)
        sys.path.append(os.path.join(project_root, "src"))

        config = Config()
        config.bind = ["0.0.0.0:3000"]
        config.use_reloader = True
        config.worker_class = "asyncio"
        config.keep_alive_timeout = 65
        config.websocket_ping_interval = 20
        config.h11_max_incomplete_event_size = 16384
        config.http_version = "quic"
        config.errorlog = "-"
        config.loglevel = "critical"

        app = self.__load_app()
        asyncio.run(serve(app, config))


if __name__ == "__main__":
    Entrypoint("src:app").run()
