import datetime

from typing import Any
from functools import wraps
from traceback import format_exc
from fastapi import Request, Depends
from fastapi_decorators import depends
from fastapi.responses import JSONResponse

from app.core.metrics import app_metrics
from app.core.connectors.logging import logger
from app.core.connectors.db.redis import redis_connector


class Cache:
    """
    Cache class
    """

    def __init__(self, request: Request):
        self.request = request
        self.cache_key = f"cache:{request.method}:{request.url.path}"

    async def get(self) -> dict | None:
        """
        Get cached data

        Returns:
            dict | None: Cached data
        """

        try:
            data = await redis_connector.get(self.cache_key)
            if data:
                return JSONResponse(content=data, media_type="application/json")
        except Exception as e:
            logger.error(
                {
                    "type": "cache",
                    "request_id": self.request.state.request_id,
                    "client_ip": self.request.state.client_ip,
                    "method": self.request.method,
                    "path": self.request.url.path,
                    "error": str(e),
                    "traceback": format_exc(),
                }
            )
            app_metrics.record_error(self.request.method, self.request.url.path, "get_error")
        return None

    async def set(self, response: JSONResponse | dict, expire: int = 300) -> None:
        """
        Set cache data

        Args:
            response (JSONResponse | dict): Response to cache
            expire (int): Cache expiration time in seconds
        """

        try:
            if isinstance(response, dict):
                response = JSONResponse(content=response)

            if (
                self.request.method == "GET"
                and response.status_code == 200
                and "application/json" in response.headers.get("content-type", "")
            ):
                await redis_connector.set(self.cache_key, response.body, ex=expire)
                app_metrics.record_success(self.request.method, self.request.url.path)

                logger.info(
                    {
                        "type": "cache",
                        "request_id": self.request.state.request_id,
                        "client_ip": self.request.state.client_ip,
                        "method": self.request.method,
                        "path": self.request.url.path,
                        "expire": f"{expire} seconds",
                    }
                )
        except Exception as e:
            logger.error(
                {
                    "type": "cache",
                    "request_id": self.request.state.request_id,
                    "client_ip": self.request.state.client_ip,
                    "method": self.request.method,
                    "path": self.request.url.path,
                    "error": str(e),
                    "traceback": format_exc(),
                }
            )
            app_metrics.record_error(self.request.method, self.request.url.path, "set_error")


async def get_cache(request: Request) -> Cache | None:
    """Dependency for cache handling

    Args:
        request (Request): Request object

    Returns:
        Cache | None: Cache instance
    """

    return Cache(request)


def cached(expire: int = 300) -> Any:
    """
    Decorator for caching route responses.
    Returns cached result only if current time is before midnight,
    otherwise updates the cache.

    Args:
        expire (int): Cache expiration time in seconds
    """

    def decorator(func):
        @depends(cache=Depends(get_cache))
        @wraps(func)
        async def wrapper(*args, cache: Cache, **kwargs):
            now = datetime.datetime.now()
            next_midnight = (now + datetime.timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            try:
                if await redis_connector.exists(cache.cache_key) and now < next_midnight:
                    cached_response = await cache.get()
                    if cached_response:
                        return cached_response

                response = await func(*args, **kwargs)
                await cache.set(response, expire)
                return response
            except Exception as e:
                logger.error(
                    {
                        "type": "cache",
                        "request_id": cache.request.state.request_id,
                        "client_ip": cache.request.state.client_ip,
                        "method": cache.request.method,
                        "path": cache.request.url.path,
                        "error": str(e),
                        "traceback": format_exc(),
                    }
                )

        return wrapper

    return decorator
