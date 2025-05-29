from traceback import format_exc
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.connectors.logging import logger


class ErrorHandlers:
    def __init__(self, app: FastAPI):
        self.__app = app
        self.__set_errors()

    def __set_errors(self) -> JSONResponse:
        """
        Error handlers
        """

        @self.__app.exception_handler(400)
        @self.__app.exception_handler(403)
        async def _(request: Request, exc: HTTPException):
            """
            400, 403 Error handler

            Args:
                request (Request): Request object
                exc (HTTPException): HTTPException object

            Returns:
                JSONResponse: JSON response
            """

            logger.error(
                {
                    "type": "HTTPException",
                    "code": exc.status_code,
                    "request_id": request.state.request_id,
                    "client_ip": request.state.client_ip,
                    "method": request.method,
                    "path": request.url.path,
                    "error": exc.detail,
                }
            )

            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "status": "error",
                    "type": "bad request" if exc.status_code == 400 else "forbidden",
                    "error": exc.detail,
                    "request_id": request.state.request_id,
                },
            )

        @self.__app.exception_handler(404)
        @self.__app.exception_handler(405)
        async def _(request: Request, exc: HTTPException):
            """
            404, 405 Error handler

            Args:
                request (Request): Request object
                exc (HTTPException): HTTPException object

            Returns:
                JSONResponse: JSON response
            """
            logger.error(
                {
                    "type": "HTTPException",
                    "code": exc.status_code,
                    "request_id": request.state.request_id,
                    "client_ip": request.state.client_ip,
                    "method": request.method,
                    "path": request.url.path,
                    "error": exc.detail,
                }
            )

            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "status": "error",
                    "type": "not found" if exc.status_code == 404 else "method not allowed",
                    "error": exc.detail,
                    "request_id": request.state.request_id,
                },
            )

        @self.__app.exception_handler(500)
        async def _(request: Request, exc: HTTPException | Exception):
            """
            500 Error handler

            Args:
                request (Request): Request object
                exc (HTTPException | Exception): HTTPException or Exception object

            Returns:
                JSONResponse: JSON response
            """

            error_message = exc.detail if hasattr(exc, "detail") else str(exc)

            logger.error(
                {
                    "type": "HTTPException",
                    "code": 500,
                    "request_id": request.state.request_id,
                    "client_ip": request.state.client_ip,
                    "method": request.method,
                    "path": request.url.path,
                    "error": error_message,
                    "traceback": format_exc(),
                }
            )

            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "type": "server error",
                    "error": error_message,
                    "request_id": request.state.request_id,
                },
            )
