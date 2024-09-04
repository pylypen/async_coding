from fastapi import Request, HTTPException
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Обробник загальних помилок
async def custom_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )

# Обробник HTTP помилок
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def http_validation_handler(request: Request, exc: ResponseValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc._errors},
    )

