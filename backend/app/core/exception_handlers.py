

# from fastapi import Request
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse

# from app.core.exceptions import AppException


# async def app_exception_handler(
#     request: Request,
#     exc: AppException,
# ) -> JSONResponse:
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "success": False,
#             "message": exc.message,
#         },
#     )


# async def validation_exception_handler(
#     request: Request,
#     exc: RequestValidationError,
# ) -> JSONResponse:
#     return JSONResponse(
#         status_code=422,
#         content={
#             "success": False,
#             "message": "Validation error",
#             "errors": exc.errors(),
#         },
#     )
    
    
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import AppException


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register centralized exception handlers.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ):
        response = {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        }

        if exc.details is not None:
            response["error"]["details"] = exc.details

        return JSONResponse(
            status_code=exc.status_code,
            content=response,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        errors = []

        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(
                        str(location)
                        for location in error.get("loc", [])
                    ),
                    "message": error.get("msg"),
                    "type": error.get("type"),
                }
            )

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": errors,
                },
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request,
        exc: IntegrityError,
    ):
        logger.exception(
            "Database integrity error: %s",
            request.url.path,
        )

        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_CONFLICT",
                    "message": "The requested operation violates a database constraint",
                },
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError,
    ):
        logger.exception(
            "Database error: %s",
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "A database error occurred",
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception(
            "Unhandled exception: %s",
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                },
            },
        )