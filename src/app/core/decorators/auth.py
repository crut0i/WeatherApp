from typing import Any
from functools import wraps
from fastapi import Request, Depends
from fastapi_decorators import depends
from fastapi.responses import JSONResponse

from app.core.connectors.config import config
from app.core.connectors.logging import logger


class Auth:
    """
    Auth class for handling authorization
    """

    def __init__(self, request: Request):
        self.request = request
        self.__auth_header = request.headers.get("Authorization")

    def validate_token(self) -> bool:
        """
        Validate authorization token

        Returns:
            bool: True if token is valid, False otherwise
        """

        if not self.__auth_header or self.__auth_header != config.auth_token:
            return False

        return True


async def get_auth(request: Request) -> Auth:
    """Dependency for auth handling

    Args:
        request (Request): Request object

    Returns:
        Auth: Auth instance
    """

    return Auth(request)


async def auth_error(request: Request, error_message: str) -> JSONResponse:
    """Auth error

    Args:
        request (Request): Request object
        error_message (str): Error message

    Returns:
        JSONResponse: JSON response
    """

    logger.error(
        {
            "type": "HTTPException",
            "code": 401,
            "request_id": request.state.request_id,
            "client_ip": request.state.client_ip,
            "method": request.method,
            "path": request.url.path,
            "error": error_message,
        }
    )

    return JSONResponse(
        status_code=401,
        content={
            "status": "error",
            "type": "unauthorized",
            "error": error_message,
            "request_id": request.state.request_id,
        },
    )


def require_auth() -> Any:
    """
    Decorator for checking authorization token.
    Returns 401 if token is missing or invalid.
    """

    def decorator(func):
        @depends(auth=Depends(get_auth))
        @wraps(func)
        async def wrapper(*args, auth: Auth, **kwargs):
            if not auth.validate_token():
                return await auth_error(auth.request, "Authorization token is missing or invalid")

            return await func(*args, **kwargs)

        return wrapper

    return decorator
