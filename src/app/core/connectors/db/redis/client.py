import asyncio
import logging
import redis.asyncio as redis

from functools import wraps
from typing import Any, TypeVar
from collections.abc import Callable, Awaitable

from app.core.connectors.config import config

T = TypeVar("T")


class RedisConnector:
    """
    Redis connector class
    """

    def __init__(self):
        self.__redis_host = config.redis_host
        self.__redis_port = config.redis_port
        self.__redis: redis.Redis | None = None
        self.__connect()

    @property
    def redis(self) -> redis.Redis:
        """Get Redis client"""
        if not self.__redis:
            self.__connect()
        return self.__redis

    def __connect(self) -> None:
        """
        Establish Redis connection
        """

        try:
            self.__redis = redis.Redis(
                host=self.__redis_host,
                port=self.__redis_port,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {str(e)}")
            raise

    @staticmethod
    def __retry_on_failure(max_retries: int = 3, retry_delay: int = 1):
        """
        Retry decorator for Redis operations
        """

        def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
            @wraps(func)
            async def wrapper(self, *args, **kwargs) -> T:
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        if not self.__redis:
                            self._connect()
                        return await func(self, *args, **kwargs)
                    except (redis.ConnectionError, redis.TimeoutError) as e:
                        last_exception = e
                        logging.warning(
                            {
                                "type": "redis",
                                "message": f"Redis operation failed (attempt \
                                    {attempt + 1}/{max_retries}): {str(e)}",
                            }
                        )
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (attempt + 1))
                            self._connect()
                raise last_exception

            return wrapper

        return decorator

    @__retry_on_failure()
    async def get(self, key: str) -> Any:
        """Get value from Redis"""
        return await self.__redis.get(key)

    @__retry_on_failure()
    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        """Set value in Redis"""
        await self.__redis.set(key, value, ex=ex)

    async def close(self) -> None:
        """Close Redis connection"""
        if self.__redis:
            await self.__redis.close()
