from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.utils import log_utils
from app.core.decorators import cached
from app.core.connectors.db.redis import redis_connector


class MainRoutes:
    """
    Main routes class
    """

    def __init__(self):
        self.router = APIRouter(tags=["Main Routes"])

        self.__set_default_routes()
        self.__set_log_routes()

    def __set_default_routes(self) -> None:
        """
        Set default API routes
        """

        @self.router.get(
            "/",
            response_class=RedirectResponse,
            status_code=302,
            description="Redirect to docs",
        )
        async def main_route():
            """
            Redirect to docs

            Returns:
                RedirectResponse: Redirect to docs
            """

            return RedirectResponse(url="/docs", status_code=302)

        @self.router.get(
            "/help",
            response_class=JSONResponse,
            status_code=200,
            description="Help message",
        )
        async def help():
            """
            Help message

            Returns:
                JSONResponse: Help message
            """

            return JSONResponse(
                status_code=200, content={"status": "success", "message": "documentation: /docs"}
            )

        @self.router.get(
            "/health",
            response_class=JSONResponse,
            status_code=200,
            description="Health check route",
        )
        async def health_route():
            """
            Health check route

            Returns:
                JSONResponse: Health check status
            """

            return JSONResponse(
                status_code=200, content={"status": "success", "message": "service is up"}
            )

    def __set_log_routes(self) -> None:
        """
        Set log API routes
        """

        @self.router.get(
            "/logs",
            response_class=JSONResponse,
            status_code=200,
            description="Get list of available log dates",
        )
        @self.router.get(
            "/exceptions",
            response_class=JSONResponse,
            status_code=200,
            description="Get list of available exception dates",
        )
        @cached(expire=3600)
        async def logs_list(request: Request):
            """
            Get list of available log dates

            Args:
                request (Request): Request object

            Returns:
                JSONResponse: List of available log dates
            """

            pattern = (
                "exception_*.log" if request.url.path.startswith("/exceptions") else "log_*.log"
            )

            return JSONResponse(
                status_code=200,
                content={"status": "success", "dates": log_utils.get_available_dates(pattern)},
            )

        @self.router.get(
            "/logs/{date}",
            response_class=JSONResponse,
            status_code=200,
            description="Get content of log file for specific date",
        )
        @self.router.get(
            "/exceptions/{date}",
            response_class=JSONResponse,
            status_code=200,
            description="Get content of exception file for specific date",
        )
        async def get_log_content(request: Request, date: str):
            """
            Get content of log file for specific date

            Args:
                date (str): Date of log file
                request (Request): Request object

            Returns:
                JSONResponse: Content of log file
            """

            pattern = "exception" if request.url.path.startswith("/exceptions") else "log"
            return JSONResponse(status_code=200, content=log_utils.get_log_content(date, pattern))

        @self.router.delete(
            "/logs/{date}",
            response_class=JSONResponse,
            status_code=200,
            description="Delete log for specific date",
        )
        @self.router.delete(
            "/exceptions/{date}",
            response_class=JSONResponse,
            status_code=200,
            description="Delete exception for specific date",
        )
        async def delete_log(request: Request, date: str):
            """
            Delete log for specific date

            Args:
                date (str): Date of log file
                request (Request): Request object

            Returns:
                JSONResponse: Deleted log file
            """

            if date == datetime.now().strftime("%Y-%m-%d"):
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "detail": "cannot delete logs for current day"},
                )

            pattern = "exception" if request.url.path.startswith("/exceptions") else "log"
            path = "/exceptions" if pattern == "exception" else "/logs"

            await redis_connector.delete(f"cache:GET:{path}")
            return JSONResponse(status_code=200, content=log_utils.delete_log(date, pattern))
