
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.authorization import get_authenticated_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = NotificationService(db)

    return service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
    )


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = NotificationService(db)

    return {
        "unread_count": service.get_unread_count(
            current_user.id
        )
    }


@router.patch("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = NotificationService(db)

    updated_count = service.mark_all_as_read(
        current_user.id
    )

    return {
        "message": "All notifications marked as read",
        "updated_count": updated_count,
    }


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = NotificationService(db)

    return service.mark_as_read(
        notification_id=notification_id,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    service = NotificationService(db)

    service.delete_notification(
        notification_id=notification_id,
        current_user_id=current_user.id,
    )

    return None


