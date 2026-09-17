
from fastapi import FastAPI

from app.api.routers import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Support Ticket Management System Backend",
    debug=settings.debug,
)


app.include_router(api_router)


@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "Support Ticket Management System is running",
    }
    