from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging_config import get_logger
from app.exceptions.business_exception import BusinessException

logger = get_logger(__name__)

VALIDATION_ERROR_CODE = "VAL_001"

INTERNAL_ERROR_CODE = "SYS_001"

DATABASE_ERROR_CODE = "SYS_002"


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(BusinessException)
    async def handle_business_exception(
            request: Request,
            exception: BusinessException
    ) -> JSONResponse:

        logger.warning(
            "Business rule violated: %s %s - %s (%s)",
            request.method,
            request.url.path,
            exception.code,
            exception.message
        )

        return JSONResponse(
            status_code=exception.http_status,
            content={
                "code": exception.code,
                "message": exception.message
            }
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
            request: Request,
            exception: RequestValidationError
    ) -> JSONResponse:

        return JSONResponse(
            status_code=422,
            content={
                "code": VALIDATION_ERROR_CODE,
                "message": "Request validation failed.",
                "details": _serialize_errors(exception.errors())
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_database_error(
            request: Request,
            exception: SQLAlchemyError
    ) -> JSONResponse:

        logger.exception(
            "Database error on %s %s",
            request.method,
            request.url.path
        )

        return JSONResponse(
            status_code=500,
            content={
                "code": DATABASE_ERROR_CODE,
                "message": "A database error occurred."
            }
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
            request: Request,
            exception: Exception
    ) -> JSONResponse:

        logger.exception(
            "Unhandled error on %s %s",
            request.method,
            request.url.path
        )

        return JSONResponse(
            status_code=500,
            content={
                "code": INTERNAL_ERROR_CODE,
                "message": "An unexpected error occurred."
            }
        )


def _serialize_errors(errors: list) -> list:
    """Drop non JSON-serialisable context pydantic may attach."""

    serialized = []

    for error in errors:
        serialized.append({
            "location": [str(part) for part in error.get("loc", [])],
            "message": error.get("msg", ""),
            "type": error.get("type", "")
        })

    return serialized
