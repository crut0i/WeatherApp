from typing import Any
from rich import traceback
from fastapi import APIRouter, FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.utils import base_utils
from app.core.views import home_routes
from app.core.handlers import ErrorHandlers
from app.core.decorators import log_operation
from app.core.connectors.config import config
from app.core.api.main.routes import main_routes
from app.core.api.v1.routes import services_routes
from app.core.connectors.db.sql import init_models
from app.core.connectors.db.redis import redis_connector
from app.core.middlewares import LoggingMiddleware, RequestParamsMiddleware, SessionMiddleware


class AppConfig:
    """
    Application configuration
    """

    def __init__(self):
        self.ORIGINS = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://weatherapp.crut0i.com",
        ]
        self.METHODS = ["*"]
        self.HEADERS = ["*"]
        self.CACHE_CLEANUP_INTERVAL = 5  # minutes
        self.ALLOW_CREDENTIALS = True


class App:
    """
    Main application class
    """

    def __init__(self):
        self.__app = FastAPI(
            lifespan=self.lifespan,
            docs_url=config.docs_url,
            redoc_url=config.redoc_url,
            openapi_url=config.openapi_url,
        )
        self.__setup_middleware()
        self.__setup_static_files()
        self.__setup_routes()
        self.__setup_instrumentation()
        self.__scheduler = AsyncIOScheduler()

        traceback.install()

    def __setup_middleware(self) -> None:
        """
        Setup application middleware
        """

        self.__app.add_middleware(
            CORSMiddleware,
            allow_origins=AppConfig().ORIGINS,
            allow_methods=AppConfig().METHODS,
            allow_headers=AppConfig().HEADERS,
            allow_credentials=AppConfig().ALLOW_CREDENTIALS,
        )

        self.__app.add_middleware(SessionMiddleware)
        self.__app.add_middleware(LoggingMiddleware)
        self.__app.add_middleware(RequestParamsMiddleware)

    def __setup_static_files(self) -> None:
        """
        Setup application static files
        """

        self.__app.mount(
            "/static", StaticFiles(directory=config.frontend_path + "/static"), name="static"
        )

    def __setup_routes(self) -> None:
        """
        Setup application routes
        """

        home_router = APIRouter()
        default_router = APIRouter(prefix="/api")
        api_router = APIRouter(prefix="/api/" + config.api_prefix)

        home_router.include_router(home_routes.router)
        default_router.include_router(main_routes.router)
        api_router.include_router(services_routes.router)

        self.__app.include_router(router=home_router)
        self.__app.include_router(router=default_router)
        self.__app.include_router(router=api_router)

    def __setup_instrumentation(self) -> None:
        """
        Setup application instrumentation
        """

        Instrumentator().instrument(self.__app).expose(app=self.__app, include_in_schema=False)
        ErrorHandlers(self.__app)

    async def __setup_db(self) -> None:
        """
        Setup application database
        """

        await init_models()

    @log_operation("job", "pycache_cleanup")
    async def __job_pycache_remove(self) -> None:
        """
        Adds a job to remove pycache
        """

        self.__scheduler.add_job(
            base_utils.remove_pycache,
            trigger=IntervalTrigger(minutes=AppConfig().CACHE_CLEANUP_INTERVAL),
            id="clear_cache",
            replace_existing=True,
        )

    @log_operation("start", "scheduler")
    async def __start_scheduler(self) -> None:
        """
        Start scheduler service
        """

        self.__scheduler.start()

    @log_operation("start", "redis")
    async def __start_redis(self) -> None:
        """
        Start Redis servic
        e"""

        await redis_connector.ping()

    @log_operation("stop", "scheduler")
    async def __stop_scheduler(self) -> None:
        """
        Stop scheduler service
        """

        self.__scheduler.shutdown()

    @log_operation("stop", "redis")
    async def __stop_redis(self) -> None:
        """
        Stop Redis service
        """

        await redis_connector.flushdb()
        await redis_connector.close()

    @asynccontextmanager
    async def lifespan(self, _: FastAPI) -> Any:
        """
        Manages the application lifecycle

        Args:
            _: FastAPI

        Returns:
            Any: Any
        """

        try:
            await self.__job_pycache_remove()
            await self.__start_scheduler()
            await self.__start_redis()
            await self.__setup_db()
            yield
        finally:
            await self.__stop_scheduler()
            await self.__stop_redis()

    @property
    def app(self) -> FastAPI:
        """
        Get application instance

        Returns:
            FastAPI: Application instance
        """

        return self.__app


app = App().app
