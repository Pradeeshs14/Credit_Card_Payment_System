import logging
import time

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("system_monitoring")


class RequestMonitoringMiddleware(MiddlewareMixin):
    """Log request duration, HTTP failures, and unexpected exceptions."""

    def process_request(self, request):
        request._monitoring_start_time = time.perf_counter()

    def process_response(self, request, response):
        start = getattr(request, "_monitoring_start_time", None)

        if start is not None:
            duration_ms = (time.perf_counter() - start) * 1000

            log_method = logger.warning if response.status_code >= 500 else logger.info

            log_method(
                "HTTP request | method=%s | path=%s | status=%s | duration_ms=%.2f",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
            )

        return response

    def process_exception(self, request, exception):
        logger.exception(
            "Unhandled request exception | method=%s | path=%s | error=%s",
            request.method,
            request.path,
            type(exception).__name__,
        )
        return None
