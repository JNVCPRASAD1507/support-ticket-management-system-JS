from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.users import router as users_router
from app.api.v1.tickets import router as ticket_router
from app.api.v1.comments import router as comment_router
from app.api.v1 import attachments
from app.api.v1 import notifications
from app.api.v1.audit_logs import router as audit_router


api_router = APIRouter()
    # (prefix="")


api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(categories_router)
api_router.include_router(ticket_router)
api_router.include_router(comment_router)
api_router.include_router(attachments.router)
api_router.include_router(notifications.router)
api_router.include_router(audit_router)

