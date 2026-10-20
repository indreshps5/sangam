"""
Global error handling middleware.
Catches exceptions and returns structured error responses.
"""

from typing import Callable
import json

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from sangam_api.core.exceptions import SANGAMException
from sangam_api.core.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that catches all exceptions and returns structured JSON errors.
    Follows RFC 7807 Problem Details format.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except SANGAMException as exc:
            logger.warning(
                "application_error",
                error_code=exc.error_code,
                message=exc.message,
                path=request.url.path,
            )
            return Response(
                content=json.dumps({
                    "type": f"https://sangam.io/errors/{exc.error_code}",
                    "title": exc.error_code,
                    "status": exc.status_code,
                    "detail": exc.message,
                    "instance": request.url.path,
                    **exc.details,
                }),
                status_code=exc.status_code,
                media_type="application/problem+json",
            )
        except Exception as exc:
            logger.error(
                "unhandled_error",
                error=str(exc),
                path=request.url.path,
                exc_info=True,
            )
            return Response(
                content=json.dumps({
                    "type": "https://sangam.io/errors/INTERNAL_ERROR",
                    "title": "Internal Server Error",
                    "status": 500,
                    "detail": "An unexpected error occurred",
                    "instance": request.url.path,
                }),
                status_code=500,
                media_type="application/problem+json",
            )
