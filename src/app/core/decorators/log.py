from functools import wraps
from traceback import format_exc
from collections.abc import Callable

from app.core.connectors.logging import logger


class LogOperation:
    """
    Log operation class
    """

    def log_operation(self, operation_type: str, service_name: str = None) -> Callable:
        """
        Decorator for logging operations

        Args:
            operation_type: Type of operation (start, stop, etc.)
            service_name: Specific service name (redis, scheduler, etc.)
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    service_info = f" for {service_name}" if service_name else ""
                    logger.info(
                        {
                            "type": operation_type,
                            "service": service_name,
                            "status": "success",
                            "message": f"{operation_type} operation completed{service_info}",
                        }
                    )
                    return result
                except Exception as e:
                    logger.error(
                        {
                            "type": operation_type,
                            "service": service_name,
                            "status": "error",
                            "error": str(e),
                            "traceback": format_exc(),
                        }
                    )
                    raise

            return wrapper

        return decorator
