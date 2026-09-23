# app/main.py

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import AppException

from app.api.routers import api_router
from app.core.config import settings
from app.core.exceptions import AppException
# from app.core.exception_handlers import (
#     app_exception_handler,
#     validation_exception_handler,
# )
from app.core.exception_handlers import register_exception_handlers


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Support Ticket Management System Backend",
    debug=settings.debug,
)


# app.add_exception_handler(
#     AppException,
#     app_exception_handler,
# )

# app.add_exception_handler(
#     RequestValidationError,
#     validation_exception_handler,
# )

# Register centralized exception handlers
register_exception_handlers(app)


app.include_router(api_router)

@app.get("/")
def root():
    return {
        "success": True,
        "message": "Welcome to Support Ticket Management System API",
        "version": "1.0.0",
    }

@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "Support Ticket Management System is running",
    }