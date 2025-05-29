import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.connectors.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logging middleware
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Dispatches the request to the next middleware or handler

        Args:
            request (Request): Request object
            call_next (Callable): Callable

        Returns:
            Response: Response object
        """

        start_time = time.time()

        try:
            response: Response = await call_next(request)

            logger.info(
                {
                    "type": "request",
                    "request_id": request.state.request_id,
                    "client_ip": request.state.client_ip,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration": round(time.time() - start_time, 4),
                }
            )
        except Exception as e:
            logger.error(
                {
                    "type": "request",
                    "request_id": request.state.request_id,
                    "client_ip": request.state.client_ip,
                    "method": request.method,
                    "path": request.url.path,
                    "duration": round(time.time() - start_time, 4),
                    "error": str(e),
                }
            )
            raise

        return response
