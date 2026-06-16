import asyncio
import logging

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    error: str
    code: str
    details: dict | None = None


class AppError(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppError):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedError(AppError):
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ConflictError(AppError):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ForbiddenError(AppError):
    # 403: authenticated but lacks permission (vs UnauthorizedError=401 not authenticated)
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestError(AppError):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class RateLimitError(AppError):
    # Distinct from SlowAPI's auto RateLimitExceeded: use for explicit app-level limits
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
    body = ErrorResponse(
        error="Validation failed",
        code="VALIDATION_ERROR",
        details={"errors": exc.errors()},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body.model_dump()
    )


async def sqlalchemy_error_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    logger.error("Database error: %s", exc, exc_info=True)
    body = ErrorResponse(
        error="Service temporarily unavailable",
        code="DATABASE_ERROR",
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=body.model_dump()
    )


async def timeout_error_handler(
    request: Request, exc: asyncio.TimeoutError
) -> JSONResponse:
    logger.warning("Request timed out on %s", request.url.path)
    body = ErrorResponse(
        error="Request timed out",
        code="TIMEOUT",
    )
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT, content=body.model_dump()
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        body = ErrorResponse(
            error=exc.detail,
            code=f"HTTP_{exc.status_code}",
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())
    logger.exception("Unhandled exception: %s", exc)
    body = ErrorResponse(
        error="Internal server error",
        code="INTERNAL_ERROR",
    )
    return JSONResponse(status_code=500, content=body.model_dump())
