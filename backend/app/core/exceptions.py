import logging

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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
