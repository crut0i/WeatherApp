from prometheus_client import Counter


class AppMetrics:
    """
    Cache metrics implementation using Prometheus
    """

    def __init__(self):
        self._cache_success = Counter(
            "cache_success_total", "Total number of successful cache operations", ["method", "path"]
        )
        self._cache_errors = Counter(
            "cache_errors_total", "Total number of cache errors", ["method", "path", "error_type"]
        )
        self._traceback = Counter(
            "traceback_total",
            "Total number of tracebacks",
            ["request_id"],
        )

    def record_success(self, method: str, path: str) -> None:
        """Record a successful cache operation

        Args:
            method (str): Method name
            path (str): Path
        """

        self._cache_success.labels(method=method, path=path).inc()

    def record_error(self, method: str, path: str, error_type: str) -> None:
        """Record a cache error

        Args:
            method (str): Method name
            path (str): Path
            error_type (str): Error type
        """

        self._cache_errors.labels(method=method, path=path, error_type=error_type).inc()

    def traceback(self, request_id: str) -> None:
        """Record a traceback

        Args:
            request_id (str): Request ID
        """

        self._traceback.labels(request_id=request_id).inc()
