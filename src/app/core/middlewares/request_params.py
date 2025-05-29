import uuid

from collections.abc import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestParamsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add a request ID to the request
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Dispatch

        Args:
            request (Request): Request object
            call_next (Callable): Callable

        Returns:
            Response: Response object
        """

        request_id = str(uuid.uuid4())
        client_ip = request.headers.get("X-Original-Forwarded-For")
        if client_ip is None:
            client_ip = request.client.host

        request.state.request_id = request_id
        request.state.client_ip = client_ip
        request.state.traceback = None

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
